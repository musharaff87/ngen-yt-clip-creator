import whisper

# Load the Whisper model
model = whisper.load_model("base")


# Function to transcribe audio and format the result into desired frames
def transcribe_audio_and_format(audio_file):
    # Transcribe the audio file with timestamps
    result = model.transcribe(audio_file)

    frames = []  # List to store the formatted frames

    # Loop through the segments and create the frame structure
    for segment in result['segments']:
        start_time = round(segment['start'], 5)
        end_time = round(segment['end'], 5)
        print(f"start_time: {start_time}, start time segment: {segment['start']}, end_time: {end_time}, end time segment: {segment['end']}")

        # Create the frame dictionary with placeholders for search_keyword and image_path
        frame = {
            "audio_duration": f"{start_time}s - {end_time}s",
            "actual_keyword": segment['text'].strip(),
            "search_keyword": "",
            "image_path": ""
        }

        # Add the frame to the list of frames
        frames.append(frame)

    return frames


# Call the function with your audio file and print the result
if __name__ == "__main__":
    formatted_frames = transcribe_audio_and_format("sample_audio/gtts_sample_us.mp3")
    for frame in formatted_frames:
        print(frame)