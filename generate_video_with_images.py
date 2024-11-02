import os
from moviepy.editor import *
from moviepy.config import change_settings
import moviepy.audio.fx.all as afx
from PIL import Image
import textwrap
import random
import moviepy.video.fx.all as vfx



change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def resize_image(image_path, target_size):
    """Resizes an image to the target size using LANCZOS for high quality."""
    image = Image.open(image_path)
    resized_images_folder = os.path.join(os.path.dirname(image_path), 'resized_images')
    os.makedirs(resized_images_folder, exist_ok=True)
    resized_image_path = os.path.join(resized_images_folder, os.path.basename(image_path))
    resized_image = image.resize(target_size, Image.Resampling.LANCZOS)
    resized_image.save(resized_image_path)
    return resized_image_path

def apply_transitions(img_clip, duration):
    """Apply transitions like fade-in and fade-out to the image clip."""
    img_clip = vfx.fadein(img_clip, duration=0.3).fadeout(0.3)  # Using fadein and fadeout from vfx
    return img_clip


def add_subtitle_to_clip(image_clip, actual_text, duration, screen_width=720, margin=50, offset=320):
    """Adds subtitles to the image clip with dynamic word wrapping."""
    text_width_limit = screen_width - (2 * margin)
    wrapped_lines = []
    current_line = []
    words = actual_text.split()

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        temp_text_clip = TextClip(test_line, fontsize=45, font='Arial-Bold')

        if temp_text_clip.size[0] > text_width_limit:
            current_line.pop()
            wrapped_lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        wrapped_lines.append(' '.join(current_line))

    wrapped_text = '\n'.join(wrapped_lines)
    subtitle = TextClip(
        wrapped_text,
        fontsize=45,
        font='Arial-Bold',
        color='white',
        stroke_color='black',
        stroke_width=2,
        size=(text_width_limit, None)
    )

    # Set the duration of the subtitle
    subtitle = subtitle.set_duration(duration)

    # Get the height of the image clip to calculate the new subtitle position
    image_height = image_clip.size[1]

    # Adjust the position to be slightly above the bottom of the image
    subtitle_y_position = image_height - offset  # Move upward from the bottom

    subtitle = subtitle.set_position(('center', subtitle_y_position)).margin(bottom=0)

    # Return a composite video clip with the image and subtitles
    return CompositeVideoClip(
        [image_clip, subtitle.set_position(('center', subtitle_y_position)).set_duration(duration)])

def audio_loop(audio_clip, duration):
    """Loops the audio until it matches the required duration."""
    looped_audio = audio_clip
    while looped_audio.duration < duration:
        looped_audio = concatenate_audioclips([looped_audio, audio_clip])
    return looped_audio.set_duration(duration)

def apply_filters_to_image_clip(image_clip):
    """Apply basic filters such as color adjustments, blur, etc."""
    # For example, adjust brightness, contrast, or add blur
    filtered_clip = image_clip.fx(vfx.colorx, 1.2).fx(vfx.lum_contrast, lum=10, contrast=40, contrast_thr=150)
    return filtered_clip


def apply_animation(img_clip):
    """Apply simple animation like zooming (Ken Burns effect)."""
    return img_clip.resize(lambda t: 1 + 0.02 * t)  # Zoom in slightly over time


def add_background_music(video, music_folder, main_audio):
    """Adds a background music track from a random file in the music folder, looping it if necessary."""
    # First set the main audio to the video
    video = video.set_audio(main_audio)
    video_duration = video.duration

    # Select random background music
    music_files = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]
    if music_files:
        random_music_path = os.path.join(music_folder, random.choice(music_files))
        print(f"Adding background music: {random_music_path}")
        background_music = AudioFileClip(random_music_path).volumex(0.2)  # Lower volume for background music

        # Calculate the number of loops needed to cover the video duration
        #loops_needed = int(video.duration // background_music.duration) + 1

        # Create a composite audio clip by concatenating the music to match the video duration
        #looped_music = concatenate_audioclips([background_music] * loops_needed).subclip(0, video.duration)

        trimmed_music = background_music.subclip(0, video_duration)
        # Combine the main audio and the looped background music
        combined_audio = CompositeAudioClip([main_audio.volumex(1), trimmed_music])

        # Set the combined audio to the video
        return video.set_audio(combined_audio)

    # If no background music is found, return the video with just the main audio
    return video

def create_video_from_images_with_audio(image_data, audio_file, output_video_file, target_size=(720, 1280), music_folder="background_music"):
    clips = []
    for i in range(len(image_data)):
        frame_data = image_data[i]
        image_path = frame_data['image_path']
        actual_keyword = frame_data['actual_keyword']
        start_time, end_time = frame_data['audio_duration'].split(' - ')

        start_time = float(start_time.replace('s', ''))
        end_time = float(end_time.replace('s', ''))

        if i < len(image_data) - 1:
            next_start_time = float(image_data[i + 1]['audio_duration'].split(' - ')[0].replace('s', ''))
            if next_start_time > end_time:
                end_time = next_start_time

        duration = end_time - start_time

        # Resize the image to the target size
        resized_image_path = resize_image(image_path, target_size)

        # Create a clip for this image
        img_clip = ImageClip(resized_image_path).set_duration(duration)

        # Add filters, transitions, and animation to the clip
        #img_clip = apply_filters_to_image_clip(img_clip)
        #if i%3 == 0:
            #img_clip = apply_transitions(img_clip, duration)

        img_clip = apply_animation(img_clip)

        # Add subtitles to the image clip
        img_clip_with_subtitle = add_subtitle_to_clip(img_clip, actual_keyword, duration, screen_width=target_size[0])

        # Set the start time for the clip
        img_clip_with_subtitle = img_clip_with_subtitle.set_start(start_time)

        clips.append(img_clip_with_subtitle)

    # Concatenate all image clips into a single video
    video = concatenate_videoclips(clips, method="compose")

    # Load the main audio file
    main_audio = AudioFileClip(audio_file)

    # Add background music
    video = add_background_music(video, music_folder, main_audio)

    # Write the final video file
    try:
        video.write_videofile(output_video_file, fps=24, codec="libx264", audio_codec="aac")
    except Exception as e:
            print(f"Error Generating Video... {e}")

