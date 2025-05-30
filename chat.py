import openai
import os

# Set your API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Make a request
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How do I use the OpenAI API?"}
    ],
    temperature=0.7
)
print(response['choices'][0]['message']['content'])


#print(openai.api_key)



