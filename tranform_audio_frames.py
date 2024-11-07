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
            chunks.append(' '.join(current_chunk[:-1]))  # Add the current chunk to the list, excluding the last word
            current_chunk = [word]  # Start a new chunk with the current word

    # Add any remaining words as the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    # Check if the last chunk has only one word
    if len(chunks) > 1 and len(chunks[-1].split()) == 1:
        # Merge the last chunk with the previous one
        chunks[-2] += ' ' + chunks[-1]
        chunks.pop()  # Remove the single-word chunk

    return chunks

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

# Function to transcribe audio and format the result into desired frames
def transcribe_audio_and_format_test(audio_file, max_length=40):
    # Transcribe the audio file with word-level timestamps
    result = model.transcribe(audio_file, word_timestamps=True)

    frames = []  # List to store the formatted frames

    # Loop through the segments and use word timestamps for accurate timing
    for segment in result['segments']:
        words = segment['words']
        current_text = ""
        chunk_start_time = None

        for word_info in words:
            word = word_info['word']
            word_start = word_info['start']
            word_end = word_info['end']

            # Initialize the start time of a chunk
            if not current_text:
                chunk_start_time = word_start

            # Add word to current text chunk if within max length
            if len(current_text + " " + word.strip()) <= max_length:
                current_text += " " + word.strip()
            else:
                # End of a chunk: store it with the accumulated text and timing
                if frames and len(current_text.split()) == 1:
                    # If the current chunk has only one word, merge it with the previous frame
                    previous_frame = frames[-1]
                    previous_frame["actual_keyword"] += " " + current_text.strip()
                    previous_frame[
                        "audio_duration"] = f"{previous_frame['audio_duration'].split(' - ')[0]}s - {word_end}s"
                else:
                    # Otherwise, add as a new frame
                    frames.append({
                        "audio_duration": f"{chunk_start_time}s - {word_end}s",
                        "actual_keyword": current_text.strip(),
                        "search_keyword": "",
                        "image_path": ""
                    })

                # Reset for the next chunk
                current_text = word.strip()
                chunk_start_time = word_start

        # Add any remaining text as the last chunk for this segment
        if current_text:
            if frames and len(current_text.split()) == 1:
                # Merge single-word last chunk with the previous frame
                previous_frame = frames[-1]
                previous_frame["actual_keyword"] += " " + current_text.strip()
                previous_frame["audio_duration"] = f"{previous_frame['audio_duration'].split(' - ')[0]}s - {word_end}s"
            else:
                # Add normally if it’s not a single word or there are no frames yet
                frames.append({
                    "audio_duration": f"{chunk_start_time}s - {word_end}s",
                    "actual_keyword": current_text.strip(),
                    "search_keyword": "",
                    "image_path": ""
                })

    return frames



# Call the function with your audio file and print the result
if __name__ == "__main__":
    formatted_frames = transcribe_audio_and_format("sample_audio/Trump Wins in US president election 202.mp3")
    for frame in formatted_frames:
        print(frame)