import os
import shutil
import re
#from text_to_speech import generate_audio_pyttsx3
from text_to_speech import generate_audio_gtts
#from text_to_speech import change_pitch
from tranform_audio_frames import transcribe_audio_and_format
from gemini_api import get_brief_content
from gemini_api import generate_search_keywords
from gemini_api import generate_video_metadata
from generate_image import update_images_path_in_frame
from generate_video_with_images import create_video_from_images_with_audio
from upload_video_in_youtube import upload_video

def sanitize_directory_name(name):
    # Replace invalid characters with underscores
    return re.sub(r'[^a-zA-Z0-9]+', '_', name).strip('_')
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

if __name__ == "__main__":
    # Step 0 - Prerequisites
    delete_existing_folders()
    sentence = "history Ballon dor football award created"
    sanitized_file_name = sanitize_directory_name(sentence)

    output_video_file = f"video_outputs/{sanitized_file_name}.mp4"
    output_audio_file = f"{sanitized_file_name}.mp3"

    # Step 1 - Generating Speech Content
    brief_content = get_brief_content(sentence)

    # Step 2 - Convert the content to single audio frames
    main_audio_path = generate_audio_gtts(brief_content, output_audio_file)
    print(f"Audio file created at: {main_audio_path}")

    # For Changing the Audio Pitch
    #output_audio = change_pitch(main_audio_path, 0.3)
    #output_audio.export("output_pitched.mp3", format="mp3")

    # Step 3 - Convert the audio to transcribed text format with frames mapped
    formatted_frames = transcribe_audio_and_format(main_audio_path)

    # Step 4 - Generate the Search keyword for each frames
    updated_frames = generate_search_keywords(formatted_frames, sentence)
    print(f"printing it outside {updated_frames}")

    # Step 5 - Generate Image and update the path in the frames
    update_images_in_frames = update_images_path_in_frame(updated_frames)
    print(update_images_in_frames)

    # Step 6 - Create the video from images and audio
    create_video_from_images_with_audio(update_images_in_frames, main_audio_path, output_video_file)

    # Step 7 - Upload Youtube Video
    title, description, tags, category_id = generate_video_metadata(sentence)
    publish_time = None

    # Call the upload_video function with generated parameters
    upload_video(
        video_file=output_video_file,
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        publish_time=publish_time
    )

