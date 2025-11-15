#!/bin/bash
# Validate timeframe format
# Usage: ./validate_timeframe.sh "06:13-06:30"
# Exit code: 0 if valid, 1 if invalid

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <timeframe>" >&2
    echo "Example: 06:13-06:30 or 00:06:13-00:06:30" >&2
    exit 1
fi

timeframe="$1"

# Check if timeframe contains a dash
if ! echo "$timeframe" | grep -q '-'; then
    echo "Invalid timeframe format: $timeframe" >&2
    echo "Expected format: START-END (e.g., 06:13-06:30)" >&2
    exit 1
fi

# Split on dash
IFS='-' read -r start_time end_time <<< "$timeframe"

# Validate each time part
validate_time() {
    local time="$1"
    local colon_count=$(echo "$time" | tr -cd ':' | wc -c | tr -d ' ')

    # Must have 1 or 2 colons
    if [ "$colon_count" -ne 1 ] && [ "$colon_count" -ne 2 ]; then
        return 1
    fi

    # Check if all parts are numbers
    if ! echo "$time" | grep -qE '^[0-9]+:[0-9]+(:[0-9]+)?$'; then
        return 1
    fi

    return 0
}

if ! validate_time "$start_time"; then
    echo "Invalid start time: $start_time" >&2
    exit 1
fi

if ! validate_time "$end_time"; then
    echo "Invalid end time: $end_time" >&2
    exit 1
fi

echo "Valid timeframe: $timeframe"
exit 0
