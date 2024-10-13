import time

import google.generativeai as genai
import json
import re


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
    prompt = f"provide a brief, up-to-date description about: {sentence}. Include living and non-living objects where relevant. Make it sound like a YouTuber explaining to viewers in a conversational tone. Also use attracting sentence in the start of the context like eg: did you know? . Also omit sentence like welcome back to channel like that just start talking with viewers.  Limit the response to 300-400 words."

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


def generate_search_keywords(formatted_frames, main_content_sentence):
    print("Generating Search Keywords from Gemini...")

    # Construct a prompt that includes all actual keywords
    actual_keywords = [frame['actual_keyword'] for frame in formatted_frames]
    keywords_prompt = "\n".join(actual_keywords)  # Join keywords with newlines
    updated_frames = []
    for frame in formatted_frames:
        actual_keyword = frame['actual_keyword']
        prompt = (
            f"this is formatted_frames = {actual_keyword}\n"
            # f"this is main_content = {main_content_sentence}\n\n"
            f"Generate relevant search keywords for the actual keyword.\n"
            f"the search keyword must have objects or living things or something sentence that is meaningful to generate images.\n"
            f"also the search keyword should contain 'hd portrait images' like keyword to generate the images. the search keyword should more likely a google search.\n"
            # f"also if the actual keyword doesn't have any meaning then generate random image generation keyword using main_content.\n"
            f"also if the actual keyword doesn't have any meaning then generate random hd image generation keyword related to nature, places around world and animals.\n"
            f"note: Also avoid giving explanation and stuff just give the search_keyword, just give like this 'search_keyword: your answer here'\n"
        )

        # Start chat session with the constructed prompt
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [prompt],
                },
            ]
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
        print(f"Response from Gemini: {response}")

        # Fix formatting issues in response text
        raw_text = response.parts[0].text  # Extract response text using attribute access

        cleaned_text = raw_text.replace("'", "").replace('"', '').strip()

        # Step 2: Apply the regex pattern to extract the search_keyword value
        search_keyword_pattern = re.compile(r"search_keyword:\s*(.+)", re.IGNORECASE)
        search_keyword_match = search_keyword_pattern.search(cleaned_text)

        # Step 3: If we find a match, use it; otherwise, fallback to main_content_sentence
        if search_keyword_match:
            search_keyword = search_keyword_match.group(1).strip()  # Extract and clean the search keyword
        else:
            search_keyword = main_content_sentence

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
