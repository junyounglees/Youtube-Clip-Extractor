#!/usr/bin/env python3
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

video_id = "AqEN8qOcAcA"
print(f"Testing video: {video_id}")

try:
    # List all available transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    print("\nAvailable transcripts:")
    for transcript in transcript_list:
        print(f"  - {transcript.language} ({transcript.language_code})")
        print(f"    Generated: {transcript.is_generated}")
        print(f"    Translatable: {transcript.is_translatable}")

    # Get Korean auto-generated
    try:
        transcript = transcript_list.find_generated_transcript(['ko'])
        data = transcript.fetch()

        print(f"\nFound Korean auto-generated transcript")
        print(f"Total segments: {len(data)}")

        # Filter for 06:13 - 06:30 (373-390 seconds)
        start_sec = 6*60 + 13  # 373
        end_sec = 6*60 + 30    # 390

        print(f"\nSegments from {start_sec}s to {end_sec}s:")
        for entry in data:
            if start_sec <= entry['start'] <= end_sec:
                mins = int(entry['start'] // 60)
                secs = int(entry['start'] % 60)
                print(f"[{mins:02d}:{secs:02d}] {entry['text']}")

    except Exception as e:
        print(f"Error getting Korean: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
