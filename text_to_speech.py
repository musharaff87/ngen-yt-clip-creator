# text_to_speech.py
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
import requests
from elevenlabs import ElevenLabs
import json
import os


def load_api_keys(filename='eleven_labs_api_keys.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['api_keys']


def generate_audio_elevenlabs(text, file_name):
    print("Loading API keys...")
    api_keys = load_api_keys()

    for api_key in api_keys:
        print(f"Checking remaining character credits for API key: {api_key[:5]}***")
        headers = {
            "xi-api-key": api_key
        }

        # Send a GET request to the user endpoint to check credits
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            character_limit = user_data['subscription']['character_limit']
            character_count = user_data['subscription']['character_count']
            remaining_characters = character_limit - character_count
            print(f"Remaining characters for synthesis: {remaining_characters}")

            # Check if enough credits are available
            if remaining_characters > len(text) // 2 - 10:
                print("Converting Text to Speech With Eleven Labs API...")
                client = ElevenLabs(api_key=api_key)

                audio_generator = client.generate(
                    text=text,
                    voice="Brian",
                    model="eleven_turbo_v2"  # Specify the desired model
                )

                output_path = f"sample_audio/{file_name}"
                with open(output_path, "wb") as f:
                    for chunk in audio_generator:
                        f.write(chunk)

                print("Conversion Completed Successfully")
                return output_path
        else:
            print(
                f"Failed to retrieve user data for API key {api_key[:5]}***: {response.status_code} - {response.text}")

    print("All API keys are exhausted, falling back to gTTS...")
    return generate_audio_gtts(text, file_name)

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
    # brief_content = "Hello this is sample content"  # Replace with actual content
    # output_file = "sample_audio/audio_1.mp3"
    #
    # # Ensure the directory exists
    # os.makedirs(os.path.dirname(output_file), exist_ok=True)
    #
    # path = generate_audio(brief_content, output_file)
    # print(f"Audio saved at: {path}")

    api_keys = load_api_keys()
    for api_key in api_keys:
        headers = {
            "xi-api-key": api_key
        }

        # Send a GET request to the user endpoint to check credits
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            character_limit = user_data['subscription']['character_limit']
            character_count = user_data['subscription']['character_count']
            remaining_characters = character_limit - character_count
            print(f"Charecter Count: #{character_count}")
            print(f"Remaining characters for synthesis: {remaining_characters}")
