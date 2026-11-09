class CharacterEstimateTokenizer:
    """Rough character heuristic; never claim this is an exact model token count."""
    name = "character-estimate"
    count_kind = "estimate"

    def count(self, text: str) -> int:
        return 0 if not text else max(1, (len(text) + 3) // 4)
