from google import genai
from google.genai.types import HttpOptions
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access your variables
api_key = os.getenv("API_KEY")


client = genai.Client(
    http_options=HttpOptions(api_version="v1"),
    api_key=api_key,

)
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="can you scrap data from html? I have a website that has a lot of data in html format. I want to scrap the data and save it in a file. Can you help me with that?",
)
print(response.text)
# Example response:
# Okay, let's break down how AI works. It's a broad field, so I'll focus on the ...
#
# Here's a simplified overview:
# ...