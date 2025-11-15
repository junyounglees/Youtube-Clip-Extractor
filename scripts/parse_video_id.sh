#!/bin/bash
# Extract video ID from YouTube URL
# Usage: ./parse_video_id.sh "https://www.youtube.com/watch?v=AqEN8qOcAcA"
# Output: AqEN8qOcAcA

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <youtube_url>" >&2
    exit 1
fi

url="$1"

# Try different YouTube URL patterns
video_id=""

# Pattern 1: youtube.com/watch?v=VIDEO_ID
if echo "$url" | grep -q 'youtube\.com/watch?v='; then
    video_id=$(echo "$url" | sed -n 's/.*[?&]v=\([^&]*\).*/\1/p')
fi

# Pattern 2: youtu.be/VIDEO_ID
if [ -z "$video_id" ] && echo "$url" | grep -q 'youtu\.be/'; then
    video_id=$(echo "$url" | sed -n 's/.*youtu\.be\/\([^?]*\).*/\1/p')
fi

# Pattern 3: youtube.com/embed/VIDEO_ID
if [ -z "$video_id" ] && echo "$url" | grep -q 'youtube\.com/embed/'; then
    video_id=$(echo "$url" | sed -n 's/.*youtube\.com\/embed\/\([^?]*\).*/\1/p')
fi

# Pattern 4: youtube.com/v/VIDEO_ID
if [ -z "$video_id" ] && echo "$url" | grep -q 'youtube\.com/v/'; then
    video_id=$(echo "$url" | sed -n 's/.*youtube\.com\/v\/\([^?]*\).*/\1/p')
fi

if [ -z "$video_id" ]; then
    echo "Could not extract video ID from URL: $url" >&2
    exit 1
fi

echo "$video_id"
