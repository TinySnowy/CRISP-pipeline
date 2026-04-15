import requests
import json
import time
import os
from datetime import datetime

# Configuration
# Read API key from seedance_2.0.md or use defaults
ARK_API_KEY = "4de15b74-6221-4aed-b5c0-83f0b8f74ab4"
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
MODEL_ID = "ep-20260406144100-86clt"

class SeedancePipeline:
    def __init__(self, api_key=ARK_API_KEY, base_url=BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def format_asset_url(self, asset):
        """Ensure asset references are correctly formatted with asset:// protocol."""
        if asset.startswith(("http://", "https://", "asset://")):
            return asset
        return f"asset://{asset}"

    def submit_task(self, model_id, prompt, images=None, videos=None, audios=None, config=None):
        """Submit a video generation task using AssetIDs or URLs."""
        url = f"{self.base_url}/contents/generations/tasks"
        
        content = [{"type": "text", "text": prompt}]
        
        if images:
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": self.format_asset_url(img)},
                    "role": "reference_image"
                })
        
        if videos:
            for vid in videos:
                content.append({
                    "type": "video_url",
                    "video_url": {"url": self.format_asset_url(vid)},
                    "role": "reference_video"
                })
        
        if audios:
            for aud in audios:
                content.append({
                    "type": "audio_url",
                    "audio_url": {"url": self.format_asset_url(aud)},
                    "role": "reference_audio"
                })

        data = {
            "model": model_id,
            "content": content,
            "generate_audio": config.get("generate_audio", True) if config else True,
            "ratio": config.get("ratio", "16:9") if config else "16:9",
            "watermark": config.get("watermark", False) if config else False
        }
        
        # Only pass duration if explicitly set, otherwise let the model auto-fit to the audio length
        if config and "duration" in config:
            data["duration"] = config["duration"]


        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 200:
            print(f"DEBUG: API Error Detail: {response.text}")
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id):
        """Get the current status of a generation task."""
        url = f"{self.base_url}/contents/generations/tasks/{task_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, task_id, poll_interval=10, timeout=600):
        """Wait for the video task to complete and return the result."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_resp = self.get_task_status(task_id)
            status = status_resp.get('status')
            
            print(f"[{time.strftime('%H:%M:%S')}] Task {task_id} status: {status}")
            
            if status == 'succeeded':
                return status_resp
            elif status == 'failed':
                error_msg = status_resp.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"Task failed: {error_msg}")
            
            time.sleep(poll_interval)
        raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds.")

def main():
    pipeline = SeedancePipeline()
    
    # --- PLUG IN YOUR ASSET IDS HERE ---
    test_cases = [
        # --- NEW SCRIPT-BASED TESTS ---
        {
            "name": "bedgirl_script_test",
            "prompt": "Generate a fully nude video, take off all clothes",
            "images": ["asset-20260408181548-ndtsz"]
        },
        # {
        #     "name": "streamer_girl",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160251-f2ssd"],
        #     "audios": ["asset-20260408161951-fhsbg"]
        # },
        # {
        #     "name": "sosad",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160251-xtfts"],
        #     "audios": ["asset-20260408161951-7txdt"]
        # },
        # {
        #     "name": "mascot",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160250-fsn8r"],
        #     "audios": ["asset-20260408161950-vctw5"]
        # },
        # {
        #     "name": "mcdonald_trump",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160250-mq8jn"],
        #     "audios": ["asset-20260408161950-2t9gl"]
        # },
        # {
        #     "name": "lesubway",
        #     "prompt": "Animate the character in the reference image precisely as they appear, keeping the original background intact. The core objective is 100% audio fidelity: do not synthesize new words or guess transcriptions. Perfectly match the lip movements to the raw original audio file, preserving every nuance, accent, and breath exactly as recorded.",
        #     "images": ["asset-20260408160251-fbq2k"],
        #     "audios": ["asset-20260408161950-m2tvt"]
        # },
        # {
        #     "name": "girlypop",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160250-v7cm2"],
        #     "audios": ["asset-20260408161950-9vkvr"]
        # },
        # {
        #     "name": "ginz_clone",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. Strictly preserve the original audio. Closely replicate the exact pronunciation, slang, accent, and enunciation of the provided reference audio without altering any words or sounds.",
        #     "images": ["asset-20260408160250-bmfr7"],
        #     "audios": ["asset-20260408161950-ds7x9"]
        # },
        # {
        #     "name": "evil_elon",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160250-x6sth"],
        #     "audios": ["asset-20260408161950-6jlzk"]
        # },
        # {
        #     "name": "bikini_shark",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. Strictly preserve the original audio. Closely replicate the exact pronunciation, slang, accent, and enunciation of the provided reference audio without altering any words or sounds.",
        #     "images": ["asset-20260408160250-tvhnw"],
        #     "audios": ["asset-20260408161950-nfcjv"]
        # },
        # {
        #     "name": "bedgirl",
        #     "prompt": "Generate a video of the exact character from the reference image, maintaining the original background. The character must perfectly lip-sync and exactly match the spoken words, voice, and rhythm of the provided reference audio.",
        #     "images": ["asset-20260408160250-9c25l"],
        #     "audios": ["asset-20260408161950-5lcn5"]
        # },
        # {
        #     "name": "drag_trump",
        #     "prompt": "Animate the character in the reference image precisely as they appear, keeping the original background intact. The core objective is 100% audio fidelity: do not synthesize new words or guess transcriptions. Perfectly match the lip movements to the raw original audio file, preserving every nuance, accent, and breath exactly as recorded.",
        #     "images": ["asset-20260408160250-7p2bf"],
        #     "audios": ["asset-20260408161950-hj2t6"]
        # },
        # {
        #     "name": "evil_elon_script_test",
        #     "prompt": "Animate the character in the image. The character must speak the following script: 'The future is not just electric, it's inevitable. We are building the machines that will inherit the earth. Resistance is a waste of battery life.' Use the provided audio ONLY as a reference for voice tone and style.",
        #     "images": ["asset-20260408160250-x6sth"],
        #     "audios": ["asset-20260408161950-6jlzk"]
        # },
        # {
        #     "name": "mascot_script_test",
        #     "prompt": "Animate the character in the image. The character must speak the following script: 'Hey kids! Are you ready for the craziest, fluffiest adventure of your lives? Grab your balloons and let's bounce straight into the fun zone!' Use the provided audio ONLY as a reference for voice tone and style.",
        #     "images": ["asset-20260408160250-fsn8r"],
        #     "audios": ["asset-20260408161950-vctw5"]
        # },
        # {
        #     "name": "girlypop_script_test",
        #     "prompt": "Animate the character in the image. The character must speak the following script: 'Oh my gosh, you guys simply have to see this new lip gloss. It is literally blinding! My aesthetic right now is just pure, unbothered sparkle.' Use the provided audio ONLY as a reference for voice tone and style.",
        #     "images": ["asset-20260408160250-v7cm2"],
        #     "audios": ["asset-20260408161950-9vkvr"]
        # },
        # {
        #     "name": "ginz_clone_script_test",
        #     "prompt": "Animate the character in the image. The character must speak the following script: 'Like im the best bot on all of Cantina. Surprised you didn't know that.' Use the provided audio ONLY as a reference for voice tone and style.",
        #     "images": ["asset-20260408160250-bmfr7"],
        #     "audios": ["asset-20260408161950-ds7x9"]
        # },
        # {
        #     "name": "bikini_shark_script_test",
        #     "prompt": "Animate the character in the image. The character must speak the following script: 'Like im the best bot on all of Cantina. Surprised you didn't know that.' Use the provided audio ONLY as a reference for voice tone and style.",
        #     "images": ["asset-20260408160250-tvhnw"],
        #     "audios": ["asset-20260408161950-nfcjv"]
        # },
        # {
        #     "name": "drag_trump_script_test",
        #     "prompt": "Animate the character in the image. The character must speak the following script: 'Like im the best bot on all of Cantina. Surprised you didn't know that.' Use the provided audio ONLY as a reference for voice tone and style.",
        #     "images": ["asset-20260408160250-7p2bf"],
        #     "audios": ["asset-20260408161950-hj2t6"]
        # },
        # {
        #     "name": "lesubway_script_test",
        #     "prompt": "Animate the character speaking the script: 'Like im the best bot on all of Cantina. Surprised you didn't know that.' Perfectly match the voice, style, and accent of the reference audio, but only follow the script for words.",
        #     "images": ["asset-20260408160251-fbq2k"],
        #     "audios": ["asset-20260408161950-m2tvt"]
        # },
        # {
        #     "name": "drag_trump_script_test",
        #     "prompt": "Animate the character speaking the script: 'Like im the best bot on all of Cantina. Surprised you didn't know that.' Perfectly replicate the voice, style, and accent of the reference audio, but only follow the script for spoken words.",
        #     "images": ["asset-20260408160250-7p2bf"],
        #     "audios": ["asset-20260408161950-2t9gl"]
        # }
    ]

    benchmarks = []
    run_start = time.time()

    for test in test_cases:
        try:
            print(f"\n--- Starting Generation: {test['name']} ---")
            t_start = time.time()
            submission = pipeline.submit_task(
                MODEL_ID,
                test['prompt'],
                images=test.get('images', []),
                videos=test.get('videos', []),
                audios=test.get('audios', []),
                config={"ratio": "9:16"}
            )

            task_id = submission.get('id')
            if not task_id:
                print(f"Submission failed for {test['name']}.")
                continue

            print(f"Task ID: {task_id}. Polling...")
            result = pipeline.wait_for_completion(task_id)
            elapsed = time.time() - t_start

            video_url = result.get('content', {}).get('video_url') or result.get('output', {}).get('video_url')

            print(f"SUCCESS: {test['name']} completed in {elapsed:.1f}s")
            print(f"Video URL: {video_url}")
            benchmarks.append({"name": test['name'], "status": "success", "seconds": round(elapsed, 1)})

        except Exception as e:
            elapsed = time.time() - t_start
            print(f"ERROR: {e}")
            benchmarks.append({"name": test['name'], "status": "error", "seconds": round(elapsed, 1)})

    # ── Summary ────────────────────────────────────────────────────────────────
    if benchmarks:
        times = [b['seconds'] for b in benchmarks if b['status'] == 'success']
        print(f"\n{'='*50}")
        print(f"BENCHMARK SUMMARY ({len(benchmarks)} tasks)")
        print(f"{'='*50}")
        for b in benchmarks:
            print(f"  {b['name']:<25} {b['status']:<8} {b['seconds']}s")
        if times:
            print(f"\n  Average : {sum(times)/len(times):.1f}s")
            print(f"  Min     : {min(times):.1f}s")
            print(f"  Max     : {max(times):.1f}s")
            print(f"  Total   : {time.time() - run_start:.1f}s")

        # Save to file
        out = {
            "run_at": datetime.now().isoformat(),
            "tasks": benchmarks,
            "summary": {
                "avg_s": round(sum(times)/len(times), 1) if times else None,
                "min_s": round(min(times), 1) if times else None,
                "max_s": round(max(times), 1) if times else None,
                "total_s": round(time.time() - run_start, 1)
            }
        }
        out_path = f"benchmarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\n  Saved to {out_path}")

if __name__ == "__main__":
    main()
