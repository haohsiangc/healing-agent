import logging
import os
from pathlib import Path
import pandas as pd
import jieba
import numpy as np
from typing import List, Tuple

logger = logging.getLogger(__name__)


class EmotionService:
    """
    Chinese (Traditional/Simplified) sentiment analysis using jieba word-segmentation
    and the CVAW corpus for Valence-Arousal scores.
    """

    def __init__(self, cvaw_path: str = "./CVAW_all_SD.csv"):
        self.cvaw_dict: dict = {}
        self._load_corpus(cvaw_path)

    def _load_corpus(self, path: str):
        if not Path(path).exists():
            logger.warning("CVAW corpus not found at %s – emotion analysis disabled.", path)
            return
        try:
            df = pd.read_csv(path, delimiter="\t")
            self.cvaw_dict = dict(
                zip(df["Word"], zip(df["Valence_Mean"], df["Arousal_Mean"]))
            )
            logger.info("Loaded %d words from CVAW corpus.", len(self.cvaw_dict))
        except Exception as exc:
            logger.error("Failed to load CVAW corpus: %s", exc)

    def analyze(
        self,
        text: str,
        valence_history: List[float],
        arousal_history: List[float],
        conversation_turns: int,
        window: int = 3,
        trigger_min_turns: int = 6,
        arousal_low: float = 4.7,
        arousal_high: float = 5.4,
    ) -> Tuple[float, float, List[float], List[float], int, bool]:
        """
        Returns:
            avg_valence, avg_arousal, updated_valence_history, updated_arousal_history,
            new_turn_count, should_trigger_meditation
        """
        conversation_turns += 1
        new_valence: List[float] = list(valence_history)
        new_arousal: List[float] = list(arousal_history)

        if self.cvaw_dict:
            words = list(jieba.cut(text))
            for word in words:
                if word in self.cvaw_dict:
                    v, a = self.cvaw_dict[word]
                    new_valence.append(v)
                    new_arousal.append(a)

        # Keep only last `window` entries
        new_valence = new_valence[-window:]
        new_arousal = new_arousal[-window:]

        if not new_valence:
            return 5.0, 5.0, new_valence, new_arousal, conversation_turns, False

        avg_valence = float(np.mean(new_valence))
        avg_arousal = float(np.mean(new_arousal))

        trigger = (
            conversation_turns >= trigger_min_turns
            and arousal_low <= avg_arousal <= arousal_high
        )

        return avg_valence, avg_arousal, new_valence, new_arousal, conversation_turns, trigger
