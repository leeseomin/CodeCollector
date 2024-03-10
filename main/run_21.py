import os
import re
import subprocess
import tempfile
import gradio as gr
import shutil
import ast
import coverage
from radon.complexity import cc_visit
from modulegraph.modulegraph import ModuleGraph

def clear_download_folder():
    download_dir = os.path.join(os.getcwd(), "down_code")
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)

def extract_code_files(repo_url, file_extensions):
    clear_download_folder()
    download_dir = os.path.join(os.getcwd(), "down_code")
    os.makedirs(download_dir, exist_ok=True)
    if not re.match(r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$', repo_url):
        return "Error: Invalid GitHub repository URL.", []
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            process = subprocess.Popen(["git", "clone", "--progress", repo_url, temp_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                print(line.decode('utf-8'), end='')
            process.wait()
            if process.returncode != 0:
                return f"Error: Failed to clone the repository. Return code: {process.returncode}", []
            downloaded_files = []
            valid_extensions = ['.py', '.js', '.java', '.c', '.cpp', '.h', '.kt', '.html', '.css', '.md', '.go', '.rs', '.ts', '.rb', '.php', '.cs', '.swift', '.ipynb', '.csproj']
            invalid_extensions = [ext for ext in file_extensions if ext not in valid_extensions]
            if invalid_extensions:
                return f"Error: Invalid file extensions: {', '.join(invalid_extensions)}", []
            for root, dirs, files in os.walk(temp_dir):
                dirs[:] = [d for d in dirs if d not in ['.git', '.github']]
                for file in files:
                    if any(file.endswith(ext) for ext in file_extensions):
                        full_path = os.path.join(root, file)
                        downloaded_files.append(os.path.relpath(full_path, start=temp_dir))
                        dest_path = os.path.join(download_dir, os.path.relpath(full_path, start=temp_dir))
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(full_path, dest_path)
            return "Extraction completed successfully.", downloaded_files
        except (subprocess.CalledProcessError, OSError, ValueError) as e:
            return f"Error: {str(e)}", []

def combine_code_files_to_markdown(repo_url, downloaded_files):
    repo_name = repo_url.split('/')[-1]
    merged_dir = os.path.join(os.getcwd(), "merged")
    os.makedirs(merged_dir, exist_ok=True)
    markdown_document_path = os.path.join(merged_dir, f"{repo_name}.md")
    repo_structure_content = ""
    with open(markdown_document_path, 'w') as md_file:
        md_file.write(f"# GitHub Repository: {repo_url}\n\n")
        md_file.write("## Repository Structure\n")
        for file_path in downloaded_files:
            md_file.write(f"- {file_path}\n")
            repo_structure_content += f"- {file_path}\n"
        md_file.write("\n")
        readme_file = None
        for file_path in downloaded_files:
            if file_path.lower() == 'readme.md':
                readme_file = file_path
                break
        if readme_file:
            md_file.write("## README.md\n")
            with open(os.path.join(os.getcwd(), "down_code", readme_file), 'r') as readme:
                md_file.write(readme.read())
            md_file.write("\n\n")
        for file_path in downloaded_files:
            if file_path != readme_file:
                language = get_language_by_extension(file_path)
                md_file.write(f"## File: {file_path}\n")
                md_file.write(f"### Language: {language}\n")
                md_file.write(f"### Description:\n")
                md_file.write(f"This file contains the implementation of...\n\n")
                md_file.write(f"### Code:\n")
                md_file.write(f"```{language}\n")
                with open(os.path.join(os.getcwd(), "down_code", file_path), 'r') as code_file:
                    code_content = code_file.read()
                    md_file.write(code_content)
                md_file.write("\n```\n\n")
    return f"Combined Markdown document created at: {markdown_document_path}", repo_structure_content

def get_language_by_extension(file_path):
    extension_to_language = {
        '.py': 'python',
        '.js': 'javascript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'cpp',
        '.kt': 'kotlin',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.go': 'go',
        '.rs': 'rust',
        '.ts': 'typescript',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.ipynb': 'json',
        '.csproj': 'xml'
    }
    _, ext = os.path.splitext(file_path)
    return extension_to_language.get(ext, 'plaintext')


def extract_core_code(repo_url):
    merged_dir = os.path.join(os.getcwd(), "merged")
    repo_name = repo_url.split('/')[-1]
    combined_md_file = os.path.join(merged_dir, f"{repo_name}.md")
    core_md_file = os.path.join(merged_dir, f"core_{repo_name}.md")

    if not os.path.exists(combined_md_file):
        return f"No combined Markdown file found for the repository: {repo_url}. Please merge the code files first."

    core_code_files = []
    total_lines = 0
    core_lines = 0
    repo_structure = ""
    readme_content = ""

    with open(combined_md_file, 'r') as combined_md:
        content = combined_md.read()
        repo_structure_match = re.search(r"## Repository Structure\n(.*?)\n##", content, re.DOTALL)
        if repo_structure_match:
            repo_structure = repo_structure_match.group(1)
        readme_match = re.search(r"## README\.md\n(.*?)\n##", content, re.DOTALL)
        if readme_match:
            readme_content = readme_match.group(1)

    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "down_code")):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    source_code = f.read()
                    total_lines += len(source_code.split('\n'))
                    tree = ast.parse(source_code)
                    if is_complex(tree, complexity_threshold=25):
                        core_code_files.append(file_path)
                        core_lines += len(source_code.split('\n'))

    with open(core_md_file, 'w') as core_md:
        core_md.write(f"# Core Code Files for Repository: {repo_url}\n\n")
        core_md.write(f"## Repository Structure\n{repo_structure}\n")
        core_md.write(f"## README.md\n{readme_content}\n")
        for file_path in core_code_files:
            core_md.write(f"## File: {file_path}\n")
            core_md.write(f"```python\n")
            with open(file_path, 'r') as code_file:
                code_content = code_file.read()
                core_md.write(code_content)
            core_md.write("\n```\n\n")

    removal_percentage = (1 - core_lines / total_lines) * 100
    return f"Core code Markdown document created at: {core_md_file}. Removed {removal_percentage:.2f}% of the code."
    

def is_complex(tree, complexity_threshold):
    complexity_score = sum([fn.complexity for fn in cc_visit(tree)])
    return complexity_score > complexity_threshold

    
    

def is_high_coverage(file_path, cov):
    cov.start()
    try:
        with open(file_path, 'r') as file:
            code = compile(file.read(), file_path, 'exec')
            try:
                exec(code, {'__name__': '__main__'})
            except SystemExit:
                pass
    except Exception as e:
        pass
    cov.stop()
    cov.save()
    analysis_result = cov.analysis(file_path)
    missing_lines = analysis_result[2]
    cov.erase()
    return len(missing_lines) == 0
    
    

def is_highly_dependent(file_path):
    graph = ModuleGraph()
    graph.run_script(file_path)
    num_dependencies = len([edge for edge in graph.edges() if edge[0].identifier == file_path])
    return num_dependencies > 5

def setup_gradio_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# GitHub Code File Extractor and Markdown Combiner")
        gr.Markdown("Download code files from a GitHub repository and combine them into a Markdown document.")
        with gr.Row():
            repo_url_input = gr.Textbox(label="GitHub Repository URL", placeholder="https://github.com/username/repository")
            file_extensions_input = gr.Textbox(label="File Extensions (comma-separated)", value=".py, .js, .java, .c, .cpp, .h, .kt, .html, .css, .md, .go, .rs, .ts, .rb, .php, .cs, .swift, .ipynb, .csproj")
        with gr.Row():
            extract_button = gr.Button("Extract Code Files")
            combine_button = gr.Button("Merge to Markdown")
            core_button = gr.Button("Extract Core Code")
            clear_button = gr.Button("Clear Output")
        output_text = gr.Textbox(label="Output", lines=10, interactive=False)
        
        def extract_files(repo_url, file_extensions):
            file_extensions = [ext.strip() for ext in file_extensions.split(',')]
            message, _ = extract_code_files(repo_url, file_extensions)
            return message
        
        def merge_to_markdown(repo_url, file_extensions):
            file_extensions = [ext.strip() for ext in file_extensions.split(',')]
            _, downloaded_files = extract_code_files(repo_url, file_extensions)
            if downloaded_files:
                markdown_path, repo_structure = combine_code_files_to_markdown(repo_url, downloaded_files)
                return f"{markdown_path}\n\n## Repository Structure\n{repo_structure}"
            return "No files to combine. Please extract files first."
        
        def extract_core(repo_url):
            message = extract_core_code(repo_url)
            return message
        
        extract_button.click(fn=extract_files, inputs=[repo_url_input, file_extensions_input], outputs=output_text)
        combine_button.click(fn=merge_to_markdown, inputs=[repo_url_input, file_extensions_input], outputs=output_text)
        core_button.click(fn=extract_core, inputs=repo_url_input, outputs=output_text)
        clear_button.click(lambda: "", None, output_text)
    
    return interface

interface = setup_gradio_interface()
interface.launch()

