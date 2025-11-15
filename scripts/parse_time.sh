#!/bin/bash
# Parse time format and convert to HH:MM:SS
# Usage: ./parse_time.sh "06:13"
# Output: 00:06:13

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <time>" >&2
    echo "Examples: 06:13, 1:30, 01:23:45" >&2
    exit 1
fi

time_input="$1"

# Count colons to determine format
colon_count=$(echo "$time_input" | tr -cd ':' | wc -c | tr -d ' ')

if [ "$colon_count" -eq 2 ]; then
    # Already HH:MM:SS format
    echo "$time_input"
elif [ "$colon_count" -eq 1 ]; then
    # MM:SS format, add HH
    IFS=':' read -r minutes seconds <<< "$time_input"
    # Pad with zeros
    printf "%02d:%02d:%02d\n" 0 "$minutes" "$seconds"
else
    echo "Invalid time format: $time_input" >&2
    echo "Expected MM:SS or HH:MM:SS" >&2
    exit 1
fi
