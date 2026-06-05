"""Multi-LLM Provider System — strategy pattern + config-driven.

Supports DeepSeek, Qwen (DashScope), Ollama (local), Moonshot (Kimi).
Auto-fallback: if primary provider fails, tries next in priority order.

Architecture inspired by MoneyPrinterTurbo (55K⭐).

Usage:
    from generators.llm_providers import LLMDispatcher
    dispatcher = LLMDispatcher()
    response = dispatcher.chat([
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
    ])
"""

import json, os, urllib.request, urllib.error
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Auto-load .env file so API keys are available in os.environ
try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass


# ─── Config ─────────────────────────────────────────────────

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "llm_config.json"


def _load_config(config_path: str = None) -> dict:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return _default_config()


def _default_config() -> dict:
    return {
        "default_model": "deepseek-chat",
        "temperature": 0.8,
        "max_tokens": 4096,
        "timeout_s": 120,
        "providers": [
            {
                "name": "deepseek", "display_name": "DeepSeek",
                "base_url": "https://api.deepseek.com",
                "api_key_env": "DEEPSEEK_API_KEY",
                "models": ["deepseek-chat"], "default_model": "deepseek-chat",
                "priority": 1, "enabled": True,
            },
        ],
        "fallback_strategy": "sequential",
        "retry_count": 1,
    }


# ─── Data Types ─────────────────────────────────────────────

@dataclass
class ProviderStatus:
    name: str
    display_name: str
    available: bool
    error: str = ""


@dataclass
class ChatResult:
    content: str
    provider: str
    model: str
    attempts: int = 1


# ─── Base Provider ─────────────────────────────────────────

class BaseLLMProvider(ABC):
    """Abstract LLM provider. All providers implement this interface."""

    def __init__(self, config: dict):
        self.config = config
        self.name = config["name"]
        self.display_name = config["display_name"]
        self.base_url = config["base_url"].rstrip("/")
        self.models = config.get("models", [])
        self.default_model = config.get("default_model", self.models[0] if self.models else "")
        self.supports_vision = config.get("supports_vision", False)
        self._available_cache = None

    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Get API key from env var or return None (for local providers)."""

    def is_available(self) -> bool:
        """Check if this provider is ready to use."""
        if self._available_cache is not None:
            return self._available_cache

        api_key = self._get_api_key()
        if api_key is None and not self._is_local():
            self._available_cache = False
            return False

        # Quick connectivity check
        try:
            self._available_cache = self._ping()
        except Exception:
            self._available_cache = False
        return self._available_cache

    def _is_local(self) -> bool:
        return False

    def _ping(self) -> bool:
        """Lightweight check. Override for provider-specific checks."""
        return bool(self._get_api_key()) or self._is_local()

    def chat(self, messages: list, model: str = None,
             temperature: float = 0.8, max_tokens: int = 4096,
             timeout_s: int = 120) -> str:
        """Send a chat completion request. Returns content string or raises."""
        return self._call_api(messages, model or self.default_model,
                             temperature, max_tokens, timeout_s)

    @abstractmethod
    def _call_api(self, messages: list, model: str,
                  temperature: float, max_tokens: int, timeout_s: int) -> str:
        """Actual API call implementation."""

    def _build_request(self, endpoint: str, data: dict, timeout_s: int,
                       extra_headers: dict = None):
        """Build and send HTTP request to OpenAI-compatible API."""
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(data).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_api_key()}",
        }
        if extra_headers:
            headers.update(extra_headers)

        req = urllib.request.Request(url, data=body, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:500] if e.fp else ""
            raise RuntimeError(f"{self.display_name} HTTP {e.code}: {body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"{self.display_name} unreachable: {e.reason}")


# ─── Concrete Providers ─────────────────────────────────────

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek API provider."""

    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("DEEPSEEK_API_KEY") or os.environ.get(self.config.get("api_key_env", ""))

    def _call_api(self, messages, model, temperature, max_tokens, timeout_s):
        return self._build_request("/v1/chat/completions", {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }, timeout_s)


