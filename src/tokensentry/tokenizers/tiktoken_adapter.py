"""Tiktoken adapter for OpenAI-compatible tokenization."""

from __future__ import annotations

from tokensentry.models import TokenCountKind
from tokensentry.tokenizers.registry import BaseTokenizer, register_tokenizer


class TiktokenTokenizer(BaseTokenizer):
    """OpenAI tiktoken tokenizer adapter."""

    name = "tiktoken"
    version = "1.0"
    count_kind = TokenCountKind.EXACT

    def __init__(self, encoding: str = "cl100k_base") -> None:
        """Initialize with specific encoding.

        Args:
            encoding: Tiktoken encoding name (e.g., cl100k_base, p50k_base, r50k_base, o200k_base)
        """
        self.encoding_name = encoding
        self.encoding = encoding
        self.model_id = encoding
        self._encoder = None

    def _get_encoder(self):  # type: ignore[return]
        """Lazy-load tiktoken encoder."""
        if self._encoder is None:
            try:
                import tiktoken  # type: ignore[import-not-found]

                self._encoder = tiktoken.get_encoding(self.encoding_name)
            except ImportError as e:
                raise ImportError(
                    "tiktoken not installed. "
                    "Install with: pip install tokensentry[openai-tokenizer]"
                ) from e
        return self._encoder

    def count(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if not text:
            return 0
        encoder = self._get_encoder()  # type: ignore[assignment]
        return len(encoder.encode(text))  # type: ignore[no-untyped-call]

    def get_model_encoding(model: str) -> str:
        """Map model name to tiktoken encoding."""
        model_lower = model.lower()
        gpt4_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"]
        if any(m in model_lower for m in gpt4_models):
            return "cl100k_base"
        davinci_models = ["text-davinci", "text-curie", "text-babbage", "text-ada", "code-davinci"]
        if any(m in model_lower for m in davinci_models):
            return "p50k_base"
        if "gpt2" in model_lower:
            return "gpt2"
        # Default to cl100k_base for newer models
        return "cl100k_base"


# Register common encodings
for enc in ["cl100k_base", "p50k_base", "r50k_base", "o200k_base", "gpt2"]:
    register_tokenizer(f"tiktoken:{enc}", lambda e=enc: TiktokenTokenizer(e))  # type: ignore[arg-type]

# Register model aliases
model_encodings = {
    "gpt-4": "cl100k_base",
    "gpt-4o": "cl100k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-davinci-003": "p50k_base",
    "text-davinci-002": "p50k_base",
    "code-davinci-002": "p50k_base",
}
for model, enc in model_encodings.items():
    register_tokenizer(f"tiktoken:{model}", lambda e=enc: TiktokenTokenizer(e))  # type: ignore[arg-type]