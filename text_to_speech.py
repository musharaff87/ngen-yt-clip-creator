# text_to_speech.py
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
import os


def generate_audio_gtts(text, file_name):
    print("Converting Text to Speech With GTTS...")
    tts = gTTS(text=text, lang='en', tld='us', slow=False) # co.uk , co.in, ca, co.za
    output_path = f"sample_audio/{file_name}"
    tts.save(output_path)
    print("Conversion Completed Successfully")
    return output_path


def generate_audio_pyttsx3(text, file_name):
    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Set voice properties
    voices = engine.getProperty('voices')

    # Look for "Microsoft Mark - English (United States)"
    for i in range(len(voices)):
        voice = voices[i]
        if 'Microsoft Mark' in voice.name:  # Look for the desired voice
            engine.setProperty('voice', voice.id)
            print(f"Using voice: {voice.name}")
            break
    else:
        print("Error: Microsoft Mark voice not found. Using default voice.")

    # Set slower speech rate
    engine.setProperty('rate', 130)  # Lower the rate for slower speech

    # Set volume level (optional)
    engine.setProperty('volume', 1.5)  # Maximum volume

    engine.setProperty('pitch', 0.2)

    # Adjust the voice to sound deeper (harder timbre)
    # Note: pyttsx3 doesn't support pitch adjustment directly, but this voice typically has a deep tone.

    # Save the audio to a file
    output_path = f"sample_audio/{file_name}"
    print("Converting Text to Speech With pyttsx3...")
    engine.save_to_file(text, output_path)

    # Run the engine
    engine.runAndWait()

    print("Conversion Completed Successfully")
    return output_path


def change_pitch(file_path, semitones):
    sound = AudioSegment.from_file(file_path)

    # Change pitch
    new_sample_rate = int(sound.frame_rate * (2 ** (semitones / 12.0)))
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    #pitched_sound = pitched_sound.speedup(playback_speed=1.1) playback speed

    # Set back to original frame rate
    pitched_sound = pitched_sound.set_frame_rate(sound.frame_rate)


    return pitched_sound




if __name__ == "__main__":
    brief_content = "Hello this is sample content"  # Replace with actual content
    output_file = "sample_audio/audio_1.mp3"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    path = generate_audio(brief_content, output_file)
    print(f"Audio saved at: {path}")