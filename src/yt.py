from youtube_transcript_api import YouTubeTranscriptApi
import re

# Checks if URL is in a valid format
def checkURL(url):
    pattern = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

    regex = re.compile(pattern)
    match = regex.match(url)

    if match:
        getTranscript(match.group(6)) # group #6 has the id for the video
        return True
    else:
        return False

def getTranscript(videoID):

    # using the srt variable with the list of dictionaries
    # obtained by the .get_transcript() function
    srt = YouTubeTranscriptApi.get_transcript(videoID) # need to setup EN language only still

    # temporarily creating or overwriting a file "subtitles.txt" with
    # the info inside the context manager
    with open("subtitles.txt", "w") as f:
        # iterating through each element of list srt
        for i in srt:
            # writing each element of srt on a new line
            f.write("{}\n".format(i))