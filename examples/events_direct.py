import sys
import pathlib
import asyncio

# Ensure the project root is on sys.path so this example can be run directly
# from the `examples/` folder (useful when the package isn't installed).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette_sdk import Cyberette

async def main():
    client = Cyberette(api_key="test_key")

    # Direct style: register event listeners
    client.on("upload_started", lambda file_path: print(f"Upload started: {file_path}"))
    
    client.on("upload_sent", lambda file_path, url: print(f"File sent: {file_path} -> {url}"))
    
    client.on("upload_success", lambda file_path, response: print(f"Upload successful: {file_path}, response: {response}"))
    
    client.on("upload_error", lambda file_path, error: print(f"Upload error: {file_path}, error: {error}"))

    # Trigger an upload (events will fire)
    try:
        result = await client.upload("testing_data/song.mp3")
        print("Final result:", result)
    except Exception as e:
        print("Exception during upload:", e)
    finally:
        await client.close()

# Run the example
asyncio.run(main())
