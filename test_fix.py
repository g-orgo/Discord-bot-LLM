import asyncio
import sys
sys.path.insert(0, ".")
import ollama as ollama_client
import system_prompt

async def test_direct():
    ollama_client.init_client()
    
    messages_to_test = [
        "Estou em uma apresentação para o papai",
        "Preciso mandar email pro cliente hoje",
        "a reunião foi cancelada por falta de quórum",
        "vou chegar atrasado na call de amanha",
    ]
    
    few_shot = system_prompt.get_few_shot()
    print(f"Few-shot examples: {len(few_shot) // 2} pairs")
    for i in range(0, len(few_shot), 2):
        print(f"  User: {few_shot[i]['content']!r}")
        print(f"  Asst: {few_shot[i+1]['content']!r}")
    print()
    
    for msg in messages_to_test:
        result = await ollama_client.ollama_chat(
            "qwen2.5:1.5b",
            system_prompt.get(),
            f"Rewrite: {msg}",
            few_shot=few_shot
        )
        print(f"IN:  {msg}")
        print(f"OUT: {result.strip()}")
        print()
    
    await ollama_client.close_client()

asyncio.run(test_direct())
