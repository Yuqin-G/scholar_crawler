from flask import Flask, render_template, request, jsonify, send_from_directory
from crawler import crawl_scholar
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    url = request.form.get('url')
    proxy = request.form.get('proxy')
    try:
        original_title, count, filename, preview = crawl_scholar(url, proxy)
        return jsonify({
            'success': True,
            'title': original_title,
            'count': count,
            'filename': filename,
            'preview': preview
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)