#!/usr/bin/env python3
"""
Read-only comprehensive verification of audio transcription output.
Performs all specified checks without modifying any files.
"""

import json
import os
import sys
import re
import subprocess
from pathlib import Path

def main():
    job_dir = r'C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2\audio_transcription\output\job-55fdd018'
    json_file = os.path.join(job_dir, 'reunión Enrique ayudas.json')
    txt_file = os.path.join(job_dir, 'reunión Enrique ayudas_transcripcion.txt')

    print("=" * 80)
    print("FINAL VERIFICATION REPORT")
    print("=" * 80)

    # 1. Check output files present in job directory
    print("\n[1] OUTPUT FILES IN JOB DIRECTORY:")
    if os.path.isdir(job_dir):
        files = sorted(os.listdir(job_dir))
        print(f"    Total files: {len(files)}")
        for f in files:
            fpath = os.path.join(job_dir, f)
            if os.path.isfile(fpath):
                size = os.path.getsize(fpath)
                print(f"      - {f} ({size} bytes)")
            else:
                print(f"      - {f} (DIR)")
    else:
        print(f"    ERROR: Directory not found: {job_dir}")
        return 1

    # 2. Load and parse JSON
    print("\n[2] LOADING JSON FILE:")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"    OK: JSON loaded successfully")
    except Exception as e:
        print(f"    ERROR: {e}")
        return 1

    # 3. Load and parse TXT
    print("\n[3] LOADING TXT FILE:")
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            txt_content = f.read()
        print(f"    OK: TXT loaded")
        print(f"    Size: {len(txt_content)} chars, {len(txt_content.encode('utf-8'))} bytes")
    except Exception as e:
        print(f"    ERROR: {e}")
        return 1

    # 4. Extract metadata
    print("\n[4] SOURCE/MODEL/LANGUAGE/DURATION:")
    metadata = {
        'source': data.get('source', 'N/A'),
        'model': data.get('model', 'N/A'),
        'language': data.get('language', 'N/A'),
        'duration': data.get('duration', 'N/A'),
    }
    for key, val in metadata.items():
        print(f"    {key}: {val}")

    # 5. Segments and transcript analysis
    segments = data.get('segments', [])
    transcript_text = data.get('transcript', '')

    print(f"\n[5] SEGMENTS AND TRANSCRIPT:")
    print(f"    Total segments: {len(segments)}")
    print(f"    Transcript chars: {len(transcript_text)}")
    print(f"    Transcript bytes: {len(transcript_text.encode('utf-8'))}")

    # 6. Timestamp coverage analysis
    print(f"\n[6] TIMESTAMP COVERAGE ANALYSIS:")
    if segments:
        first_start = segments[0].get('start', None)
        last_end = segments[-1].get('end', None)
        print(f"    First segment start: {first_start}s")
        print(f"    Last segment end: {last_end}s")
        
        # Find segment covering/crossing 1800
        seg_1800 = None
        for i, seg in enumerate(segments):
            start = seg.get('start', float('inf'))
            end = seg.get('end', 0)
            if start <= 1800 <= end:
                seg_1800 = (i, seg)
                break
        
        if seg_1800:
            idx, seg = seg_1800
            print(f"    Segment covering 1800s: index {idx}, [{seg.get('start')}s-{seg.get('end')}s]")
        else:
            print(f"    Segment covering 1800s: NONE")
        
        # First start after 1800
        first_after_1800 = None
        for i, seg in enumerate(segments):
            if seg.get('start', 0) > 1800:
                first_after_1800 = (i, seg)
                break
        
        if first_after_1800:
            idx, seg = first_after_1800
            print(f"    First start after 1800s: index {idx}, starts at {seg.get('start')}s")
        else:
            print(f"    First start after 1800s: NONE")
    else:
        print(f"    (No segments)")

    # 7. JSON-to-TXT reconstruction check
    print(f"\n[7] JSON-TO-TXT RECONSTRUCTION CHECK:")
    reconstructed_lines = []
    for seg in segments:
        text = seg.get('text', '').strip()
        if text:
            reconstructed_lines.append(text)
    reconstructed_transcript = ' '.join(reconstructed_lines)

    if reconstructed_transcript == transcript_text:
        print(f"    OK: Perfect reconstruction match")
        reconstruction_ok = True
    else:
        print(f"    ERROR: Reconstruction mismatch")
        print(f"      Reconstructed length: {len(reconstructed_transcript)}")
        print(f"      Original length: {len(transcript_text)}")
        reconstruction_ok = False
        # Find first difference
        for i, (c1, c2) in enumerate(zip(reconstructed_transcript, transcript_text)):
            if c1 != c2:
                print(f"      First diff at pos {i}: got '{c1}', expected '{c2}'")
                break

    # 8. Timestamp validity
    print(f"\n[8] TIMESTAMP VALIDITY:")
    finite_err = []
    order_err = []
    for i, seg in enumerate(segments):
        start = seg.get('start')
        end = seg.get('end')
        
        if start is None or end is None:
            finite_err.append(f"      Segment {i}: missing start/end")
        elif not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            finite_err.append(f"      Segment {i}: non-numeric")
        elif start >= end:
            order_err.append(f"      Segment {i}: start={start} >= end={end}")

    timestamp_ok = True
    if finite_err:
        print(f"    ERROR: Non-finite/missing timestamps:")
        for e in finite_err:
            print(e)
        timestamp_ok = False
    else:
        print(f"    OK: All timestamps finite")

    if order_err:
        print(f"    ERROR: Invalid ranges (end <= start):")
        for e in order_err:
            print(e)
        timestamp_ok = False
    else:
        print(f"    OK: All end > start")

    # Check monotonic starts
    starts = [seg.get('start') for seg in segments if seg.get('start') is not None]
    monotonic = all(starts[i] <= starts[i+1] for i in range(len(starts)-1)) if len(starts) > 1 else True
    if monotonic:
        print(f"    OK: Starts monotonically increasing")
    else:
        print(f"    ERROR: Starts NOT monotonic")
        timestamp_ok = False

    # 9. Count overlaps
    print(f"\n[9] OVERLAPS:")
    overlaps = 0
    for i in range(len(segments)-1):
        curr_end = segments[i].get('end', 0)
        next_start = segments[i+1].get('start', float('inf'))
        if curr_end > next_start:
            overlaps += 1
    print(f"    Overlapping segment pairs: {overlaps}")

    # 10. Maximum consecutive identical normalized text
    print(f"\n[10] MAXIMUM CONSECUTIVE IDENTICAL NORMALIZED TEXT:")
    def normalize_text(text):
        return re.sub(r'\s+', ' ', text.lower().strip())

    max_consecutive = 0
    max_value = None
    current_normalized = None
    current_count = 0

    for seg in segments:
        text = seg.get('text', '')
        if not text.strip():
            if current_count > max_consecutive:
                max_consecutive = current_count
                max_value = current_normalized
            current_normalized = None
            current_count = 0
        else:
            norm = normalize_text(text)
            if norm == current_normalized:
                current_count += 1
            else:
                if current_count > max_consecutive:
                    max_consecutive = current_count
                    max_value = current_normalized
                current_normalized = norm
                current_count = 1

    if current_count > max_consecutive:
        max_consecutive = current_count
        max_value = current_normalized

    print(f"    Max consecutive: {max_consecutive}")
    if max_value:
        preview = max_value[:70] + ('...' if len(max_value) > 70 else '')
        print(f"    Value: '{preview}'")

    # 11. Maximum consecutive 'no.' (literal, case-insensitive)
    print(f"\n[11] MAXIMUM CONSECUTIVE NORMALIZED 'no.':")
    max_no = 0
    current_no_count = 0
    for seg in segments:
        text = seg.get('text', '').strip()
        if re.match(r'^no\.?$', text, re.IGNORECASE):
            current_no_count += 1
            max_no = max(max_no, current_no_count)
        else:
            current_no_count = 0
    print(f"    Max consecutive 'no.': {max_no}")

    # 12. Regex pattern check
    print(f"\n[12] REGEX PATTERN CHECK (?i)\\bsegment\\s+\\d+\\b:")
    pattern = re.compile(r'(?i)\bsegment\s+\d+\b')
    full_text = ' '.join([seg.get('text', '') for seg in segments])
    matches = pattern.findall(full_text)
    pattern_ok = True
    if matches:
        print(f"    ERROR: Pattern FOUND ({len(matches)} matches)")
        for m in matches[:5]:
            print(f"      '{m}'")
        pattern_ok = False
    else:
        print(f"    OK: Pattern not found")

    # 13. Last 10 nonempty segment texts
    print(f"\n[13] LAST 10 NONEMPTY SEGMENT TEXTS:")
    nonempty_segs = [seg.get('text', '').strip() for seg in segments if seg.get('text', '').strip()]
    start_idx = max(0, len(nonempty_segs) - 10)
    for i, text in enumerate(nonempty_segs[start_idx:], start=start_idx):
        preview = text[:70] + ('...' if len(text) > 70 else '')
        print(f"      [{i}] {preview}")

    # 14. FFprobe source duration comparison
    print(f"\n[14] SOURCE FILE FFPROBE COMPARISON:")
    source_path = metadata['source']
    ffprobe_ok = True
    if source_path and source_path != 'N/A':
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1', source_path],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                ffprobe_duration = float(result.stdout.strip())
                json_duration = float(metadata['duration']) if metadata['duration'] != 'N/A' else None
                print(f"    FFprobe: {ffprobe_duration:.3f}s")
                if json_duration:
                    print(f"    JSON: {json_duration:.3f}s")
                    diff = abs(ffprobe_duration - json_duration)
                    if diff < 0.1:
                        print(f"    OK: Durations match (diff={diff:.3f}s)")
                    else:
                        print(f"    WARNING: Diff={diff:.3f}s")
            else:
                print(f"    WARNING: FFprobe error: {result.stderr[:200]}")
        except Exception as e:
            print(f"    WARNING: FFprobe failed: {str(e)[:200]}")
    else:
        print(f"    Source not specified")

    # FINAL VERDICT
    print("\n" + "=" * 80)
    print("FINAL VERDICT:")
    exit_code = 0

    if not reconstruction_ok:
        print("  FAIL: JSON-to-TXT reconstruction mismatch")
        exit_code = 1

    if not timestamp_ok:
        print("  FAIL: Timestamp validity check")
        exit_code = 1

    if not pattern_ok:
        print("  FAIL: Regex pattern found in transcript")
        exit_code = 1

    if overlaps > 0:
        print(f"  WARNING: {overlaps} overlapping segment pairs")

    if exit_code == 0:
        print("  SUCCESS: All critical checks passed")

    print("=" * 80)
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
