import whisper
from difflib import SequenceMatcher

# Load the Whisper model
model = whisper.load_model("base")


def align_and_correct(transcribed_words, original_words):
    """
    Aligns and corrects transcribed words using the original content for reference.
    """
    corrected_words = []

    for word_info in transcribed_words:
        transcribed_word = word_info['word'].strip()

        # Find the most similar word in the original content
        best_match = max(original_words, key=lambda original_word: SequenceMatcher(None, transcribed_word, original_word).ratio())
        similarity = SequenceMatcher(None, transcribed_word, best_match).ratio()

        # If similarity is above a threshold (e.g., 0.8), replace with the original word
        if similarity > 0.8:
            corrected_word = best_match
        else:
            corrected_word = transcribed_word

        corrected_words.append({
            "word": corrected_word,
            "start": word_info["start"],
            "end": word_info["end"]
        })

    return corrected_words


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

    full_context = " ".join(segment['text'] for segment in result['segments'])

    # Print the full context
    print("Full Transcription Context:")
    print(full_context)

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
def transcribe_audio_and_format_test(audio_file, original_content, max_length=40):
    # Transcribe the audio file with word-level timestamps
    result = model.transcribe(audio_file, word_timestamps=True)

    # Tokenize original content
    original_words = original_content.split()

    # Align and correct transcribed words with the original content
    transcribed_words = result['segments'][0]['words']
    corrected_words = align_and_correct(transcribed_words, original_words)

    print(f"transcribed_words: {transcribed_words}")
    print(f"corrected_words: {corrected_words}")

    frames = []  # List to store the formatted frames
    current_text = ""
    chunk_start_time = None

    # Create frames based on corrected words
    for word_info in corrected_words:
        word = word_info["word"]
        word_start = word_info["start"]
        word_end = word_info["end"]

        # Initialize the start time of a chunk
        if not current_text:
            chunk_start_time = word_start

        # Add word to current text chunk if within max length
        if len(current_text + " " + word.strip()) <= max_length:
            current_text += " " + word.strip()
        else:
            # Add the current chunk to frames
            frames.append({
                "audio_duration": f"{chunk_start_time}s - {word_end}s",
                "actual_keyword": current_text.strip(),
                "search_keyword": "",
                "image_path": ""
            })
            # Reset for the next chunk
            current_text = word.strip()
            chunk_start_time = word_start

    # Add any remaining text as the last chunk
    if current_text:
        frames.append({
            "audio_duration": f"{chunk_start_time}s - {word_end}s",
            "actual_keyword": current_text.strip(),
            "search_keyword": "",
            "image_path": ""
        })

    return frames




# Call the function with your audio file and print the result
if __name__ == "__main__":
    sample_content = " You have to know about this crazy scene in Attack On Titan.  Grisha and eron discover Mikasa's parents murdered and Mikasa is kidnaped.  Grisha orders eren to wait, but we get this epic shot of Eren's wide-eyed intense face,  seriously unsettling. He's clearly distressed, maybe even furious. But here's the wild part.  Eren completely ignores his dad. He finds a knife somehow locates the cabin where  Mikasa is being held and rescues her. Seriously, how? The manga doesn't explain it. It's a major  mystery. This moment is huge for understanding Eren's character development, his disobedience,  his fierce protectiveness of Mikasa and that chilling unforgettable stare.  The scene leaves you with so many questions. Did he have some kind of ability we haven't seen yet?  Let me know your theories in the comments."
    #formatted_frames = transcribe_audio_and_format("sample_audio/test_eren.mp3")
    formatted_frames = transcribe_audio_and_format_test("sample_audio/test_eren.mp3", sample_content)
    for frame in formatted_frames:
        print(frame)