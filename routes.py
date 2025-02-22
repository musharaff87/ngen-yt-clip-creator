from flask import render_template_string, request, redirect, url_for, send_file
from video_logic import get_processed_videos, add_sentence, get_pending_sentences, generate_videos, schedule_video
import os
from datetime import datetime

def init_routes(app):
    # Common CSS for all templates
    base_css = """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1e3a8a, #3b82f6);
            color: #ffffff;
            min-height: 100vh;
            margin: 0;
            padding: 1rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
        h1 {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        h2 {
            font-size: 1.75rem;
            color: #e5e7eb;
            margin-bottom: 1rem;
        }
        a, button, input[type="submit"] {
            transition: all 0.3s ease;
        }
        a:hover, button:hover, input[type="submit"]:hover {
            transform: scale(1.05);
        }
        .video-player {
            width: 100%;
            max-width: 400px;
            border-radius: 0.5rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        @media (max-width: 768px) {
            h1 { font-size: 1.75rem; }
            h2 { font-size: 1.25rem; }
            .container { padding: 0.5rem; }
            table, thead, tbody, th, td, tr { display: block; }
            th, td { width: 100%; box-sizing: border-box; }
            td { padding: 0.75rem; }
            .video-player { max-width: 100%; }
        }
    </style>
    """

    @app.route('/')
    def home():
        videos = get_processed_videos()
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Video Management</title>
            """ + base_css + """
        </head>
        <body>
            <div class="container">
                <h1>Video Management Dashboard</h1>
                <p class="text-center mb-4"><a href="/generate" class="text-white bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700">Generate New Videos</a></p>
                <h2>Processed Videos</h2>
                {% if videos %}
                    <div class="overflow-x-auto">
                        <table class="w-full text-left bg-white bg-opacity-20 rounded-lg">
                            <thead class="bg-blue-800 bg-opacity-50">
                                <tr>
                                    <th class="px-4 py-2">ID</th>
                                    <th class="px-4 py-2">Title</th>
                                    <th class="px-4 py-2">Status</th>
                                    <th class="px-4 py-2">Video File</th>
                                    <th class="px-4 py-2">Playable</th>
                                    <th class="px-4 py-2">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for video in videos %}
                                <tr class="hover:bg-blue-600 hover:bg-opacity-30">
                                    <td class="px-4 py-2">{{ video.id }}</td>
                                    <td class="px-4 py-2">{{ video.title }}</td>
                                    <td class="px-4 py-2">{{ video.status }}</td>
                                    <td class="px-4 py-2">{{ video.video_file }}</td>
                                    <td class="px-4 py-2">
                                        <video class="video-player" controls>
                                            <source src="/video_outputs/{{ video.video_file | replace('video_outputs/', '') }}" type="video/mp4">
                                            Your browser does not support the video tag.
                                        </video>
                                    </td>
                                    <td class="px-4 py-2">
                                        <form action="/schedule/{{ video.id }}" method="get">
                                            <button type="submit" class="bg-green-500 text-white px-3 py-1 rounded-lg hover:bg-green-600">Schedule</button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-center text-gray-300">No videos found with status "Processing: Video created".</p>
                {% endif %}
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, videos=videos)

    @app.route('/generate', methods=['GET', 'POST'])
    def generate_page():
        if request.method == 'POST':
            if 'add_sentence' in request.form:
                sentence = request.form.get('sentence')
                add_sentence(sentence)
            elif 'generate' in request.form:
                generate_videos()
                return redirect(url_for('home'))
        pending = get_pending_sentences()
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Generate Videos</title>
            """ + base_css + """
            <style>
                .form-group { margin-bottom: 1rem; }
                input[type="text"] { 
                    width: 100%; 
                    max-width: 500px; 
                    padding: 0.5rem; 
                    border-radius: 0.5rem; 
                    border: none; 
                    background: rgba(255, 255, 255, 0.2); 
                    color: white; 
                }
                input[type="submit"] { 
                    background: #10b981; 
                    color: white; 
                    padding: 0.5rem 1rem; 
                    border-radius: 0.5rem; 
                    border: none; 
                    cursor: pointer; 
                }
                input[type="submit"]:hover { background: #059669; }
                ul { margin-top: 1rem; }
                li { 
                    background: rgba(255, 255, 255, 0.15); 
                    padding: 0.5rem; 
                    border-radius: 0.5rem; 
                    margin-bottom: 0.5rem; 
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Generate New Videos</h1>
                <p class="text-center mb-4"><a href="/" class="text-white bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700">Back to Home</a></p>
                <form method="post" class="form-group">
                    <label for="sentence" class="block text-lg mb-2">Add a Sentence:</label>
                    <input type="text" id="sentence" name="sentence" placeholder="Enter your sentence here">
                    <input type="submit" name="add_sentence" value="Add Sentence" class="mt-2">
                </form>
                <h2>Pending Sentences</h2>
                {% if pending %}
                    <ul>
                        {% for sentence in pending %}
                            <li>{{ sentence }}</li>
                        {% endfor %}
                    </ul>
                    <form method="post" class="mt-4">
                        <input type="submit" name="generate" value="Generate Videos">
                    </form>
                {% else %}
                    <p class="text-gray-300">No sentences added yet.</p>
                {% endif %}
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, pending=pending)

    @app.route('/schedule/<int:video_id>', methods=['GET', 'POST'])
    def schedule_video_page(video_id):
        videos = get_processed_videos()
        video = next((v for v in videos if v['id'] == video_id), None)
        if not video:
            return "Video not found", 404

        if request.method == 'POST':
            publish_time_str = request.form.get('publish_time')
            publish_time = datetime.strptime(publish_time_str, "%Y-%m-%dT%H:%M")
            if publish_time <= datetime.now():
                return "Publish time must be in the future", 400
            schedule_video(
                video['id'],
                video['video_file'],
                video['title'],
                video['description'],
                video['tags'],
                video['category'],
                publish_time
            )
            return redirect(url_for('home'))

        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Schedule Video</title>
            """ + base_css + """
            <style>
                .form-group { margin-bottom: 1.5rem; }
                input[type="datetime-local"] { 
                    padding: 0.5rem; 
                    border-radius: 0.5rem; 
                    border: none; 
                    background: rgba(255, 255, 255, 0.2); 
                    color: white; 
                    width: 100%; 
                    max-width: 300px; 
                }
                input[type="submit"] { 
                    background: #10b981; 
                    color: white; 
                    padding: 0.5rem 1rem; 
                    border-radius: 0.5rem; 
                    border: none; 
                    cursor: pointer; 
                }
                input[type="submit"]:hover { background: #059669; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Schedule Video: {{ video.title }}</h1>
                <p class="text-center mb-4"><a href="/" class="text-white bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700">Back to Home</a></p>
                <form method="post" class="form-group">
                    <label for="publish_time" class="block text-lg mb-2">Schedule Date and Time (IST):</label>
                    <input type="datetime-local" id="publish_time" name="publish_time" required>
                    <input type="submit" value="Schedule" class="mt-2">
                </form>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, video=video)

    @app.route('/video_outputs/<path:filename>')
    def serve_video(filename):
        video_path = os.path.join('video_outputs', filename)
        if not os.path.exists(video_path):
            video_path = os.path.join('video_outputs', 'old_videos', filename)
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
        return "File not found", 404