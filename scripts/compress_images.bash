#!/bin/bash

command -v optipng >/dev/null 2>&1 || { echo "Running compress_images requires: optipng.  Aborting." >&2; exit 1; }
command -v svgo >/dev/null 2>&1 || { echo "Running compress_images requires: svgo.  Aborting." >&2; exit 1; }
command -v jpeg-recompress >/dev/null 2>&1 || { echo "Running compress_images requires: jpeg-recompress.  Aborting." >&2; exit 1; }

cd app/assets/ || { echo "Environment misconfigured! Couldn't find assets directory!" >&2; exit 1; }

echo "Optimizing project images...  This might take a while..."
echo "Optimizing PNG files..."
find ./ -type f -name '*.png' -exec optipng -o4 {} \;

echo "Squashing SVG files..."
find ./ -type f -name '*.svg' -exec svgo {} \;

echo "Compressing JPG files..."
find ./ -type f -name '*.jpg' -exec jpeg-recompress -a -s -c {} {} \;

echo "Image processing completed!"
