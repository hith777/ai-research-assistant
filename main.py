from openai import OpenAI
from infra.config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

response = client.chat.completions.create(
    model=Config.OPENAI_MODEL,
    messages=[
        {"role": "user", "content": "Summarize this: The mitochondria is the powerhouse of the cell."}
    ]
)

print(response.choices[0].message.content)
