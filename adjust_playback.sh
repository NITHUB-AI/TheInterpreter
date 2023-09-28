#!/bin/bash

# Takes in an original audio and a translated audio, and determines the speed at which the translated audio needs to be
# played at to match the duration of the original audio. Then, it comverts it to that playback speed.

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_original_audio> <path_to_translated_audio>"
    exit 1
fi

# Extract file paths from command-line arguments
original_audio="$1"
translated_audio="$2"
adjusted_audio="${translated_audio%.*}_adjusted.${translated_audio##*.}"

# Extract durations in seconds
duration_original=$(ffmpeg -i "$original_audio" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, ":"); split(A[3], B, "."); print 3600*A[1] + 60*A[2] + B[1] }')
duration_translated=$(ffmpeg -i "$translated_audio" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, ":"); split(A[3], B, "."); print 3600*A[1] + 60*A[2] + B[1] }')

# Compute speed adjustment factor
factor=$(echo "$duration_translated / $duration_original" | bc -l)

# Adjust playback speed
ffmpeg -i "$translated_audio" -filter:a "atempo=$factor" "$adjusted_audio"