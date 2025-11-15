---
name: youtube-clip-extractor
description: "Extract specific time segments from YouTube videos as B-roll clips. Triggered by requests like 'extract YouTube clip', 'download video segment', 'get B-roll from YouTube', or when user provides YouTube URL with timeframe (MM:SS-MM:SS or HH:MM:SS-HH:MM:SS)."
---

# YouTube Clip Extractor
**READ THIS FILE ENTIRELY BEFORE START**
**MAKE SURE FINAL OUTPUT IS A DOWNLOADABLE VIDEO CLIP**

## Overview

Extract specific time segments from YouTube videos using yt-dlp and ffmpeg. The skill provides atomic scripts for parsing video URLs, validating timeframes, and extracting precise video clips for B-roll usage.

## ⚠️ CRITICAL RULE: Complete Clip Extraction

**When extracting a YouTube clip:**

1. **Parse the video URL correctly**:
   - Support: `youtube.com/watch?v=VIDEO_ID`, `youtu.be/VIDEO_ID`, `youtube.com/embed/VIDEO_ID`
   - Extract: VIDEO_ID only

2. **Validate timeframe format**:
   - Accept: `MM:SS-MM:SS` or `HH:MM:SS-HH:MM:SS`
   - Verify: End time is after start time
   - Calculate: Duration in seconds

3. **Extract with quality preservation**:
   - Download: Best available quality (prefer mp4)
   - Extract: Exact timeframe specified
   - Encode: H.264 video + AAC audio for compatibility

4. **Handle errors gracefully**:
   - ✅ Report: "Video unavailable or private"
   - ✅ Report: "Invalid timeframe format"
   - ✅ Report: "Download failed - check URL"
   - ❌ NOT: Silent failures or partial clips

---

## Workflow: YouTube Clip Extraction

**MANDATORY**: Create To-Do Checklist with below steps before starting.

### Step 1: Parse Video URL

```bash
# Extract video ID from URL
video_id=$(./scripts/parse_video_id.sh "https://www.youtube.com/watch?v=AqEN8qOcAcA")
# Returns: AqEN8qOcAcA
```

### Step 2: Validate Timeframe

```bash
# Validate timeframe format
./scripts/validate_timeframe.sh "06:13-06:30"
# Options:
# - MM:SS-MM:SS format: "06:13-06:30"
# - HH:MM:SS-HH:MM:SS format: "00:06:13-00:06:30"
# Exit code 0 if valid, 1 if invalid
```

### Step 3: Parse Time Components

```bash
# Convert to HH:MM:SS format for ffmpeg
start_time=$(./scripts/parse_time.sh "06:13")
end_time=$(./scripts/parse_time.sh "06:30")
# Returns: 00:06:13 and 00:06:30
```

### Step 4: Extract Clip

```bash
# Extract clip from video
./scripts/extract_clip.sh \
    "https://www.youtube.com/watch?v=AqEN8qOcAcA" \
    "06:13-06:30" \
    "output_clip.mp4"
# Creates: output_clip.mp4 with the specified segment
```

### Step 5: Verify Output

**Use the Output Format Template** (see below)

**Termination**:
- Clip file successfully created
- Duration matches requested timeframe
- Video quality preserved
- No errors during extraction

**MANDATORY**:
- Always verify output file exists and is playable
- Check file size is reasonable (not 0 bytes)
- Confirm duration matches requested timeframe

---

## Atomic Scripts

All scripts are in `scripts/` directory:

| Script | Purpose | Usage |
|--------|---------|-------|
| `parse_video_id.sh` | Extract video ID from URL | `./scripts/parse_video_id.sh <url>` |
| `parse_time.sh` | Convert time to HH:MM:SS format | `./scripts/parse_time.sh <time>` |
| `validate_timeframe.sh` | Validate timeframe format | `./scripts/validate_timeframe.sh <timeframe>` |
| `extract_clip.sh` | Main extraction script | `./scripts/extract_clip.sh <url> <timeframe> [output]` |

---

## Common Mistakes

❌ **Invalid timeframe format** (CRITICAL)
- Issue: Timeframe not in MM:SS-MM:SS or HH:MM:SS-HH:MM:SS format
- Example:
  - ❌ WRONG: "6:13 to 6:30" or "06:13~06:30"
  - ✅ RIGHT: "06:13-06:30" or "00:06:13-00:06:30"
- Fix: Validate format before extraction
- Prevention: Use validate_timeframe.sh script

