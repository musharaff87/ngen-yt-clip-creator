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

def resize_image2(image_path, target_size):
    """
    Resizes an image to a mobile-friendly aspect ratio (similar to 9:16),
    cropping edges if necessary, and then resizes to the target size.
    """
    image = Image.open(image_path)
    original_width, original_height = image.size
    original_aspect_ratio = original_width / original_height
    mobile_aspect_ratio = target_size[0] / target_size[1]  # 9:16 ratio

    # Print original details
    print(f"Original Image Size: {original_width}x{original_height}")
    print(f"Original Aspect Ratio: {original_aspect_ratio:.2f}")
    print(f"Target Aspect Ratio: {mobile_aspect_ratio:.2f}")

    # Determine if we need to crop
    if abs(original_aspect_ratio - mobile_aspect_ratio) > 0.05:
        print("Aspect ratio difference detected, cropping required.")
        # Crop to maintain a 9:16 aspect ratio
        if original_aspect_ratio > mobile_aspect_ratio:
            # Wider than 9:16, crop width
            new_width = int(mobile_aspect_ratio * original_height)
            left = (original_width - new_width) // 2
            print(f"Cropping width from {original_width} to {new_width}")
            print(f"Crop box (left, top, right, bottom): ({left}, 0, {left + new_width}, {original_height})")
            image = image.crop((left, 0, left + new_width, original_height))
        else:
            # Taller than 9:16, crop height
            new_height = int(original_width / mobile_aspect_ratio)
            top = (original_height - new_height) // 2
            print(f"Cropping height from {original_height} to {new_height}")
            print(f"Crop box (left, top, right, bottom): (0, {top}, {original_width}, {top + new_height})")
            image = image.crop((0, top, original_width, top + new_height))
    else:
        print("Aspect ratio is close enough, no cropping needed.")

    # Resize the cropped or original image
    resized_image = image.resize(target_size, Image.Resampling.LANCZOS)
    print(f"Resized Image Size: {target_size[0]}x{target_size[1]}")

    # Save the resized image
    resized_images_folder = os.path.join(os.path.dirname(image_path), 'resized_images')
    os.makedirs(resized_images_folder, exist_ok=True)
    resized_image_path = os.path.join(resized_images_folder, os.path.basename(image_path))
    resized_image.save(resized_image_path)

    print(f"Resized image saved to: {resized_image_path}")

    return resized_image_path

def apply_transitions(img_clip, duration):
    """Apply transitions like fade-in and fade-out to the image clip."""
    img_clip = vfx.fadein(img_clip, duration=0.3).fadeout(0.3)  # Using fadein and fadeout from vfx
    return img_clip


def add_subtitle_to_clip(image_clip, actual_text, duration, screen_width=720, margin=50, offset=600):
    """Adds subtitles to the image clip with enhanced styling and dynamic word wrapping."""
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
        stroke_color='yellow',    # Set the stroke color to yellow
        stroke_width=2,           # Increase stroke width for a thicker outline
        size=(text_width_limit, None)
    ).margin(bottom=0)

    # Adding a slight shadow for additional visibility
    shadow = TextClip(
        wrapped_text,
        fontsize=45,
        font='Arial-Bold',
        color='black',
        stroke_color='black',
        stroke_width=1,
        size=(text_width_limit, None)
    ).set_position((5, 5))  # Offset for shadow

    # Composite subtitle with shadow and main text
    subtitle_composite = CompositeVideoClip([shadow, subtitle])

    # Set the duration and position of the composite subtitle
    subtitle_composite = subtitle_composite.set_duration(duration)
    image_height = image_clip.size[1]
    subtitle_y_position = image_height - offset

    # Return the final composite video clip with the image and styled subtitles
    return CompositeVideoClip(
        [image_clip, subtitle_composite.set_position(('center', subtitle_y_position)).set_duration(duration)]
    )

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
    for i, frame_data in enumerate(image_data):
        image_path = frame_data['image_path']
        actual_keyword = frame_data['actual_keyword']
        start_time, end_time = frame_data['audio_duration'].split(' - ')

        start_time = float(start_time.replace('s', ''))
        end_time = float(end_time.replace('s', ''))

        # Ensure end_time does not overlap with the next clip’s start time
        if i < len(image_data) - 1:
            next_start_time = float(image_data[i + 1]['audio_duration'].split(' - ')[0].replace('s', ''))
            if next_start_time > end_time:
                end_time = next_start_time

        duration = end_time - start_time

        # Resize the image to the target size
        resized_image_path = resize_image(image_path, target_size)

        # Create and configure the image clip
        img_clip = ImageClip(resized_image_path).set_duration(duration)

        # Add filters, transitions, and animation to the clip
        #img_clip = apply_filters_to_image_clip(img_clip)
        #if i%3 == 0:
            #img_clip = apply_transitions(img_clip, duration)

        img_clip = apply_animation(img_clip)

        # Add subtitles
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

    # Write the final video file with high-quality settings
    try:
        video.write_videofile(
            output_video_file,
            fps=30,                        # Increase FPS if needed for smoothness
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",               # Increase bitrate for better quality
            preset="slow",                 # Use 'slow' preset for high-quality compression
            threads=4                      # Use multi-threading for efficiency
        )
    except Exception as e:
        print(f"Error Generating Video... {e}")

