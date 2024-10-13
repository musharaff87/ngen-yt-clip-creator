from text_to_speech import generate_audio_pyttsx3
from text_to_speech import generate_audio_gtts
from text_to_speech import change_pitch
from tranform_audio_frames import transcribe_audio_and_format
from gemini_api import generate_search_keywords
from generate_image import update_images_path_in_frame

if __name__ == "__main__":
    # Example sentences
    sentence = "peacock is the beautiful bird"
    sample_content_1 = """ Did you know that parrots are some of the most intelligent birds on the planet? Seriously, they're like the Einstein's of the bird world! But let's talk about them in a little more detail.

Parrots are a diverse group of birds, with over 350 species found all over the world. They're known for their bright colors, their ability to mimic sounds (including human speech!), and their complex social structures.  These guys are super social, living in flocks and communicating with each other using a variety of calls and whistles. It's like their own little bird language!

Their beaks are powerful tools, helping them crack open nuts and seeds (non-living objects!), and even shred their food. Some species, like the Amazon parrots, are known for their incredible ability to mimic sounds. They can learn words, phrases, and even entire songs! This is because they have a special structure in their vocal cords called a syrinx, which allows them to produce a wide range of sounds.

Parrots have evolved to live in a variety of habitats, from lush rainforests to dry grasslands. They often build their nests in tree cavities (non-living objects!), using sticks, leaves, and even feathers for bedding.  They play a vital role in their ecosystems, helping to disperse seeds and control insect populations.

So next time you see a parrot, remember that these amazing creatures are more than just pretty faces. They're intelligent, social, and vital members of the natural world! """

    #brief_content = get_brief_content(sentence)
    brief_content = sample_content_1

    # Convert the content to single audio frames
    main_audio_path = generate_audio_gtts(brief_content, "gtts_sample_us.mp3")
    print(f"Audio file created at: {main_audio_path}")

    # For Changing the Audio Pitch
    #output_audio = change_pitch(main_audio_path, 0.3)
    #output_audio.export("output_pitched.mp3", format="mp3")

    # Convert the audio to transcribed text format with frames mapped
    formatted_frames = transcribe_audio_and_format(main_audio_path)
    #print(formatted_frames)
    updated_frames = generate_search_keywords(formatted_frames, sentence)
    print(f"printing it outside {updated_frames}")
    #updated_frames = [{'audio_duration': '0.0s - 5.04s', 'actual_keyword': 'Did you know that parrots are some of the most intelligent birds on the planet?', 'search_keyword': 'hd portrait images of colorful parrots', 'image_path': ''}, {'audio_duration': '5.04s - 9.12s', 'actual_keyword': "Seriously, they're like the Einstein's of the bird world.", 'search_keyword': 'hd portrait images of peacocks with colorful feathers', 'image_path': ''}, {'audio_duration': '9.12s - 12.24s', 'actual_keyword': "But let's talk about them in a little more detail.", 'search_keyword': 'peacock hd portrait images', 'image_path': ''}, {'audio_duration': '12.24s - 15.04s', 'actual_keyword': 'Parrots are a diverse group of birds.', 'search_keyword': 'hd portrait images of peacocks', 'image_path': ''}, {'audio_duration': '15.04s - 21.44s', 'actual_keyword': "With over 350 species found all over the world, they're known for their bright colors,", 'search_keyword': 'peacock hd portrait images', 'image_path': ''}, {'audio_duration': '21.44s - 25.92s', 'actual_keyword': 'their ability to mimic sounds, including human speech,', 'search_keyword': 'hd portrait images of peacocks with vibrant plumage', 'image_path': ''}, {'audio_duration': '25.92s - 28.8s', 'actual_keyword': 'and their complex social structures.', 'search_keyword': 'hd portrait images of peacocks with vibrant plumage', 'image_path': ''}, {'audio_duration': '28.8s - 33.84s', 'actual_keyword': 'These guys are super social, living in flocks and communicating with each other', 'search_keyword': 'hd portrait images of peacocks in a flock communicating', 'image_path': ''}, {'audio_duration': '33.84s - 36.16s', 'actual_keyword': 'using a variety of calls and whistles.', 'search_keyword': 'hd portrait images of peacock', 'image_path': ''}, {'audio_duration': '37.04s - 39.84s', 'actual_keyword': "It's like their own little bird language.", 'search_keyword': 'hd portrait images of peacocks with vibrant plumage', 'image_path': ''}, {'audio_duration': '39.84s - 44.8s', 'actual_keyword': 'Their beaks are powerful tools, helping them crack open nuts and seeds,', 'search_keyword': 'hd portrait images of birds cracking nuts with their beaks', 'image_path': ''}, {'audio_duration': '45.44s - 49.2s', 'actual_keyword': 'non-living objects, and even shred their food.', 'search_keyword': 'hd portrait images of peacocks in their natural habitat', 'image_path': ''}, {'audio_duration': '49.2s - 56.64s', 'actual_keyword': 'Some species, like the Amazon parrots, are known for their incredible ability to mimic sounds.', 'search_keyword': 'hd portrait images of amazon parrots mimicking sounds', 'image_path': ''}, {'audio_duration': '56.72s - 61.6s', 'actual_keyword': 'They can learn words, phrases, and even entire songs.', 'search_keyword': 'hd portrait images of a peacock with vibrant colors', 'image_path': ''}, {'audio_duration': '61.6s - 66.24s', 'actual_keyword': 'This is because they have a special structure in their vocal cords called a serenx,', 'search_keyword': 'hd portrait images of peacocks with vibrant plumage', 'image_path': ''}, {'audio_duration': '67.2s - 70.24s', 'actual_keyword': 'which allows them to produce a wide range of sounds.', 'search_keyword': 'hd portrait images of a peacock', 'image_path': ''}, {'audio_duration': '70.88s - 74.08s', 'actual_keyword': 'Parrots have evolved to live in a variety of habitats.', 'search_keyword': 'hd portrait images of peacocks in their natural habitat', 'image_path': ''}, {'audio_duration': '74.72s - 80.64s', 'actual_keyword': 'From lush rainforests to dry grasslands, they often build their nests and tree cavities,', 'search_keyword': 'hd portrait images of peacock in a rainforest', 'image_path': ''}, {'audio_duration': '81.28s - 87.84s', 'actual_keyword': 'non-living objects, using sticks, leaves, and even feathers for bedding.', 'search_keyword': 'hd portrait images of a peacock with colorful feathers in a natural setting', 'image_path': ''}, {'audio_duration': '87.84s - 90.48s', 'actual_keyword': 'They play a vital role in their ecosystems,', 'search_keyword': 'peacock hd portrait images', 'image_path': ''}, {'audio_duration': '91.12s - 94.88s', 'actual_keyword': 'helping to disperse seeds and control insect populations.', 'search_keyword': 'hd portrait images of peacocks in their natural habitat', 'image_path': ''}, {'audio_duration': '95.52s - 100.8s', 'actual_keyword': 'So next time you see a parrot, remember that these amazing creatures are more than just', 'search_keyword': 'hd portrait images of peacocks with vibrant colors', 'image_path': ''}, {'audio_duration': '100.8s - 106.8s', 'actual_keyword': "pretty faces. They're intelligent, social, and vital members of the natural world.", 'search_keyword': 'hd portrait images of peacocks', 'image_path': ''}]
    update_images_in_frames = update_images_path_in_frame(updated_frames)
    print(update_images_in_frames)
    # for frame in formatted_frames:
    #     print(frame)

