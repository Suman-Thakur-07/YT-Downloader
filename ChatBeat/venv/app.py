from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

# Function to get available formats (quality options) using yt-dlp
def get_video_info(url):
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        return formats, info_dict['title']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_formats', methods=['POST'])
def get_formats():
    url = request.json['url']
    formats, title = get_video_info(url)
    
    available_formats = [
        {
            'format_id': f['format_id'],
            'resolution': f.get('resolution', 'Unknown'),
            'ext': f.get('ext', 'Unknown'),
            'filesize': f.get('filesize', 'Unknown'),
            'vcodec': f.get('vcodec', 'Unknown'),
            'acodec': f.get('acodec', 'Unknown'),
            'format_note': f.get('format_note', '')
        }
        for f in formats
        if f.get('vcodec') != 'none' or f.get('acodec') != 'none'
    ]

    # Sort formats by resolution (assuming higher resolution is better)
    available_formats.sort(key=lambda x: (x['resolution'] if x['resolution'] != 'Unknown' else '0'), reverse=True)

    return jsonify({'formats': available_formats, 'title': title})

@app.route('/download_video/<format_id>')
def download_video(format_id):
    url = request.args.get('url')
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info_dict)

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
