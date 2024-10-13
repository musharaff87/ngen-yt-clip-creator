import time

import google.generativeai as genai
import json
import re
import random


def load_api_key():
    # Ensure the JSON file has the correct path and structure
    with open('gemini_credential.json', 'r') as file:
        config = json.load(file)
    return config['api_key']


# Configure the API key
genai.configure(api_key=load_api_key())

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 4000,  # Set max output tokens to 400
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


def get_brief_content(sentence):
    print("Generating Content from Gemini...")
    # Create a prompt that includes the user's input
    prompt = f"provide a brief, up-to-date description about: {sentence}. Include living and non-living objects where relevant. Make it sound like a YouTuber explaining to viewers in a conversational tone. Also use attracting sentence in the start of the context like eg: did you know? . Also omit sentence like welcome back to channel like that just start talking with viewers. Also make sure every sentence in the content must have pull stop with minimum of 10 words.   Limit the response to 250 - 300 words."

    # Start chat session with initial message
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [prompt],
            },
        ]
    )

    # Send message and get response
    response = chat_session.send_message(prompt)
    print("Content Generated Successfully")
    return response.text.strip()


additional_sentences = [
    "is often admired for its vibrant colors.",
    "has been a topic of fascination for centuries.",
    "is known for its unique behaviors and characteristics.",
    "plays a significant role in its ecosystem.",
    "has various cultural meanings around the world.",
    "is often featured in folklore and mythology.",
    "can be found in diverse habitats across the globe.",
    "is one of the most popular subjects in wildlife photography.",
    "is an important symbol in many cultures.",
    "can be seen in various documentaries and wildlife shows."
]


def generate_search_keywords(formatted_frames, main_content_sentence):
    print("Generating Search Keywords from Gemini...")

    # Store unique search keywords
    unique_search_keywords = set()
    # Construct a prompt that includes all actual keywords
    actual_keywords = [frame['actual_keyword'] for frame in formatted_frames]
    updated_frames = []

    for frame in formatted_frames:
        actual_keyword = frame['actual_keyword']
        prompt = (
            f"this is formatted_frames = {actual_keyword}\n"
            f"this is main_content = {main_content_sentence}\n\n"
            f"Generate relevant search keywords for the actual keyword.\n"
            f"the search keyword must have objects or living things or something sentence that is meaningful to generate images.\n"
            f"also the search keyword should contain 'hd portrait images' like keyword to generate the images. the search keyword should more likely a google search.\n"
            f"also if the actual keyword doesn't have any meaning then generate random image generation keyword using main_content.\n"
            f"note: Also avoid giving explanation and stuff just give the search_keyword, just give like this 'search_keyword: your answer here'\n"
        )

        # Start chat session with the constructed prompt
        chat_session = model.start_chat(
            history=[{
                "role": "user",
                "parts": [prompt],
            }]
        )

        # Send message and get response
        try:
            response = chat_session.send_message(prompt)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying time count 1...")
            time.sleep(10)
            try:
                response = chat_session.send_message(prompt)
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Retrying time count 2...")
                time.sleep(30)
                response = chat_session.send_message(prompt)

        #print(f"Response from Gemini: {response}")

        # Fix formatting issues in response text
        raw_text = response.parts[0].text
        cleaned_text = raw_text.replace("'", "").replace('"', '').strip()

        # Extract the search keyword
        search_keyword_pattern = re.compile(r"search_keyword:\s*(.+)", re.IGNORECASE)
        search_keyword_match = search_keyword_pattern.search(cleaned_text)

        # If we find a match, use it; otherwise, fallback to main_content_sentence
        if search_keyword_match:
            search_keyword = search_keyword_match.group(1).strip()
        else:
            search_keyword = main_content_sentence

        # Check for duplicates and combine if necessary
        if search_keyword in unique_search_keywords:
            # Randomly select a sentence to append to the main content
            additional_sentence = random.choice(additional_sentences)
            combined_keyword = f"{main_content_sentence} {additional_sentence}"
            print(f"Duplicate keyword found, combining with additional sentence: {combined_keyword}")

            # Generate a new search keyword using the combined keyword
            prompt_combined = (
                f"this is formatted_frames = {actual_keyword}\n"
                f"this is main_content = {combined_keyword}\n\n"
                f"Generate relevant search keywords for the actual keyword.\n"
                f"the search keyword must have objects or living things or something sentence that is meaningful to generate images.\n"
                f"also the search keyword should contain 'hd portrait images' like keyword to generate the images. the search keyword should more likely a google search.\n"
                f"note: Also avoid giving explanation and stuff just give the search_keyword, just give like this 'search_keyword: your answer here'\n"
            )

            # Start a new chat session with the combined prompt
            chat_session_combined = model.start_chat(
                history=[{
                    "role": "user",
                    "parts": [prompt_combined],
                }]
            )

            try:
                time.sleep(20)
                response_combined = chat_session_combined.send_message(prompt_combined)
                raw_text_combined = response_combined.parts[0].text
                cleaned_text_combined = raw_text_combined.replace("'", "").replace('"', '').strip()

                search_keyword_combined_match = search_keyword_pattern.search(cleaned_text_combined)
                if search_keyword_combined_match:
                    search_keyword = search_keyword_combined_match.group(1).strip()
            except Exception as e:
                print(f"An error occurred while generating combined keyword: {e}")

        # Add the search keyword to the set
        unique_search_keywords.add(search_keyword)

        frame['search_keyword'] = search_keyword
        updated_frames.append(frame)

        print(f"Updated frame: {frame}")

    print("Search Keywords Generated Successfully")
    return updated_frames

# Example usage
if __name__ == "__main__":
    print("What do you want? \n")
    sentence = input()
    #sentence = "beautiful bird is peacock"
    brief_content = get_brief_content(sentence)
    print(brief_content)
