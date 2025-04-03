from enum import Enum
import json
from pathlib import Path

_JSON_PATH = Path("./config/llm_prompts.json")


class AugmentationType(Enum):
    EMOTIONAL_TONE = 0
    PERSPECTIVE_FLIP = 1
    POLARITY_ADJUST = 2
    TENSE_SHIFTING = 3
    PARAPHRASING = 4
    SENTENCE_REORDERING = 5

    def input_directory(self) -> str:
        path = "./data/element"

        match self:
            case AugmentationType.EMOTIONAL_TONE:
                return path + "raw/"
            case AugmentationType.PERSPECTIVE_FLIP:
                return path + "augmented/emotional_tone/"
            case AugmentationType.POLARITY_ADJUST:
                return path + "augmented/perspective_flip/"
            case AugmentationType.TENSE_SHIFTING:
                return path + "augmented/polarity_adjust/"
            case AugmentationType.PARAPHRASING:
                return path + "augmented/tense_shift/"
            case AugmentationType.SENTENCE_REORDERING:
                return path + "augmented/paraphrase/"
            case _:
                raise ValueError(f"Unknown AugmentationType: {self}")

    def output_directory(self) -> str:
        path = "./data/element"

        match self:
            case AugmentationType.EMOTIONAL_TONE:
                return path + "augmented/emotional_tone/"
            case AugmentationType.PERSPECTIVE_FLIP:
                return path + "augmented/perspective_flip/"
            case AugmentationType.POLARITY_ADJUST:
                return path + "augmented/polarity_adjust/"
            case AugmentationType.TENSE_SHIFTING:
                return path + "augmented/tense_shift/"
            case AugmentationType.PARAPHRASING:
                return path + "augmented/paraphrase/"
            case AugmentationType.SENTENCE_REORDERING:
                return path + "augmented/sentence_reordering/"
            case _:
                raise ValueError(f"Unknown AugmentationType: {self}")

    def get_prompt(self) -> str:
        with _JSON_PATH.open("r", encoding="utf-8") as f:
            content = f.read()
            data: dict = json.loads(content) if content.strip() else None

        if data is None:
            raise ValueError("No data found in the JSON file.")

        specific = data.get(self.name.lower())
        if not specific:
            raise ValueError(f"No prompt data found for augmentation type: {self.name.lower()}")

        return data["precursor"] + specific