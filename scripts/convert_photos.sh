#!/usr/bin/env bash

CWEBP="${CWEBP:-cwebp}"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIR="${1:-$SCRIPT_DIR/animeitor}"
OUTPUT_DIR="${2:-$SCRIPT_DIR/animeitor_photos_converted}"

mkdir -p "$OUTPUT_DIR"

find "$SOURCE_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | while read -r file; do
    rel="${file#$SOURCE_DIR/}"
    output="$OUTPUT_DIR/${rel%.*}.webp"
    mkdir -p "$(dirname "$output")"
    echo "Converting: $file -> $output"
    "$CWEBP" -quiet "$file" -o "$output"
done

echo "Done."
