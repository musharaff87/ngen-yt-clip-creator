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
from sheet import push_video_metadata_to_sheet

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
    formatted_date = today_date.strftime('%Y-%m-%d')
    push_video_metadata_to_sheet([sentence, title, description, ",".join(tags), formatted_date])

    sani_file_name = sanitize_directory_name(sentence)
    if len(sani_file_name) > 40:
        sani_file_name = sani_file_name[:39]

    # Generate audio
    output_audio_file = f"{sani_file_name}.mp3"
    brief_content = get_brief_content(sentence)
    brief_content = brief_content.replace("*", "")
    brief_content = brief_content.replace("#", "")
    main_audio_path = generate_audio_elevenlabs(brief_content, output_audio_file)

    # Update status to indicate audio creation success
    update_video_status(video_id, "Processing: Audio generated")

    # Transcribe audio and generate frames
    formatted_frames = transcribe_audio_and_format(main_audio_path)
    update_video_status(video_id, "Proces sing: Audio transcribed")
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

    contents = ["Multiple Thors: Beyond the well-known Thor, there exists a character named Throg, who is a frog with powers similar to Thor's. He leads the Pet Avengers, a group of animal heroes",
                "Michael Jackson's Interest: Pop icon Michael Jackson once attempted to buy Marvel Comics with the intention of playing Spider-Man in a film adaptation, showcasing the character's immense cultural impact even outside traditional comic book fans",
                "Superman's Purchase Price: Superman was sold to DC Comics for only $130 in 1938 by his creators Jerry Siegel and Joe Shuster. This deal is often cited as one of the most significant miscalculations in comic book history, given Superman's subsequent success",
                "Batman’s Utility Belt: The concept of Batman's utility belt was first introduced in Detective Comics No. 29 (July 1939), which has since become an iconic aspect of his character design and functionality",
                "Shazam’s Name Change: Originally named Captain Marvel, Shazam had to change his name due to trademark issues with Marvel Comics, which registered their own Captain Marvel",
                "game of thrones: Though Ned Stark is well known as the Hand to King Robert Baratheon, he wasn't the first Stark to have been the Hand of the King. After the Dance of the Dragons, which is likely to be depicted in House of the Dragon, Cregan Stark served as the Hand of the King to Aegon III Targaryen.",
                "game of thrones: There's a reason that the Starks and the North were vulnerable to attack by the Iron Fleet when Theon Greyjoy came to attack Winterfell. After Brandon the Shipwright was lost at sea, thousands of years before the main series, the next King of Winter, Brandon the Burner, set fire to the entire Northern Navy in a promise to never to see the Starks at sea again.",
                "Benedict Cumberbatch is talking about Doctor Strange's future in the MCU, including whether he will appear in Avengers: Doomsday. "]
    for content in contents:
        generate_video_for_sentence(content)