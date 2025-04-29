# 这个脚本是通过输入API密钥和频道ID，爬取该频道上传的视频信息，并保存到videos.json文件中。

from googleapiclient.discovery import build
import json, os
from dotenv import load_dotenv  # 新增导入

# 加载.env文件
load_dotenv()

# 从环境变量获取API密钥
API_KEY = os.getenv('API_KEY')
# 替换为你要爬取的频道ID
CHANNEL_ID = 'UCH6Oc4MAJzzmK0SM805ZnjQ'

def get_channel_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 获取频道上传的播放列表ID
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    
    while True:
        # 获取播放列表中的视频
        res = youtube.playlistItems().list(
            playlistId=playlist_id,
            part='snippet',
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        for item in res['items']:
            video_id = item['snippet']['resourceId']['videoId']
            
            # 获取视频详情以获取时长
            video_details = youtube.videos().list(
                id=video_id,
                part='contentDetails'
            ).execute()
            
            duration = video_details['items'][0]['contentDetails']['duration']
            
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            thumbnail_url = item['snippet']['thumbnails'].get('maxres', {}).get('url') or item['snippet']['thumbnails'].get('standard', {}).get('url') or item['snippet']['thumbnails']['high']['url']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            
            videos.append({
                'title': video_title,
                'description': video_description,
                'thumbnail': thumbnail_url,
                'url': video_url,
                'duration': duration  # 添加视频时长
            })
        
        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break
    
    return videos

if __name__ == '__main__':
    videos = get_channel_videos(API_KEY, CHANNEL_ID)
    
    # 将结果写入JSON文件
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    
    print(f"成功爬取了{len(videos)}个视频信息，并保存到videos.json文件中")
