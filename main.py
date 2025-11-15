import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
deployment_name = "gpt-5-chat"
api_key = os.getenv('AZURE_OPENAI_API_KEY')

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)


def main():
    print('hello')


main()