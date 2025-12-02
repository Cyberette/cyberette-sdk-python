import sys
import pathlib
import asyncio

# Ensure the project root is on sys.path so this example can be run directly
# from the `examples/` folder (useful when the package isn't installed).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette import Cyberette

async def main():
    print("Initializing SDK...")
    sdk = Cyberette(api_key="your-api-key")

    # ---- Event handlers ----
    @sdk.on("upload_started")
    def on_start(file_path):
        print(f"[EVENT] Upload started for: {file_path}")

    @sdk.on("video_has_audio")
    def audio_detected(file_path):
        print(f"[EVENT] Audio detected in video: {file_path}")

    @sdk.on("upload_success")
    async def on_success(file_path, response):
        print(f"[EVENT] Upload successful! Response: {response}")
        print("Status:", response.get("status"))
        print("Score:", response.get("score"))

    @sdk.on("upload_error")
    def on_error(file_path, error):
        print(f"[EVENT] Error during upload: {error}")

    # ---- Perform upload ----
    print("Uploading file for analysis...")
    response = await sdk.upload("testing_data\\dog.jpg")

    print("Upload completed.")
    print("Final response:", response)

    await sdk.close()

asyncio.run(main())