❌ **End time before start time** (CRITICAL)
- Issue: Negative duration calculated
- Example: "06:30-06:13" (backwards)
- Fix: Swap start/end or reject with error
- Prevention: Calculate duration and check > 0

❌ **Download entire video unnecessarily** (PERFORMANCE)
- Issue: Downloading full video when only small segment needed
- Fix: Use yt-dlp `--download-sections` for efficiency
- Prevention: Always specify section download first, fallback to full if needed

❌ **Wrong codec/format** (COMPATIBILITY)
- Issue: Extracted clip not playable in common players
- Fix: Use H.264 video + AAC audio (most compatible)
- Prevention: Always specify `-c:v libx264 -c:a aac` in ffmpeg

❌ **Not cleaning up temp files** (DISK SPACE)
- Issue: Temporary video files left in /tmp directory
- Fix: Always remove temp files after extraction
- Prevention: Use trap or explicit rm commands

❌ **Missing error handling** (USER EXPERIENCE)
- Issue: Script fails silently or with cryptic errors
- Fix: Validate each step and provide clear error messages
- Prevention: Check exit codes and file existence

---

## Output Format Template

**MANDATORY**: Present final output in structured format:

```markdown
## 🎬 YouTube Clip Extracted

**Video ID**: [VIDEO_ID]
**Timeframe**: [START] - [END] (Duration: [DURATION]s)
**Output File**: [FILENAME]
**File Size**: [SIZE]

---

### Extraction Details

✅ Video URL parsed
✅ Timeframe validated
✅ Clip downloaded and extracted
✅ Output file created: `[FILENAME]`

**Quality**: [RESOLUTION] @ [FPS]fps
**Format**: MP4 (H.264 + AAC)

---

**✅ Clip extraction complete**
**Ready for use as B-roll**
```

**Critical Requirements**:
- Include video metadata (ID, timeframe, duration)
- Display output file path and size
- Confirm all steps completed successfully
- Provide file format details
- Clear visual separation with `---`

---

## Timeframe Format Support

### Supported Formats

| Format | Example | Description |
|--------|---------|-------------|
| MM:SS-MM:SS | `06:13-06:30` | Minutes:Seconds (most common) |
| HH:MM:SS-HH:MM:SS | `00:06:13-00:06:30` | Hours:Minutes:Seconds |
| M:SS-M:SS | `1:30-2:45` | Single digit minutes |

### Automatic Conversion

All formats are automatically converted to HH:MM:SS for internal processing:
- `06:13` → `00:06:13`
- `1:30` → `00:01:30`
- `01:23:45` → `01:23:45` (no change)

---

## Advanced Options

### Custom Output Filename

```bash
# Specify custom output filename
./scripts/extract_clip.sh \
    "https://youtube.com/watch?v=ABC" \
    "06:13-06:30" \
    "my_broll_clip.mp4"
```

### Quality Selection

The script automatically downloads best available quality. For custom quality:

```bash
# Modify extract_clip.sh line with yt-dlp format option
# --format "bestvideo[height<=720]+bestaudio/best[height<=720]"
```

### Batch Extraction

```bash
# Extract multiple clips from same video
for timeframe in "00:30-01:00" "02:15-02:45" "05:00-05:30"; do
    ./scripts/extract_clip.sh "VIDEO_URL" "$timeframe" "clip_${timeframe//:/-}.mp4"
done
```

---

## Success Criteria

✅ Video ID correctly parsed from any YouTube URL format
✅ Timeframe validated and converted to HH:MM:SS format
✅ Clip extracted with exact start/end times
✅ Output file created with reasonable size
✅ Video quality preserved (best available)
✅ Audio synchronized with video
✅ Compatible format (MP4/H.264/AAC)
✅ Temporary files cleaned up
✅ Error handling for edge cases
✅ **Final validation: Clip is playable and correct duration**

---

## Dependencies

Required tools:

- **yt-dlp**: YouTube video downloader (version 2024.08.06+)
  - Installation: `brew install yt-dlp` (macOS)
  - Alternative: `pip install yt-dlp`
- **ffmpeg**: Video processing tool (version 4.0+)
  - Installation: `brew install ffmpeg` (macOS)
  - Alternative: `apt install ffmpeg` (Ubuntu/Debian)
- **ffprobe**: Video analysis (included with ffmpeg)
- **bash**: Script execution (version 4.0+)

