import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import stopwords
from database import *
import re


def list_all_video_sentences():
    """Retrieve all previously used sentences from video_metadata."""
    cursor = CONN.cursor()
    cursor.execute('SELECT sentence FROM video_metadata')
    rows = cursor.fetchall()
    cursor.close()
    return [row[0] for row in rows]


def clean_text(text):
    """Helper function to clean and preprocess text."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text


def calculate_semantic_similarity(new_sentence, previous_sentences, threshold=0.7):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    new_embedding = model.encode(new_sentence)
    previous_embeddings = model.encode(previous_sentences)

    # Calculate similarity scores
    similarities = util.cos_sim(new_embedding, previous_embeddings)[0]
    max_similarity = max(similarities)

    return max_similarity.item(), max_similarity.item() < threshold


def calculate_similarity(sentence, existing_sentences):
    """Calculate the similarity of the generated sentence with existing ones."""
    all_sentences = [sentence] + existing_sentences
    all_sentences = [clean_text(sent) for sent in all_sentences]

    # Convert sentences to TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
    tfidf_matrix = vectorizer.fit_transform(all_sentences)

    # Calculate cosine similarity between the first sentence and others
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Return the highest similarity score
    return max(similarity_scores)


def generate_unique_sentence_for_category(category):
    from gemini_api import call_gemini_with_retry
    """Generate a unique sentence for a category, avoiding previously used ones."""
    existing_sentences = list_all_video_sentences()
    unique_sentence = None
    attempts = 0
    uploaded_sentences = []
    original_prompt = f"Randomly Generate a True news content in a sentence for a YouTube video in the '{category}' category. It should be a today's trending story, fact, or incident related to the category and formatted to engage viewers.\n just return one sentence only."
    prompt = original_prompt
    while unique_sentence is None and attempts < 10:  # Limit attempts to avoid infinite loops
        response = call_gemini_with_retry(prompt)
        sentence = response.text.strip()

        # Check if the new sentence is similar to any previous sentences
        similarity_score, is_unique = calculate_semantic_similarity(sentence, existing_sentences)
        if is_unique:
            unique_sentence = sentence  # Accept as unique
        else:
            uploaded_sentences.append(sentence)
            prompt = original_prompt + f"\n And This should not be related to these news {uploaded_sentences}"
            print(f"Generated sentence is too similar: {sentence}")

        attempts += 1

    if unique_sentence:
        print(f"Unique Sentence Found: {unique_sentence}")
    else:
        print("Failed to generate a unique sentence after multiple attempts.")

    return unique_sentence

if __name__ == "__main__":
    # Sample sentences for testing
    new_sentence = "hidden city of atlantis"
    previous_sentences = [
        "Scientists found a hidden city in the desert sands.",
        "The truth behind the lost city of Atlantis.",
        "Underneath the desert, a lost city has been uncovered."
    ]

    # # Calculate similarity
    # similarity_score = calculate_similarity(new_sentence, previous_sentences)
    # print(f"Similarity Score with closest sentence: {similarity_score}")
    #
    # # Threshold test
    # threshold = 0.75
    # if similarity_score < threshold:
    #     print("The new sentence is unique enough to be used.")
    # else:
    #     print("The new sentence is too similar to previous ones; generating a new one is recommended.")

    # similarity_score, is_unique = calculate_semantic_similarity(new_sentence, previous_sentences)
    # print(f"Max Similarity Score with closest sentence: {similarity_score}")
    #
    # if is_unique:
    #     print("The new sentence is unique enough to be used.")
    # else:
    #     print("The new sentence is too similar to previous ones; generating a new one is recommended.")
    val = generate_unique_sentence_for_category("Entertainment")
    print(val)
