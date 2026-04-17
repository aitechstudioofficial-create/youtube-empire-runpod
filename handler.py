def handler(job):
    try:
        input_data = job["input"]
        frequency  = str(input_data.get("frequency", "432"))
        duration   = int(input_data.get("duration", 60))
        job_id     = job.get("id", "test")

        # Debug — find actual paths
        debug = {}
        if os.path.exists("/runpod-volume"):
            debug["volume"] = os.listdir("/runpod-volume")
            if os.path.exists("/runpod-volume/music"):
                debug["music"] = os.listdir("/runpod-volume/music")
                if os.path.exists("/runpod-volume/music/tracks"):
                    debug["tracks"] = os.listdir("/runpod-volume/music/tracks")
        
        return {"debug": debug}
