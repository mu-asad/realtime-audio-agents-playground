import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=api_key
)

completion = client.chat.completions.create(
    model="gpt-4o",
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