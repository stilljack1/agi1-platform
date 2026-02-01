import os

code = """import os
import json
import time
from openai import OpenAI

class AutonomousCortex:
    def __init__(self):
        # We use the standard OpenAI client but point it to OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        # PHASE 1: FREE TIER MODEL
        self.model_id = "google/gemini-2.0-flash-lite-preview-02-05:free"

    def think(self, prompt, context="General"):
        system_prompt = f'''
You are AGI-1, an advanced autonomous factory system.
ROLE: {context}
TASK: {prompt}

OUTPUT INSTRUCTIONS:
- Return ONLY the executable answer or JSON.
- No preamble. Be concise and logical.
'''
        try:
            # Call OpenRouter
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Execute task."}
                ],
                extra_headers={
                    "HTTP-Referer": "https://agi1.factory",
                    "X-Title": "AGI-1 Autonomous System",
                }
            )
            
            output_text = response.choices[0].message.content
            return {"status": "SUCCESS", "output": output_text, "model": self.model_id}
            
        except Exception as e:
            return {"status": "ERROR", "output": str(e), "model": "Fallback-Error"}

# Singleton Instance
CORTEX = AutonomousCortex()
"""

# Ensure directory exists
os.makedirs("core/intelligence", exist_ok=True)

# Write the file
with open("core/intelligence/brain.py", "w") as f:
    f.write(code)

print("✅ Successfully wrote core/intelligence/brain.py")
