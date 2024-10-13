import os
import random
import re
import glob
import hashlib
import shutil
from PIL import Image
from pygoogle_image import image as pi

def get_newly_created_folder(base_folder):
    # Find all subfolders in the base folder sorted by creation time
    subfolders = [f.path for f in os.scandir(base_folder) if f.is_dir()]
    if not subfolders:
        return None
    latest_folder = max(subfolders, key=os.path.getctime)
    return latest_folder


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
            print(f"Image moved and renamed: {new_img_path}")

            # Copy the image to the all_images folder
            if is_9_16_ratio(new_img_path):
                shutil.copy(new_img_path, all_images_folder)
                print(f"Image copied to all_images folder: {new_img_path}")
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


# Method to select the best portrait image based on quality and aspect ratio
def select_best_fit_image(frame_folder):
    image_files = glob.glob(os.path.join(frame_folder, '*'))
    best_image = None
    best_resolution = 0

    for img_path in image_files:
        try:
            img = Image.open(img_path)
            is_portrait, resolution = evaluate_image_quality(img)

            # If portrait and higher quality, update best image
            if is_portrait and resolution > best_resolution:
                best_image = img_path
                best_resolution = resolution
                print(f"Best image updated: {img_path} with resolution {resolution}")

        except Exception as e:
            print(f"Error opening image {img_path}: {e}")

    if best_image:
        print(f"Best portrait image found: {best_image}")
        return best_image

    # If no portrait-like image is found, select a random image
    if image_files:
        selected_image = random.choice(image_files)
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
        search_keyword = frame['search_keyword']

        # Sanitize the search keyword for downloading
        sanitized_keyword = sanitize_directory_name(search_keyword)

        # Download images (your logic here)
        downloaded_images = pi.download(keywords=sanitized_keyword, limit=5)

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
        selected_image_path = select_best_fit_image(frame_folder)

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
                print(f"Image not found in all_images folder for removal: {image_to_remove_path}")

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
    updated_frames = [{'audio_duration': '0.0s - 5.04s',
                       'actual_keyword': 'Did you know that parrots are some of the most intelligent birds on the planet?',
                       'search_keyword': 'hd portrait images of colorful parrots', 'image_path': ''},
                      {'audio_duration': '5.04s - 9.12s',
                       'actual_keyword': "Seriously, they're like the Einstein's of the bird world.",
                       'search_keyword': 'hd portrait images of peacocks with colorful feathers', 'image_path': ''},
                      {'audio_duration': '100.8s - 106.8s',
                       'actual_keyword': "pretty faces. They're intelligent, social, and vital members of the natural world.",
                       'search_keyword': 'hd portrait images of peacocks', 'image_path': ''}]

    new_updated_frames = update_images_path_in_frame(updated_frames)
    print(new_updated_frames)
