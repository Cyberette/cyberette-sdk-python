import sys
import pathlib
import asyncio

# Ensure the project root is on sys.path so this example can be run directly
# from the `examples/` folder (useful when the package isn't installed).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette import Cyberette

async def main():
    sdk = Cyberette(api_key="your_api_key")
    
    try:
        result = await sdk.upload("testing_data\\test_audio.mp3")
        print("Success:", result)
        resultimg = await sdk.upload("testing_data\\dog.jpg")
        print("Success:", resultimg)
        resultvid = await sdk.upload("testing_data\\test_video.mp4")
        print("Success:", resultvid)
        resultvid_aud = await sdk.upload("testing_data\\test_video_audio.mp4")
        print("Success:", resultvid_aud)
    except Exception as e:
        print("Error:", e)
    finally:
        await sdk.close()

if __name__ == "__main__":
    asyncio.run(main())
