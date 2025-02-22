import time
import google.generativeai as genai
from similarity_searching import generate_unique_sentence_for_category
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
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4000,  # Set max output tokens to 400
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


def generate_video_metadata(sentence):
    # Construct prompt to get a catchy title, description, trending tags, and publish time suggestion
    prompt = f"""
    Generate YouTube video metadata based on this true news content: "{sentence}".\n
    1. Start with a catchy, click-worthy title with important words in capital letters.\n
    2. Write a conversational description for viewers, beginning with a hook phrase like "Did you know?" or "You won't believe this!"\n
    3. Generate 10-15 trending tags related to the topic, focusing on relevant and popular terms.\n
    4. Provide the appropriate YouTube Data API category ID based on the content. For example, if about sports, choose "Sports" (category_id=17).\n

    Please follow this format strictly:\n
    Title: [Catchy Title]\n
    Description: [Conversational Description starting with a hook]\n
    Tags: [Tag1, Tag2, Tag3, ..., TagN]\n
    Category ID: [Numeric Category ID]\n

    Ensure each item is labeled clearly as shown and provide one item per line.\n
    """

    # Start the chat session
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [prompt],
            },
        ]
    )

    # Send message and get response
    response = call_gemini_with_retry(prompt)

    # Check how to access the actual text from response
    response_text = response.text if hasattr(response, 'text') else str(response)

    # Parse the response into variables
    lines = response_text.strip().split("\n")

    title = ""
    description = ""
    tags = []
    category_id = 22  # Default category ID

    for line in lines:
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        elif line.startswith("Description:"):
            description = line.replace("Description:", "").strip()
        elif line.startswith("Tags:"):
            tags = line.replace("Tags:", "").strip().split(", ")
        elif line.startswith("Category ID:"):
            try:
                category_id_str = line.replace("Category ID:", "").strip()
                category_id = int(category_id_str)
            except ValueError:
                category_id = 22  # Default in case of conversion error
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Tags: {tags}")
    print(f"Category ID: {category_id}")

    return title, description, tags, category_id




def get_brief_content(sentence):
    print("Generating Content from Gemini...")
    # Create a prompt that includes the user's input
    prompt = f"content:  \"{sentence}\"\n provide a short up-to-date content about this recent news or existing story in books based on the content i mentioned above .\n Search From Web And Get the correct news or story. \n Make it sound like a YouTuber explaining to viewers in a conversational tone\n. Also use attracting sentence in the start of the context like eg: did you know?, you must know this, etc.. related to content \n . Also omit sentence like welcome back to channel like that just start talking with viewers and don't give unwanted talk just explain content\n Note: Must Limit the response to 120 - 160 words."

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
    response = call_gemini_with_retry(prompt)
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
            f"this is actual_keyword = {actual_keyword}\n"
            f"this is main_content = {main_content_sentence}\n\n"
            f"Generate relevant search keywords for the actual_keyword also that is some what related to main_content.\n"
            f"the search keyword must have objects or living things or something sentence that is meaningful to generate images.\n"
            f"Also if any name or person present in actual keyword generate search keyword related to that\n"
            f"also the search keyword should more likely a google search keyword.\n"
            f"the search keyword must some what related to main_content and it should be unique relation to actual keyword\n"
            # f"also if the actual keyword doesn't have any meaning then generate random image generation keyword using main_content.\n"
            f"note: Also avoid giving explanation and stuff just give the search_keyword and also make sure the sentence should contain maximum of 60 letters, just give like this 'search_keyword: your answer here'\n"
        )

        # Start chat session with the constructed prompt
        chat_session = model.start_chat(
            history=[{
                "role": "user",
                "parts": [prompt],
            }]
        )

        # Send message and get response
        response = call_gemini_with_retry(prompt)
        # try:
        #     response = chat_session.send_message(prompt)
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     print("Retrying time count 1...")
        #     time.sleep(10)
        #     try:
        #         response = chat_session.send_message(prompt)
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        #         print("Retrying time count 2...")
        #         time.sleep(30)
        #         response = chat_session.send_message(prompt)

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
                f"this is actual_keyword = {combined_keyword}\n"
                f"this is main_content = {main_content_sentence}\n\n"
                f"Generate relevant search keywords for the actual keyword.\n"
                f"Also if any name or person present in actual keyword generate search keyword related to that\n"
                f"the search keyword must have objects or living things or something sentence that is meaningful to generate images.\n"
                # f"also the search keyword should contain 'hd portrait images' like keyword to generate the images. the search keyword should more likely a google search.\n"
                f"the search keyword should more likely a google search to find hd images.\n"
                f"the search keyword should some what related to main content\n"
                f"note: Also avoid giving explanation and stuff just give the search_keyword and also make sure the sentence should contain maximum of 60 letters, just give like this 'search_keyword: your answer here'\n"
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
                response_combined = call_gemini_with_retry(prompt_combined)
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

def generate_sentence_for_category(category):
    return generate_unique_sentence_for_category(category)
    # prompt = f"Generate a sentence for a YouTube video in the '{category}' category. It should be a story, fact, or incident related to the category and formatted to engage viewers, under 6 to 10 words."
    # response = call_gemini_with_retry(prompt)
    # sentence = response.text.strip()
    # print(f"Generated Sentence: {sentence}")
    # return sentence



def call_gemini_with_retry(prompt, max_retries=10, initial_sleep=2, max_sleep=30):
    """
    Calls Gemini in a loop with exponential backoff sleep until a response is received or max retries are reached.
    Returns the response or None if unsuccessful.
    """
    chat_session = model.start_chat(
        history=[{
            "role": "user",
            "parts": [prompt],
        }]
    )

    # Set the sleep time to the initial value
    sleep_time = initial_sleep

    # Attempt to send the message and get a response
    for attempt in range(max_retries):
        try:
            # Send the prompt and try to get a response
            response = chat_session.send_message(prompt)

            # If a valid response is received, return it
            if response:
                return response

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

        # Sleep for the current sleep_time and then increase it (exponential backoff)
        print(f"Sleeping for {sleep_time} seconds before retrying...")
        time.sleep(sleep_time)

        # Gradually increase the sleep time but cap it at max_sleep
        sleep_time = min(sleep_time * 2, max_sleep)

    # If we exhaust all retries, return None or handle the failure as needed
    print("Max retries reached. No response received.")
    return "Random Nature hd"

# Example usage
if __name__ == "__main__":
    print("What do you want? \n")
    sentence = input()
    #sentence = "beautiful bird is peacock"
    brief_content = get_brief_content(sentence)
    print(brief_content)
