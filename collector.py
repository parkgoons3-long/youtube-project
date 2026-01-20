import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# .env 파일에 저장된 변수 불러오기
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

def get_video_list(query):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # 키워드로 동영상 검색 요청
    request = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=5,
        type='video'
    )
    response = request.execute()

    for item in response.get('items', []):
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        print(f"제목: {title}\n링크: https://www.youtube.com/watch?v={video_id}\n")

if __name__ == "__main__":
    # 원하는 검색 키워드 입력
    get_video_list('경제 지표')
