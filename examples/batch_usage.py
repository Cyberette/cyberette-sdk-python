import sys
import pathlib
import asyncio

# Ensure the project root is on sys.path so this example can be run directly
# from the `examples/` folder (useful when the package isn't installed).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette_sdk import Cyberette

async def main():
    sdk = Cyberette(api_key="your_api_key")
    
    try:
        results = await sdk.batch_upload(["testing_data\\song.mp3", "testing_data\\song.wav", "testing_data\\test_audio.mp3"])
        for r in results:
            if r["error"]:
                print("Error:", r["file"], "->", r["error"])
            else:
                print("Success:", r["file"], "->", r["result"])
    except Exception as e:
        print("Error:", e)
    finally:
        await sdk.close()

if __name__ == "__main__":
    asyncio.run(main())
