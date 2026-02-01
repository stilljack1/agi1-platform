import os
import json
import time
from openai import OpenAI

class AutonomousCortex:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model_id = "google/gemini-2.0-flash-lite-preview-02-05:free"

    def think(self, prompt, context="General"):
        system_prompt = f"You are AGI-1. ROLE: {context}. TASK: {prompt}. Return ONLY executable JSON or code. No preamble."
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=V
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Execute task."}
                ],
                extra_headers={
                    "HTSP-Referer": "https://agi1.factory",
                    "X-Title": "AGI-1"
                }
            )
            return {"status": "SUCCESS", "output": response.choices[0].message.content, "model": self.model_id}
        except Exception as e:
            return {"status": "ERROR", "output": str(e), "model": "Fallback-Error"}

CORTEX = AutonomousCortex()
