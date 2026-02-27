#!/usr/bin/env python3
"""
OpenClaw Complete v2.0 - Agent Gateway
=======================================
Unified communication layer for all AI providers.
Handles API calls, retries, rate limiting, and response parsing.
"""

import os
import json
import time
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger("openclaw.gateway")


class RateLimiter:
    """Token bucket rate limiter per provider."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.tokens = requests_per_minute
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.rpm, self.tokens + elapsed * (self.rpm / 60.0))
            self.last_refill = now
            if self.tokens < 1:
                wait = (1 - self.tokens) / (self.rpm / 60.0)
                logger.debug(f"Rate limited, waiting {wait:.2f}s")
                await asyncio.sleep(wait)
                self.tokens = 0
            else:
                self.tokens -= 1


class ProviderClient:
    """Base client for an AI provider."""

    def __init__(self, name: str, base_url: str, api_key: str, rate_limit: int = 60):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.limiter = RateLimiter(rate_limit)
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_requests = 0
        self.total_tokens_used = 0
        self.errors = 0

    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
            )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def stats(self) -> Dict:
        return {
            "provider": self.name,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens_used,
            "errors": self.errors
        }


class AnthropicClient(ProviderClient):
    """Anthropic API client (Claude models)."""

    async def send(self, model: str, messages: List[Dict],
                   max_tokens: int = 8192, temperature: float = 0.5,
                   system: str = "") -> Dict[str, Any]:
        await self.ensure_session()
        await self.limiter.acquire()

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        if system:
            payload["system"] = system

        for attempt in range(3):
            try:
                async with self.session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                ) as resp:
                    self.total_requests += 1
                    data = await resp.json()

                    if resp.status == 200:
                        usage = data.get("usage", {})
                        self.total_tokens_used += usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                        return {
                            "success": True,
                            "content": data["content"][0]["text"] if data.get("content") else "",
                            "usage": usage,
                            "model": model,
                            "provider": "anthropic"
                        }
                    elif resp.status == 429:
                        wait = 2 ** attempt * 5
                        logger.warning(f"Anthropic rate limited, retrying in {wait}s")
                        await asyncio.sleep(wait)
                        continue
                    else:
                        self.errors += 1
                        return {"success": False, "error": data.get("error", {}).get("message", str(data)), "provider": "anthropic"}
            except Exception as e:
                self.errors += 1
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e), "provider": "anthropic"}

        return {"success": False, "error": "Max retries exceeded", "provider": "anthropic"}


class OpenAIClient(ProviderClient):
    """OpenAI API client (GPT, CodeX models)."""

    async def send(self, model: str, messages: List[Dict],
                   max_tokens: int = 8192, temperature: float = 0.5,
                   system: str = "") -> Dict[str, Any]:
        await self.ensure_session()
        await self.limiter.acquire()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model": model,
            "messages": full_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        for attempt in range(3):
            try:
                async with self.session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as resp:
                    self.total_requests += 1
                    data = await resp.json()

                    if resp.status == 200:
                        usage = data.get("usage", {})
                        self.total_tokens_used += usage.get("total_tokens", 0)
                        return {
                            "success": True,
                            "content": data["choices"][0]["message"]["content"],
                            "usage": usage,
                            "model": model,
                            "provider": "openai"
                        }
                    elif resp.status == 429:
                        wait = 2 ** attempt * 5
                        logger.warning(f"OpenAI rate limited, retrying in {wait}s")
                        await asyncio.sleep(wait)
                        continue
                    else:
                        self.errors += 1
                        return {"success": False, "error": data.get("error", {}).get("message", str(data)), "provider": "openai"}
            except Exception as e:
                self.errors += 1
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e), "provider": "openai"}

        return {"success": False, "error": "Max retries exceeded", "provider": "openai"}


class GoogleClient(ProviderClient):
    """Google AI API client (Gemini models)."""

    async def send(self, model: str, messages: List[Dict],
                   max_tokens: int = 8192, temperature: float = 0.5,
                   system: str = "") -> Dict[str, Any]:
        await self.ensure_session()
        await self.limiter.acquire()

        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"

        for attempt in range(3):
            try:
                async with self.session.post(url, json=payload) as resp:
                    self.total_requests += 1
                    data = await resp.json()

                    if resp.status == 200:
                        candidates = data.get("candidates", [])
                        text = ""
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            text = parts[0].get("text", "") if parts else ""
                        usage = data.get("usageMetadata", {})
                        self.total_tokens_used += usage.get("totalTokenCount", 0)
                        return {
                            "success": True,
                            "content": text,
                            "usage": usage,
                            "model": model,
                            "provider": "google"
                        }
                    elif resp.status == 429:
                        wait = 2 ** attempt * 5
                        logger.warning(f"Google rate limited, retrying in {wait}s")
                        await asyncio.sleep(wait)
                        continue
                    else:
                        self.errors += 1
                        return {"success": False, "error": str(data), "provider": "google"}
            except Exception as e:
                self.errors += 1
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e), "provider": "google"}

        return {"success": False, "error": "Max retries exceeded", "provider": "google"}


class AgentGateway:
    """
    Unified gateway for all AI agent communication.
    Routes requests to the correct provider and model.
    """

    def __init__(self, config_path: str = "agents.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.clients: Dict[str, ProviderClient] = {}
        self.agents: Dict[str, Dict] = {}
        self.message_log: List[Dict] = []
        self._init_clients()
        self._init_agents()

    def _load_config(self) -> Dict:
        with open(self.config_path) as f:
            return json.load(f)

    def _init_clients(self):
        providers = self.config["providers"]

        # Anthropic
        ak = os.getenv(providers["anthropic"]["env_key"], "")
        if ak:
            self.clients["anthropic"] = AnthropicClient(
                "anthropic", providers["anthropic"]["base_url"], ak
            )
            logger.info("Anthropic client initialized")

        # OpenAI
        ok = os.getenv(providers["openai"]["env_key"], "")
        if ok:
            self.clients["openai"] = OpenAIClient(
                "openai", providers["openai"]["base_url"], ok
            )
            logger.info("OpenAI client initialized")

        # Google
        gk = os.getenv(providers["google"]["env_key"], "")
        if gk:
            self.clients["google"] = GoogleClient(
                "google", providers["google"]["base_url"], gk
            )
            logger.info("Google client initialized")

    def _init_agents(self):
        for agent in self.config["agents"]:
            self.agents[agent["id"]] = agent

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        return self.agents.get(agent_id)

    def get_agents_for_task(self, task_type: str) -> List[str]:
        routing = self.config.get("task_routing", {})
        return routing.get(task_type, [])

    async def send_to_agent(self, agent_id: str, messages: List[Dict],
                            system: str = "", **kwargs) -> Dict[str, Any]:
        agent = self.agents.get(agent_id)
        if not agent:
            return {"success": False, "error": f"Agent {agent_id} not found"}

        provider_name = agent["provider"]
        if provider_name == "internal":
            return self._handle_internal(agent, messages, system)

        client = self.clients.get(provider_name)
        if not client:
            return {"success": False, "error": f"Provider {provider_name} not configured (missing API key)"}

        model_key = agent["model"]
        model_id = self.config["providers"][provider_name]["models"][model_key]

        result = await client.send(
            model=model_id,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", agent.get("max_tokens", 8192)),
            temperature=kwargs.get("temperature", agent.get("temperature", 0.5)),
            system=system
        )

        # Log the exchange
        self.message_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "role": agent["role"],
            "provider": provider_name,
            "success": result.get("success", False),
            "tokens": result.get("usage", {}),
            "error": result.get("error")
        })

        return result

    def _handle_internal(self, agent: Dict, messages: List[Dict], system: str) -> Dict:
        """Handle internal agents (OpenClaw, Ralph Loop) locally."""
        return {
            "success": True,
            "content": f"[{agent['name']}] Internal agent processing. Messages queued.",
            "usage": {"internal": True},
            "model": agent["model"],
            "provider": "internal"
        }

    async def broadcast(self, message: str, agent_ids: List[str],
                        system: str = "") -> Dict[str, Dict]:
        """Send a message to multiple agents concurrently."""
        tasks = {}
        for aid in agent_ids:
            tasks[aid] = self.send_to_agent(
                aid, [{"role": "user", "content": message}], system=system
            )
        results = {}
        for aid, coro in tasks.items():
            results[aid] = await coro
        return results

    def get_stats(self) -> Dict:
        stats = {"providers": {}, "total_messages": len(self.message_log)}
        for name, client in self.clients.items():
            stats["providers"][name] = client.stats()
        return stats

    async def close_all(self):
        for client in self.clients.values():
            await client.close()


# Convenience function
def create_gateway(config_path: str = None) -> AgentGateway:
    """Create and return an AgentGateway instance."""
    path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents.json")
    return AgentGateway(path)
