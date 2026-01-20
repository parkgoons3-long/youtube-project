import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import requests
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)

def analyze_youtube(query):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    search_res = youtube.search().list(q=query, part='snippet', maxResults=10, type='video').execute()
    
    results = []
    viral_report = f"🚀 <b>2026-01-20 유튜브 분석 보고서</b>\n\n"
    found_viral = False

    for item in search_res.get('items', []):
        v_id = item['id']['videoId']
        v_stats = youtube.videos().list(part='statistics,snippet', id=v_id).execute()['items'][0]
        c_id = v_stats['snippet']['channelId']
        c_stats = youtube.channels().list(part='statistics', id=c_id).execute()['items'][0]
        
        title = v_stats['snippet']['title']
        views = int(v_stats['statistics'].get('viewCount', 0))
        subs = int(c_stats['statistics'].get('subscriberCount', 0))
        perf_index = (views / subs * 100) if subs > 500 else 0
        
        results.append({'Title': title, 'Views': views, 'Subs': subs, 'Perf_Index': perf_index})

        # 성과지수가 10%를 넘으면 텔레그램 알림 대상으로 분류
        if perf_index > 10:
            viral_report += f"🔥 <b>급상승 발견!</b>\n제목: {title[:30]}...\n성과지수: {perf_index:.1f}%\n\n"
            found_viral = True

    df = pd.DataFrame(results)
    df.to_csv('historical_performance.csv', index=False, encoding='utf-8-sig')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df.sort_values('Perf_Index', ascending=False).head(5), x='Perf_Index', y='Title')
    plt.title(f"유튜브 성과 분석 ({datetime.now().strftime('%Y-%m-%d')})")
    plt.savefig('performance_report.png')
    
    if found_viral:
        send_telegram(viral_report)
    else:
        send_telegram("✅ 오늘의 분석 완료: 특별한 급상승 영상이 없습니다.")

if __name__ == "__main__":
    analyze_youtube("2026년 반도체 경기 전망")
