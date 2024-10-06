import google.generativeai as genai
import json


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
    "max_output_tokens": 400,  # Set max output tokens to 400
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


def get_brief_content(sentence):
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

    return response.text.strip()


# Example usage
if __name__ == "__main__":
    print("What do you want? \n")
    sentence = input()
    #sentence = "beautiful bird is peacock"
    brief_content = get_brief_content(sentence)
    print(brief_content)
