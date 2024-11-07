import os
import shutil
import re
from text_to_speech import *
from tranform_audio_frames import *
from gemini_api import *
from generate_image import *
from generate_video_with_images import *
from upload_video_in_youtube import *
from database import *

import time
from datetime import datetime, timedelta

# Define video categories and times
SCHEDULE = [
    ("Entertainment", "08:00"),
    ("Sports", "11:00"),
    ("Trending News", "13:00"),
    ("Story or History", "17:00"),
    ("Trending News", "20:00")
]

def delete_existing_folders():
    base_folder = "images"
    selected_folder = "frames"
    selected_images_folder = "selected_images"
    all_images_folder = "all_images"
    folders = [base_folder, selected_folder, selected_images_folder, all_images_folder]

    # Loop through the folder list and delete if they exist
    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            try:
                shutil.rmtree(folder)  # Delete the folder and all its contents
                print(f"Deleted folder: {folder}")
            except Exception as e:
                print(f"Error deleting folder {folder}: {e}")
        else:
            print(f"Folder not found or already deleted: {folder}")
def generate_and_upload_video_for_slot(category, target_time, time_slot):
    if check_existing_video(target_time):
        print(f"Video for {target_time} has already been uploaded.")
        return

        # Generate video sentence and metadata
    delete_existing_folders()
    sentence = generate_sentence_for_category(category)
    title, description, tags, category_id = generate_video_metadata(sentence)
    today_date = datetime.now().date()

    # Insert initial record with "Processing" status and get the video_id
    video_id = insert_video_metadata(
        status="Processing: Generating audio content",
        sentence=sentence,
        title=title,
        description=description,
        tags=",".join(tags),
        category=category,
        time_slot=time_slot,
        upload_date=today_date
    )

    # Generate audio
    output_audio_file = f"{sanitize_directory_name(sentence)}.mp3"
    brief_content = get_brief_content(sentence)
    main_audio_path = generate_audio_elevenlabs(brief_content, output_audio_file)

    # Update status to indicate audio creation success
    update_video_status(video_id, "Processing: Audio generated")

    # Transcribe audio and generate frames
    formatted_frames = transcribe_audio_and_format(main_audio_path)
    update_video_status(video_id, "Processing: Audio transcribed")
    update_record(video_id, 'audio_file', main_audio_path)


    # Generate search keywords and update frames
    updated_frames = generate_search_keywords(formatted_frames, sentence)
    update_video_status(video_id, "Processing: Keywords generated")

    # Generate images for frames
    update_images_in_frames = update_images_path_in_frame(updated_frames)
    update_video_status(video_id, "Processing: Images generated")

    # Create video from images and audio
    output_video_file = f"video_outputs/{sanitize_directory_name(sentence)}.mp4"
    create_video_from_images_with_audio(update_images_in_frames, main_audio_path, output_video_file)
    update_video_status(video_id, "Processing: Video created")
    update_record(video_id, 'video_file', output_video_file)

    # Calculate publish time and update it in the database
    # publish_datetime = target_time
    # update_video_publish_time(video_id, publish_datetime)
    #
    # # Upload video to YouTube
    # upload_video(
    #     video_file=output_video_file,
    #     title=title,
    #     description=description,
    #     tags=tags,
    #     category_id=category_id,
    #     publish_time=publish_datetime
    # )
    #
    # # Update the final status as "Uploaded Successfully"
    # update_video_status(video_id, "Uploaded Successfully")
    #
    # print(f"Uploaded video for {category} at {time_slot}.")


def schedule_daily_videos(days=1):
    now = datetime.now()

    # Iterate over each day in the specified range
    for day in range(days):
        current_day = datetime.now().date() + timedelta(days=day)

        for category, time_slot in SCHEDULE:
            # Create a full datetime object for the scheduled time
            target_time = datetime.combine(current_day, datetime.strptime(time_slot, "%H:%M").time())

            # Check if the target time is in the future
            if target_time > now:
                print(f"Uploading video for category '{category}' at scheduled time '{target_time}' immediately.")

                # Check if video already exists for this time slot
                if check_existing_video(target_time):
                    print(f"Video for {target_time} has already been uploaded.")
                    continue

                # Generate and upload video for the slot
                generate_and_upload_video_for_slot(category, target_time, time_slot)
            else:
                print(f"Skipping past time slot '{target_time}' for category '{category}' as it has already passed.")


def generate_video_for_sentence(sentence):

    # Generate video sentence and metadata
    delete_existing_folders()
    #sentence = generate_sentence_for_category(category)
    title, description, tags, category_id = generate_video_metadata(sentence)
    today_date = datetime.now().date()

    # Insert initial record with "Processing" status and get the video_id
    video_id = insert_video_metadata(
        status="Processing: Generating audio content",
        sentence=sentence,
        title=title,
        description=description,
        tags=",".join(tags),
        category="NA",
        upload_date=today_date
    )
    sani_file_name = sanitize_directory_name(sentence)
    if len(sani_file_name) > 40:
        sani_file_name = sani_file_name[:39]

    # Generate audio
    output_audio_file = f"{sani_file_name}.mp3"
    brief_content = get_brief_content(sentence)
    main_audio_path = generate_audio_elevenlabs(brief_content, output_audio_file)

    # Update status to indicate audio creation success
    update_video_status(video_id, "Processing: Audio generated")

    # Transcribe audio and generate frames
    formatted_frames = transcribe_audio_and_format(main_audio_path)
    update_video_status(video_id, "Processing: Audio transcribed")
    update_record(video_id, 'audio_file', main_audio_path)


    # Generate search keywords and update frames
    updated_frames = generate_search_keywords(formatted_frames, sentence)
    update_video_status(video_id, "Processing: Keywords generated")

    # Generate images for frames
    update_images_in_frames = update_images_path_in_frame(updated_frames)
    update_video_status(video_id, "Processing: Images generated")

    # Create video from images and audio
    output_video_file = f"video_outputs/{sani_file_name}.mp4"
    create_video_from_images_with_audio(update_images_in_frames, main_audio_path, output_video_file)
    update_video_status(video_id, "Processing: Video created")
    update_record(video_id, 'video_file', output_video_file)


if __name__ == "__main__":
    #schedule_daily_videos()

    contents = ["US shares and Bitcoin hit record high on Trump win in 2024 election", "ROSÉ & Bruno Mars - APT. (Official Lyric Video) - something about this recently released song"]
    val = ["Who should Henry Cavill play in the MCU after Deadpool & Wolverine's Cavillrine cameo?",
                "Top 5 Programming Languages to learn before 2025",
                "What would be Avengers: Secret Wars' best superhero team-up?",
                "Tips to improve your aim in Valorant to move to Radiant Rank",
                "Squid Game 2 things you missed in recent trailer"]

    for content in contents:
        generate_video_for_sentence(content)