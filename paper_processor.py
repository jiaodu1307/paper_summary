import os
import re
import csv
import pdfplumber
from openai import OpenAI
import yaml
from datetime import datetime
from tqdm import tqdm

class PaperProcessor:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self.client = OpenAI(api_key=self.config['deepseek']['api_key'], base_url="https://api.deepseek.com")
        self.domain_labels = {
            'high_priority': ['Medical_AI', 'Fintech', 'Quantum_Physics', 'Climate_Model'],
            'method': ['Experimental', 'Theoretical', 'Review'],
            'application': ['Healthcare', 'Finance', 'Energy']
        }

    def _load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def extract_metadata(self, pdf_path):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages[:3]:  # 只读取前三页来提取元数据
                    text += page.extract_text() + "\n"

                # 使用AI模型提取元数据
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "请从以下文本中提取论文的标题、作者（前三位）和年份，格式为JSON：{\"title\": \"\", \"authors\": [], \"year\": \"\", \"language\": \"EN\"}"},
                        {"role": "user", "content": text}
                    ]
                )
                metadata = eval(response.choices[0].message.content)
                return metadata
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return None

    def generate_filename(self, metadata):
        # 处理作者
        first_author = metadata['authors'][0].split()[-1] if metadata['authors'] else 'Unknown'
        author_str = f"{first_author}_etal" if len(metadata['authors']) > 1 else first_author

        # 处理标题
        title = metadata['title']
        # 移除常见的停用词
        stop_words = ['a', 'an', 'the', 'investigation', 'of', 'on', 'in', 'at', 'to']
        for word in stop_words:
            title = re.sub(f'\\b{word}\\b', '', title, flags=re.IGNORECASE)
        
        # 提取关键词并限制长度
        keywords = re.sub('[^a-zA-Z0-9\\s-]', '', title)
        keywords = '-'.join(keywords.split()[:3])[:30]

        # 组合文件名
        new_filename = f"{author_str}_{metadata['year']}_{keywords}.pdf"
        return new_filename

    def classify_paper(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:5]:  # 读取前5页用于分类
                text += page.extract_text() + "\n"

        # 使用AI模型进行分类
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "请分析文本并返回最相关的领域标签（从" + str(self.domain_labels) + "中选择）和置信度，格式为JSON：{\"labels\": [], \"confidence\": 0.0}"},
                {"role": "user", "content": text}
            ]
        )
        classification = eval(response.choices[0].message.content)
        return classification

    def process_papers(self, input_dir, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        report_data = []

        for root, _, files in os.walk(input_dir):
            for file in tqdm(files):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    warnings = []

                    # 提取元数据
                    metadata = self.extract_metadata(pdf_path)
                    if not metadata:
                        continue

                    # 生成新文件名
                    new_filename = self.generate_filename(metadata)

                    # 处理文件名冲突
                    base_name = new_filename[:-4]
                    ext = new_filename[-4:]
                    counter = 1
                    while os.path.exists(os.path.join(output_dir, new_filename)):
                        new_filename = f"{base_name}_v{counter}{ext}"
                        counter += 1
                        warnings.append(f"文件名冲突，已重命名为{new_filename}")

                    # 分类论文
                    classification = self.classify_paper(pdf_path)
                    
                    # 创建分类目录
                    class_path = os.path.join(output_dir, '_'.join(classification['labels']))
                    os.makedirs(class_path, exist_ok=True)

                    # 复制文件到新位置
                    new_path = os.path.join(class_path, new_filename)
                    with open(pdf_path, 'rb') as src, open(new_path, 'wb') as dst:
                        dst.write(src.read())

                    # 添加到报告
                    report_data.append({
                        '原文件名': file,
                        '新文件名': new_filename,
                        '分类路径': '/'.join(classification['labels']),
                        '置信度': f"{classification['confidence']*100:.0f}%",
                        '警告信息': '; '.join(warnings) if warnings else '无'
                    })

        # 生成CSV报告
        report_path = os.path.join(output_dir, 'processing_report.csv')
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['原文件名', '新文件名', '分类路径', '置信度', '警告信息'])
            writer.writeheader()
            writer.writerows(report_data)

        return report_path

if __name__ == "__main__":
    processor = PaperProcessor()
    input_dir = r"C:\Users\jiaod\Desktop\learning\paper\paper_summary\test_pdf"  # 输入PDF文件夹路径
    output_dir = r"C:\Users\jiaod\Desktop\learning\paper\paper_summary\test_processor"  # 输出文件夹路径
    report_path = processor.process_papers(input_dir, output_dir)
    print(f"处理完成，报告已保存至：{report_path}")