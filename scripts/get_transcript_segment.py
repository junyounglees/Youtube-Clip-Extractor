#!/usr/bin/env python3
"""
Get transcript segment for specific timeframe
Usage: ./get_transcript_segment.py <video_id> <start_time> <end_time>
Example: ./get_transcript_segment.py "AqEN8qOcAcA" "00:06:13" "00:06:30"
"""

import sys
from youtube_transcript_api import YouTubeTranscriptApi

def time_to_seconds(time_str):
    """Convert HH:MM:SS or MM:SS to seconds"""
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
    else:
        h = '0'
        m, s = parts

    return int(h) * 3600 + int(m) * 60 + int(s)

def seconds_to_time(seconds):
    """Convert seconds to MM:SS format"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def get_transcript_segment(video_id, start_time, end_time):
    """Get transcript for specific timeframe"""
    try:
        # Create API instance
        api = YouTubeTranscriptApi()

        # Try to get transcript in multiple languages
        languages_to_try = [
            ['en'],
            ['ko'],
            ['ja'],
            ['zh-Hans'],
            ['es'],
            ['fr'],
            ['de']
        ]

        transcript_data = None
        for langs in languages_to_try:
            try:
                fetched = api.fetch(video_id, languages=langs)
                transcript_data = fetched
                break
            except:
                continue

        if not transcript_data:
            return None, "No transcript available"

        # Convert times to seconds
        start_sec = time_to_seconds(start_time)
        end_sec = time_to_seconds(end_time)

        # Filter transcript by timeframe
        # Note: In new API, entries have .start, .duration, .text attributes (not dict)
        segments = []
        for entry in transcript_data:
            entry_start = entry.start
            entry_end = entry_start + entry.duration

            # Check if this entry overlaps with our timeframe
            if entry_end < start_sec:
                continue
            if entry_start > end_sec:
                break

            segments.append({
                'time': seconds_to_time(entry_start),
                'text': entry.text.strip()
            })

        return segments

    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    if len(sys.argv) != 4:
        print("Usage: ./get_transcript_segment.py <video_id> <start_time> <end_time>", file=sys.stderr)
        print("Example: ./get_transcript_segment.py 'AqEN8qOcAcA' '00:06:13' '00:06:30'", file=sys.stderr)
        sys.exit(1)

    video_id = sys.argv[1]
    start_time = sys.argv[2]
    end_time = sys.argv[3]

    result = get_transcript_segment(video_id, start_time, end_time)

    if isinstance(result, tuple):  # Error case
        _, error_msg = result
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    segments = result

    if not segments:
        print("No transcript found in this timeframe")
    else:
        for seg in segments:
            print(f"[{seg['time']}] {seg['text']}")

if __name__ == "__main__":
    main()
