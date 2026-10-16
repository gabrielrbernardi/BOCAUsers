#!/usr/bin/env bash

FFMPEG="${FFMPEG:-ffmpeg}"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIR="${1:-$SCRIPT_DIR/animeitor}"
OUTPUT_DIR="${2:-$SCRIPT_DIR/animeitor_sounds_converted}"

mkdir -p "$OUTPUT_DIR"

find "$SOURCE_DIR" -type f \( -iname "*.wav" -o -iname "*.ogg" -o -iname "*.flac" -o -iname "*.aac" -o -iname "*.m4a" -o -iname "*.wma" -o -iname "*.mp3" \) | while read -r file; do
    rel="${file#$SOURCE_DIR/}"
    output="$OUTPUT_DIR/${rel%.*}.mp3"
    mkdir -p "$(dirname "$output")"
    echo "Converting: $file -> $output"
    "$FFMPEG" -y -i "$file" -q:a 2 "$output" -loglevel error < /dev/null
done

echo "Done."
