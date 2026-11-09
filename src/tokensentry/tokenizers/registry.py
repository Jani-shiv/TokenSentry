"""Tokenizer registry and base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from tokensentry.models import TokenCountKind, TokenizerInfo


class BaseTokenizer(ABC):
    """Abstract base class for tokenizers."""

    name: str = "base"
    version: str | None = None
    model_id: str | None = None
    encoding: str | None = None
    count_kind: TokenCountKind = TokenCountKind.ESTIMATE

    @abstractmethod
    def count(self, text: str) -> int:
        """Count tokens in text."""
        pass

    def get_info(self) -> TokenizerInfo:
        """Get tokenizer metadata."""
        return TokenizerInfo(
            name=self.name,
            version=self.version,
            model_id=self.model_id,
            encoding=self.encoding,
            count_kind=self.count_kind,
            is_exact=self.count_kind == TokenCountKind.EXACT,
        )


class CharacterEstimateTokenizer(BaseTokenizer):
    """Rough character heuristic; never claim this is an exact model token count."""

    name = "character-estimate"
    version = "1.0"
    count_kind = TokenCountKind.ESTIMATE

    def count(self, text: str) -> int:
        return 0 if not text else max(1, (len(text) + 3) // 4)


# Registry
_TOKENIZERS: dict[str, type[BaseTokenizer]] = {
    "character-estimate": CharacterEstimateTokenizer,
}


def register_tokenizer(name: str, tokenizer_cls: type[BaseTokenizer]) -> None:
    """Register a tokenizer class."""
    if name in _TOKENIZERS:
        raise ValueError(f"Tokenizer already registered: {name}")
    _TOKENIZERS[name] = tokenizer_cls


def get_tokenizer(name: str, **kwargs: Any) -> BaseTokenizer:
    """Get tokenizer instance by name."""
    if name not in _TOKENIZERS:
        available = ", ".join(sorted(_TOKENIZERS.keys()))
        raise ValueError(f"Unknown tokenizer: {name}. Available: {available}")
    return _TOKENIZERS[name](**kwargs)


def list_tokenizers() -> list[str]:
    """List available tokenizer names."""
    return sorted(_TOKENIZERS.keys())


def load_tokenizer_adapters() -> None:
    """Load optional tokenizer adapters (tiktoken, HF, SentencePiece)."""
    # Tiktoken adapter
    try:
        from tokensentry.tokenizers.tiktoken_adapter import TiktokenTokenizer  # noqa: F401
    except ImportError:
        pass

    # Hugging Face adapter
    try:
        from tokensentry.tokenizers.huggingface_adapter import HuggingFaceTokenizer  # noqa: F401
    except ImportError:
        pass

    # SentencePiece adapter
    try:
        from tokensentry.tokenizers.sentencepiece_adapter import SentencePieceTokenizer  # noqa: F401
    except ImportError:
        pass


# Load adapters on module import
load_tokenizer_adapters()