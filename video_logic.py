import os
from database import list_all_videos_api
from schedule_video import generate_video_for_sentence
from upload_video_in_youtube import upload_video
from threading import Thread
from datetime import datetime

pending_sentences = []

def get_processed_videos():
    all_videos = list_all_videos_api()
    processed_videos = []
    for video in all_videos:
        video_id, status, sentence, title, description, tags, category, upload_date, video_file, audio_file = video
        if status == "Processing: Video created" and video_file:
            if not os.path.exists(video_file):
                continue
            processed_videos.append({
                "id": video_id,
                "title": title,
                "status": status,
                "video_file": video_file,
                "description": description,
                "tags": tags.split(",") if tags else [],
                "category": "24"  # Default to Entertainment; adjust as needed
            })
    return processed_videos

def add_sentence(sentence):
    if sentence and sentence.strip():
        pending_sentences.append(sentence.strip())

def get_pending_sentences():
    return pending_sentences

def generate_videos():
    def run_generation():
        for sentence in pending_sentences[:]:
            generate_video_for_sentence(sentence)
            pending_sentences.remove(sentence)
    thread = Thread(target=run_generation)
    thread.start()

def schedule_video(video_id, video_file, title, description, tags, category_id, publish_time):
    """Schedule a video upload to YouTube."""
    def run_upload():
        upload_video(video_id, video_file, title, description, tags, category_id, publish_time)
    thread = Thread(target=run_upload)
    thread.start()