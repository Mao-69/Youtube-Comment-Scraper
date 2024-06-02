import os
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
data_dir = "data"

def measure_sentiment(csv_file):
    df = pd.read_csv(csv_file)
    df['Sentiment'] = df['Comment'].apply(lambda x: sia.polarity_scores(x)['compound'])
    overall_sentiment = df['Sentiment'].mean()
    return df, overall_sentiment

subdirectories = [subdir for subdir in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, subdir))]

while True:
    print("Choose a subdirectory to run sentiment analysis on:")
    for idx, subdir in enumerate(subdirectories):
        print(f"{idx + 1}. {subdir}")
    print("Enter 'q' to quit.")
    
    choice = input("Enter your choice: ")
    
    if choice.lower() == 'q':
        break
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(subdirectories):
            subdir = subdirectories[choice - 1]
            subdir_path = os.path.join(data_dir, subdir)
            
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
                        break
                    elif user_input.lower() == 'b':
                        break
                    elif user_input.lower() != 'n':
                        print("Invalid input. Please press 'n' to continue, 'b' to go back, or 'q' to quit.")
                        break
        else:
            print("Invalid choice. Please enter a number corresponding to a subdirectory.")
    except ValueError:
        print("Invalid choice. Please enter a number corresponding to a subdirectory or 'q' to quit.")
