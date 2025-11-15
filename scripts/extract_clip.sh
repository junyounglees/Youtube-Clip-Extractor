#!/bin/bash
# Extract YouTube clip for specified timeframe
# Usage: ./extract_clip.sh <youtube_url> <timeframe> [output_file]
# Example: ./extract_clip.sh "https://youtube.com/watch?v=ABC" "06:13-06:30" "clip.mp4"

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage check
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${RED}Usage:${NC} $0 <youtube_url> <timeframe> [output_file]"
    echo ""
    echo "Examples:"
    echo "  $0 'https://youtube.com/watch?v=ABC' '06:13-06:30'"
    echo "  $0 'https://youtube.com/watch?v=ABC' '06:13-06:30' 'my_clip.mp4'"
    echo ""
    echo "Timeframe formats:"
    echo "  MM:SS-MM:SS     (e.g., 06:13-06:30)"
    echo "  HH:MM:SS-HH:MM:SS (e.g., 00:06:13-00:06:30)"
    exit 1
fi

URL="$1"
TIMEFRAME="$2"
OUTPUT_FILE="${3:-clip.mp4}"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  YouTube Clip Extractor${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Step 1: Parse video ID
echo -e "${YELLOW}[1/5]${NC} Parsing video URL..."
VIDEO_ID=$("$SCRIPT_DIR/parse_video_id.sh" "$URL")
if [ -z "$VIDEO_ID" ]; then
    echo -e "${RED}✗${NC} Failed to extract video ID"
    exit 1
fi
echo -e "${GREEN}✓${NC} Video ID: $VIDEO_ID"
echo ""

# Step 2: Validate timeframe
echo -e "${YELLOW}[2/5]${NC} Validating timeframe..."
if ! "$SCRIPT_DIR/validate_timeframe.sh" "$TIMEFRAME" >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} Invalid timeframe format"
    exit 1
fi
echo -e "${GREEN}✓${NC} Timeframe: $TIMEFRAME"
echo ""

# Step 3: Parse start and end times
echo -e "${YELLOW}[3/5]${NC} Parsing timestamps..."
IFS='-' read -r START_TIME END_TIME <<< "$TIMEFRAME"
START_TIME_FORMATTED=$("$SCRIPT_DIR/parse_time.sh" "$START_TIME")
END_TIME_FORMATTED=$("$SCRIPT_DIR/parse_time.sh" "$END_TIME")
echo -e "${GREEN}✓${NC} Start: $START_TIME_FORMATTED"
echo -e "${GREEN}✓${NC} End: $END_TIME_FORMATTED"
echo ""

# Calculate duration
IFS=':' read -r sh sm ss <<< "$START_TIME_FORMATTED"
IFS=':' read -r eh em es <<< "$END_TIME_FORMATTED"
start_seconds=$((10#$sh * 3600 + 10#$sm * 60 + 10#$ss))
end_seconds=$((10#$eh * 3600 + 10#$em * 60 + 10#$es))
duration_seconds=$((end_seconds - start_seconds))

if [ $duration_seconds -le 0 ]; then
    echo -e "${RED}✗${NC} Invalid timeframe: end time must be after start time"
    exit 1
fi

echo -e "Duration: ${duration_seconds}s"
echo ""

# Step 4: Download video section
echo -e "${YELLOW}[4/5]${NC} Downloading video segment..."
TEMP_VIDEO="/tmp/yt_temp_${VIDEO_ID}.mp4"

# Download with yt-dlp (download only the needed section for efficiency)
yt-dlp \
    --quiet \
    --no-warnings \
    --format "best[ext=mp4]/best" \
    --output "$TEMP_VIDEO" \
    --download-sections "*${START_TIME_FORMATTED}-${END_TIME_FORMATTED}" \
    "https://www.youtube.com/watch?v=${VIDEO_ID}" 2>&1 | while read -r line; do
        echo "  $line"
    done

if [ ! -f "$TEMP_VIDEO" ]; then
    # Fallback: download full video if section download failed
    echo -e "${YELLOW}⚠${NC} Section download not supported, downloading full video..."
    yt-dlp \
        --quiet \
        --no-warnings \
        --format "best[ext=mp4]/best" \
        --output "$TEMP_VIDEO" \
        "https://www.youtube.com/watch?v=${VIDEO_ID}"
fi

if [ ! -f "$TEMP_VIDEO" ]; then
    echo -e "${RED}✗${NC} Failed to download video"
    exit 1
fi

echo -e "${GREEN}✓${NC} Video downloaded"
echo ""

# Step 5: Extract clip with ffmpeg
echo -e "${YELLOW}[5/5]${NC} Extracting clip..."

# If yt-dlp downloaded only the section, copy it directly
# Otherwise, use ffmpeg to extract the exact timeframe
video_duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TEMP_VIDEO" 2>/dev/null | cut -d'.' -f1)

if [ "$video_duration" -le "$((duration_seconds + 5))" ]; then
    # Video is already roughly the right length (yt-dlp section download worked)
    echo -e "${BLUE}ℹ${NC} Using downloaded segment directly"
    mv "$TEMP_VIDEO" "$OUTPUT_FILE"
else
    # Extract exact timeframe with ffmpeg
    echo -e "${BLUE}ℹ${NC} Extracting exact timeframe with ffmpeg"
    ffmpeg \
        -i "$TEMP_VIDEO" \
        -ss "$START_TIME_FORMATTED" \
        -t "$duration_seconds" \
        -c:v libx264 \
        -c:a aac \
        -avoid_negative_ts make_zero \
        -fflags +genpts \
        "$OUTPUT_FILE" \
        -y \
        -loglevel error 2>&1 | while read -r line; do
            echo "  $line"
        done

    # Clean up temp file
    rm -f "$TEMP_VIDEO"
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo -e "${RED}✗${NC} Failed to create clip"
    rm -f "$TEMP_VIDEO"
    exit 1
fi

echo -e "${GREEN}✓${NC} Clip extracted successfully"
echo ""

# Get output file size
file_size=$(du -h "$OUTPUT_FILE" | cut -f1)

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "Output file: ${GREEN}$OUTPUT_FILE${NC}"
echo -e "File size: ${file_size}"
echo -e "Duration: ${duration_seconds}s"
echo ""
