from flask import Flask, render_template, request, send_from_directory
import os
import markdown

app = Flask(__name__)

@app.route('/')
def index():
    # List all markdown files in the markdown_files directory
    markdown_files = [f for f in os.listdir('daily_news') if f.endswith('.md')]
    markdown_files = sorted(markdown_files)
    return render_template('index.html', files=markdown_files)

@app.route('/view/<filename>')
def view_file(filename):
    # Ensure the file is a markdown file
    if not filename.endswith('.md'):
        return "Invalid file type.", 400
    
    # Read the content of the markdown file
    with open(os.path.join('daily_news', filename), 'r') as f:
        content = f.read()

    # Convert markdown content to HTML
    html_content = markdown.markdown(content)
    return render_template('view.html', content=html_content, filename=filename)

@app.route('/markdown_files/<path:filename>')
def download_file(filename):
    # Provide a download route for the markdown files
    return send_from_directory('markdown_files', filename)

if __name__ == '__main__':
    app.run(debug=True)