if __name__ == "__main__":
  update_images_in_frames = [{'audio_duration': '0.0s - 1.86667s', 'actual_keyword': 'Hey, everyone, you got to hear this.', 'search_keyword': 'Game of Thrones best series dragon scene', 'image_path': 'selected_images\\sample_image_3_1.jpeg'},
{'audio_duration': '1.86667s - 3.73334s', 'actual_keyword': 'Game of Thrones is still the King of TV', 'search_keyword': 'Game of Thrones Iron Throne still best TV show', 'image_path': 'selected_images\\sample_image_3_2.jpeg'},
{'audio_duration': '3.73333s - 5.6s', 'actual_keyword': 'even after that', 'search_keyword': 'Game of Thrones characters even after the ending', 'image_path': 'selected_images\\sample_image_8_3.jpeg'},
{'audio_duration': '5.6s - 7.76s', 'actual_keyword': "controversial ending. Why? Because it's", 'search_keyword': 'Game of Thrones ending fan art', 'image_path': 'selected_images\\sample_image_10_4.jpeg'},
{'audio_duration': '7.76s - 9.92s', 'actual_keyword': 'got everything. Epic battles with', 'search_keyword': 'Game of Thrones epic battle scenes', 'image_path': 'selected_images\\sample_image_1_5.jpeg'},
{'audio_duration': '9.92s - 12.08s', 'actual_keyword': 'dragons soaring', 'search_keyword': 'dragon soaring over a castle', 'image_path': 'selected_images\\sample_image_10_6.jpeg'},
{'audio_duration': '12.08s - 14.34667s', 'actual_keyword': 'through the sky. I see landscapes and', 'search_keyword': 'dragons flying over landscapes in game of thrones', 'image_path': 'selected_images\\sample_image_5_7.jpeg'},
{'audio_duration': '14.34667s - 16.61334s', 'actual_keyword': 'swords clashing. Then there are the', 'search_keyword': 'swords clashing in game of thrones battle', 'image_path': 'selected_images\\sample_image_6_8.jpeg'},
{'audio_duration': '16.61333s - 18.88s', 'actual_keyword': 'characters. Oh, man,', 'search_keyword': 'Game of Thrones characters with swords', 'image_path': 'selected_images\\sample_image_6_9.png'},
{'audio_duration': '18.88s - 21.92s', 'actual_keyword': "they're complex and flawed. You've got", 'search_keyword': 'Game of Thrones characters with flaws', 'image_path': 'selected_images\\sample_image_3_10.png'},
{'audio_duration': '21.92s - 24.96s', 'actual_keyword': 'John Snow, the noble bastard, Daenerys Targaryen,', 'search_keyword': 'Daenerys Targaryen dragons Game of Thrones', 'image_path': 'selected_images\\sample_image_3_11.jpeg'},
{'audio_duration': '24.96s - 26.77333s', 'actual_keyword': 'the Queen with fire in her eyes, and', 'search_keyword': 'Daenerys Targaryen with fire in her eyes', 'image_path': 'selected_images\\sample_image_7_12.jpeg'},
{'audio_duration': '26.77333s - 28.58666s', 'actual_keyword': 'Tyrion Lannister, the cleverest dwarf', 'search_keyword': 'Tyrion Lannister Game of Thrones Quotes', 'image_path': 'selected_images\\sample_image_4_13.jpeg'},
{'audio_duration': '28.58667s - 30.4s', 'actual_keyword': 'in Westeros.', 'search_keyword': 'Westeros map with important locations', 'image_path': 'selected_images\\sample_image_5_14.jpeg'},
{'audio_duration': '31.04s - 33.12s', 'actual_keyword': "Plus, the plot is so intricate, it's", 'search_keyword': 'Game of Thrones intricate plot details', 'image_path': 'selected_images\\sample_image_7_15.jpeg'},
{'audio_duration': '33.12s - 35.2s', 'actual_keyword': 'like trying to untangle a thousand', 'search_keyword': 'untangling a thousand threads of plot in Game of Thrones', 'image_path': 'selected_images\\sample_image_8_16.jpeg'},
{'audio_duration': '35.2s - 37.28s', 'actual_keyword': 'knots. But the real genius', 'search_keyword': 'Game of Thrones characters with intricate hair knots', 'image_path': 'selected_images\\sample_image_8_17.jpeg'},
{'audio_duration': '37.28s - 38.90667s', 'actual_keyword': 'of Game of Thrones is the way it makes', 'search_keyword': 'Game of Thrones characters with dragons', 'image_path': 'selected_images\\sample_image_4_18.jpeg'},
{'audio_duration': '38.90667s - 40.53334s', 'actual_keyword': "you question everything. It's not black", 'search_keyword': 'Questioning the Game of Thrones ending', 'image_path': 'selected_images\\sample_image_5_19.jpeg'},
{'audio_duration': '40.53333s - 42.16s', 'actual_keyword': 'and white,', 'search_keyword': 'black and white wolf with red eyes', 'image_path': 'selected_images\\sample_image_10_20.jpeg'},
{'audio_duration': '42.16s - 44.05333s', 'actual_keyword': "it's shades of gray with everyone", 'search_keyword': 'Game of Thrones characters with gray morality', 'image_path': 'selected_images\\sample_image_9_21.jpeg'},
{'audio_duration': '44.05333s - 45.94666s', 'actual_keyword': "playing the game of power. It's a", 'search_keyword': 'Iron Throne Game of Thrones power struggle', 'image_path': 'selected_images\\sample_image_6_22.jpeg'},
{'audio_duration': '45.94667s - 47.84s', 'actual_keyword': 'series that stays with you long', 'search_keyword': 'Best TV series that leave a lasting impact', 'image_path': 'selected_images\\sample_image_9_23.jpeg'},
{'audio_duration': '47.84s - 49.89333s', 'actual_keyword': 'after you finish watching, leaving you', 'search_keyword': 'Feeling empty after finishing a great tv show', 'image_path': 'selected_images\\sample_image_5_24.jpeg'},
{'audio_duration': '49.89333s - 51.94666s', 'actual_keyword': 'thinking about the politics, the', 'search_keyword': 'Game of Thrones political alliances and betrayals', 'image_path': 'selected_images\\sample_image_9_25.jpeg'},
{'audio_duration': '51.94667s - 54.0s', 'actual_keyword': 'characters, and the fate of Westeros.', 'search_keyword': 'Game of Thrones characters and their fates in Westeros', 'image_path': 'selected_images\\sample_image_8_26.jpeg'},
{'audio_duration': '54.0s - 59.4s', 'actual_keyword': "So if you haven't seen it yet, you're", 'search_keyword': '** Game of Thrones characters', 'image_path': 'selected_images\\sample_image_9_14.png'},
{'audio_duration': '59.4s - 64.8s', 'actual_keyword': 'missing out on a truly epic journey.', 'search_keyword': 'Epic journey through Westeros', 'image_path': 'selected_images\\sample_image_7_28.jpeg'},
]
  audio_file = 'sample_audio/why game of thrones is best series.mp3'
  output_video_file = 'video_outputs/edited_got.mp4'

  # Create the video from images and audio
  create_video_from_images_with_audio(update_images_in_frames, audio_file, output_video_file)