Verify installations:
```bash
yt-dlp --version  # Should return 2024.08.06 or newer
ffmpeg -version   # Should return 4.0 or newer
ffprobe -version  # Should return 4.0 or newer
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not extract video ID" | Invalid YouTube URL | Verify URL format |
| "Invalid timeframe format" | Wrong timeframe syntax | Use MM:SS-MM:SS format |
| "End time before start time" | Backwards timeframe | Swap start/end times |
| "Video unavailable" | Private/deleted video | Verify video is public |
| "Download failed" | Network/permission issue | Check internet and URL |
| "yt-dlp not found" | Tool not installed | Install yt-dlp |
| "ffmpeg not found" | Tool not installed | Install ffmpeg |

### Validation Checklist

Before presenting output:
- [ ] Video ID correctly extracted?
- [ ] Timeframe format valid?
- [ ] Start time before end time?
- [ ] Clip file created?
- [ ] File size > 0 bytes?
- [ ] Duration matches requested timeframe?
- [ ] Temporary files cleaned up?

**❌ DO NOT present output if any checkbox is unchecked**

---

## Configuration

No API key required. yt-dlp works with public YouTube videos without authentication.

For rate-limited or private videos, users can configure:
```bash
# Optional: Set cookies for authenticated access
yt-dlp --cookies-from-browser chrome
```

---

## Examples

### Example 1: Simple Clip (MM:SS format)

```
User: "Extract clip from https://www.youtube.com/watch?v=AqEN8qOcAcA
       from 06:13 to 06:30"

Process:
1. Parse video ID: AqEN8qOcAcA
2. Validate timeframe: 06:13-06:30 ✓
3. Convert times: 00:06:13 - 00:06:30
4. Extract 17-second clip
5. Save as clip.mp4

Output: clip.mp4 (3.0MB, 17s)
```

### Example 2: Custom Output Name

```
User: "Get B-roll from youtu.be/XYZ123 from 1:30 to 2:00,
       save as intro_broll.mp4"

Process:
1. Parse video ID: XYZ123
2. Validate timeframe: 1:30-2:00 ✓
3. Convert times: 00:01:30 - 00:02:00
4. Extract 30-second clip
5. Save as intro_broll.mp4

Output: intro_broll.mp4 (5.2MB, 30s)
```

### Example 3: Long Timeframe (HH:MM:SS)

```
User: "Extract from https://youtube.com/watch?v=ABC
       from 01:23:45 to 01:25:30"

Process:
1. Parse video ID: ABC
2. Validate timeframe: 01:23:45-01:25:30 ✓
3. Times already in HH:MM:SS format
4. Extract 1m45s clip
5. Save as clip.mp4

Output: clip.mp4 (18.4MB, 105s)
```

### Example 4: Error - Invalid Format

```
User: "Get clip from youtube.com/watch?v=XYZ
       from 6:13 to 6:30"

Process:
1. Parse video ID: XYZ
2. Validate timeframe: ERROR - missing dash separator
3. Report error to user

Output: "Invalid timeframe format. Expected: 06:13-06:30 (with dash)"
```

---

## Test Suite

The skill includes comprehensive TDD tests:

```bash
# Run all tests
bash tests/test_clip_extractor.sh

# Expected output:
# ✓ Parse MM:SS format (06:13 -> 00:06:13)
# ✓ Parse HH:MM:SS format (01:23:45 -> 01:23:45)
# ✓ Parse short format (1:30 -> 00:01:30)
# ✓ Extract ID from standard URL
# ✓ Extract ID from short URL
# ✓ Extract ID from embed URL
# ✓ Valid timeframe format (06:13-06:30)
# ✓ Valid HH:MM:SS timeframe
# ✓ yt-dlp is installed
# ✓ ffmpeg is installed
#
# Test Summary: 10 passed, 0 failed
```

---

## Future Enhancements

Potential improvements (not required for initial implementation):
- Batch clip extraction (multiple timeframes from one video)
- Automatic thumbnail generation from clip
- Video quality selection (720p, 1080p, 4K)
- Audio-only extraction option
- Subtitle embedding in clips
- Integration with video editing tools
- Cloud storage upload (S3, GDrive, Dropbox)
- Metadata preservation (title, description, tags)

---

## Usage in Claude Code

When user requests clip extraction:

1. **Parse Request**:
   - Extract YouTube URL
   - Extract timeframe
   - Extract optional output filename

2. **Execute Workflow**:
   - Run validation scripts
   - Execute extraction
   - Verify output

3. **Present Results**:
   - Use output format template
   - Show file path and metadata
   - Confirm completion

4. **Error Handling**:
   - Provide clear error messages
   - Suggest fixes for common issues
   - Guide user to resolution

---

**License**: MIT
**Author**: Claude Code Skill
**Version**: 1.0.0
**Last Updated**: 2025-01-15
