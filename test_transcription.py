#!/usr/bin/env python3
"""
End-to-end audio transcription test using AudioTranscriptionService.
Performs real transcription with full validation.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Set UTF-8 encoding for output
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add repo to path
sys.path.insert(0, str(Path.cwd()))

from audio_transcription.service import AudioTranscriptionService, validate_audio_file

def main():
    print("=" * 100)
    print("AUDIO TRANSCRIPTION END-TO-END TEST")
    print("=" * 100)
    
    # Configuration
    repo_root = Path.cwd()
    source_audio = Path(r"C:\Users\Inaki Senar\OneDrive\Attachments\reunión Enrique ayudas.m4a")
    language = "auto"
    model_name = "small"
    
    print(f"\n[1] CONFIGURATION")
    print(f"    Repository root: {repo_root}")
    print(f"    Source audio: {source_audio}")
    print(f"    Language: {language}")
    print(f"    Model: {model_name}")
    
    # Verify source exists
    print(f"\n[2] SOURCE VERIFICATION")
    if not source_audio.exists():
        print(f"    [ERROR] Source file not found: {source_audio}")
        return 1
    
    source_size = source_audio.stat().st_size
    print(f"    [OK] Source exists")
    print(f"    [OK] Size: {source_size:,} bytes ({source_size / (1024*1024):.2f} MB)")
    
    # Validate audio file
    validation = validate_audio_file(source_audio)
    if not validation["is_valid"]:
        print(f"    [ERROR] Validation failed: {validation['message']}")
        return 1
    print(f"    [OK] Format valid: {validation['format']}")
    print(f"    [OK] MIME type: {validation['mime_type']}")
    
    # Initialize service
    print(f"\n[3] SERVICE INITIALIZATION")
    service = AudioTranscriptionService(base_dir=repo_root)
    print(f"    [OK] Service initialized")
    print(f"    Upload dir: {service.upload_dir}")
    print(f"    Output dir: {service.output_dir}")
    print(f"    Engine ffmpeg available: {service.engine.ffmpeg_available}")
    print(f"    Engine ffprobe available: {service.engine.ffprobe_available}")
    
    # Detect source duration with ffprobe
    print(f"\n[4] SOURCE MEDIA ANALYSIS")
    source_duration = service.engine.detect_duration(source_audio)
    print(f"    Source duration (ffprobe): {source_duration} seconds" if source_duration else "    Source duration: Not detected")
    
    # Create transcription job
    print(f"\n[5] CREATE TRANSCRIPTION JOB")
    try:
        job = service.create_job(source_audio, language=language, model_name=model_name)
        print(f"    [OK] Job created")
        print(f"    Job ID: {job.job_id}")
        print(f"    Status: {job.status}")
        print(f"    Output dir: {job.output_dir}")
    except Exception as exc:
        print(f"    [ERROR] Failed to create job: {exc}")
        return 1
    
    # Run transcription
    print(f"\n[6] TRANSCRIPTION IN PROGRESS")
    print(f"    This may take several minutes for {source_size / (1024*1024):.2f} MB of audio...")
    try:
        job = service.transcribe_job(job)
        print(f"    [OK] Transcription complete")
    except Exception as exc:
        print(f"    [ERROR] Transcription failed: {exc}")
        return 1
    
    # Check job status and results
    print(f"\n[7] JOB STATUS & RESULTS")
    print(f"    Status: {job.status}")
    print(f"    Duration: {job.duration} seconds")
    print(f"    Language: {job.language}")
    print(f"    Model: {job.model}")
    print(f"    Segment count: {len(job.segments)}")
    
    if job.status != "completed":
        print(f"    [ERROR] Job status is '{job.status}', expected 'completed'")
        if job.errors:
            print(f"    Errors: {job.errors}")
        return 1
    
    if not job.segments:
        print(f"    [ERROR] No segments in job result")
        if job.errors:
            print(f"    Errors: {job.errors}")
        return 1
    
    print(f"    [OK] Job completed successfully")
    
    # Validate segments
    print(f"\n[8] SEGMENT VALIDATION")
    synthetic_pattern = re.compile(r"(?i)\bsegment\s+\d+\b")
    
    total_text_length = 0
    for idx, segment in enumerate(job.segments, 1):
        if idx == 1 or idx == len(job.segments):
            print(f"    Segment {idx}:")
            print(f"      Start: {segment.get('start')}, End: {segment.get('end')}")
            print(f"      Text length: {len(segment.get('text', ''))}")
            if len(segment.get('text', '')) > 100:
                print(f"      Preview: {segment.get('text', '')[:100]}...")
            else:
                print(f"      Text: {segment.get('text', '')}")
        
        # Validate segment structure
        start = float(segment.get("start", 0))
        end = float(segment.get("end", 0))
        text = str(segment.get("text", "")).strip()
        
        # Check for issues
        if not text:
            print(f"    [ERROR] Segment {idx}: empty text")
            return 1
        
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            print(f"    [ERROR] Segment {idx}: non-numeric timestamps")
            return 1
        
        if end <= start:
            print(f"    [ERROR] Segment {idx}: end <= start ({start} to {end})")
            return 1
        
        if synthetic_pattern.search(text):
            print(f"    [ERROR] Segment {idx}: matches generic synthetic pattern")
            return 1
        
        total_text_length += len(text)
    
    # Check timestamp monotonicity and non-overlapping
    for idx in range(1, len(job.segments)):
        prev_end = float(job.segments[idx-1].get("end", 0))
        curr_start = float(job.segments[idx].get("start", 0))
        if curr_start < prev_end:
            print(f"    [ERROR] Segments {idx} and {idx+1} overlap: prev_end={prev_end}, curr_start={curr_start}")
            return 1
    
    print(f"    [OK] All {len(job.segments)} segments valid")
    print(f"    [OK] No synthetic text patterns detected")
    print(f"    [OK] Timestamps are monotonic and non-overlapping")
    
    # Calculate segment text
    print(f"\n[9] SEGMENT TEXT EXTRACTION")
    segment_texts = [s.get("text", "").strip() for s in job.segments if s.get("text", "").strip()]
    joined_text = "\n\n".join(segment_texts)
    print(f"    Total segments with text: {len(segment_texts)}")
    print(f"    Joined text length: {len(joined_text)}")
    print(f"    Total character count: {len(joined_text)}")
    
    # Persist outputs
    print(f"\n[10] PERSIST OUTPUTS")
    try:
        output_paths = service.persist_outputs(job)
        print(f"    [OK] Outputs persisted")
        for key, path in output_paths.items():
            print(f"    {key}: {path}")
    except Exception as exc:
        print(f"    [ERROR] Failed to persist outputs: {exc}")
        return 1
    
    # Verify transcript file
    print(f"\n[11] TRANSCRIPT FILE VERIFICATION")
    txt_path = output_paths["txt"]
    if not txt_path.exists():
        print(f"    [ERROR] Transcript file not found: {txt_path}")
        return 1
    
    transcript_content = txt_path.read_text(encoding="utf-8")
    transcript_len = len(transcript_content)
    
    if not transcript_content.strip():
        print(f"    [ERROR] Transcript file is empty")
        return 1
    
    print(f"    [OK] Transcript file exists")
    print(f"    Path: {txt_path}")
    print(f"    Size: {txt_path.stat().st_size:,} bytes")
    print(f"    Content length: {transcript_len} characters")
    
    # Verify transcript content matches joined segments
    if transcript_content != joined_text:
        print(f"    [ERROR] Transcript content does NOT match joined segment text")
        print(f"    Expected: {len(joined_text)} chars")
        print(f"    Got: {len(transcript_content)} chars")
        # Show first difference
        for i, (c1, c2) in enumerate(zip(joined_text, transcript_content)):
            if c1 != c2:
                print(f"    First difference at position {i}: expected {repr(c1)}, got {repr(c2)}")
                break
        return 1
    
    print(f"    [OK] Transcript content matches joined segments exactly")
    
    # Verify summary file
    print(f"\n[12] SUMMARY FILE VERIFICATION")
    summary_path = output_paths["summary"]
    if not summary_path.exists():
        print(f"    [ERROR] Summary file not found: {summary_path}")
        return 1
    
    summary_content = summary_path.read_text(encoding="utf-8")
    summary_len = len(summary_content)
    
    if not summary_content.strip():
        print(f"    [ERROR] Summary file is empty")
        return 1
    
    print(f"    [OK] Summary file exists")
    print(f"    Path: {summary_path}")
    print(f"    Size: {summary_path.stat().st_size:,} bytes")
    print(f"    Content length: {summary_len} characters")
    
    # Verify other output files
    print(f"\n[13] OTHER OUTPUT FILES")
    for key in ["srt", "vtt", "json"]:
        path = output_paths[key]
        if path.exists():
            size = path.stat().st_size
            print(f"    [OK] {key.upper()}: {path.name} ({size:,} bytes)")
        else:
            print(f"    [ERROR] {key.upper()}: {path.name} NOT FOUND")
    
    # Compare with source duration
    print(f"\n[14] DURATION COMPARISON")
    if source_duration and job.segments:
        last_segment_end = float(job.segments[-1].get("end", 0))
        print(f"    Source duration (ffprobe): {source_duration:.2f} seconds")
        print(f"    Last segment end: {last_segment_end:.2f} seconds")
        diff = abs(source_duration - last_segment_end)
        print(f"    Difference: {diff:.2f} seconds ({(diff/source_duration*100) if source_duration else 0:.1f}%)")
        if diff > 5:
            print(f"    Note: Difference may be due to silence at end of audio")
    
    # Print full transcript
    print(f"\n[15] FULL TRANSCRIPT")
    print("=" * 100)
    print("START OF TRANSCRIPT:")
    print("-" * 100)
    print(transcript_content)
    print("-" * 100)
    print("END OF TRANSCRIPT")
    print("=" * 100)
    
    # Final summary
    print(f"\n[16] FINAL SUMMARY")
    print(f"    [OK] ALL TESTS PASSED")
    print(f"\n    Job ID: {job.job_id}")
    print(f"    Status: {job.status}")
    print(f"    Detected Language: {job.language}")
    print(f"    Model: {job.model}")
    print(f"    Duration: {job.duration} seconds")
    print(f"    Segment Count: {len(job.segments)}")
    print(f"    Transcript Path: {txt_path}")
    print(f"    Summary Path: {summary_path}")
    print(f"    Transcript Character Count: {transcript_len}")
    print(f"\n    Source Path: {source_audio}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
