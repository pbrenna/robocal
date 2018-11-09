#!/bin/bash
OGGI=$(date '+%Y-%m-%dT%H.%M')
ffmpeg -i "http://icestreaming.rai.it/3.mp3" "$OGGI"" $3.ogg" -y
