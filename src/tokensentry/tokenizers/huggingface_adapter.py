"""Hugging Face tokenizer adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tokensentry.config import get_config
from tokensentry.models import TokenCountKind
from tokensentry.tokenizers.registry import BaseTokenizer, register_tokenizer


class HuggingFaceTokenizer(BaseTokenizer):
    """Hugging Face tokenizer adapter."""

    name = "huggingface"
    version = "1.0"
    count_kind = TokenCountKind.EXACT

    def __init__(
        self,
        model_id: str,
        *,
        revision: str | None = None,
        use_fast: bool = True,
        trust_remote_code: bool = False,
        local_files_only: bool | None = None,
    ) -> None:
        """Initialize HF tokenizer.

        Args:
            model_id: Model identifier on HF Hub or local path
            revision: Model revision
            use_fast: Use fast tokenizer if available
            trust_remote_code: Trust remote code (required for some models)
            local_files_only: Force local files only (uses config default if None)
        """
        self.model_id = model_id
        self.revision = revision
        self.use_fast = use_fast
        self.trust_remote_code = trust_remote_code
        config = get_config()
        self.local_files_only = (
            local_files_only
            if local_files_only is not None
            else config.hf_offline_mode
        )
        self._tokenizer = None

    def _get_tokenizer(self):
        """Lazy-load HF tokenizer."""
        if self._tokenizer is None:
            try:
                from transformers import AutoTokenizer
            except ImportError as e:
                raise ImportError(
                    "transformers not installed. "
                    "Install with: pip install tokensentry[huggingface-tokenizer]"
                ) from e

            kwargs: dict[str, Any] = {
                "revision": self.revision,
                "use_fast": self.use_fast,
                "trust_remote_code": self.trust_remote_code,
                "local_files_only": self.local_files_only,
            }

            # Handle local paths
            if Path(self.model_id).exists():
                kwargs["local_files_only"] = True

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, **kwargs)

        return self._tokenizer

    def count(self, text: str) -> int:
        """Count tokens using HF tokenizer."""
        if not text:
            return 0
        tokenizer = self._get_tokenizer()
        # Use encode without special tokens for accurate count
        return len(tokenizer.encode(text, add_special_tokens=False))

    @property
    def encoding(self) -> str:
        """Return tokenizer type."""
        tokenizer = self._get_tokenizer()
        return tokenizer.__class__.__name__


# Register common models
common_models = [
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Llama-2-70b-hf",
    "meta-llama/Meta-Llama-3-8B",
    "meta-llama/Meta-Llama-3-70B",
    "mistralai/Mistral-7B-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mixtral-8x7B-v0.1",
    "google/gemma-7b",
    "google/gemma-7b-it",
    "microsoft/Phi-3-mini-4k-instruct",
    "microsoft/Phi-3-medium-4k-instruct",
    "Qwen/Qwen2-7B",
    "Qwen/Qwen2-7B-Instruct",
    "tiiuae/falcon-7b",
    "tiiuae/falcon-40b",
]

for model in common_models:
    # Register with short name
    short = model.split("/")[-1].lower()
    register_tokenizer(f"hf:{short}", lambda m=model: HuggingFaceTokenizer(m))
    register_tokenizer(f"hf:{model}", lambda m=model: HuggingFaceTokenizer(m))