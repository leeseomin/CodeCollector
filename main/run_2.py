import os
import re
import subprocess
import tempfile
import gradio as gr
import shutil

def extract_code_files(repo_url, file_extensions):
    # Path to the down_code directory in the current working directory of the script
    download_dir = os.path.join(os.getcwd(), "down_code")
    os.makedirs(download_dir, exist_ok=True)  # Create down_code if it doesn't exist

    # Validate the GitHub repository URL
    if not re.match(r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$', repo_url):
        return "Error: Invalid GitHub repository URL."

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository with a progress indicator
            process = subprocess.Popen(["git", "clone", "--progress", repo_url, temp_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                print(line.decode('utf-8'), end='')
            process.wait()

            if process.returncode != 0:
                return f"Error: Failed to clone the repository. Return code: {process.returncode}"

            code_files = []
            file_extensions = [ext.strip() for ext in file_extensions.split(',')]
            for root, dirs, files in os.walk(temp_dir):
                dirs[:] = [d for d in dirs if d not in ['.git', '.github']]  # Exclude .git and .github directories
                for file in files:
                    if any(file.endswith(ext) for ext in file_extensions):
                        full_path = os.path.join(root, file)
                        code_files.append(os.path.relpath(full_path, start=temp_dir))

                        # Determine the relative path for the file to preserve directory structure
                        rel_path = os.path.relpath(full_path, start=temp_dir)
                        # Create the same structure in download_dir
                        dest_path = os.path.join(download_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(full_path, dest_path)

            if code_files:
                message = "Code files downloaded:\n" + "\n".join(code_files)
            else:
                message = "No code files found with the specified extensions."
            return message

        except subprocess.CalledProcessError as e:
            return f"Error: {str(e)}"

def setup_gradio_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# GitHub Code File Extractor")
        gr.Markdown("Download code files from a GitHub repository to the 'down_code' folder.")

        with gr.Row():
            repo_url_input = gr.Textbox(label="GitHub Repository URL", placeholder="https://github.com/username/repository")
            file_extensions_input = gr.Textbox(label="File Extensions (comma-separated)", value=".c, .cpp, .h, .java, .py, .rs, .go, .js, .ts, .rb, .php")

        with gr.Row():
            extract_button = gr.Button("Extract Code Files")
            clear_button = gr.Button("Clear Output")

        output_text = gr.Textbox(label="Output", lines=10)

        extract_button.click(fn=extract_code_files, inputs=[repo_url_input, file_extensions_input], outputs=output_text)
        clear_button.click(lambda: "", None, output_text, queue=False)

    return interface

# Launch the web UI
interface = setup_gradio_interface()
interface.launch()


