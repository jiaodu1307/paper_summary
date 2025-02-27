# 文献摘要生成器

## 项目简介
文献摘要生成器是一个Python项目，旨在自动提取PDF文献中的文本内容，并使用DeepSeek API生成文献的核心结论、研究方法和关键贡献的摘要。生成的摘要将以Markdown格式保存，方便后续的文献管理和阅读。

## 功能
- 递归扫描指定目录下的PDF文件。
- 提取PDF文件中的文本内容。
- 使用DeepSeek API生成文献摘要。
- 将生成的摘要以Markdown格式保存到指定目录。

## 依赖
- Python 3.x
- `pdfplumber`：用于提取PDF文本。
- `openai`：用于调用DeepSeek API。
- `PyYAML`：用于读取配置文件。
- `tqdm`：用于显示进度条。

## 安装
1. 克隆此项目：
   ```bash
   git clone <your-repo-url>
   cd paper_summary
   ```

2. 创建并激活虚拟环境（可选）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Linux或macOS上
   venv\Scripts\activate  # 在Windows上
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 配置
在项目根目录下创建一个名为 `config.yaml` 的文件，内容如下：
```yaml
model_params:
  temperature: 0.7
  top_p: 0.9
file_paths:
  pdf_directory: "C:/Users/jiaod/Desktop/learning/paper/paper_summary/test_pdf"
  notes_directory: "C:/Users/jiaod/Desktop/learning/paper/paper_summary/test_notes"
prompt_template: "请总结以下文献的核心结论、研究方法和关键贡献："
deepseek:
  api_key: "YOUR_DEEPSEEK_API_KEY"
```

请将 `YOUR_DEEPSEEK_API_KEY` 替换为您的实际API密钥。

## 使用
1. 将PDF文件放入指定的 `pdf_directory` 目录。
2. 运行主程序：
   ```bash
   python main.py
   ```
3. 生成的Markdown文件将保存在指定的 `notes_directory` 目录中。

## 注意事项
- 确保您的网络连接正常，以便能够访问DeepSeek API。
- 如果PDF文件内容较长，可能需要调整文本截断的逻辑，以确保不会超过API的最大上下文长度。

## 贡献
欢迎任何形式的贡献！请提交问题或拉取请求。

## 许可证
此项目采用MIT许可证，详情请参阅LICENSE文件。
