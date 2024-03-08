import os
import subprocess
import tempfile
import gradio as gr
import shutil

def extract_code_files(repo_url):
    # Path to the down_code directory in the current working directory of the script
    download_dir = os.path.join(os.getcwd(), "down_code")
    os.makedirs(download_dir, exist_ok=True)  # Create down_code if it doesn't exist
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True)
            
            code_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.c', '.cpp', '.h', '.java', '.py')):
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
                message = "No code files found."
                
            return message
        
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output.decode()}"

def setup_gradio_interface():
    with gr.Blocks() as interface:
        repo_url_input = gr.Textbox(label="GitHub Repository URL")
        output_text = gr.Textbox(label="Output", lines=10)
        
        extract_button = gr.Button("Extract Code Files")
        extract_button.click(fn=extract_code_files, inputs=repo_url_input, outputs=output_text)

        interface.title = "GitHub Code File Extractor"
        interface.description = "Download code files (.c, .cpp, .h, .java, .py) from a GitHub repository to the 'down_code' folder."
    
    return interface

# Launch the web UI
interface = setup_gradio_interface()
interface.launch()
