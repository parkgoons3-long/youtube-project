import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib # 이 한 줄만 추가하면 됩니다!
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

def analyze_channel_performance(query):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # 1. 검색 결과 가져오기
    search_response = youtube.search().list(
        q=query, part='snippet', maxResults=5, type='video'
    ).execute()
    
    video_results = []
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')

    for item in search_response.get('items', []):
        v_id = item['id']['videoId']
        c_id = item['snippet']['channelId']
        
        # 2. 영상 상세 데이터 및 채널 통계 병합 호출
        v_stats = youtube.videos().list(part='statistics,snippet', id=v_id).execute()['items'][0]
        c_stats = youtube.channels().list(part='statistics', id=c_id).execute()['items'][0]
        
        views = int(v_stats['statistics'].get('viewCount', 0))
        subs = int(c_stats['statistics'].get('subscriberCount', 0))
        
        # 성과 지표: 구독자 대비 조회수 비율 (%)
        performance_idx = round((views / subs * 100), 2) if subs > 0 else 0
        
        video_results.append({
            'Date': current_date,
            'Title': item['snippet']['title'][:25],
            'Channel': item['snippet']['channelTitle'],
            'Subscribers': subs,
            'Views': views,
            'Perf_Index': performance_idx
        })

    df = pd.DataFrame(video_results)
    
    # 3. 데이터 누적 저장 (기존 파일이 있으면 합치고, 없으면 새로 생성)
    file_name = 'historical_performance.csv'
    if os.path.exists(file_name):
        existing_df = pd.read_csv(file_name)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    
    # 4. 시각화: 구독자 대비 성과(Perf_Index) 분석
    plt.figure(figsize=(12, 7))
    sns.set_theme(style="darkgrid")
    ax = sns.barplot(x='Perf_Index', y='Title', data=df.drop_duplicates('Title', keep='last').sort_values('Perf_Index', ascending=False), palette='magma')
    
    plt.title(f'Video Performance Index (Views/Subs %) - {current_date}')
    plt.xlabel('Performance Index (%)')
    plt.tight_layout()
    plt.savefig('performance_report.png')
    
    print(f"분석 완료: {file_name}에 누적되었으며 보고서 이미지가 갱신되었습니다.")

if __name__ == "__main__":
    # 2026년 01월 20일 최신 경제 트렌드 반영 [cite: 2026-01-12]
    get_query = '2026년 반도체 경기 전망'
    analyze_channel_performance(get_query)
