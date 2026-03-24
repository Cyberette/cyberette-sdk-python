import asyncio
import os
import sys
import pathlib

# Ensure the project root is on sys.path so this example can be run directly
# from the `examples/` folder (useful when the package isn't installed).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette_sdk.client import Cyberette

# Set your API key and the folder you want to upload
API_KEY = ""
FOLDER_PATH = r"folder-path-here"  # Change this to the path of the folder you want to upload

async def main():
    client = Cyberette(api_key=API_KEY)
    try:
        results = await client.upload_folder(FOLDER_PATH)
        for result in results:
            print(f"File: {result['file']}")
            if result['error']:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Result: {result['result']}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
