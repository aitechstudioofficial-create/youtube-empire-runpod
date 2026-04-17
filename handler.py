import runpod
import os
import random
import subprocess

TRACKS_BASE = "/runpod-volume/music/tracks"
LOOPS_DIR   = "/runpod-volume/music/loops"
OUTPUT_DIR  = "/runpod-volume/outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def handler(job):
    try:
        input_data = job["input"]
        frequency  = str(input_data.get("frequency", "432"))
        duration   = int(input_data.get("duration", 60))
        job_id     = job.get("id", "test")

        track_folder = os.path.join(TRACKS_BASE, f"PRE {frequency}")
        tracks = [f for f in os.listdir(track_folder) if f.endswith(".mp3")]
        track_file = os.path.join(track_folder, random.choice(tracks))

        loops = [f for f in os.listdir(LOOPS_DIR) if f.endswith(".mp4")]
        loop_file = os.path.join(LOOPS_DIR, random.choice(loops))

        output_file = os.path.join(OUTPUT_DIR, f"rms_{frequency}hz_{duration}sec_{job_id}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", loop_file,
            "-i", track_file,
            "-map", "0:v",
            "-map", "1:a",
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr[-500:]}

        return {
            "status": "success",
            "output_file": output_file,
            "track_used": os.path.basename(track_file),
            "loop_used": os.path.basename(loop_file),
            "frequency": frequency,
            "duration": duration,
            "file_size_mb": round(os.path.getsize(output_file) / 1024 / 1024, 2)
        }

    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
