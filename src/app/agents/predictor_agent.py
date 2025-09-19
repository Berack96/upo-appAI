import json
import os
from typing import Any

import anthropic
import requests
from dotenv import load_dotenv
from google.genai import Client
from openai import OpenAI

load_dotenv()

class PredictorAgent:
    def __init__(self):
        # Ollama via HTTP locale
        self.providers = {
            "ollama": {"type": "ollama", "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"), "model": "gpt-oss:latest"}
        }

        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            client = OpenAI(api_key=openai_key)
            self.providers["openai"] = {
                "type": "openai",
                "client": client,
                "model": "gpt-4o-mini"
            }

        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            client = anthropic.Anthropic(api_key=anthropic_key)
            self.providers["anthropic"] = {
                "type": "anthropic",
                "client": client,
                "model": "claude-3-haiku-20240307"
            }

        # Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if google_key:
            client = Client(api_key=google_key)
            self.providers["google"] = {"type": "google", "client": client, "model": "gemini-1.5-flash"}

        # DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.providers["deepseek"] = {"type": "deepseek", "api_key": deepseek_key, "model": "deepseek-chat"}

        print("✅ Providers attivi:", list(self.providers.keys()))

    def predict(self, data, sentiment, style="conservative", provider="mock"):
        provider = provider.lower()
        if provider == "mock" or provider not in self.providers:
            return self._predict_mock(style)

        prompt = f"""
            Sei un consulente finanziario crypto.
            Dati di mercato: {data}
            Sentiment estratto: {sentiment}
            Stile richiesto: {style}
            Fornisci una strategia di investimento chiara e breve (max 5 frasi),
            con percentuali di portafoglio e motivazioni sintetiche."""

        cfg: Any = self.providers[provider]
        try:
            if cfg["type"] == "ollama":
                return self._predict_ollama_http(prompt, cfg["host"], cfg["model"])
            elif cfg["type"] == "openai":
                return self._predict_openai(prompt, cfg["client"], cfg["model"])
            elif cfg["type"] == "anthropic":
                return self._predict_anthropic(prompt, cfg["client"], cfg["model"])
            elif cfg["type"] == "google":
                return self._predict_google(prompt, cfg["client"], cfg["model"])
            elif cfg["type"] == "deepseek":
                return self._predict_deepseek(prompt, cfg["api_key"], cfg["model"])
            return None
        except Exception as e:
            return f"⚠️ Provider {provider} non riconosciuto: {e}"

    @staticmethod
    def _predict_ollama_http(prompt, host, model):
        url = host.rstrip("/") + "/api/generate"
        payload = {"model": model, "prompt": prompt, "max_tokens": 300}
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        try:
            data = r.json()
            if isinstance(data, dict):
                for key in ("text", "generated", "content"):
                    if key in data:
                        return str(data[key])
                if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                    c = data["choices"][0]
                    if "text" in c:
                        return c["text"]
            return json.dumps(data)
        except ValueError:
            return r.text

    @staticmethod
    def _predict_openai(prompt, client, model):
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Sei un consulente finanziario crypto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()

    @staticmethod
    def _predict_anthropic(prompt, client, model):
        response = client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return response.completion.strip()

    @staticmethod
    def _predict_google(prompt, client, model):
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 300
            }
        )
        return response.text.strip()

    @staticmethod
    def _predict_deepseek(prompt, api_key, model):
        url = "https://api.deepseek.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _predict_mock(style):
        if style.lower() in ("aggressive", "aggr"):
            return (
                "🚀 Strategia aggressiva (mock): "
                "30% BTC, 20% ETH, 50% altcoins emergenti. "
                "Motivo: alta volatilità + potenziale upside."
            )
        return (
            "🛡️ Strategia conservativa (mock): "
            "60% BTC, 30% ETH, 10% stablecoins. "
            "Motivo: protezione da volatilità + focus su asset solidi."
        )
