# CodeCollector 

TL;DR: This **Gradio web app** allows users to **extract code files from GitHub repositories, merge them into a Markdown document**, and identify core code files using complexity, coverage, and dependency analysis.

<img src="https://github.com/leeseomin/CodeCollector/blob/main/pic/4.png" width="100%">

<br>

<br>

### 💙 Key Features 💙

1. Code extraction by language:
   - The code selectively extracts code files from a GitHub repository based on the file extensions specified by the user.
   - The extracted files are saved in the "down_code" directory.

2. Merging into a single Markdown file:
   - The extracted code files are merged into a single Markdown document.
   - The content of each file is included in the Markdown document along with the file path and language type.
   - The merged Markdown document is saved in the "merged" directory with the name "repo_name.md".

3. Automatically incorporates text from related arxiv papers linked in the readme into the merged markdown file (if such paper links exist).
   - If the readme.md file for the GitHub project contains any links to related papers on https://arxiv.org/,
     the tool will automatically detect these links, download the corresponding PDF files using wget, extract the text content from the PDFs, and append this extracted text to the merged markdown file

4. Core Code Extraction: experimental feature 
   - It identifies the core code using techniques such as AST analysis, code coverage analysis, and dependency analysis.
   - Files with high complexity, high test coverage, and many dependencies are considered as core code.
   - It generates a separate Markdown document containing only the core code.
   - This feature helps in quickly understanding the essential parts of the repository.
   - The merged Markdown document is saved in the "merged" directory with the name "core_repo_name.md".


## 🟧 Running the Application

To run the CodeCollector application, execute the following command:

```
python run_12.py
```

<br/>

The application will launch a Gradio web UI where you can input the GitHub repository URL, specify the file extensions, and perform code extraction and Markdown merging with the click of a button.


## 🟧 Running the Application : advanced mode 
(⭐⭐ An experimental feature for extracting core code has been added, and related papers are also downloaded together.)

```
pip install astroid coverage modulegraph pylint radon gradio pdfminer.six wget httpx==0.25.0

```

```
python run_23.py 
```



## 🟩 Application

By leveraging this application, users can upload a generated markdown document to a Large Language Model (LLM), enabling them to engage in a wide range of discussions and gain valuable insights pertaining to their specific project.

<img src="https://github.com/leeseomin/CodeCollector/blob/main/pic/ex.png" width="100%">



