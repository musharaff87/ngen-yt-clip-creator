from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
import requests
import os

SEARCH_ENGINE_URL = "https://www.google.com/search?tbm=isch&q="
MIN_WIDTH = 720
MIN_HEIGHT = 1280
MIN_ASPECT_RATIO = 1.5
MAX_IMAGES = 5

def is_shrinked(img_width, img_height):
    aspect_ratio = img_width / img_height
    return aspect_ratio >= MIN_ASPECT_RATIO and img_width >= MIN_WIDTH and img_height >= MIN_HEIGHT

def search_and_download_images(query, num_images=MAX_IMAGES, save_dir="downloads"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    found_images = 0
    image_urls = set()
    print(f"[INFO] Searching for: {query}")
    print(f"[INFO] Target folder for downloads: {save_dir}")

    with sync_playwright() as p:
        print("[INFO] Launching headless browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        search_url = SEARCH_ENGINE_URL + query.replace(" ", "+")
        print(f"[INFO] Navigating to: {search_url}")
        page.goto(search_url)

        try:
            page.wait_for_selector("img", timeout=60000)
            print("[INFO] Images loaded on the page.")
        except Exception as e:
            print(f"[ERROR] Timeout waiting for images: {e}")
            return

        img_elements = page.query_selector_all("img")
        print(f"[INFO] Found {len(img_elements)} image elements on the page.")

        for img_element in img_elements:
            if found_images >= num_images:
                break

            img_url = img_element.get_attribute("src")
            if not img_url or img_url in image_urls:
                continue

            try:
                print(f"[INFO] Processing image URL: {img_url}")
                img_response = requests.get(img_url, stream=True, timeout=10)
                img_response.raise_for_status()
                img = Image.open(BytesIO(img_response.content))
                img_width, img_height = img.size
                print(f"[INFO] Image dimensions: {img_width}x{img_height}")

                if is_shrinked(img_width, img_height):
                    filename = os.path.join(save_dir, f"image_{found_images + 1}.jpg")
                    img.save(filename, "JPEG")
                    print(f"[SUCCESS] Downloaded: {filename}")
                    found_images += 1
                    image_urls.add(img_url)
                else:
                    print("[INFO] Image does not match the desired aspect ratio or resolution.")

            except Exception as e:
                print(f"[ERROR] Failed to process image URL: {img_url}, Error: {e}")

        browser.close()
        print("[INFO] Browser closed.")

    if found_images < num_images:
        print(f"[WARNING] Only {found_images} images were found.")
    else:
        print("[SUCCESS] All images downloaded successfully.")

if __name__ == "__main__":
    search_query = input("Enter your search query: ")
    search_and_download_images(search_query)
