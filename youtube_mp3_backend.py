from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
from moviepy.editor import AudioFileClip

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Load YouTube cookies from environment variable
cookies = os.getenv("COOKIES")
if cookies:
    with open("cookies.txt", "w") as f:
        f.write(cookies)

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    video_url = data.get("url")
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt' if cookies else None  # Use cookies if available
        }
        
        # Download the video/audio file using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Convert the downloaded file to MP3 using MoviePy
        audio = AudioFileClip(filename)
        mp3_filename = filename.rsplit('.', 1)[0] + ".mp3"
        audio.write_audiofile(mp3_filename, codec='mp3')
        
        # Clean up the original file (optional)
        os.remove(filename)

        # Return the MP3 file
        return send_file(mp3_filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
