#!/usr/bin/env python3
"""
YouTube Clip Extractor - Web GUI
Simple web interface for extracting YouTube clips
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import subprocess
import os
import json
from pathlib import Path
import threading
import time

app = Flask(__name__)

SCRIPT_DIR = Path(__file__).parent / "scripts"
DOWNLOAD_DIR = Path.home() / "Downloads" / "youtube_clips"
DOWNLOAD_DIR.mkdir(exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Clip Extractor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input[type="text"], input[type="url"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .time-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        #thumbnail {
            width: 100%;
            max-height: 400px;
            object-fit: contain;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
        }
        #videoInfo {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        #videoInfo h3 {
            margin-bottom: 5px;
            color: #333;
            font-size: 16px;
        }
        #videoInfo p {
            color: #666;
            font-size: 13px;
        }
        #status {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        #status.loading {
            background: #fff3cd;
            color: #856404;
            display: block;
        }
        #status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        #status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
            margin: 15px 0;
            display: none;
        }
        .progress-bar.active {
            display: block;
        }
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            animation: progress 2s ease-in-out infinite;
        }
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }
        .hint {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 YouTube Clip Extractor</h1>
        <p class="subtitle">Extract specific segments from YouTube videos as B-roll clips</p>

        <form id="extractForm">
            <div class="form-group">
                <label for="videoUrl">YouTube URL</label>
                <input type="url" id="videoUrl" placeholder="https://www.youtube.com/watch?v=..." required>
                <button type="button" class="btn" onclick="loadVideo()" style="margin-top: 10px; width: auto;">Load Preview</button>
            </div>

            <div id="videoPlayer" style="display: none; margin-bottom: 15px;">
                <iframe id="youtubePlayer" width="100%" height="400" frameborder="0" allowfullscreen
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
                </iframe>
            </div>
            <div id="videoInfo"></div>

            <div class="form-group">
                <label>Timeframe</label>
                <div class="time-inputs">
                    <div>
                        <input type="text" id="startTime" placeholder="06:13" value="06:13" required>
                        <p class="hint">Start time (MM:SS)</p>
                    </div>
                    <div>
                        <input type="text" id="endTime" placeholder="06:30" value="06:30" required>
                        <p class="hint">End time (MM:SS)</p>
                    </div>
                </div>
                <button type="button" class="btn" onclick="loadTranscript()" style="margin-top: 10px; width: auto;">📝 Preview Transcript</button>
            </div>

            <div id="transcriptPreview" style="display: none; margin-bottom: 20px;">
                <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <h3 style="margin: 0 0 10px 0; color: #333; font-size: 14px; font-weight: 600;">📝 Transcript Preview (Click timestamps to jump!)</h3>
                    <div id="transcriptText" style="font-family: monospace; font-size: 12px; line-height: 1.8; color: #555; max-height: 200px; overflow-y: auto; white-space: pre-wrap;"></div>
                </div>
            </div>

            <div class="form-group">
                <label for="filename">Filename</label>
                <input type="text" id="filename" placeholder="clip.mp4" value="clip.mp4" required>
                <p class="hint">File will be saved to: ~/Downloads/youtube_clips/</p>
            </div>

            <div class="progress-bar" id="progressBar">
                <div class="progress-bar-fill"></div>
            </div>

            <button type="submit" class="btn" id="downloadBtn">⬇ Download Clip</button>
        </form>

        <div id="status"></div>
    </div>

    <script>
        let currentVideoId = '';

        function jumpToTime(timeString) {
            // Parse time string like "06:09" to seconds
            const parts = timeString.split(':');
            let seconds = 0;
            if (parts.length === 2) {
                seconds = parseInt(parts[0]) * 60 + parseInt(parts[1]);
            } else if (parts.length === 3) {
                seconds = parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
            }

            // Update iframe src with time parameter (preserve Korean audio settings)
            const iframe = document.getElementById('youtubePlayer');
            const currentSrc = iframe.src.split('?')[0];
            iframe.src = currentSrc + '?start=' + seconds + '&autoplay=1&hl=ko&cc_lang_pref=ko';
        }

        async function loadTranscript() {
            const startTime = document.getElementById('startTime').value;
            const endTime = document.getElementById('endTime').value;

            if (!currentVideoId) {
                showStatus('Please load a video first', 'error');
                return;
            }

            if (!startTime || !endTime) {
                showStatus('Please enter start and end times', 'error');
                return;
            }

            showStatus('Loading transcript preview...', 'loading');

            try {
                const response = await fetch('/api/get_transcript', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        videoId: currentVideoId,
                        startTime: startTime,
                        endTime: endTime
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Make timestamps clickable
                    const transcriptDiv = document.getElementById('transcriptText');
                    const lines = data.transcript.split('\\n');
                    transcriptDiv.innerHTML = '';

                    lines.forEach(line => {
                        // Match timestamps like [06:09] or [00:06:09]
                        const timestampMatch = line.match(/\[(\d{1,2}:\d{2}(?::\d{2})?)\]/);

                        if (timestampMatch) {
                            const timestamp = timestampMatch[1];
                            const text = line.substring(timestampMatch[0].length).trim();

                            const lineDiv = document.createElement('div');
                            lineDiv.style.marginBottom = '5px';

                            const timeLink = document.createElement('span');
                            timeLink.textContent = '[' + timestamp + ']';
                            timeLink.style.color = '#667eea';
                            timeLink.style.cursor = 'pointer';
                            timeLink.style.fontWeight = 'bold';
                            timeLink.style.textDecoration = 'underline';
                            timeLink.onclick = () => jumpToTime(timestamp);

                            lineDiv.appendChild(timeLink);
                            lineDiv.appendChild(document.createTextNode(' ' + text));
                            transcriptDiv.appendChild(lineDiv);
                        } else {
                            const lineDiv = document.createElement('div');
                            lineDiv.textContent = line;
                            transcriptDiv.appendChild(lineDiv);
                        }
                    });

                    document.getElementById('transcriptPreview').style.display = 'block';
                    showStatus('Transcript loaded - Click timestamps to jump!', 'success');
                } else {
                    document.getElementById('transcriptText').textContent = 'Transcript not available: ' + (data.error || 'Unknown error');
                    document.getElementById('transcriptPreview').style.display = 'block';
                    showStatus('Transcript unavailable for this video', 'error');
                }
            } catch (error) {
                showStatus('Error loading transcript: ' + error, 'error');
            }
        }

        async function loadVideo() {
            const url = document.getElementById('videoUrl').value;
            if (!url) {
                showStatus('Please enter a YouTube URL', 'error');
                return;
            }

            showStatus('Loading video information...', 'loading');

            try {
                const response = await fetch('/api/load_video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();

                if (data.success) {
                    // Store video ID for transcript fetching
                    currentVideoId = data.videoId;

                    // Load YouTube player with original audio track
                    const playerDiv = document.getElementById('videoPlayer');
                    const iframe = document.getElementById('youtubePlayer');
                    iframe.src = 'https://www.youtube.com/embed/' + data.videoId + '?hl=ko&cc_lang_pref=ko';
                    playerDiv.style.display = 'block';

                    document.getElementById('videoInfo').innerHTML = `
                        <h3>${data.title}</h3>
                        <p>👤 ${data.uploader} | ⏱ ${data.duration}</p>
                    `;
                    document.getElementById('videoInfo').style.display = 'block';

                    // Set filename suggestion
                    document.getElementById('filename').value = data.filename;

                    showStatus('Video loaded successfully!', 'success');
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showStatus('Error loading video: ' + error, 'error');
            }
        }

        document.getElementById('extractForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const url = document.getElementById('videoUrl').value;
            const startTime = document.getElementById('startTime').value;
            const endTime = document.getElementById('endTime').value;
            const filename = document.getElementById('filename').value;

            document.getElementById('downloadBtn').disabled = true;
            document.getElementById('progressBar').classList.add('active');
            showStatus('Downloading and extracting clip...', 'loading');

            try {
                const response = await fetch('/api/extract_clip', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, startTime, endTime, filename })
                });

                const data = await response.json();

                if (data.success) {
                    showStatus(`✅ Success! Clip saved to: ${data.output_path}`, 'success');
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error, 'error');
            } finally {
                document.getElementById('downloadBtn').disabled = false;
                document.getElementById('progressBar').classList.remove('active');
            }
        });

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = type;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/load_video', methods=['POST'])
def load_video():
    data = request.json
    url = data.get('url', '')

    try:
        # Extract video ID
        result = subprocess.run(
            [str(SCRIPT_DIR / "parse_video_id.sh"), url],
            capture_output=True,
            text=True,
            check=True
        )
        video_id = result.stdout.strip()

        # Fetch video info
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        video_info = json.loads(result.stdout)

        # Extract info
        title = video_info.get('title', 'Unknown')
        thumbnail = video_info.get('thumbnail', '')
        duration = video_info.get('duration', 0)
        uploader = video_info.get('uploader', 'Unknown')

        duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}"
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"{safe_title}.mp4"

        return jsonify({
            'success': True,
            'videoId': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration_str,
            'uploader': uploader,
            'filename': filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/get_transcript', methods=['POST'])
def get_transcript():
    data = request.json
    video_id = data.get('videoId', '')
    start_time = data.get('startTime', '')
    end_time = data.get('endTime', '')

    if not video_id or not start_time or not end_time:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters'
        })

    try:
        # Run transcript extraction
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT_DIR / "get_transcript_segment.py"),
                video_id,
                start_time,
                end_time
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            transcript = result.stdout.strip()
            return jsonify({
                'success': True,
                'transcript': transcript if transcript else 'No transcript available in this timeframe'
            })
        else:
            error_msg = result.stderr.strip() if result.stderr else 'No transcript available'
            return jsonify({
                'success': False,
                'error': error_msg
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/extract_clip', methods=['POST'])
def extract_clip():
    data = request.json
    url = data.get('url', '')
    start_time = data.get('startTime', '')
    end_time = data.get('endTime', '')
    filename = data.get('filename', 'clip.mp4')

    if not filename.endswith('.mp4'):
        filename += '.mp4'

    output_path = DOWNLOAD_DIR / filename
    timeframe = f"{start_time}-{end_time}"

    try:
        # Run extraction
        result = subprocess.run(
            [
                str(SCRIPT_DIR / "extract_clip.sh"),
                url,
                timeframe,
                str(output_path)
            ],
            capture_output=True,
            text=True,
            timeout=300,
            check=True
        )

        return jsonify({
            'success': True,
            'output_path': str(output_path)
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'error': e.stderr or str(e)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎬 YouTube Clip Extractor - Web GUI")
    print("="*50)
    print(f"\n✅ Server starting...")
    print(f"📂 Download folder: {DOWNLOAD_DIR}")
    print(f"\n🌐 Open in browser: http://localhost:5001")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=False, host='127.0.0.1', port=5001)
