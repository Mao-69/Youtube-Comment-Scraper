import os
import pandas as pd
import csv
import json
from googleapiclient.discovery import build
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

API_KEY = 'YOUR API KEY HERE'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

DATA_DIR = "data"
WHITE = '\033[97m'
BLUE = '\033[94m'
RESET = '\033[0m'

banner = """
            __,aaPPPPPPPPPPPaa,__
         ,adP\"\"\"\"'            `\"\"\"Yb,_
      ,adP'                          `\"Yb,
    ,dP'     ,aadPP\"\"\"\"\"\"YYba,_        `\"Y,
   ,P'    ,aP\"'              `\"\"Ya,       \"Yb,
  ,P'    aP'     _________        `\"Ya     `Yb,
 ,P'    d\"    ,adP\"\"\"\"\"\"\"\"\"\"\"Yba,    `Y,     \"Y,
,d'   ,d'   ,dP\"               `Yb,    `Y,    `Y,
d'   ,d'   ,d'    ,dP\"\"888Yb,    `Y,    `Y,    `b
8    d'    d'   ,d\"(\\(\\     \"b,   `Y,   `8,     Y,
8    8     8    d' ( -.-)_   `Y,    `8   `8    `b
8    8     8    8  o_(\" \")( \")      `8    8     8
8    Y,    Y,   `b,  ,aP      P     8    ,P     8
I,   `Y,   `Ya    \"\"\"\"      d'     ,P    d\"    ,P
`Y,   `8,    `Ya         ,8\"     ,P'    ,P'    d'
 `Y,   `Ya,    `Ya,,__,,d\"'     ,P'    ,P\"    ,P
  `Y,    `Ya,     `\"\"\"\"\"'      ,P'   ,d\"    ,P'
   `Yb,    `\"Ya,_           ,d\"    ,P'    ,P'
     `Yb,      \"\"YbaaaaaadP\"     ,P'    ,P'
       `Yba,                   ,d'    ,dP'
          `\"Yba,__       __,adP\"     dP\"
              `\"\"\"\"\"\"\"\"\"\"\"\"\"\"'
"""

banner = banner.replace("'", WHITE + "'" + RESET)
banner = banner.replace(",", WHITE + "," + RESET)

for char in ['8', 'd', 'b', 'P', 'p', 'a', '"\"', 'Y', '-', 'I', '--']:
    banner = banner.replace(char, BLUE + char + RESET)

sia = SentimentIntensityAnalyzer()

def measure_sentiment(csv_file):
    df = pd.read_csv(csv_file)
    df['Sentiment'] = df['Comment'].apply(lambda x: sia.polarity_scores(x)['compound'])
    overall_sentiment = df['Sentiment'].mean()
    return df, overall_sentiment

subdirectories = [subdir for subdir in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, subdir))]

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

def show_sentiment_for_comments():
    while True:
        print("Choose a subdirectory to run sentiment analysis on:")
        for idx, subdir in enumerate(subdirectories):
            print(f"{idx + 1}. {subdir}")
        print("Enter 'q' to quit.")
        
        choice = input("Enter your choice: ")
        
        if choice.lower() == 'q':
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(subdirectories):
                subdir = subdirectories[choice - 1]
                subdir_path = os.path.join(DATA_DIR, subdir)
                
                os.system('cls' if os.name == 'nt' else 'clear')
                
                for file in os.listdir(subdir_path):
                    if file.endswith(".csv"):
                        csv_file = os.path.join(subdir_path, file)
                        df_with_sentiment, overall_sentiment = measure_sentiment(csv_file)
                        print("-" * 50)
                        print(f"Sentiment measurements for file: {csv_file}")
                        print(df_with_sentiment[['Comment', 'Sentiment']])
                        print(f"Overall Sentiment: {overall_sentiment}")
                        print("-" * 50)
                        user_input = input("Press 'n' for next result, 'b' to go back to subdir choice, 'q' to quit: ")
                        os.system('cls' if os.name == 'nt' else 'clear')
                        if user_input.lower() == 'q':
                            return
                        elif user_input.lower() == 'b':
                            break
                        elif user_input.lower() != 'n':
                            print("Invalid input. Please press 'n' to continue, 'b' to go back, or 'q' to quit.")
                            break
            else:
                print("Invalid choice. Please enter a number corresponding to a subdirectory.")
        except ValueError:
            print("Invalid choice. Please enter a number corresponding to a subdirectory or 'q' to quit.")

def print_menu():
    print("Menu:")
    print("1. Get Comments")
    print("2. Show Sentiment for Comments")
    print("0. Exit")

def main():
    print(banner)
    while True:
        print_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            print("You selected: Get Comments")
            search_query = input("Enter your search query: ").strip().replace(" ", "+")
            try:
                while True:
                    search_videos(search_query)
                    user_input = input("Press 'q' to quit, or press Enter to continue fetching comments for the next video: ")
                    if user_input.lower() == 'q':
                        break
            except KeyboardInterrupt:
                print("\nProgram interrupted by the user.")
        elif choice == "2":
            print("You selected: Show Sentiment for Comments")
            show_sentiment_for_comments()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
