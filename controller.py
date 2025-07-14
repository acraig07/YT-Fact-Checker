from src.yt     import checkURL, getTranscript
from src.claims import getClaims
from src.factcheck import factCheck
from src.data import save_factcheck
from datetime import datetime

class FactCheckController:
    def run(self, url: str):
        error_messages = {
            401: "ERROR: Video duration exceeds 20 minutes, try a different video.",
            402: f"ERROR: No English transcript available for {url}.",
            403: f"ERROR: {url} is not a YouTube URL or an invalid YouTube URL format. Please enter a new YouTube URL.",
            405: "ERROR: API failed. Please try again in a minute.",
        }
        valid, code_or_video_id = checkURL(url)
        if not valid:
            msg = error_messages.get(code_or_video_id, f"Unknown error ({code_or_video_id}).")
            return False, msg

        transcript = getTranscript(code_or_video_id)

        try:
            claims = getClaims(transcript)
            results, LLM1, LLM2, LLM3 = factCheck(claims)
        except Exception:
            return False, error_messages[405]

        entry_id = save_factcheck(url, LLM1, LLM2, LLM3, results, datetime.utcnow())

        return True, results
