import ollama
while True:
    promp = input("promp:")

    response = ollama.chat(
        model='qwen3:1.7B',
        messages=[
            {'role': 'user', 'content': f'antworte auf deutsch. {promp}'}
        ]
    )

    print(response['message']['content'])
