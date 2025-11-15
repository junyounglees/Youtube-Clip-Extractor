#!/bin/bash
# Test suite for YouTube clip extractor
# Run with: bash tests/test_clip_extractor.sh

# Don't exit on error - we want to run all tests
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Test helper functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"

    if [ "$expected" = "$actual" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Expected: $expected"
        echo -e "  Got: $actual"
        ((TESTS_FAILED++))
    fi
}

assert_file_exists() {
    local file="$1"
    local test_name="$2"

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  File not found: $file"
        ((TESTS_FAILED++))
    fi
}

assert_not_empty() {
    local value="$1"
    local test_name="$2"

    if [ -n "$value" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Value is empty"
        ((TESTS_FAILED++))
    fi
}

echo "======================================"
echo "YouTube Clip Extractor - Test Suite"
echo "======================================"
echo ""

# Test 1: Parse time format (MM:SS to HH:MM:SS)
echo "Test Suite: Time Parsing"
echo "------------------------"

test_time_parse_mmss() {
    local input="06:13"
    local expected="00:06:13"
    local actual=$("$SCRIPT_DIR/scripts/parse_time.sh" "$input")
    assert_equals "$expected" "$actual" "Parse MM:SS format (06:13 -> 00:06:13)"
}

test_time_parse_hhmmss() {
    local input="01:23:45"
    local expected="01:23:45"
    local actual=$("$SCRIPT_DIR/scripts/parse_time.sh" "$input")
    assert_equals "$expected" "$actual" "Parse HH:MM:SS format (01:23:45 -> 01:23:45)"
}

test_time_parse_short() {
    local input="1:30"
    local expected="00:01:30"
    local actual=$("$SCRIPT_DIR/scripts/parse_time.sh" "$input")
    assert_equals "$expected" "$actual" "Parse short format (1:30 -> 00:01:30)"
}

# Test 2: Parse video ID from URL
echo ""
echo "Test Suite: Video ID Extraction"
echo "--------------------------------"

test_video_id_standard() {
    local url="https://www.youtube.com/watch?v=AqEN8qOcAcA"
    local expected="AqEN8qOcAcA"
    local actual=$("$SCRIPT_DIR/scripts/parse_video_id.sh" "$url")
    assert_equals "$expected" "$actual" "Extract ID from standard URL"
}

test_video_id_short() {
    local url="https://youtu.be/AqEN8qOcAcA"
    local expected="AqEN8qOcAcA"
    local actual=$("$SCRIPT_DIR/scripts/parse_video_id.sh" "$url")
    assert_equals "$expected" "$actual" "Extract ID from short URL"
}

test_video_id_embed() {
    local url="https://www.youtube.com/embed/AqEN8qOcAcA"
    local expected="AqEN8qOcAcA"
    local actual=$("$SCRIPT_DIR/scripts/parse_video_id.sh" "$url")
    assert_equals "$expected" "$actual" "Extract ID from embed URL"
}

# Test 3: Validate timeframe format
echo ""
echo "Test Suite: Timeframe Validation"
echo "---------------------------------"

test_timeframe_valid() {
    local timeframe="06:13-06:30"
    "$SCRIPT_DIR/scripts/validate_timeframe.sh" "$timeframe" 2>/dev/null
    local exit_code=$?
    assert_equals "0" "$exit_code" "Valid timeframe format (06:13-06:30)"
}

test_timeframe_hhmmss() {
    local timeframe="00:06:13-00:06:30"
    "$SCRIPT_DIR/scripts/validate_timeframe.sh" "$timeframe" 2>/dev/null
    local exit_code=$?
    assert_equals "0" "$exit_code" "Valid HH:MM:SS timeframe"
}

# Test 4: Check dependencies
echo ""
echo "Test Suite: Dependencies"
echo "------------------------"

test_yt_dlp_installed() {
    command -v yt-dlp >/dev/null 2>&1
    local exit_code=$?
    assert_equals "0" "$exit_code" "yt-dlp is installed"
}

test_ffmpeg_installed() {
    command -v ffmpeg >/dev/null 2>&1
    local exit_code=$?
    assert_equals "0" "$exit_code" "ffmpeg is installed"
}

# Run all tests
if [ -f "$SCRIPT_DIR/scripts/parse_time.sh" ]; then
    test_time_parse_mmss
    test_time_parse_hhmmss
    test_time_parse_short
else
    echo -e "${YELLOW}⊘${NC} Skipping time parsing tests (script not yet implemented)"
fi

if [ -f "$SCRIPT_DIR/scripts/parse_video_id.sh" ]; then
    test_video_id_standard
    test_video_id_short
    test_video_id_embed
else
    echo -e "${YELLOW}⊘${NC} Skipping video ID tests (script not yet implemented)"
fi

if [ -f "$SCRIPT_DIR/scripts/validate_timeframe.sh" ]; then
    test_timeframe_valid
    test_timeframe_hhmmss
else
    echo -e "${YELLOW}⊘${NC} Skipping timeframe validation tests (script not yet implemented)"
fi

test_yt_dlp_installed
test_ffmpeg_installed

# Summary
echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
echo -e "${RED}Failed:${NC} $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
