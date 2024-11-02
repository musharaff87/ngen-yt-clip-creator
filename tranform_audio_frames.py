import whisper

# Load the Whisper model
model = whisper.load_model("base")


def split_text(text, max_length=55):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        # Add the word to the current chunk
        current_chunk.append(word)
        # Check if adding the next word would exceed the max length
        if len(' '.join(current_chunk)) >= max_length:
            chunks.append(' '.join(current_chunk[:-1]))  # Add the current chunk to the list
            current_chunk = [word]  # Start a new chunk with the current word

    # Add any remaining words as the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

# Function to transcribe audio and format the result into desired frames
def transcribe_audio_and_format(audio_file, max_length=40):
    # Transcribe the audio file with timestamps
    result = model.transcribe(audio_file)

    frames = []  # List to store the formatted frames

    # Loop through the segments and create the frame structure
    for segment in result['segments']:
        start_time = round(segment['start'], 5)
        end_time = round(segment['end'], 5)
        print(f"start_time: {start_time}, start time segment: {segment['start']}, end_time: {end_time}, end time segment: {segment['end']}")

        # Split the segment text into smaller chunks
        text_chunks = split_text(segment['text'].strip(), max_length)

        # Calculate duration for each chunk
        chunk_duration = (end_time - start_time) / len(text_chunks) if text_chunks else 0

        for i, chunk in enumerate(text_chunks):
            # Calculate start and end time for the chunk
            chunk_start_time = round(start_time + i * chunk_duration, 5)
            chunk_end_time = round(chunk_start_time + chunk_duration, 5)

            # Create the frame dictionary with placeholders for search_keyword and image_path
            frame = {
                "audio_duration": f"{chunk_start_time}s - {chunk_end_time}s",
                "actual_keyword": chunk,
                "search_keyword": "",
                "image_path": ""
            }

            # Add the frame to the list of frames
            frames.append(frame)

    return frames



# Call the function with your audio file and print the result
if __name__ == "__main__":
    formatted_frames = transcribe_audio_and_format("sample_audio/iran_war.mp3")
    for frame in formatted_frames:
        print(frame)