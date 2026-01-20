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

def get_latest_keyword():
    """텔레그램 봇에게 보낸 마지막 메시지를 키워드로 가져옵니다."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        response = requests.get(url).json()
        if response.get("result"):
            # 가장 최근 메시지들 중 마지막 텍스트 메시지 찾기
            for update in reversed(response["result"]):
                if "message" in update and "text" in update["message"]:
                    # 내가 보낸 메시지인지 확인
                    if str(update["message"]["chat"]["id"]) == TELEGRAM_CHAT_ID:
                        return update["message"]["text"]
    except Exception as e:
        print(f"텔레그램 메시지 확인 중 오류: {e}")
    
    # 메시지가 없거나 오류 시 기본 키워드 사용 [cite: 2026-01-12]
    return "2026년 반도체 경기 전망"

def send_telegram(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)

def analyze_youtube(query):
    print(f"🔍 현재 분석 키워드: {query}")
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    search_res = youtube.search().list(q=query, part='snippet', maxResults=10, type='video').execute()
    
    results = []
    viral_report = f"🚀 <b>{datetime.now().strftime('%Y-%m-%d')} '{query}' 분석 보고서</b>\n\n"
    found_viral = False

    for item in search_res.get('items', []):
        v_id = item['id']['videoId']
        v_stats = youtube.videos().list(part='statistics,snippet', id=v_id).execute()['items'][0]
        c_id = v_stats['snippet']['channelId']
        c_stats = youtube.channels().list(part='statistics', id=c_id).execute()['items'][0]
        
        title = v_stats['snippet']['title']
        channel_name = v_stats['snippet']['channelTitle']
        views = int(v_stats['statistics'].get('viewCount', 0))
        subs = int(c_stats['statistics'].get('subscriberCount', 0))
        perf_index = (views / subs * 100) if subs > 500 else 0
        
        results.append({'Title': title, 'Views': views, 'Subs': subs, 'Perf_Index': perf_index})

        if perf_index > 10:
            viral_report += (
                f"🔥 <b>급상승 발견!</b>\n"
                f"<b>제목:</b> {title}\n"
                f"<b>채널:</b> {channel_name}\n"
                f"<b>조회수:</b> {views:,}회 / <b>구독자:</b> {subs:,}명\n"
                f"<b>성과지수:</b> {perf_index:.1f}%\n"
                f"<b>링크:</b> https://www.youtube.com/watch?v={v_id}\n\n"
            )
            found_viral = True

    # 그래프 생성
    df = pd.DataFrame(results)
    if not df.empty:
        df.to_csv('historical_performance.csv', index=False, encoding='utf-8-sig')
        plt.figure(figsize=(12, 10))
        sns.barplot(data=df.sort_values('Perf_Index', ascending=False).head(5), x='Perf_Index', y='Title')
        plt.title(f"'{query}' 성과 분석 ({datetime.now().strftime('%Y-%m-%d')})")
        plt.tight_layout()
        plt.savefig('performance_report.png')
    
    if found_viral:
        send_telegram(viral_report)
    else:
        send_telegram(f"✅ <b>'{query}'</b> 분석 완료\n특별한 급상승 영상이 없습니다.")

if __name__ == "__main__":
    # 텔레그램에서 키워드를 가져와 분석 수행 [cite: 2026-01-20]
    target_keyword = get_latest_keyword()
    analyze_youtube(target_keyword)