if __name__ == "__main__":
  update_images_in_frames = [{'audio_duration': '0.0s - 4.32s', 'actual_keyword': 'Did you know that the tensions between Iran and Israel are at a boiling point?', 'search_keyword': 'Iran and Israel conflict hd portrait images', 'image_path': 'selected_images\\sample_image_2_1.jpeg'}, {'audio_duration': '5.2s - 7.2s', 'actual_keyword': "It's like a pressure cooker.", 'search_keyword': 'hd portrait images of a pressure cooker with a war-torn landscape in the background', 'image_path': 'selected_images\\sample_image_6_2.jpeg'}, {'audio_duration': '7.2s - 12.8s', 'actual_keyword': 'With both sides constantly throwing barbs and threats across the volatile landscape of the middle.', 'search_keyword': 'Iranian and Israeli soldiers facing each other on a battlefield hd portrait images', 'image_path': 'selected_images\\sample_image_4_3.jpeg'}, {'audio_duration': '13.52s - 18.16s', 'actual_keyword': 'East the latest news is a mix of saber rattling and diplomatic maneuvering.', 'search_keyword': 'hd portrait images of soldiers from Iran and Israel facing each other', 'image_path': 'selected_images\\sample_image_5_2.jpeg'}, {'audio_duration': '18.88s - 24.48s', 'actual_keyword': "But the underlying threat of an all-out war is still hanging over everyone's heads like a dark cloud.", 'search_keyword': 'hd portrait images of soldiers from Iran and Israel standing face to face with a dark cloud above them', 'image_path': 'selected_images\\sample_image_5_5.jpeg'}, {'audio_duration': '25.36s - 32.24s', 'actual_keyword': 'Last week, Iranian officials vowed to wipe Israel off the map while Israeli Prime Minister Benjamin.', 'search_keyword': 'hd portrait images of iranian and israeli leaders facing each other', 'image_path': 'selected_images\\sample_image_7_6.jpeg'}, {'audio_duration': '33.04s - 37.84s', 'actual_keyword': 'Netanyahu countered with threats of crushing Iranian nuclear facilities.', 'search_keyword': 'hd portrait images of Benjamin Netanyahu looking stern and determined', 'image_path': 'selected_images\\sample_image_4_5.jpeg'}, {'audio_duration': '38.4s - 44.08s', 'actual_keyword': "It's a dangerous game of chicken, with the possibility of an accidental spark setting off a", 'search_keyword': 'hd portrait images of iranian and israeli soldiers facing each other with tension', 'image_path': 'selected_images\\sample_image_1_4.jpeg'}, {'audio_duration': '44.08s - 52.16s', 'actual_keyword': 'firestorm across the region. The US, caught in the middle, is trying to de-escalate the situation,', 'search_keyword': 'hd portrait images of a burning city skyline with a US flag waving in the wind', 'image_path': 'selected_images\\sample_image_2_9.jpeg'}, {'audio_duration': '52.16s - 57.44s', 'actual_keyword': 'but its influence seems to be waning, leaving a dangerous power vacuum.', 'search_keyword': 'hd portrait images of soldiers from iran and israel in a conflict scene', 'image_path': 'selected_images\\sample_image_8_10.jpeg'}, {'audio_duration': '57.44s - 62.24s', 'actual_keyword': 'The tension is further amplified by the ongoing shadow war in the cyber realm.', 'search_keyword': 'hd portrait images of soldiers in cyber warfare', 'image_path': 'selected_images\\sample_image_10_11.jpeg'}, {'audio_duration': '63.04s - 68.88s', 'actual_keyword': 'With Iranian hackers targeting Israeli infrastructure and Israeli cyber warriors launching,', 'search_keyword': 'hd portrait images of soldiers from israel and iran facing each other', 'image_path': 'selected_images\\sample_image_7_12.jpeg'}, {'audio_duration': '69.44s - 75.76s', 'actual_keyword': "counter attacks. It's a silent battle, fought in the dark with lines of code instead of bullets.", 'search_keyword': 'hd portrait images of a soldier in the dark with code flowing around them', 'image_path': 'selected_images\\sample_image_6_13.jpeg'}, {'audio_duration': '76.24s - 81.6s', 'actual_keyword': 'But the potential damage is just as real. The world is watching with baited breath.', 'search_keyword': 'hd portrait images of people watching news about Iran vs Israel war with concern', 'image_path': 'selected_images\\sample_image_7_4.jpeg'}, {'audio_duration': '81.6s - 92.16s', 'actual_keyword': "Hoping this tense standoff won't escalate into a full-blown war.", 'search_keyword': 'hd portrait images of soldiers from Iran and Israel standing face to face', 'image_path': 'selected_images\\sample_image_5_15.jpeg'}]
  audio_file = 'sample_audio/iran_war.mp3'
  output_video_file = 'video_outputs/edited_war.mp4'

  # Create the video from images and audio
  create_video_from_images_with_audio(update_images_in_frames, audio_file, output_video_file)