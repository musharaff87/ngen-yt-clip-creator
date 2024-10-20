import os
from moviepy.editor import *
from moviepy.config import change_settings
from PIL import Image
import textwrap

change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def resize_image(image_path, target_size):
  """Resizes an image to the target size using LANCZOS for high quality."""
  image = Image.open(image_path)

  # Ensure the folder for resized images exists
  resized_images_folder = os.path.join(os.path.dirname(image_path), 'resized_images')
  os.makedirs(resized_images_folder, exist_ok=True)

  # Construct new path for resized image
  resized_image_path = os.path.join(resized_images_folder, os.path.basename(image_path))

  # Resize and save the image
  resized_image = image.resize(target_size, Image.Resampling.LANCZOS)
  resized_image.save(resized_image_path)
  return resized_image_path

def add_subtitle_to_clip(image_clip, actual_text, duration, screen_width=720, margin=50):
    """Adds subtitles to the image clip with dynamic word wrapping."""

    # Calculate the width for the text (reduce the width of the text to fit within margins)
    text_width_limit = screen_width - (2 * margin)

    # Initialize the wrapped text with a rough estimate of 4 words per line
    wrapped_lines = []
    current_line = []
    words = actual_text.split()

    # Break the words into lines based on their approximate width
    for word in words:
      current_line.append(word)
      # Temporarily join current line and measure the length
      test_line = ' '.join(current_line)

      # Create a temporary TextClip to measure width
      temp_text_clip = TextClip(test_line, fontsize=50, font='Arial-Bold')

      # Check if the current line fits within the width limit
      if temp_text_clip.size[0] > text_width_limit:
        # If it doesn't fit, move the last word to a new line
        current_line.pop()
        wrapped_lines.append(' '.join(current_line))
        current_line = [word]

    # Add any remaining words to the final line
    if current_line:
      wrapped_lines.append(' '.join(current_line))

    # Join wrapped lines with newline characters to display as multi-line text
    wrapped_text = '\n'.join(wrapped_lines)

    # Create a text clip with the wrapped text
    subtitle = TextClip(wrapped_text, fontsize=50, font='Arial-Bold', color='white',
                        stroke_color='black', stroke_width=2, size=(text_width_limit, None))

    # Set the duration of the subtitle to match the image clip's duration
    subtitle = subtitle.set_duration(duration)

    # Position the subtitle at the bottom center of the screen without unnecessary margin
    subtitle = subtitle.set_position(('center', 'bottom')).margin(bottom=0)

    # Overlay the subtitle on the image clip
    return CompositeVideoClip([image_clip, subtitle.set_position(('center', 'bottom')).set_duration(duration)])


