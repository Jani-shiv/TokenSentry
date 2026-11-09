"""SentencePiece tokenizer adapter."""

from __future__ import annotations

from pathlib import Path

from tokensentry.models import TokenCountKind
from tokensentry.tokenizers.registry import BaseTokenizer


class SentencePieceTokenizer(BaseTokenizer):
    """SentencePiece tokenizer adapter."""

    name = "sentencepiece"
    version = "1.0"
    count_kind = TokenCountKind.EXACT

    def __init__(
        self,
        model_path: str | Path,
        *,
        nbest_size: int = -1,
        alpha: float = 0.1,
        enable_sampling: bool = False,
    ) -> None:
        """Initialize SentencePiece tokenizer.

        Args:
            model_path: Path to .model file
            nbest_size: N-best size for sampling
            alpha: Smoothing parameter for sampling
            enable_sampling: Enable sampling mode
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"SentencePiece model not found: {self.model_path}")
        self.nbest_size = nbest_size
        self.alpha = alpha
        self.enable_sampling = enable_sampling
        self.model_id = str(self.model_path)
        self.encoding = "sentencepiece"
        self._processor = None

    def _get_processor(self):
        """Lazy-load SentencePiece processor."""
        if self._processor is None:
            try:
                import sentencepiece as spm
            except ImportError as e:
                raise ImportError(
                    "sentencepiece not installed. "
                    "Install with: pip install tokensentry[sentencepiece]"
                ) from e

            self._processor = spm.SentencePieceProcessor()
            self._processor.Load(str(self.model_path))

        return self._processor

    def count(self, text: str) -> int:
        """Count tokens using SentencePiece."""
        if not text:
            return 0
        processor = self._get_processor()
        if self.enable_sampling:
            return len(processor.SampleEncodeAsPieces(text, self.nbest_size, self.alpha))
        return len(processor.EncodeAsPieces(text))

    def encode_as_ids(self, text: str) -> list[int]:
        """Encode text as token IDs."""
        if not text:
            return []
        processor = self._get_processor()
        return processor.EncodeAsIds(text)

    def decode(self, ids: list[int]) -> str:
        """Decode token IDs to text."""
        processor = self._get_processor()
        return processor.DecodeIds(ids)


# Register with model path if provided via environment
# Users can register their own models like:
# register_tokenizer("spm:my-model", lambda: SentencePieceTokenizer("/path/to/model.model"))