import csv
import json
import os
import sys
from googleapiclient.discovery import build

API_KEY = 'YOUR API KEY HERE'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
DATA_DIR = "data"

def get_video_comments(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText'
        ).execute()

        comments = []
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        return comments
    except Exception as e:
        print("An error occurred while retrieving comments:", e)
        return None

def save_comments(video_id, comments, search_query):
    directory = os.path.join(DATA_DIR, search_query.replace("+", " "))
    os.makedirs(directory, exist_ok=True)

    csv_filename = os.path.join(directory, f"{video_id}.csv")
    json_filename = os.path.join(directory, f"{video_id}.json")

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Comment'])
        for comment in comments:
            writer.writerow([comment])

    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(comments, json_file, ensure_ascii=False, indent=4)

    print(f"Comments saved to {csv_filename} and {json_filename}")

def search_videos(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    try:
        search_response = youtube.search().list(
            q=query,
            part='id',
            maxResults=100  # Adjust as needed
        ).execute()

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                video_id = search_result['id']['videoId']
                comments = get_video_comments(video_id)
                if comments:
                    save_comments(video_id, comments, query)
    except Exception as e:
        print("An error occurred while searching for videos:", e)

search_query = input("Enter your search query: ").strip().replace(" ", "+")
try:
    while True:
        search_videos(search_query)
        user_input = input("Press 'q' to quit, or press Enter to continue fetching comments for the next video: ")
        if user_input.lower() == 'q':
            break
except KeyboardInterrupt:
    print("\nProgram interrupted by the user.")
