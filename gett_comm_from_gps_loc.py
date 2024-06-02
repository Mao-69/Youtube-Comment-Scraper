import sys
import os
import csv
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langdetect import detect
from translate import Translator

API_KEY = 'YOUR API KEY HERE'

def detect_language(comment):
    try:
        detected_language = detect(comment)
        return detected_language
    except:
        return None

def translate_comment(comment, target_language):
    try:
        translator = Translator(to_lang=target_language)
        translated_comment = translator.translate(comment)
        return translated_comment
    except:
        return comment

def get_video_info(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    video_info = response['items'][0]['snippet']
    return video_info

def get_video_location(video_info):
    region = video_info.get('region', '')
    city = video_info.get('city', '')
    country = video_info.get('country', '')
    return region, city, country

def get_video_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,  # Maximum number of comments to retrieve per page
            textFormat='plainText'
        ).execute()
    except HttpError as e:
        if e.resp.status == 403:
            print(f"Comments are disabled for the video with ID {video_id}")
            return [], None, None, None
        else:
            raise e

    comments = []
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    video_info = get_video_info(video_id)
    region, city, country = get_video_location(video_info)
    return comments, region, city, country

def search_videos_by_location(latitude, longitude, radius, query):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    response = youtube.search().list(
        part='snippet',
        type='video',
        location=f"{latitude},{longitude}",
        locationRadius=f"{radius}km",
        q=query,
        maxResults=50  # Adjust as needed
    ).execute()

    video_ids = [item['id']['videoId'] for item in response['items']]
    return video_ids

def save_comments(comments, region, city, country, video_id, query):
    data_gps_zone_dir = 'data_gps_zone'
    query_dir = os.path.join(data_gps_zone_dir, query)
    region_dir = os.path.join(query_dir, region)
    city_dir = os.path.join(region_dir, city)
    country_dir = os.path.join(city_dir, country)

    for directory in [data_gps_zone_dir, query_dir, region_dir, city_dir, country_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    csv_file_path = os.path.join(country_dir, f'{video_id}_comments.csv')
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Comment', 'Region', 'City', 'Country'])
        for comment in comments:
            writer.writerow([comment, region, city, country])

    json_file_path = os.path.join(country_dir, f'{video_id}_comments.json')
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump({'comments': comments, 'region': region, 'city': city, 'country': country}, jsonfile, ensure_ascii=False)

if __name__ == '__main__':
    latitude = float(input("Enter the latitude: "))
    longitude = float(input("Enter the longitude: "))
    radius = float(input("Enter the radius (in kilometers): "))
    query = input("Enter the search query to filter videos: ")
    video_ids = search_videos_by_location(latitude, longitude, radius, query)

    if not video_ids:
        print("No videos found within the specified GPS zone.")
        sys.exit()

    for video_id in video_ids:
        print(f"Fetching comments for video: {video_id}")
        comments, region, city, country = get_video_comments(video_id)
        if comments:
            print("Comments:")
            for comment in comments:
                detected_language = detect_language(comment)
                if detected_language:
                    translated_comment = translate_comment(comment, 'en')
                    print(f"Original ({detected_language}): {comment}")
                    print(f"Translation (English): {translated_comment}")
                    print()
                else:
                    print("Failed to detect language for comment:", comment)
            print(f"Location: {region}, {city}, {country}")
            save_comments(comments, region, city, country, video_id, query)
        else:
            print("No comments available for this video.")
        
        choice = input("Press 'q' to quit or any other key to continue: ")
        if choice.lower() == 'q':
            sys.exit("Exiting program.")
