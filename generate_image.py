import os
import random
import re
import glob
import hashlib
import shutil
import time

from PIL import Image
from pygoogle_image import image as pi
import pytesseract
import cv2
import numpy as np
import threading


def get_newly_created_folder(base_folder):
    # Find all subfolders in the base folder sorted by creation time
    subfolders = [f.path for f in os.scandir(base_folder) if f.is_dir()]
    if not subfolders:
        return None
    latest_folder = max(subfolders, key=os.path.getctime)
    return latest_folder


def download_images(frame):
    search_keyword = frame['search_keyword']
    words = search_keyword.split()
    max_attempts = len(words) // 2 + (1 if len(words) % 2 != 0 else 0)
    attempt_counter = 1

    for attempt in range(max_attempts):
        sanitized_keyword = sanitize_directory_name(' '.join(words))

        print(f"Attempting to download with keyword ({attempt_counter}): '{sanitized_keyword}'")
        if attempt_counter != 1:
            time.sleep(10)
        attempt_counter = attempt_counter + 1

        downloaded_images = []

        def download_function():
            nonlocal downloaded_images
            print("Downloading Image...")
            downloaded_images = pi.download(keywords=sanitized_keyword, limit=10)

        # Create a thread to run the download function
        download_thread = threading.Thread(target=download_function)
        download_thread.start()

        # Wait for the download to complete, but only for 5 seconds
        download_thread.join(timeout=20)

        if download_thread.is_alive():
            print("Download timed out. Proceeding to next step...")
            # Optionally, you can also check if you got any images
            if not downloaded_images:
                print("No images downloaded, retrying with reduced keyword...")
        else:
            # If the download completes successfully within 5 seconds
            if downloaded_images:
                print("Download Successful")
                return downloaded_images

        # Reduce the number of words in the keyword by 3 for the next attempt
        words = words[:-2]
        if not words:
            print("No more words to try. Exiting...")
            break

    return None


# Method to move and rename images to the frame folder
def move_and_rename_images(source_folder, frame_folder, frame_index, all_images_folder):
    """Move images from source folder to the frame folder and also copy them to all_images folder."""
    # Create the frame folder if it doesn't exist
    os.makedirs(frame_folder, exist_ok=True)

    # Find all image files in the source folder
    image_files = glob.glob(os.path.join(source_folder, '*'))

    for i, img_path in enumerate(image_files, start=1):
        try:
            # Extract the image extension
            ext = img_path.split('.')[-1]
            # Define the new path with renamed images
            new_img_name = f"sample_image_{i}_{frame_index}.{ext}"
            new_img_path = os.path.join(frame_folder, new_img_name)

            # Move and rename the image to the frame folder
            shutil.move(img_path, new_img_path)
            #print(f"Image moved and renamed: {new_img_path}")

            # Copy the image to the all_images folder
            if is_9_16_ratio(new_img_path):
                shutil.copy(new_img_path, all_images_folder)
                #print(f"Image copied to all_images folder: {new_img_path}")
        except Exception as e:
            print(f"Error moving and renaming {img_path}: {e}")


# Method to check if an image is in portrait mode and its quality
def evaluate_image_quality(image):
    width, height = image.size
    ratio = height / width
    resolution = width * height
    #print(f"Image ratio: {ratio}, width: {width}, height: {height}")

    # Conditions for portrait-like image
    is_portrait = ratio >= 1.3
    return is_portrait, resolution

def is_mobile_portrait_ratio(img):
    width, height = img.size
    aspect_ratio = width / height
    return 0.5 < aspect_ratio < 0.75

def remove_image(img_path):
    try:
        os.remove(img_path)
        print(f"Removed image: {img_path}")
    except Exception as e:
        print(f"Error removing image {img_path}: {e}")

