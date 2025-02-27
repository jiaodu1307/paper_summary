import os
import yaml
import pdfplumber
import openai
from tqdm import tqdm
import frontmatter
from openai import OpenAI

# 读取配置文件
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# 提取PDF文本
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# 截断文本以适应模型的最大上下文长度
def truncate_text(text, max_tokens=65536):
    words = text.split()
    truncated_text = ' '.join(words[:max_tokens])
    return truncated_text

# 生成Markdown内容
def generate_markdown(title, summary, methods, contributions, references):
    markdown_content = f"## [{title}]\n"
    markdown_content += f"### [{title}]\n"  # 这里可以直接使用标题
    markdown_content += f"- **核心结论**: {summary}\n"
    markdown_content += f"- **研究方法**: {methods}\n"
    markdown_content += f"- **关键贡献**: {contributions}\n"
    markdown_content += f"- **关联文献**: {references}\n"
    return markdown_content

# 调用OpenAI API生成内容
def generate_summary(text):
    client = OpenAI(api_key=config['deepseek']['api_key'], base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "请总结以下文献的核心结论、研究方法和关键贡献："},
            {"role": "user", "content": text},
        ],
        stream=False
    )
    return response.choices[0].message.content  # 返回生成的摘要

# 主程序
if __name__ == "__main__":
    config = load_config()
    
    # 使用用户提供的PDF文件夹和Notes文件夹地址
    pdf_directory = r"C:\Users\jiaod\Desktop\learning\paper\paper_summary\test_pdf"
    notes_directory = r"C:\Users\jiaod\Desktop\learning\paper\paper_summary\test_notes"

    # 确保目标目录存在
    os.makedirs(notes_directory, exist_ok=True)

    for root, dirs, files in os.walk(pdf_directory):
        for file in tqdm(files):
            if file.endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                text = extract_text_from_pdf(pdf_path)
                
                # 使用文件名作为标题
                title = file[:-4]  # 去掉文件扩展名
                
                # 截断文本以适应模型的最大上下文长度
                truncated_text = truncate_text(text)
                
                # 生成摘要
                summary = generate_summary(truncated_text)
                
                # 生成Markdown内容
                markdown_content = generate_markdown(title, summary, "方法论内容", "关键贡献内容", "关联文献内容")
                
                # 保存Markdown文件
                md_file_path = os.path.join(notes_directory, f"{title}.md")
                with open(md_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(markdown_content)