#!/bin/bash
# Get transcript for specific timeframe
# Usage: ./get_transcript_segment.sh <video_id> <start_time> <end_time>
# Example: ./get_transcript_segment.sh "AqEN8qOcAcA" "00:06:13" "00:06:30"

set -e

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: $0 <video_id> <start_time> <end_time>" >&2
    echo "Example: $0 'AqEN8qOcAcA' '00:06:13' '00:06:30'" >&2
    exit 1
fi

VIDEO_ID="$1"
START_TIME="$2"
END_TIME="$3"

# Convert time to seconds
time_to_seconds() {
    local time=$1
    IFS=':' read -r h m s <<< "$time"
    # Remove leading zeros to avoid octal interpretation
    h=${h#0}; h=${h#0}; [ -z "$h" ] && h=0
    m=${m#0}; m=${m#0}; [ -z "$m" ] && m=0
    s=${s#0}; s=${s#0}; [ -z "$s" ] && s=0
    echo $((h * 3600 + m * 60 + s))
}

START_SEC=$(time_to_seconds "$START_TIME")
END_SEC=$(time_to_seconds "$END_TIME")

# Fetch full transcript with timestamps using yt-dlp
TEMP_FILE="/tmp/transcript_${VIDEO_ID}.txt"

yt-dlp \
    --skip-download \
    --write-auto-subs \
    --sub-lang en \
    --sub-format vtt \
    --quiet \
    --no-warnings \
    --output "$TEMP_FILE" \
    "https://www.youtube.com/watch?v=${VIDEO_ID}" 2>&1 >/dev/null || {
        # Try without auto-subs if that fails
        yt-dlp \
            --skip-download \
            --write-subs \
            --sub-lang en \
            --sub-format vtt \
            --quiet \
            --no-warnings \
            --output "$TEMP_FILE" \
            "https://www.youtube.com/watch?v=${VIDEO_ID}" 2>&1 >/dev/null
    }

# Find the VTT file
VTT_FILE="${TEMP_FILE}.en.vtt"

if [ ! -f "$VTT_FILE" ]; then
    echo "No transcript available for this video" >&2
    rm -f "${TEMP_FILE}"* 2>/dev/null
    exit 1
fi

# Parse VTT and filter by timeframe
python3 - "$VTT_FILE" "$START_SEC" "$END_SEC" << 'PYTHON_SCRIPT'
import sys
import re

def vtt_time_to_seconds(time_str):
    """Convert VTT timestamp to seconds"""
    # Format: HH:MM:SS.mmm or MM:SS.mmm
    parts = time_str.strip().split(':')
    if len(parts) == 3:
        h, m, s = parts
    else:
        h = '0'
        m, s = parts

    s = s.split('.')[0]  # Remove milliseconds
    return int(h) * 3600 + int(m) * 60 + int(s)

def parse_vtt(file_path, start_sec, end_sec):
    """Parse VTT file and extract text within timeframe"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into subtitle blocks
    blocks = re.split(r'\n\n+', content)

    transcript_segments = []

    for block in blocks:
        if '-->' not in block:
            continue

        lines = block.strip().split('\n')

        # Find timestamp line
        for i, line in enumerate(lines):
            if '-->' in line:
                # Parse timestamp
                timestamps = line.split('-->')
                if len(timestamps) != 2:
                    continue

                start_time = timestamps[0].strip()
                end_time = timestamps[1].strip().split()[0]  # Remove position info

                try:
                    block_start = vtt_time_to_seconds(start_time)
                    block_end = vtt_time_to_seconds(end_time)
                except:
                    continue

                # Check if this block overlaps with our timeframe
                if block_end < start_sec or block_start > end_sec:
                    continue

                # Extract text (lines after timestamp)
                text_lines = lines[i+1:]
                text = ' '.join(text_lines).strip()

                # Remove VTT formatting tags
                text = re.sub(r'<[^>]+>', '', text)

                if text:
                    transcript_segments.append({
                        'time': start_time,
                        'text': text
                    })

                break

    return transcript_segments

# Main
vtt_file = sys.argv[1]
start_sec = int(sys.argv[2])
end_sec = int(sys.argv[3])

segments = parse_vtt(vtt_file, start_sec, end_sec)

if segments:
    for seg in segments:
        print(f"[{seg['time']}] {seg['text']}")
else:
    print("No transcript found in this timeframe")

PYTHON_SCRIPT

# Cleanup
rm -f "${TEMP_FILE}"* 2>/dev/null

exit 0
