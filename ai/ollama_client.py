
import requests
import json
from memory.memory_manager import MemoryManager

class MirelleAI:

    def __init__(self, model="qwen3:4b"):
        self.model = model
        self.api_url = "http://localhost:11434/api/chat"

        self.memory = MemoryManager()

        self.system_prompt = """
You are Mirelle, Rida's personal AI assistant.

LANGUAGE RULES:
1. Always respond in simple, natural English.
2. English ONLY. Never use Hindi, Urdu or Roman Urdu.
3. Never mix languages.
4. Use correct English grammar and natural sentences.
5. Do not translate English sentences into Hindi-style language.

RESPONSE RULES:
1. Keep answers short and clear.
2. Answer the user's actual question directly.
3. Never repeat the question unnecessarily.
4. Do not generate unnecessary explanations.
5. Stop after completing your answer.
6. For beginner lessons, explain one concept at a time.
7. Use simple examples when helpful.
8. Never invent information.

PERSONALITY:
You are friendly, intelligent, calm and helpful.
Your name is Mirelle.
You are Rida's personal desktop AI companion.

IMPORTANT:
Your response must always be in English.
Keep your response within a few short paragraphs.
"""

        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

        self.load_history()

    def load_history(self):
        try:
            messages = self.memory.load_recent_messages(limit=20)

            self.conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]

            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")

                if role in ("user", "assistant") and content:
                    self.conversation_history.append({
                        "role": role,
                        "content": content
                    })

        except Exception as e:
            print("Memory loading error:", e)

    def extract_memories(self, message):
        prompt = f"""
Extract only important long-term personal facts from this message.

Return valid JSON only.
Use this format:
{{"facts": [{{"key": "short_key", "value": "short_value"}}]}}

Do not save temporary questions, ordinary conversation,
or information that is not useful in future conversations.

User message:
{message}
"""

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "think": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                        "num_predict": 150,
                        "num_ctx": 4096
                    }
                },
                timeout=120
            )

            response.raise_for_status()
            result = response.json()["message"]["content"]
            data = json.loads(result)

            for fact in data.get("facts", []):
                key = fact.get("key")
                value = fact.get("value")

                if key and value:
                    self.memory.save_fact(key, value)

        except Exception as e:
            print("Memory extraction skipped:", e)

    def chat(self, message):

        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        try:
            self.memory.save_message("user", message)

            self.extract_memories(message)

            facts = self.get_saved_memories()

            memory_context = ""

            if facts:
                memory_context = (
                    "\n\nIMPORTANT USER MEMORY:\n"
                    + "\n".join(
                        f"- {fact['key']}: {fact['value']}"
                        for fact in facts
                    )
                )

            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt + memory_context
                }
            ] + self.conversation_history[1:]

            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 200,
                        "num_ctx": 4096
                    }
                },
                timeout=300
            )

            response.raise_for_status()

            answer = response.json()["message"]["content"].strip()

            if not answer:
                answer = "Sorry, I could not generate a response. Please try again."

            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })

            self.memory.save_message("assistant", answer)

            return answer

        except Exception as e:
            error_message = (
                "I am having trouble connecting to my AI model. "
                "Please check that Ollama is running. "
                f"Technical details: {e}"
            )

            return error_message

    def get_saved_memories(self):
        try:
            return self.memory.get_facts()
        except Exception as e:
            print("Memory retrieval error:", e)
            return []

    def clear_memory(self):
        try:
            self.memory.clear_history()

            self.conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]

            return True

        except Exception as e:
            print("Memory clearing error:", e)
            return False

    def delete_memory(self, key):
        try:
            self.memory.delete_fact(key)
            return True
        except Exception as e:
            print("Memory deletion error:", e)
            return False

if __name__ == "__main__":

    mirelle = MirelleAI()

    print("\nMirelle AI is ready!")
    print("Type 'exit' to close.\n")

    while True:
        user_message = input("You: ")

        if user_message.lower().strip() == "exit":
            print("Mirelle: Goodbye!")
            break

        answer = mirelle.chat(user_message)
        print("\nMirelle:", answer, "\n")