class QwenProvider(BaseLLMProvider):
    """Qwen via DashScope (OpenAI-compatible API).

    Note: DashScope /compatible-mode/v1 is used for OpenAI-compatible endpoint.
    """

    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("DASHSCOPE_API_KEY") or os.environ.get(self.config.get("api_key_env", ""))

    def _call_api(self, messages, model, temperature, max_tokens, timeout_s):
        return self._build_request("/chat/completions", {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }, timeout_s)


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider (runs on localhost, no API key needed)."""

    def _get_api_key(self) -> Optional[str]:
        return "ollama"  # Ollama doesn't need a real key

    def _is_local(self) -> bool:
        return True

    def _ping(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/models")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                installed = [m.get("name", "") for m in data.get("data", [])]
                # Check if any configured model is installed
                return any(m in installed for m in self.models)
        except Exception:
            return False

    def _call_api(self, messages, model, temperature, max_tokens, timeout_s):
        return self._build_request("/v1/chat/completions", {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }, timeout_s)


class MoonshotProvider(BaseLLMProvider):
    """Moonshot (Kimi) API provider."""

    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("MOONSHOT_API_KEY") or os.environ.get(self.config.get("api_key_env", ""))

    def _call_api(self, messages, model, temperature, max_tokens, timeout_s):
        return self._build_request("/v1/chat/completions", {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }, timeout_s)


# ─── Provider Registry ─────────────────────────────────────

class DoubaoProvider(BaseLLMProvider):
    """Doubao via Volcengine Ark (OpenAI-compatible, supports vision)."""

    def _get_api_key(self):
        return os.environ.get("SEEDREAM_API_KEY") or os.environ.get(self.config.get("api_key_env", ""))

    def _call_api(self, messages, model, temperature, max_tokens, timeout_s):
        return self._build_request("/chat/completions", {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }, timeout_s)


PROVIDER_CLASSES = {
    "deepseek": DeepSeekProvider,
    "qwen": QwenProvider,
    "ollama": OllamaProvider,
    "moonshot": MoonshotProvider,
    "doubao": DoubaoProvider,
}


# ─── Dispatcher ────────────────────────────────────────────

class LLMDispatcher:
    """Multi-provider dispatcher with auto-fallback.

    Usage:
        dispatcher = LLMDispatcher()
        result = dispatcher.chat(messages)
        # result.content -> response text
        # result.provider -> which provider responded (e.g. "deepseek")
    """

    def __init__(self, config_path: str = None):
        self.config = _load_config(config_path)
        self.temperature = self.config.get("temperature", 0.8)
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.timeout_s = self.config.get("timeout_s", 120)
        self.retry_count = self.config.get("retry_count", 1)

        # Build provider instances sorted by priority
        self._providers: list[BaseLLMProvider] = []
        self._statuses: dict[str, ProviderStatus] = {}

        for pconf in sorted(self.config.get("providers", []),
                            key=lambda x: x.get("priority", 99)):
            if not pconf.get("enabled", True):
                self._statuses[pconf["name"]] = ProviderStatus(
                    name=pconf["name"], display_name=pconf["display_name"],
                    available=False, error="Disabled in config")
                continue

            cls = PROVIDER_CLASSES.get(pconf["name"])
            if not cls:
                continue

            provider = cls(pconf)
            self._providers.append(provider)

    # ─── Public API ─────────────────────────────────────

    def chat(self, messages: list, model: str = None,
             temperature: float = None, max_tokens: int = None,
             timeout_s: int = None) -> ChatResult:
        """Send chat request with automatic fallback.

        Tries each provider in priority order. If one fails, tries the next.
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        timeout = timeout_s if timeout_s is not None else self.timeout_s
        used_model = model or self.config.get("default_model", "")

        last_error = ""
        attempts = 0

        # Check if messages contain image content
        has_vision_content = any(
            isinstance(m.get("content"), list) and 
            any(item.get("type") == "image_url" for item in m.get("content", []))
            for m in messages
        )
        # Filter providers: if vision content, skip text-only providers
        if has_vision_content:
            providers_to_try = [p for p in self._providers if p.supports_vision]
            if not providers_to_try:
                raise RuntimeError("Vision content detected but no vision-capable provider available")
        else:
            providers_to_try = self._providers

        for provider in providers_to_try:
            if not provider.is_available():
                self._statuses[provider.name] = ProviderStatus(
                    name=provider.name, display_name=provider.display_name,
                    available=False, error=last_error or "Not available")
                continue

            prov_model = model or provider.default_model
            for attempt in range(self.retry_count + 1):
                attempts += 1
                try:
                    content = provider.chat(
                        messages, model=prov_model,
                        temperature=temp, max_tokens=max_tok, timeout_s=timeout,
                    )
                    self._statuses[provider.name] = ProviderStatus(
                        name=provider.name, display_name=provider.display_name,
                        available=True)
                    return ChatResult(
                        content=content, provider=provider.name,
                        model=prov_model, attempts=attempts,
                    )
                except Exception as e:
                    last_error = str(e)
                    if attempt < self.retry_count:
                        continue  # retry same provider

            # Provider exhausted — mark and move to next
            self._statuses[provider.name] = ProviderStatus(
                name=provider.name, display_name=provider.display_name,
                available=False, error=last_error)

        raise RuntimeError(
            f"All LLM providers exhausted ({attempts} attempts). "
            f"Last error: {last_error}"
        )

    def chat_simple(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Convenience: system + user messages, returns text only."""
        result = self.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ], **kwargs)
        return result.content

    def get_providers_status(self) -> list[ProviderStatus]:
        """Get availability status of all configured providers."""
        results = []
        for provider in self._providers:
            if provider.name in self._statuses:
                results.append(self._statuses[provider.name])
            else:
                available = provider.is_available()
                status = ProviderStatus(
                    name=provider.name, display_name=provider.display_name,
                    available=available,
                    error="" if available else "Not available")
                self._statuses[provider.name] = status
                results.append(status)
        return results

    def print_status(self):
        """Print a provider status table."""
        print("\n  LLM Provider Status:")
        print(f"  {'Provider':<20} {'Available':<12} {'Error'}")
        print(f"  {'-'*20} {'-'*12} {'-'*30}")
        for s in self.get_providers_status():
            status = "[ONLINE]" if s.available else "[OFFLINE]"
            error = s.error[:50] if s.error else ""
            print(f"  {s.display_name:<20} {status:<12} {error}")


# ─── Singleton ─────────────────────────────────────────────

_dispatcher: Optional[LLMDispatcher] = None


def get_dispatcher(config_path: str = None) -> LLMDispatcher:
    """Get or create the global LLM dispatcher."""
    global _dispatcher
    if _dispatcher is None or config_path:
        _dispatcher = LLMDispatcher(config_path)
    return _dispatcher
