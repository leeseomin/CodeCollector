# CodeCollector

### "CodeCollector: A Gradio Web UI"

<img src="https://github.com/leeseomin/CodeCollector/blob/main/pic/4.png" width="100%">

<br>

<br>

### Key Features

1. Code extraction by language:
   - The code selectively extracts code files from a GitHub repository based on the file extensions specified by the user.
   - The extracted files are saved in the "down_code" directory.

2. Merging into a single Markdown file:
   - The extracted code files are merged into a single Markdown document.
   - The content of each file is included in the Markdown document along with the file path and language type.
   - The merged Markdown document is saved in the "merged" directory with the name "combined_code_files.md".



## Running the Application

To run the CodeCollector application, execute the following command:

```
python run_12.py
```

<br/>

The application will launch a Gradio web UI where you can input the GitHub repository URL, specify the file extensions, and perform code extraction and Markdown merging with the click of a button.




## Application

By leveraging this application, users can upload a generated markdown document to a Large Language Model (LLM), enabling them to engage in a wide range of discussions and gain valuable insights pertaining to their specific project.

<img src="https://github.com/leeseomin/CodeCollector/blob/main/pic/ex.png" width="100%">



