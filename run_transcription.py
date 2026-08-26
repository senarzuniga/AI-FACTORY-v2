#!/usr/bin/env python
"""Real transcription script using AudioTranscriptionService."""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add repo to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

from audio_transcription.service import AudioTranscriptionService

def verify_transcript_quality(transcript_txt: Path, job_duration: float | None, last_segment_end: float | None) -> dict:
    """Verify the transcript is real (not synthetic) and valid."""
    if not transcript_txt.exists():
        return {"valid": False, "reason": "Transcript file not found"}
    
    content = transcript_txt.read_text(encoding="utf-8").strip()
    if not content:
        return {"valid": False, "reason": "Transcript is empty"}
    
    # Check for synthetic patterns
    if "segment" in content.lower() and any(f"segment {i}" in content.lower() for i in range(100)):
        # Check if it's really synthetic (would have pattern like "audio_file segment 0", "audio_file segment 1", etc.)
        if content.count("segment") > len(content) / 100:  # Too many "segment" mentions
            return {"valid": False, "reason": "Transcript appears synthetic (too many segment markers)"}
    
    # Valid real transcription
    return {
        "valid": True,
        "size_bytes": len(content.encode("utf-8")),
        "char_count": len(content),
        "line_count": len(content.split("\n")),
        "preview": content[:200] if len(content) > 200 else content
    }

def verify_timestamp_monotonicity(segments: list[dict]) -> dict:
    """Verify timestamps are monotonic and non-empty text."""
    if not segments:
        return {"valid": False, "reason": "No segments"}
    
    prev_end = 0.0
    issues = []
    
    for i, seg in enumerate(segments):
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        text = str(seg.get("text", "")).strip()
        
        if not text:
            issues.append(f"Segment {i}: empty text")
        
        if start < prev_end:
            issues.append(f"Segment {i}: start ({start}s) < prev_end ({prev_end}s)")
        
        if end <= start:
            issues.append(f"Segment {i}: end ({end}s) <= start ({start}s)")
        
        prev_end = end
    
    if issues:
        return {"valid": False, "issues": issues}
    
    return {
        "valid": True,
        "segment_count": len(segments),
        "total_duration": max((float(seg.get("end", 0)) for seg in segments), default=0.0),
        "min_start": min((float(seg.get("start", 0)) for seg in segments), default=0.0),
    }

def main():
    # Determine audio file path
    preferred = Path("C:/Users/Inaki Senar/Documents/GitHub/AI-FACTORY-v2/audio_transcription/uploads/ui_uploads/reunión Enrique ayudas.m4a")
    fallback = Path("C:/Users/Inaki Senar/OneDrive/Attachments/reunión Enrique ayudas.m4a")
    
    audio_file = preferred if preferred.exists() else fallback
    if not audio_file.exists():
        print(f"ERROR: Audio file not found at {preferred} or {fallback}")
        sys.exit(1)
    
    audio_file = audio_file.resolve()
    print(f"SOURCE_PATH={audio_file}")
    
    # Create service
    service = AudioTranscriptionService()
    
    try:
        # Create transcription job
        job = service.create_job(
            audio_path=audio_file,
            language="auto",
            model_name="small"
        )
        print(f"JOB_ID={job.job_id}")
        
        # Run transcription
        job = service.transcribe_job(job)
        print(f"STATUS={job.status}")
        
        if job.status != "completed":
            error_msg = " | ".join(job.errors) if job.errors else "Unknown error"
            print(f"ERRORS={error_msg}")
            sys.exit(1)
        
        print(f"LANGUAGE={job.language}")
        print(f"MODEL={job.model}")
        print(f"DURATION={job.duration}")
        print(f"SEGMENT_COUNT={len(job.segments)}")
        
        # Persist outputs
        outputs = service.persist_outputs(job)
        transcript_path = outputs["txt"]
        summary_path = outputs["summary"]
        
        print(f"TRANSCRIPT_PATH={transcript_path}")
        print(f"SUMMARY_PATH={summary_path}")
        
        # Verify transcript quality
        transcript_content = transcript_path.read_text(encoding="utf-8")
        print(f"TRANSCRIPT_CHARS={len(transcript_content)}")
        
        preview = transcript_content[:150].replace("\n", " ")
        if len(transcript_content) > 150:
            preview += "..."
        print(f"TRANSCRIPT_PREVIEW={preview}")
        
        # Verify timestamp monotonicity
        ts_check = verify_timestamp_monotonicity(job.segments)
        if not ts_check["valid"]:
            print(f"ERRORS=Timestamp validation failed: {ts_check}")
            sys.exit(1)
        
        # Verify transcript is not synthetic
        quality_check = verify_transcript_quality(transcript_path, job.duration, 
                                                  max((float(seg.get("end", 0)) for seg in job.segments), default=0.0))
        if not quality_check["valid"]:
            print(f"ERRORS=Transcript quality check failed: {quality_check}")
            sys.exit(1)
        
        print("VERIFICATION_PASSED=YES")
        print("COMPLETION_TIME=" + datetime.now().isoformat())
        
    except Exception as e:
        print(f"ERRORS={type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
