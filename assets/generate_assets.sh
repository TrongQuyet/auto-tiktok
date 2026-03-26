#!/bin/bash
# Generate royalty-free BGM and SFX using FFmpeg's built-in synthesizer
# These are simple generated tones/beats - no copyright issues

BGM_DIR="$(dirname "$0")/bgm"
SFX_DIR="$(dirname "$0")/sfx"
mkdir -p "$BGM_DIR" "$SFX_DIR"

echo "Generating BGM..."

# Dramatic - low bass drone with slow pulse
ffmpeg -y -f lavfi -i "sine=frequency=80:duration=30" -f lavfi -i "sine=frequency=120:duration=30" \
  -filter_complex "[0][1]amix=inputs=2:duration=longest,volume=0.3,atempo=1.0" \
  "$BGM_DIR/dramatic.mp3" 2>/dev/null

# Lo-fi - warm sine waves layered
ffmpeg -y -f lavfi -i "sine=frequency=220:duration=30" -f lavfi -i "sine=frequency=330:duration=30" -f lavfi -i "sine=frequency=440:duration=30" \
  -filter_complex "[0][1][2]amix=inputs=3:duration=longest,volume=0.2,lowpass=f=800" \
  "$BGM_DIR/lofi.mp3" 2>/dev/null

# Upbeat - faster rhythm with higher frequencies
ffmpeg -y -f lavfi -i "sine=frequency=440:duration=30" -f lavfi -i "sine=frequency=554:duration=30" \
  -filter_complex "[0][1]amix=inputs=2:duration=longest,volume=0.25,tremolo=f=4:d=0.5" \
  "$BGM_DIR/upbeat.mp3" 2>/dev/null

# Calm - soft ambient tone
ffmpeg -y -f lavfi -i "sine=frequency=174:duration=30" -f lavfi -i "sine=frequency=261:duration=30" \
  -filter_complex "[0][1]amix=inputs=2:duration=longest,volume=0.15,lowpass=f=500" \
  "$BGM_DIR/calm.mp3" 2>/dev/null

echo "Generating SFX..."

# Woosh - quick frequency sweep
ffmpeg -y -f lavfi -i "sine=frequency=200:duration=0.4" \
  -af "volume=0.5,afade=t=in:st=0:d=0.1,afade=t=out:st=0.2:d=0.2,asetrate=44100*1.5,atempo=0.8" \
  "$SFX_DIR/woosh.mp3" 2>/dev/null

# Ding - bright bell sound
ffmpeg -y -f lavfi -i "sine=frequency=1200:duration=0.5" \
  -af "volume=0.4,afade=t=out:st=0.1:d=0.4" \
  "$SFX_DIR/ding.mp3" 2>/dev/null

# Boom - low impact
ffmpeg -y -f lavfi -i "sine=frequency=60:duration=0.6" \
  -af "volume=0.6,afade=t=in:st=0:d=0.05,afade=t=out:st=0.1:d=0.5" \
  "$SFX_DIR/boom.mp3" 2>/dev/null

# Transition - soft whoosh
ffmpeg -y -f lavfi -i "sine=frequency=400:duration=0.3" \
  -af "volume=0.3,afade=t=in:st=0:d=0.05,afade=t=out:st=0.1:d=0.2,lowpass=f=2000" \
  "$SFX_DIR/transition.mp3" 2>/dev/null

echo "Assets generated!"
ls -la "$BGM_DIR" "$SFX_DIR"
