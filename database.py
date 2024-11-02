import psycopg2
from datetime import datetime

CONN = psycopg2.connect(
    host="localhost",          # e.g., "localhost" if running locally
    database="video_gen",   # e.g., "video_database"
    user="musharaf",       # e.g., "postgres"
    password="123456",   # e.g., "yourpassword"
    port="5432"                 # Default PostgreSQL port
)
CONN.autocommit = True  # Ensure that changes are committed automatically

def create_db_connection():
    # Replace these values with your PostgreSQL credentials
    connection = psycopg2.connect(
        host="localhost",          # e.g., "localhost" if running locally
        database="video_gen",   # e.g., "video_database"
        user="musharaf",       # e.g., "postgres"
        password="123456",   # e.g., "yourpassword"
        port="5432"                 # Default PostgreSQL port
    )
    connection.autocommit = True  # Ensure that changes are committed automatically
    return connection

def create_video_metadata_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_metadata (
            id SERIAL PRIMARY KEY,
            status TEXT,
            sentence TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            tags TEXT,
            category VARCHAR(50),
            time_slot VARCHAR(10),
            publish_time TIMESTAMP,
            audio_file TEXT,
            video_file TEXT,
            category_id TEXT,
            upload_date DATE
        )
    ''')
    conn.commit()
    cursor.close()

def check_existing_video(time_slot):
    cursor = CONN.cursor()
    today = datetime.now().date()
    cursor.execute('''
        SELECT * FROM video_metadata 
        WHERE time_slot = %s AND upload_date = %s
    ''', (time_slot, today))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists

def list_all_videos():
    cursor = CONN.cursor()
    cursor.execute('SELECT * FROM video_metadata')
    rows = cursor.fetchall()
    cursor.close()
    return rows


def update_record(video_id, column_name, value):
    """Update a specified column for a video record in the video_metadata table."""
    cursor = CONN.cursor()
    query = f'UPDATE video_metadata SET {column_name} = %s WHERE id = %s'
    cursor.execute(query, (value, video_id))
    CONN.commit()
    cursor.close()

def update_video_status(video_id, status_message):
    """Update the status of the video processing in the video_metadata table."""
    cursor = CONN.cursor()
    cursor.execute('UPDATE video_metadata SET status = %s WHERE id = %s', (status_message, video_id))
    CONN.commit()
    cursor.close()

def insert_video_metadata(status, sentence, title, description, tags, category, time_slot, upload_date):
    """Inserts a new video metadata record and returns the generated video ID."""
    print("Inserting video metadata:")
    print(f"Status: {status}")
    print(f"Sentence: {sentence}")
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Tags: {tags}")  # Ensure this is a string
    print(f"Category: {category}")
    print(f"Time Slot: {time_slot}")
    print(f"Upload Date: {upload_date}")
    cursor = CONN.cursor()
    cursor.execute('''
        INSERT INTO video_metadata (status, sentence, title, description, tags, category, time_slot, upload_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (status, sentence, title, description, tags, category, time_slot, upload_date))
    video_id = cursor.fetchone()[0]
    CONN.commit()
    cursor.close()
    return video_id

def update_video_publish_time(video_id, publish_datetime):
    """Updates the publish time for a given video record in the video_metadata table."""
    cursor = CONN.cursor()
    cursor.execute('UPDATE video_metadata SET publish_time = %s WHERE id = %s', (publish_datetime, video_id))
    CONN.commit()
    cursor.close()

if __name__ == "__main__":
    time_slot = "8AM"
    if check_existing_video(time_slot):
        print(f"A video has already been uploaded for the {time_slot} time slot today.")
    else:
        print(f"No video found for the {time_slot} time slot today.")

    # List all videos in the video_metadata table
    videos = list_all_videos()
    for video in videos:
        print(video)

    CONN.close()