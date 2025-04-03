import csv

import emoji
from pandas import DataFrame, Series
from spellchecker import SpellChecker

import enums
from data import AUGMENT_PATH, NORMALISATION_PATH, SLANG_PATH, LOCALISATION_PATH, PUNCTUATION_PATH, ELEMENT_PATHS
import pandas as pd



def text_transform(text: str) -> str:
    """
    Converting to lowercase
    Trimming whitespace
    """
    return text \
        .lower() \
        .strip()


def emoji_replace(text: str) -> str:
    return emoji.demojize(text, delimiters=(" ", " "))  # 😂 -> joy


class Normaliser:

    def __init__(self, element_type: str):
        self.element_type = element_type
        file = element_type + ".csv"

        self.input = AUGMENT_PATH + file
        self.output = NORMALISATION_PATH + file

        self.data: DataFrame = pd.read_csv(self.input)

        self.slang: Series = pd.read_json(SLANG_PATH, orient='index', typ='series')
        self.localisation: Series = pd.read_json(LOCALISATION_PATH, orient='index', typ='series')
        self.punctuation: Series = pd.read_json(PUNCTUATION_PATH, orient='index', typ='series')
        self.spell_check = SpellChecker()
        self._spell_cache = {}

    def _write_csv(self):
        output_df = self.data[["sentence"]].copy()
        output_df["is_type"] = (self.data["type"] > 0).astype(int)

        # Open the file and write the header manually
        with open(self.output, 'w', newline='', encoding='utf-8') as f:
            f.write(','.join(output_df.columns) + '\n')  # Manually write the header
            output_df.to_csv(f, index=False, header=False, quoting=4) # Quote strings

    def normalise(self):
        print(f"Removing invalid data")
        self.invalid_removal()

        print(f"Starting sentence cleaning")
        self.data["sentence"] = self.data["sentence"].swifter.apply(self.clean_sentence)
        print(f"Finished sentence cleaning")

        self.duplicate_removal()
        self._write_csv()

    def clean_sentence(self, text: str) -> str:
        text = text_transform(text)
        text = emoji_replace(text)
        text = self.replace_slang(text)
        text = self.replace_localisation(text)
        text = self.replace_punctuation(text)
        text = self.spellcheck(text)
        return text

    def replace_slang(self, text: str) -> str:
        return " ".join([self.slang.get(word.lower(), word) for word in text.split()])

    def replace_localisation(self, text: str) -> str:
        return " ".join([self.localisation.get(word.lower(), word) for word in text.split()])

    def replace_punctuation(self, text: str) -> str:
        return " ".join([self.punctuation.get(word.lower(), word) for word in text.split()])

    def duplicate_removal(self):
        self.data.drop_duplicates(subset=['sentence'], inplace=True)

    def invalid_removal(self):
        self.data = self.data[self.data["sentence"].str.contains(r"[a-zA-Z]", na=False)]

    def spellcheck(self, text: str) -> str:
        words = text.split()
        known = self.spell_check.known(words)

        corrected = []
        append = corrected.append

        for word in words:
            if word in known or len(word) <= 2 or not word.isalpha():
                append(word)
            else:
                if word in self._spell_cache:
                    correction = self._spell_cache[word]
                else:
                    correction = self.spell_check.correction(word)
                    self._spell_cache[word] = correction
                append(correction if correction else word)

        return " ".join(corrected)


def main():
    for element, name in ELEMENT_PATHS.items():
        print(f"Normalising {name}")
        Normaliser(name).normalise()
        print(f"Normalisation complete!")


if __name__ == "__main__":
    main()
