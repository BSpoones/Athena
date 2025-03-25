from enum import Enum
import json
from pathlib import Path

_JSON_PATH = Path("./config/llm_prompts.json")

class AugmentationType(Enum):
    INSULT_CHANGE = 0
    EMPHASIS_WORDING = 1
    TENSE_SHIFTING = 2
    PARAPHRASING = 3

    def get_prompt(self) -> str:
        with _JSON_PATH.open("r", encoding="utf-8") as f:
            content = f.read()
            data: dict[any] = json.loads(content) if content.strip() else None

        if data is None:
            raise ValueError("No data found in the JSON file.")

        specific = data[self.name.lower()]
        if not specific:
            raise ValueError("No data found for the specific augmentation type.")

        return data["precursor"] + specific
