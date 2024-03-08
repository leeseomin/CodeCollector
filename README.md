# CodeCollector

### "CodeCollector: A Gradio Web UI"

<img src="https://github.com/leeseomin/CodeCollector/blob/main/pic/3.png" width="100%">

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
python run_8.py
```

<br/>

The application will launch a Gradio web UI where you can input the GitHub repository URL, specify the file extensions, and perform code extraction and Markdown merging with the click of a button.
