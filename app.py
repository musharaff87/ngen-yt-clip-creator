from text_to_speech import generate_audio_pyttsx3
from text_to_speech import generate_audio_gtts
from text_to_speech import change_pitch
from tranform_audio_frames import transcribe_audio_and_format
from gemini_api import get_brief_content
from gemini_api import generate_search_keywords
from generate_image import update_images_path_in_frame
from generate_video_with_images import create_video_from_images_with_audio

if __name__ == "__main__":
    # Example sentences
    sentence = "about Marvel Spiderman"
    sample_content_1 = """ Did you know that parrots are some of the most intelligent birds on the planet? Seriously, they're like the Einstein's of the bird world! But let's talk about them in a little more detail.

Parrots are a diverse group of birds, with over 350 species found all over the world. They're known for their bright colors, their ability to mimic sounds (including human speech!), and their complex social structures.  These guys are super social, living in flocks and communicating with each other using a variety of calls and whistles. It's like their own little bird language!

Their beaks are powerful tools, helping them crack open nuts and seeds (non-living objects!), and even shred their food. Some species, like the Amazon parrots, are known for their incredible ability to mimic sounds. They can learn words, phrases, and even entire songs! This is because they have a special structure in their vocal cords called a syrinx, which allows them to produce a wide range of sounds.

Parrots have evolved to live in a variety of habitats, from lush rainforests to dry grasslands. They often build their nests in tree cavities (non-living objects!), using sticks, leaves, and even feathers for bedding.  They play a vital role in their ecosystems, helping to disperse seeds and control insect populations.

So next time you see a parrot, remember that these amazing creatures are more than just pretty faces. They're intelligent, social, and vital members of the natural world! """

    brief_content = get_brief_content(sentence)
    #brief_content = sample_content_1

    # Convert the content to single audio frames
    main_audio_path = generate_audio_gtts(brief_content, "spider_us.mp3")
    print(f"Audio file created at: {main_audio_path}")

    # For Changing the Audio Pitch
    #output_audio = change_pitch(main_audio_path, 0.3)
    #output_audio.export("output_pitched.mp3", format="mp3")

    # Convert the audio to transcribed text format with frames mapped
    formatted_frames = transcribe_audio_and_format(main_audio_path)
    print(formatted_frames)
    updated_frames = generate_search_keywords(formatted_frames, sentence)
    print(f"printing it outside {updated_frames}")
    update_images_in_frames = update_images_path_in_frame(updated_frames)
    print(update_images_in_frames)
    output_video_file = 'video_outputs/output_video_2.mp4'

    # Create the video from images and audio
    create_video_from_images_with_audio(update_images_in_frames, main_audio_path, output_video_file)

    #print(update_images_in_frames)
    # for frame in formatted_frames:
    #     print(frame)

