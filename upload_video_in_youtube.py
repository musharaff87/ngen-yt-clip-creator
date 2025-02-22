import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta, timezone

# New imports

import os
import google_auth_httplib2
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allows HTTP for local testing

    client_secrets_file = "client_secret_new_1.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES
    )

    credentials = flow.run_local_server(port=8080)  # Handles redirect automatically

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials
    )

    return youtube

def get_authenticated_service():
    # Load credentials from the JSON file
    with open("youtube_secrets.json", "r") as file:
        creds_data = json.load(file)

    creds = Credentials(
        token=creds_data["access_token"],
        refresh_token=creds_data["refresh_token"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"]
    )

    # Build the YouTube API client with the credentials
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def upload_video(video_file, title, description, tags, category_id, publish_time):
    youtube = authenticate_youtube()
    ist_offset = timedelta(hours=5, minutes=30)
    publish_time = publish_time - ist_offset
    # Prepare the video metadata
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "private",  # Video will be private until publish time
            "license": "youtube",
            "publishAt": publish_time.isoformat(),  # Schedule publish time
            "selfDeclaredMadeForKids": False  # Set whether the video is made for kids
        }
    }

    # Create media file upload instance
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/*")

    # Call YouTube API to upload the video
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")

    print("Upload Complete!")
    return response


if __name__ == "__main__":
    # Authenticate and initialize the YouTube API service
    #youtube = get_authenticated_service()

    # Define video details
    video_file = "video_outputs/got.mp4"
    title = "Unbelievable Game of Thrones Revelation: The Stark Who Served as Hand Before Ned!"
    description = """ In the intricate political landscape of Westeros, the role of Hand of the King stands as one of the most influential positions, second only to the monarch. While Eddard "Ned" Stark's tenure as Hand to King Robert Baratheon is well-documented, a lesser-known chapter of history reveals that he was not the first Stark to hold this esteemed title. Delving into the annals of the Seven Kingdoms, we uncover the story of Lord Cregan Stark, a formidable leader from the North, who briefly assumed the mantle of Hand during a tumultuous period known as the Hour of the Wolf.

Cregan Stark, the Lord of Winterfell during the Targaryen civil war termed the Dance of the Dragons, was renowned for his unwavering honor and martial prowess. Following the death of King Aegon II, a power vacuum emerged in King's Landing, leading to political chaos. Seizing this critical moment, Cregan marched south with a formidable northern host, aiming to restore order and uphold justice. Upon his arrival, he was appointed Hand of the King to the newly crowned Aegon III. His tenure, though brief—lasting only a single day—was marked by decisive actions that left an indelible mark on the realm's history.

This period, aptly named the Hour of the Wolf, saw Cregan Stark preside over the trials of those implicated in the poisoning of King Aegon II. Demonstrating both his commitment to justice and the stern demeanor characteristic of the North, Cregan's actions during this short span reinforced the Stark legacy of honor and duty. His return to Winterfell after relinquishing the title of Hand underscored his primary dedication to the North, yet his impact on the broader political sphere of Westeros remains a testament to his leadership.

The narrative of Cregan Stark's role as Hand provides a profound insight into the longstanding involvement of House Stark in the governance of the Seven Kingdoms, predating Ned's more widely known service. This revelation not only enriches the lore of the Stark family but also offers a deeper understanding of the North's intricate relationship with the Iron Throne.

For enthusiasts eager to delve deeper into this captivating chapter of Westerosi history, the tale of Cregan Stark serves as a compelling reminder of the North's enduring influence and the often-overlooked stories that have shaped the realm.


#gameofthrones #houseofthestark #nedstark #creganstark #handoftheking #westeroshistory #danceofthedragons #hoursofthewolf #ironthrone #sevenkingdoms #starkfamily #winterfell #targaryencivilwar #gameofthroneslore #asoiaf #georgerrmartin #westeros #gameofthronessecrets #starklegacy #gameofthronesfacts """
    tags = ['game of thrones stark family', 'ned stark hand of the king', 'cregan stark hour of the wolf', 'house stark history', 'westeros political intrigue', 'dance of the dragons', 'targaryen civil war', 'game of thrones lore', 'george rr martin', 'westeros history', 'iron throne succession', 'seven kingdoms politics', 'game of thrones revelations', 'stark family secrets', 'winterfell legacy', 'game of thrones deep dive']
    category_id = "22"  # 22 is for 'People & Blogs'. Adjust based on your content.

    # Get publish time input in IST from user
    ist_publish_time_str = "2025-02-25 11:30" #input("Enter the publish time in IST (format: YYYY-MM-DD HH:MM): ")
    ist_publish_time = datetime.strptime(ist_publish_time_str, "%Y-%m-%d %H:%M")

    # Convert IST to UTC
    ist_offset = timedelta(hours=5, minutes=30)
    publish_time = ist_publish_time #- ist_offset  # Convert IST time to UTC

    # Upload the video
    upload_response = upload_video(video_file, title, description, tags, category_id, publish_time)

    # Print the response
    print(f"Video uploaded. Video ID: {upload_response['id']}")