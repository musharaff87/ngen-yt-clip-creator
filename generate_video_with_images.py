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
  update_images_in_frames = [{'audio_duration': '0.0s - 5.04s', 'actual_keyword': 'Did you know that parrots are some of the most intelligent birds on the planet?', 'search_keyword': 'hd portrait images of colorful parrots', 'image_path': 'selected_images\\sample_image_1_1.jpeg'}, {'audio_duration': '5.04s - 9.12s', 'actual_keyword': "Seriously, they're like the Einstein's of the bird world.", 'search_keyword': 'hd portrait images of parrots with intelligent expressions', 'image_path': 'selected_images\\sample_image_1_2.jpeg'}, {'audio_duration': '9.12s - 12.24s', 'actual_keyword': "But let's talk about them in a little more detail.", 'search_keyword': 'hd portrait images of parrots in folklore and mythology', 'image_path': 'selected_images\\sample_image_1_3.jpeg'}, {'audio_duration': '12.24s - 15.04s', 'actual_keyword': 'Parrots are a diverse group of birds.', 'search_keyword': 'hd portrait images of colorful parrots', 'image_path': 'selected_images\\sample_image_4_4.jpeg'}, {'audio_duration': '15.04s - 21.44s', 'actual_keyword': "With over 350 species found all over the world, they're known for their bright colors,", 'search_keyword': 'hd portrait images of colorful parrots in their natural habitat', 'image_path': 'selected_images\\sample_image_3_5.jpeg'}, {'audio_duration': '21.44s - 25.92s', 'actual_keyword': 'their ability to mimic sounds, including human speech,', 'search_keyword': 'hd portrait images of parrots mimicking human speech', 'image_path': 'selected_images\\sample_image_5_6.jpeg'}, {'audio_duration': '25.92s - 28.8s', 'actual_keyword': 'and their complex social structures.', 'search_keyword': 'hd portrait images of parrots in their natural habitat', 'image_path': 'selected_images\\sample_image_4_7.jpeg'}, {'audio_duration': '28.8s - 33.84s', 'actual_keyword': 'These guys are super social, living in flocks and communicating with each other', 'search_keyword': 'hd portrait images of parrots in a flock communicating', 'image_path': 'selected_images\\sample_image_1_8.jpeg'}, {'audio_duration': '33.84s - 36.16s', 'actual_keyword': 'using a variety of calls and whistles.', 'search_keyword': 'hd portrait images of colorful parrots', 'image_path': 'selected_images\\sample_image_3_22.jpeg'}, {'audio_duration': '37.04s - 39.84s', 'actual_keyword': "It's like their own little bird language.", 'search_keyword': 'hd portrait images of parrots talking to each other', 'image_path': 'selected_images\\sample_image_4_10.jpeg'}, {'audio_duration': '39.84s - 44.8s', 'actual_keyword': 'Their beaks are powerful tools, helping them crack open nuts and seeds,', 'search_keyword': 'parrot beak hd portrait images', 'image_path': 'selected_images\\sample_image_3_11.jpeg'}, {'audio_duration': '45.44s - 49.2s', 'actual_keyword': 'non-living objects, and even shred their food.', 'search_keyword': 'hd portrait images of parrots on branches', 'image_path': 'selected_images\\sample_image_2_12.jpeg'}, {'audio_duration': '49.2s - 56.64s', 'actual_keyword': 'Some species, like the Amazon parrots, are known for their incredible ability to mimic sounds.', 'search_keyword': 'hd portrait images of amazon parrots', 'image_path': 'selected_images\\sample_image_3_13.jpeg'}, {'audio_duration': '56.72s - 61.6s', 'actual_keyword': 'They can learn words, phrases, and even entire songs.', 'search_keyword': 'hd portrait images of parrots singing', 'image_path': 'selected_images\\sample_image_1_14.jpeg'}, {'audio_duration': '61.6s - 66.24s', 'actual_keyword': 'This is because they have a special structure in their vocal cords called a serenx,', 'search_keyword': 'hd portrait images of parrots with colorful feathers', 'image_path': 'selected_images\\sample_image_4_15.jpeg'}, {'audio_duration': '67.2s - 70.24s', 'actual_keyword': 'which allows them to produce a wide range of sounds.', 'search_keyword': 'hd portrait images of colorful parrots in their natural habitat', 'image_path': 'selected_images\\sample_image_4_23.jpeg'}, {'audio_duration': '70.88s - 74.08s', 'actual_keyword': 'Parrots have evolved to live in a variety of habitats.', 'search_keyword': 'hd portrait images of colorful parrots in their natural habitats', 'image_path': 'selected_images\\sample_image_4_13.jpeg'}, {'audio_duration': '74.72s - 80.72s', 'actual_keyword': 'From lush rainforests to dry grasslands, they often build their nests and tree cavities,', 'search_keyword': 'parrot hd portrait images in rainforest', 'image_path': 'selected_images\\sample_image_3_18.jpeg'}, {'audio_duration': '81.28s - 87.84s', 'actual_keyword': 'non-living objects, using sticks, leaves, and even feathers for bedding.', 'search_keyword': 'hd portrait images of parrots in their natural habitat with sticks, leaves, and feathers for bedding', 'image_path': 'selected_images\\sample_image_4_19.png'}, {'audio_duration': '87.84s - 94.88s', 'actual_keyword': 'They play a vital role in their ecosystems, helping to disperse seeds and control insect populations.', 'search_keyword': '**HD portrait images of colorful parrots in their natural habitat**', 'image_path': 'selected_images\\sample_image_1_13.jpeg'}, {'audio_duration': '95.52s - 101.12s', 'actual_keyword': 'So next time you see a parrot, remember that these amazing creatures are more than just pretty', 'search_keyword': 'hd portrait images of parrots', 'image_path': 'selected_images\\sample_image_5_21.jpeg'}, {'audio_duration': '101.12s - 106.8s', 'actual_keyword': "faces. They're intelligent, social, and vital members of the natural world.", 'search_keyword': 'hd portrait images of parrots with beautiful feathers', 'image_path': 'selected_images\\sample_image_5_22.jpeg'}]

  audio_file = 'sample_audio/gtts_sample_us.mp3'
  output_video_file = 'video_outputs/output_video.mp4'

  # Create the video from images and audio
  create_video_from_images_with_audio(update_images_in_frames, audio_file, output_video_file)