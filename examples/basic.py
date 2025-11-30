import asyncio
from cyberette_sdk.client import Cyberette

async def main():
    sdk = Cyberette(api_key="your_api_key")
    
    try:
        result = await sdk.upload("testing_data\\test_audio.mp3")
        print("Success:", result)
    except Exception as e:
        print("Error:", e)
    finally:
        await sdk.close()

if __name__ == "__main__":
    asyncio.run(main())
