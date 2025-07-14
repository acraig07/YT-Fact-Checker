import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.proxies import WebshareProxyConfig
import googleapiclient.discovery
import re
import isodate


load_dotenv()
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv('YOUTUBE_API_KEY')
# PROXY_USERNAME = os.getenv("PROXY_USERNAME")
# PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

def checkURL(url):
    pattern = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

    regex = re.compile(pattern)
    match = regex.match(url)

    if match:

        video_id = match.group(6)

        requestDuration = youtube.videos().list(
            part="contentDetails",
            id=video_id
        )
        responseDuration = requestDuration.execute()

        duration_iso = responseDuration['items'][0]['contentDetails']['duration']
        duration_timedelta = isodate.parse_duration(duration_iso)
        total_seconds = int(duration_timedelta.total_seconds())

        if total_seconds > 1200:
            return False, 401


        requestLanguage = youtube.captions().list(
            part="snippet",
            videoId=video_id
        )

        responseLanguage = requestLanguage.execute()

        for item in responseLanguage.get('items', []):
            if item.get('snippet', {}).get('language') == 'en':
                return True, video_id

        return False, 402
    else:
        return False, 403

def getTranscript(videoID):

    # USE THE BELOW CODE IF IP BLOCKED FROM YT, UN COMMENT OUT .env VARIABLES AT TOP OF FILE AND LIBRARY IMPORT.
    # SEE WORKING AROUND IP BANS SECTION. https://pypi.org/project/youtube-transcript-api/

    # ytt_api = YouTubeTranscriptApi(
    #     proxy_config=WebshareProxyConfig(
    #         proxy_username=PROXY_USERNAME,
    #         proxy_password=PROXY_PASSWORD,
    #     )
    # )

    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(videoID, languages=['en'])
    transcript = transcript.to_raw_data()
    transcriptString = str(transcript)
    return transcriptString