# 这个脚本是通过输入API密钥和频道ID，爬取该频道上传的视频信息，并保存到videos.json文件中。
# 记得要填API_KEY和CHANNEL_ID
# 自动记录打印时长


from googleapiclient.discovery import build
import json, os ,time
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


# 待填写
API_KEY = os.getenv('API_KEY')



# 替换为你要爬取的频道ID
CHANNEL_ID = os.getenv('CHANNEL_ID')

def get_channel_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 获取频道上传的播放列表ID
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    if not res.get('items'):
        print("错误：无法找到该频道ID，请检查CHANNEL_ID是否正确。")
        return []
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    
    while True:
        # 1. 获取播放列表中的视频ID和基本信息
        pl_res = youtube.playlistItems().list(
            playlistId=playlist_id,
            part='snippet',
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        video_ids = [item['snippet']['resourceId']['videoId'] for item in pl_res['items']]
        
        if not video_ids:
            break

        # 2. 批量获取视频的详细信息（时长等）
        video_res = youtube.videos().list(
            id=','.join(video_ids),
            part='contentDetails,snippet'
        ).execute()
        
        # 创建一个视频详情的字典，方便查找
        video_details = {item['id']: item for item in video_res['items']}
        
        # 3. 组合信息
        for item in pl_res['items']:
            video_id = item['snippet']['resourceId']['videoId']
            
            # 从批量获取的结果中查找对应的视频详情
            detail = video_details.get(video_id)
            if not detail:
                continue

            duration = detail['contentDetails']['duration']
            # 使用 playlistItems 的 snippet 获取发布日期和标题，信息更准确
            published_at = item['snippet']['publishedAt']
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            
            thumbnail_url = item['snippet']['thumbnails'].get('maxres', {}).get('url') or                             item['snippet']['thumbnails'].get('standard', {}).get('url') or                             item['snippet']['thumbnails']['high']['url']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            
            videos.append({
                'title': video_title,
                'description': video_description,
                'thumbnail': thumbnail_url,
                'url': video_url,
                'duration': duration,
                'published_at': published_at
            })
        
        next_page_token = pl_res.get('nextPageToken')
        if not next_page_token:
            break
            
    return videos

if __name__ == '__main__':
    if not API_KEY or not CHANNEL_ID:
        print("错误：请确保你的.env文件中已经正确填写了 API_KEY 和 CHANNEL_ID。")
    else:
        start_time = time.time()

        videos = get_channel_videos(API_KEY, CHANNEL_ID)
        
        if videos:
            # 获取频道名称用于生成文件名
            youtube = build('youtube', 'v3', developerKey=API_KEY)
            channel_response = youtube.channels().list(id=CHANNEL_ID, part='snippet').execute()
            channel_title = channel_response['items'][0]['snippet']['title']
            safe_channel_title = "".join(c for c in channel_title if c.isalnum() or c in (' ', '_')).rstrip()
            
            # 将结果写入以频道名命名的JSON文件
            file_name = f"{safe_channel_title}.json"
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(videos, f, ensure_ascii=False, indent=4)
            print(f"成功爬取 {len(videos)} 个视频，并保存到 {file_name}")

        end_time = time.time()
        # 计算总耗时（秒）
        total_seconds = end_time - start_time

        # 转换为分钟和秒
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)

        # 格式化输出
        print(f"爬取时间：{minutes}分{seconds}秒")
