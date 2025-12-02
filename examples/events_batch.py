import sys
import pathlib
import asyncio

# Allow examples/ to find the sdk source
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette import Cyberette

async def main():
    sdk = Cyberette(api_key="your_api_key")

    # ------------------------------
    # EVENT HANDLERS
    # ------------------------------
    
    @sdk.on("batch_started")
    def on_batch_started(files):
        print("\n[BATCH STARTED]")
        print("Files:", files)

    @sdk.on("batch_file_success")
    def on_file_success(file, result):
        print(f"[SUCCESS] {file} -> {result}")

    @sdk.on("batch_file_error")
    def on_file_error(file, error):
        print(f"[ERROR] {file} -> {error}")

    @sdk.on("batch_finished")
    def on_batch_finished(results):
        print("\n[BATCH FINISHED]")
        print("Final Results:")
        for r in results:
            print(r)

    # ------------------------------
    # START BATCH PROCESSING
    # ------------------------------
    try:
        await sdk.batch_upload([
            "testing_data\\song.mp3",
            "testing_data\\song.wav",
            "testing_data\\test_audio.mp3"
        ])
    except Exception as e:
        print("Exception:", e)
    finally:
        await sdk.close()


if __name__ == "__main__":
    asyncio.run(main())