def contains_text(img_path):
    unwanted_words = ["alamy", "shutter", "tter", "depositphotos", "snutter", "shut", "drea", "dream", "alam", "www", "stock", "image", "photo" ".com"]
    # Use OpenCV to preprocess the image for better text detection
    img_cv = cv2.imread(img_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # Apply thresholding to make the text stand out
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Use Tesseract OCR to detect text
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    print(text.strip().lower())
    if len(text.strip()) > 1:
        for word in unwanted_words:
            if word in text.strip().lower():
                print(f"Unwanted word '{word}' found in the image.")
                return True


    return False

def select_best_fit_image(frame_folder, all_images_folder):
    image_files = glob.glob(os.path.join(frame_folder, '*'))
    valid_images = []
    best_image = None
    best_resolution = 0
    quality_images = []

    for img_path in image_files:
        try:
            img = Image.open(img_path)

            # Skip images with text or watermarks
            if contains_text(img_path):
                print(f"Skipping image with text/watermark: {img_path}")
                img.close()
                remove_image(img_path)  # Remove from frames folder
                all_image_path = os.path.join(all_images_folder, os.path.basename(img_path))
                if os.path.exists(all_image_path):
                    remove_image(all_image_path)
                continue

            valid_images.append(img_path)

            is_portrait, resolution = evaluate_image_quality(img)

            # If portrait and higher quality, update best image
            if is_portrait and resolution > best_resolution:
                best_image = img_path
                best_resolution = resolution
                print(f"Best image updated: {img_path} with resolution {resolution}")

            if is_mobile_portrait_ratio(img):
                quality_images.append((img_path, resolution))
                print(f"Image added to quality candidates: {img_path} with resolution {resolution}")

        except Exception as e:
            print(f"Error opening image {img_path}: {e}")

    if best_image:
        print(f"Best portrait image found: {best_image}")
        return best_image

    # If no portrait-like image is found, select the best quality random image near mobile portrait ratio
    if quality_images:
        selected_image = max(quality_images, key=lambda x: x[1])[0]  # Select the image with the highest resolution
        print(f"No portrait-like image found, selecting best quality image: {selected_image}")
        return selected_image

    # If no images meet criteria, select a random image
    if valid_images:
        selected_image = random.choice(valid_images)
        print(f"No portrait-like image found, selecting random image: {selected_image}")
        return selected_image

    return None


def convert_to_9_16(image_path, save_folder):
    # Define the target aspect ratio (9:16)
    target_aspect_ratio = 9 / 16
    image = Image.open(image_path)
    width, height = image.size
    current_aspect_ratio = height / width

    # If the image is already in 9:16 ratio, return it as is
    if round(current_aspect_ratio, 2) == round(target_aspect_ratio, 2):
        print(f"Image already in 9:16 ratio: {image_path}")
        return image_path

    # Determine the crop dimensions
    if current_aspect_ratio > target_aspect_ratio:
        # Image is taller than 9:16, so we crop the height
        new_height = int(width * target_aspect_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left, right = 0, width  # No change to width
    else:
        # Image is wider than 9:16, so we crop the width
        new_width = int(height / target_aspect_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        top, bottom = 0, height  # No change to height

    # Crop the image to fit the 9:16 ratio
    cropped_image = image.crop((left, top, right, bottom))

    # Save the cropped image
    img_name = os.path.basename(image_path)
    portrait_img_path = os.path.join(save_folder, img_name)
    cropped_image.save(portrait_img_path, quality=95)
    print(f"Cropped image to 9:16 ratio and saved: {portrait_img_path}")

    return portrait_img_path

def sanitize_directory_name(name):
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Process images for frames and convert selected images to 9:16 ratio
def compute_image_hash(image_path):
    """Compute the SHA-256 hash of an image."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')  # Ensure the image is in RGB mode
        img_bytes = img.tobytes()
        return hashlib.sha256(img_bytes).hexdigest()

def is_9_16_ratio(image_path):
    """Check if the image has a 9:16 aspect ratio."""
    with Image.open(image_path) as image:
        width, height = image.size
        ratio = height / width
        is_portrait = ratio >= 1.3
        return is_portrait

def process_images_for_frames(updated_frames):
    base_folder = "images"
    selected_folder = "frames"
    selected_images_folder = "selected_images"
    all_images_folder = "all_images"

    os.makedirs(selected_images_folder, exist_ok=True)
    os.makedirs(all_images_folder, exist_ok=True)

    selected_image_hashes = set()  # Track selected image hashes

    for frame in updated_frames:
        search_keyword = frame['search_keyword'] #+ "9:16 ratio"

        # Sanitize the search keyword for downloading
        sanitized_keyword = sanitize_directory_name(search_keyword)

        # Download images (your logic here)
        print(f"Downloading Image...{sanitized_keyword}")
        download_images(frame)
        #downloaded_images = pi.download(keywords=sanitized_keyword, limit=10)
        print("Download Successful")

        # Get the newly created folder
        new_folder = get_newly_created_folder(base_folder)
        if not new_folder:
            print(f"No folder found for keyword: {search_keyword}")
            continue

        print(f"New folder found: {new_folder}")

        # Move and rename images to frame folder and all images folder
        frame_folder = os.path.join(selected_folder, f"frame_{updated_frames.index(frame) + 1}_images")
        move_and_rename_images(new_folder, frame_folder, updated_frames.index(frame) + 1, all_images_folder)

        # Delete the original folder after moving images
        shutil.rmtree(new_folder)

        # Select the best fit image (portrait or random) and copy it to the selected folder
        selected_image_path = select_best_fit_image(frame_folder, all_images_folder)

        if selected_image_path:
            img_hash = compute_image_hash(selected_image_path)
            print(f"selected image - path: {selected_image_path}, img_hash: {img_hash}")
            # Check if the selected image has already been chosen based on its hash
            if img_hash in selected_image_hashes:
                print("DUPLICATE IMAGE FOUND.....")
                # Select a random image from the all_images folder
                all_images = [os.path.join(all_images_folder, img) for img in os.listdir(all_images_folder)]
                # Filter only for 9:16 ratio images
                all_images = [img for img in all_images if is_9_16_ratio(img)]

                # Remove already selected images from the selection pool based on hash
                all_images = [img for img in all_images if compute_image_hash(img) not in selected_image_hashes]

                if all_images:
                    selected_image_path = random.choice(all_images)  # Pick a random image
                    img_hash = compute_image_hash(selected_image_path)  # Recompute hash for the new selection
                    print(f"++++++++++++++++++ RANDOM IMAGE PICKED --- Img Path - {selected_image_path} ++++++++++++++++++")

            selected_image_hashes.add(img_hash)  # Add to selected hashes

            img_name = os.path.basename(selected_image_path)
            final_image_path = os.path.join(selected_images_folder, img_name)
            shutil.copy(selected_image_path, final_image_path)
            print(f"Selected image copied to final folder: {final_image_path}")

            # Remove the selected image from the all_images folder
            image_to_remove_path = os.path.join(all_images_folder, img_name)
            if os.path.exists(image_to_remove_path):
                os.remove(image_to_remove_path)
                print(f"Removed selected image from all_images folder: {img_name}")
            else:
                print(f"Image not found in all_images folder for removal: {img_name}")

            # Update frame with the path of the selected image
            frame['image_path'] = final_image_path
        else:
            print(f"No suitable image found for frame: {frame['search_keyword']}")

        # if selected_image_path:
        #     # Convert the selected image to a 9:16 aspect ratio
        #     portrait_image_path = convert_to_9_16(selected_image_path, portrait_images_folder)
        #
        #     # Now copy the portrait image to the final folder
        #     img_name = os.path.basename(portrait_image_path)
        #     final_image_path = os.path.join(selected_images_folder, img_name)
        #     shutil.copy(portrait_image_path, final_image_path)
        #     print(f"Selected image copied to final folder: {final_image_path}")
        #
        #     # Update frame with the path of the new portrait image
        #     frame['image_path'] = final_image_path
        # else:
        #     print(f"No suitable image found for frame: {frame['search_keyword']}")
    shutil.rmtree(all_images_folder)


# Main function to call the processing method
def update_images_path_in_frame(updated_frames):
    process_images_for_frames(updated_frames)

    # Print the updated frames with image paths
    for frame in updated_frames:
        print(frame)
    return updated_frames


# Example usage
if __name__ == "__main__":
    # Define your updated_frames here as a list of dictionaries
    updated_frames = [
        {
            'audio_duration': '0.0s - 5.04s',
            'actual_keyword': 'Did you know that parrots are some of the most intelligent birds on the planet?',
            'search_keyword': 'hd portrait images of parrots',
            'image_path': 'selected_images\\sample_image_5_1.jpeg'
        },
        {
            'audio_duration': '5.04s - 9.12s',
            'actual_keyword': "Seriously, they're like the Einstein's of the bird world.",
            'search_keyword': 'hd portrait images of intelligent birds',
            'image_path': 'selected_images\\sample_image_2_2.jpeg'
        },
        {
            'audio_duration': '9.12s - 12.24s',
            'actual_keyword': "But let's talk about them in a little more detail.",
            'search_keyword': 'hd portrait images of people talking in detail',
            'image_path': 'selected_images\\sample_image_5_3.png'
        },
        {
            'audio_duration': '12.24s - 15.04s',
            'actual_keyword': 'Parrots are a diverse group of birds.',
            'search_keyword': 'hd portrait images of colorful parrots',
            'image_path': 'selected_images\\sample_image_1_4.png'
        },
        {
            'audio_duration': '15.04s - 21.44s',
            'actual_keyword': "With over 350 species found all over the world, they're known for their bright colors,",
            'search_keyword': 'hd portrait images of colorful birds from around the world',
            'image_path': 'selected_images\\sample_image_3_5.png'
        },
        {
            'audio_duration': '21.44s - 25.92s',
            'actual_keyword': 'their ability to mimic sounds, including human speech,',
            'search_keyword': 'hd portrait images of parrots mimicking human speech',
            'image_path': 'selected_images\\sample_image_5_6.jpeg'
        },
        {
            'audio_duration': '25.92s - 28.8s',
            'actual_keyword': 'and their complex social structures.',
            'search_keyword': 'hd portrait images of people in complex social structures',
            'image_path': 'selected_images\\sample_image_4_7.jpeg'
        },
        {
            'audio_duration': '28.8s - 33.84s',
            'actual_keyword': 'These guys are super social, living in flocks and communicating with each other',
            'search_keyword': 'hd portrait images of birds in a flock communicating',
            'image_path': 'selected_images\\sample_image_5_8.jpeg'
        },
        {
            'audio_duration': '33.84s - 36.16s',
            'actual_keyword': 'using a variety of calls and whistles.',
            'search_keyword': 'hd portrait images of birds singing and whistling',
            'image_path': 'selected_images\\sample_image_3_9.jpeg'
        },
        {
            'audio_duration': '37.04s - 39.84s',
            'actual_keyword': "It's like their own little bird language.",
            'search_keyword': 'hd portrait images of birds communicating',
            'image_path': 'selected_images\\sample_image_3_10.jpeg'
        },
        {
            'audio_duration': '39.84s - 44.8s',
            'actual_keyword': 'Their beaks are powerful tools, helping them crack open nuts and seeds,',
            'search_keyword': 'hd portrait images of birds with powerful beaks cracking open nuts and seeds',
            'image_path': 'selected_images\\sample_image_4_11.jpeg'
        },
        {
            'audio_duration': '45.44s - 49.2s',
            'actual_keyword': 'non-living objects, and even shred their food.',
            'search_keyword': 'hd portrait images of animals shredding their food',
            'image_path': 'selected_images\\sample_image_4_12.jpeg'
        },
        {
            'audio_duration': '49.2s - 56.64s',
            'actual_keyword': 'Some species, like the Amazon parrots, are known for their incredible ability to mimic sounds.',
            'search_keyword': 'Amazon parrot hd portrait images',
            'image_path': 'selected_images\\sample_image_4_13.jpeg'
        },
        {
            'audio_duration': '56.72s - 61.6s',
            'actual_keyword': 'They can learn words, phrases, and even entire songs.',
            'search_keyword': 'hd portrait images of people learning words and phrases',
            'image_path': 'selected_images\\sample_image_5_14.jpeg'
        },
        {
            'audio_duration': '61.6s - 66.24s',
            'actual_keyword': 'This is because they have a special structure in their vocal cords called a serenx,',
            'search_keyword': 'hd portrait images of animals with unique vocal cords',
            'image_path': 'selected_images\\sample_image_1_15.jpeg'
        },
        {
            'audio_duration': '67.2s - 70.24s',
            'actual_keyword': 'which allows them to produce a wide range of sounds.',
            'search_keyword': 'hd portrait images of a musician playing a variety of instruments',
            'image_path': 'selected_images\\sample_image_1_16.jpeg'
        },
        {
            'audio_duration': '70.88s - 74.08s',
            'actual_keyword': 'Parrots have evolved to live in a variety of habitats.',
            'search_keyword': 'hd portrait images of parrots in different habitats',
            'image_path': 'selected_images\\sample_image_2_17.jpeg'
        },
        {
            'audio_duration': '74.72s - 80.64s',
            'actual_keyword': 'From lush rainforests to dry grasslands, they often build their nests and tree cavities,',
            'search_keyword': 'hd portrait images of birds building nests in tree cavities in lush rainforests',
            'image_path': 'selected_images\\sample_image_2_18.jpeg'
        },
        {
            'audio_duration': '81.28s - 87.84s',
            'actual_keyword': 'non-living objects, using sticks, leaves, and even feathers for bedding.',
            'search_keyword': 'hd portrait images of bird nests made of sticks, leaves, and feathers',
            'image_path': 'selected_images\\sample_image_4_19.jpeg'
        },
        {
            'audio_duration': '87.84s - 90.48s',
            'actual_keyword': 'They play a vital role in their ecosystems,',
            'search_keyword': 'hd portrait images of animals in their natural ecosystems',
            'image_path': 'selected_images\\sample_image_3_20.png'
        },
        {
            'audio_duration': '91.12s - 94.88s',
            'actual_keyword': 'helping to disperse seeds and control insect populations.',
            'search_keyword': 'hd portrait images of birds and insects in a forest',
            'image_path': 'selected_images\\sample_image_1_21.jpeg'
        },
        {
            'audio_duration': '95.52s - 100.8s',
            'actual_keyword': 'So next time you see a parrot, remember that these amazing creatures are more than just',
            'search_keyword': 'hd portrait images of parrots in tropical rainforest',
            'image_path': 'selected_images\\sample_image_3_22.jpeg'
        },
        {
            'audio_duration': '100.8s - 106.8s',
            'actual_keyword': "pretty faces. They're intelligent, social, and vital members of the natural world.",
            'search_keyword': 'hd portrait images of intelligent animals',
            'image_path': 'selected_images\\sample_image_2_23.jpeg'
        }
    ]

    new_updated_frames = update_images_path_in_frame(updated_frames)
    print(new_updated_frames)
