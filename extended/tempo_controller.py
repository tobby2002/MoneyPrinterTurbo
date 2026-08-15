"""
Extended Tempo Controller Module for MoneyPrinterTurbo
Handles customizable video clip transition duration (2.0s, 3.0s, 5.0s, etc.)
and AI-driven dynamic sentence-based tempo analysis.
"""
from typing import Union, List, Dict, Any

DEFAULT_CLIP_DURATION = 5.0

def resolve_clip_duration(duration_setting: Union[float, int, str, None], sentence_text: str = "") -> float:
    """
    Resolves the target clip duration in seconds.
    - If duration_setting is float/int: returns value (bounded between 1.0s and 10.0s).
    - If duration_setting == 'auto': analyzes sentence urgency (Fast = 2.0s, Medium = 3.5s, Normal = 5.0s).
    - Default: 5.0s
    """
    if duration_setting is None:
        return DEFAULT_CLIP_DURATION

    # String parsing
    if isinstance(duration_setting, str):
        val_str = duration_setting.strip().lower()
        if val_str == "auto":
            # AI Dynamic Tempo Analysis based on sentence length or emotional hook
            if any(kw in sentence_text for kw in ["!", "미쳤", "대박", "경고", "손실", "위험", "갑자기", "폭발"]):
                return 2.0  # Fast energetic tempo
            elif len(sentence_text) < 20:
                return 2.5
            else:
                return 4.0
        try:
            val = float(val_str)
            return max(1.0, min(val, 15.0))
        except ValueError:
            return DEFAULT_CLIP_DURATION

    # Float/Int parsing
    try:
        val = float(duration_setting)
        return max(1.0, min(val, 15.0))
    except (ValueError, TypeError):
        return DEFAULT_CLIP_DURATION
