# cyberette-sdk-python

pip install cyberette

from cyberette import Cyberette

client = Cyberette(api_key="YOUR_KEY")
result = await client.upload("image.jpg")
print(result)
