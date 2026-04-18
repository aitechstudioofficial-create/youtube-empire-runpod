import runpod
import os
import random
import subprocess
import boto3
from botocore.client import Config

TRACKS_BASE = "/runpod-volume/music/tracks"
LOOPS_DIR   = "/runpod-volume/music/loops"
OUTPUT_DIR  = "/runpod-volume/outputs"

# S3 Configuration
S3_ENDPOINT  = "https://s3api-us-nc-1.runpod.io"
S3_BUCKET    = "7v3iptl9ep"
S3_REGION    = "us-nc-1"
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def upload_to_s3(file_path, file_name):
    s3 = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
        config=Config(signature_version="s3v4")
    )
    s3_key = f"outputs/{file_name}"
    s3.upload_file(file_path, S3_BUCKET, s3_key)
    url = f"{S3_ENDPOINT}/{S3_BUCKET}/{s3_key}"
    return url

def handler(job):
    try:
        input_data = job["input"]
        frequency  = str(input_data.get("frequency", "432"))
        duration   = int(input_data.get("duration", 60))
        job_id     = job.get("id", "test")

        track_folder = os.path.join(TRACKS_BASE, frequency)

        if not os.path.exists(track_folder):
            return {"error": f"Not found: {track_folder}"}

        tracks = [f for f in os.listdir(track_folder) if f.endswith(".mp3")]
        if not tracks:
            return {"error": f"No MP3 in {track_folder}"}

        track_file = os.path.join(track_folder, random.choice(tracks))

        loops = [f for f in os.listdir(LOOPS_DIR) if f.endswith(".mp4")]
        if not loops:
            return {"error": "No loops found"}

        loop_file = os.path.join(LOOPS_DIR, random.choice(loops))

        output_file = os.path.join(OUTPUT_DIR, f"rms_{frequency}hz_{duration}sec_{job_id}.mp4")
        file_name   = f"rms_{frequency}hz_{duration}sec_{job_id}.mp4"

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

        # Upload to S3
        s3_url = upload_to_s3(output_file, file_name)

        return {
            "status": "success",
            "output_file": output_file,
            "s3_url": s3_url,
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
