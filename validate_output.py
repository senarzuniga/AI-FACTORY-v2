#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import os
import sys
from pathlib import Path
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
base_dir = r"C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2"
json_file = os.path.join(base_dir, r"audio_transcription\output\job-7ccc6c8e\reunión Enrique ayudas.json")
txt_file = os.path.join(base_dir, r"audio_transcription\output\job-7ccc6c8e\reunión Enrique ayudas_transcripcion.txt")
audio_file = r"C:\Users\Inaki Senar\OneDrive\Attachments\reunión Enrique ayudas.m4a"

print("=" * 80)
print("FILE EXISTENCE CHECK")
print("=" * 80)
json_exists = os.path.isfile(json_file)
txt_exists = os.path.isfile(txt_file)
print(f"JSON file exists: {json_exists} ({json_file})")
print(f"TXT file exists: {txt_exists} ({txt_file})")
print(f"Audio file exists: {os.path.isfile(audio_file)} ({audio_file})")
print()

if not (json_exists and txt_exists):
    print("ERROR: Required files do not exist!")
    sys.exit(1)

# Load files
print("=" * 80)
print("LOADING FILES")
print("=" * 80)
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"✓ Loaded JSON: {json_file}")

with open(txt_file, 'r', encoding='utf-8') as f:
    transcript_text = f.read()
print(f"✓ Loaded TXT: {txt_file}")
print()

# Transcript byte size and character count
print("=" * 80)
print("TRANSCRIPT METRICS")
print("=" * 80)
txt_bytes = len(transcript_text.encode('utf-8'))
txt_chars = len(transcript_text)
print(f"Byte size: {txt_bytes}")
print(f"Character count: {txt_chars}")
print()

# JSON metadata
print("=" * 80)
print("JSON METADATA")
print("=" * 80)
print(f"Language: {data.get('language', 'N/A')}")
print(f"Model: {data.get('model', 'N/A')}")
print(f"Duration: {data.get('duration', 'N/A')}")
print()

# Segment validation
print("=" * 80)
print("SEGMENT VALIDATION")
print("=" * 80)
segments = data.get('segments', [])
segment_count = len(segments)
print(f"Segment count: {segment_count}")
print()

if segment_count > 0:
    first_start = segments[0].get('start')
    last_end = segments[-1].get('end')
    print(f"First start: {first_start}")
    print(f"Last end: {last_end}")
    print()
    
    # Check all segment texts nonempty
    print("Checking segment texts nonempty...")
    empty_segments = []
    for i, seg in enumerate(segments):
        if not seg.get('text', '').strip():
            empty_segments.append(i)
    if empty_segments:
        print(f"WARNING: Empty text in segments: {empty_segments}")
    else:
        print(f"✓ All {segment_count} segments have nonempty text")
    print()
    
    # Check timestamps finite and end > start
    print("Checking timestamps...")
    bad_timestamps = []
    for i, seg in enumerate(segments):
        start = seg.get('start')
        end = seg.get('end')
        if start is None or end is None:
            bad_timestamps.append((i, 'missing'))
        elif not (isinstance(start, (int, float)) and isinstance(end, (int, float))):
            bad_timestamps.append((i, 'not numeric'))
        elif start == float('inf') or end == float('inf') or start == float('-inf') or end == float('-inf'):
            bad_timestamps.append((i, 'infinite'))
        elif end <= start:
            bad_timestamps.append((i, f'end({end}) <= start({start})'))
    if bad_timestamps:
        print(f"WARNING: Bad timestamps in segments: {bad_timestamps}")
    else:
        print(f"✓ All timestamps valid (finite, end > start)")
    print()
    
    # Check starts monotonic
    print("Checking start monotonicity...")
    overlaps = []
    non_monotonic = []
    for i in range(1, len(segments)):
        prev_start = segments[i-1].get('start')
        prev_end = segments[i-1].get('end')
        curr_start = segments[i].get('start')
        if curr_start is not None and prev_start is not None:
            if curr_start < prev_start:
                non_monotonic.append((i-1, i, f"prev_start={prev_start}, curr_start={curr_start}"))
        if curr_start is not None and prev_end is not None:
            if curr_start < prev_end:
                overlaps.append((i-1, i, f"prev_end={prev_end}, curr_start={curr_start}"))
    if non_monotonic:
        print(f"ERROR: Non-monotonic starts: {non_monotonic}")
    else:
        print(f"✓ Starts are monotonic")
    if overlaps:
        print(f"Overlapping segments: {len(overlaps)} overlaps")
        for o in overlaps[:5]:
            print(f"  Segments {o[0]}-{o[1]}: {o[2]}")
        if len(overlaps) > 5:
            print(f"  ... and {len(overlaps)-5} more")
    else:
        print(f"✓ No overlapping segments")
    print()

# Transcript reconstruction
print("=" * 80)
print("TRANSCRIPT RECONSTRUCTION")
print("=" * 80)
reconstructed = '\n\n'.join(seg.get('text', '') for seg in segments if seg.get('text', '').strip())
matches = (reconstructed == transcript_text)
print(f"Transcript matches reconstructed: {matches}")
if not matches:
    print(f"  Reconstructed length: {len(reconstructed)}")
    print(f"  Original length: {len(transcript_text)}")
    # Find first difference
    min_len = min(len(reconstructed), len(transcript_text))
    for idx in range(min_len):
        if reconstructed[idx] != transcript_text[idx]:
            print(f"  First difference at index {idx}: reconstructed={repr(reconstructed[idx])}, original={repr(transcript_text[idx])}")
            break
    else:
        if len(reconstructed) != len(transcript_text):
            print(f"  Lengths differ: reconstructed={len(reconstructed)}, original={len(transcript_text)}")
print()

# Regex check
print("=" * 80)
print("REGEX CHECK: (?i)\\bsegment\\s+\\d+\\b")
print("=" * 80)
pattern = re.compile(r'(?i)\bsegment\s+\d+\b')
matches = pattern.findall(transcript_text)
if matches:
    print(f"ERROR: Pattern found {len(matches)} times: {matches[:5]}")
else:
    print(f"✓ Pattern not found in transcript")
print()

# ffprobe check
print("=" * 80)
print("AUDIO FILE FFPROBE")
print("=" * 80)
if os.path.isfile(audio_file):
    import subprocess
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_format', '-show_streams', 
             '-of', 'json', audio_file],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            audio_data = json.loads(result.stdout)
            if 'format' in audio_data:
                duration = float(audio_data['format'].get('duration', 'N/A'))
                print(f"Audio duration: {duration} seconds")
            print(f"✓ ffprobe succeeded")
        else:
            print(f"ffprobe error (code {result.returncode}): {result.stderr}")
    except FileNotFoundError:
        print("ffprobe not found in PATH")
    except Exception as e:
        print(f"Error running ffprobe: {e}")
else:
    print(f"Audio file not found: {audio_file}")

print()
print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