def create_video_from_images_with_audio(image_data, audio_file, output_video_file,
                                        target_size=(720, 1280)):  # Mobile portrait size
    clips = []

    # Loop through the image data and process each frame
    for i in range(len(image_data)):
        frame_data = image_data[i]
        image_path = frame_data['image_path']
        actual_keyword = frame_data['actual_keyword']
        start_time, end_time = frame_data['audio_duration'].split(' - ')

        # Convert start and end times to float
        start_time = float(start_time.replace('s', ''))
        end_time = float(end_time.replace('s', ''))

        print(f"Initial Processing clip from {start_time}s to {end_time}s")

        # If this is not the last frame, check the next frame's start time
        if i < len(image_data) - 1:
            next_start_time = float(image_data[i + 1]['audio_duration'].split(' - ')[0].replace('s', ''))
            print(f"Comparing with next frame: next_start_time = {next_start_time}s")

            # Extend current frame's end time if the next frame's start time is greater than the current end time
            if next_start_time > end_time:
                print(f"Adjusting end_time from {end_time}s to {next_start_time}s")
                end_time = next_start_time  # Adjust current end time to the next start time

        # Calculate duration
        duration = end_time - start_time

        print(f"Final Processing clip from {start_time}s to {end_time}s, duration: {duration}s")

        # Resize the image to the target size
        resized_image_path = resize_image(image_path, target_size)

        # Create a clip for this image
        img_clip = ImageClip(resized_image_path).set_duration(duration)

        # Add subtitles to the image clip (pass screen width for subtitle positioning)
        img_clip_with_subtitle = add_subtitle_to_clip(img_clip, actual_keyword, duration,
                                                      screen_width=target_size[0])

        # Set the start time for the clip
        img_clip_with_subtitle = img_clip_with_subtitle.set_start(start_time)

        clips.append(img_clip_with_subtitle)

    # Concatenate all image clips into a single video
    video = concatenate_videoclips(clips, method="compose")

    # Load the audio file and set it to the video
    audio = AudioFileClip(audio_file)
    video = video.set_audio(audio)

    # Write the final video file
    video.write_videofile(output_video_file, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
  update_images_in_frames = [{'audio_duration': '0.0s - 4.32s', 'actual_keyword': 'Did you know that the tensions between Iran and Israel are at a boiling point?', 'search_keyword': 'Iran and Israel conflict hd portrait images', 'image_path': 'selected_images\\sample_image_2_1.jpeg'}, {'audio_duration': '5.2s - 7.2s', 'actual_keyword': "It's like a pressure cooker.", 'search_keyword': 'hd portrait images of a pressure cooker with a war-torn landscape in the background', 'image_path': 'selected_images\\sample_image_6_2.jpeg'}, {'audio_duration': '7.2s - 12.8s', 'actual_keyword': 'With both sides constantly throwing barbs and threats across the volatile landscape of the middle.', 'search_keyword': 'Iranian and Israeli soldiers facing each other on a battlefield hd portrait images', 'image_path': 'selected_images\\sample_image_4_3.jpeg'}, {'audio_duration': '13.52s - 18.16s', 'actual_keyword': 'East the latest news is a mix of saber rattling and diplomatic maneuvering.', 'search_keyword': 'hd portrait images of soldiers from Iran and Israel facing each other', 'image_path': 'selected_images\\sample_image_5_2.jpeg'}, {'audio_duration': '18.88s - 24.48s', 'actual_keyword': "But the underlying threat of an all-out war is still hanging over everyone's heads like a dark cloud.", 'search_keyword': 'hd portrait images of soldiers from Iran and Israel standing face to face with a dark cloud above them', 'image_path': 'selected_images\\sample_image_5_5.jpeg'}, {'audio_duration': '25.36s - 32.24s', 'actual_keyword': 'Last week, Iranian officials vowed to wipe Israel off the map while Israeli Prime Minister Benjamin.', 'search_keyword': 'hd portrait images of iranian and israeli leaders facing each other', 'image_path': 'selected_images\\sample_image_7_6.jpeg'}, {'audio_duration': '33.04s - 37.84s', 'actual_keyword': 'Netanyahu countered with threats of crushing Iranian nuclear facilities.', 'search_keyword': 'hd portrait images of Benjamin Netanyahu looking stern and determined', 'image_path': 'selected_images\\sample_image_4_5.jpeg'}, {'audio_duration': '38.4s - 44.08s', 'actual_keyword': "It's a dangerous game of chicken, with the possibility of an accidental spark setting off a", 'search_keyword': 'hd portrait images of iranian and israeli soldiers facing each other with tension', 'image_path': 'selected_images\\sample_image_1_4.jpeg'}, {'audio_duration': '44.08s - 52.16s', 'actual_keyword': 'firestorm across the region. The US, caught in the middle, is trying to de-escalate the situation,', 'search_keyword': 'hd portrait images of a burning city skyline with a US flag waving in the wind', 'image_path': 'selected_images\\sample_image_2_9.jpeg'}, {'audio_duration': '52.16s - 57.44s', 'actual_keyword': 'but its influence seems to be waning, leaving a dangerous power vacuum.', 'search_keyword': 'hd portrait images of soldiers from iran and israel in a conflict scene', 'image_path': 'selected_images\\sample_image_8_10.jpeg'}, {'audio_duration': '57.44s - 62.24s', 'actual_keyword': 'The tension is further amplified by the ongoing shadow war in the cyber realm.', 'search_keyword': 'hd portrait images of soldiers in cyber warfare', 'image_path': 'selected_images\\sample_image_10_11.jpeg'}, {'audio_duration': '63.04s - 68.88s', 'actual_keyword': 'With Iranian hackers targeting Israeli infrastructure and Israeli cyber warriors launching,', 'search_keyword': 'hd portrait images of soldiers from israel and iran facing each other', 'image_path': 'selected_images\\sample_image_7_12.jpeg'}, {'audio_duration': '69.44s - 75.76s', 'actual_keyword': "counter attacks. It's a silent battle, fought in the dark with lines of code instead of bullets.", 'search_keyword': 'hd portrait images of a soldier in the dark with code flowing around them', 'image_path': 'selected_images\\sample_image_6_13.jpeg'}, {'audio_duration': '76.24s - 81.6s', 'actual_keyword': 'But the potential damage is just as real. The world is watching with baited breath.', 'search_keyword': 'hd portrait images of people watching news about Iran vs Israel war with concern', 'image_path': 'selected_images\\sample_image_7_4.jpeg'}, {'audio_duration': '81.6s - 92.16s', 'actual_keyword': "Hoping this tense standoff won't escalate into a full-blown war.", 'search_keyword': 'hd portrait images of soldiers from Iran and Israel standing face to face', 'image_path': 'selected_images\\sample_image_5_15.jpeg'}]
  audio_file = 'sample_audio/gtts_sample_us.mp3'
  output_video_file = 'video_outputs/output_video.mp4'

  # Create the video from images and audio
  create_video_from_images_with_audio(update_images_in_frames, audio_file, output_video_file)