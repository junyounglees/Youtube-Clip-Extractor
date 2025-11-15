# YouTube Clip Extractor Skill

Extract specific time segments from YouTube videos as B-roll clips using TDD-developed scripts.

## Quick Start

### Basic Usage

```bash
./scripts/extract_clip.sh "YOUTUBE_URL" "START-END" [output.mp4]
```

### Examples

```bash
# Example 1: Extract 17-second clip (MM:SS format)
./scripts/extract_clip.sh \
    "https://www.youtube.com/watch?v=AqEN8qOcAcA" \
    "06:13-06:30" \
    "my_clip.mp4"

# Example 2: Using HH:MM:SS format
./scripts/extract_clip.sh \
    "https://youtu.be/XYZ123" \
    "00:01:30-00:02:00" \
    "intro_broll.mp4"

# Example 3: Default output name (clip.mp4)
./scripts/extract_clip.sh \
    "https://www.youtube.com/watch?v=ABC" \
    "1:30-2:45"
```

## Timeframe Formats

Supported formats:
- `MM:SS-MM:SS` → `06:13-06:30` (most common)
- `HH:MM:SS-HH:MM:SS` → `00:06:13-00:06:30`
- `M:SS-M:SS` → `1:30-2:45`

## Running Tests

```bash
# Run complete test suite
bash tests/test_clip_extractor.sh

# Expected: 10 tests passed, 0 failed
```

## Use in Claude Code

Once installed as a skill, you can use it in Claude Code:

```
User: "Extract a clip from https://youtube.com/watch?v=ABC
       from 06:13 to 06:30"

Claude: [Activates youtube-clip-extractor skill]
        [Extracts clip automatically]
        [Presents download link and metadata]
```

## File Structure

```
youtube-clip-extractor/
├── SKILL.md                    # Skill documentation for Claude
├── README.md                   # This file
├── scripts/
│   ├── parse_video_id.sh      # Extract video ID from URL
│   ├── parse_time.sh          # Convert time formats
│   ├── validate_timeframe.sh  # Validate timeframe syntax
│   └── extract_clip.sh        # Main extraction script
├── tests/
│   └── test_clip_extractor.sh # TDD test suite (10 tests)
└── assets/
    └── (future: screenshots, examples)
```

## Dependencies

- **yt-dlp** (2024.08.06+): `brew install yt-dlp`
- **ffmpeg** (4.0+): `brew install ffmpeg`
- **bash** (4.0+): Pre-installed on macOS

## Features

✅ TDD-developed with comprehensive test coverage
✅ Supports all major YouTube URL formats
✅ Flexible timeframe formats (MM:SS or HH:MM:SS)
✅ Best quality video download
✅ Efficient segment extraction (downloads only needed portion)
✅ Compatible MP4 output (H.264 + AAC)
✅ Clear progress indication
✅ Robust error handling
✅ Automatic temporary file cleanup

## Output

Creates MP4 files with:
- **Video codec**: H.264 (maximum compatibility)
- **Audio codec**: AAC
- **Format**: MP4 container
- **Quality**: Best available from YouTube

## Error Messages

| Message | Cause | Solution |
|---------|-------|----------|
| "Could not extract video ID" | Invalid URL | Verify YouTube URL format |
| "Invalid timeframe format" | Wrong syntax | Use `MM:SS-MM:SS` format |
| "End time before start time" | Backwards times | Swap start/end |
| "Video unavailable" | Private/deleted | Check video is public |
| "yt-dlp not found" | Missing dependency | Install yt-dlp |
| "ffmpeg not found" | Missing dependency | Install ffmpeg |

## Development

Built with Test-Driven Development (TDD):

1. ✅ **Tests written first** → `tests/test_clip_extractor.sh`
2. ✅ **Implementation follows** → All scripts in `scripts/`
3. ✅ **All tests pass** → 10/10 green
4. ✅ **Integration verified** → Real YouTube extraction tested

## License

MIT

## Version

1.0.0 (2025-01-15)
