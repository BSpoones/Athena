import csv
import pandas as pd


from lib.processing.Normaliser import Normaliser, text_transform, emoji_replace

class DummySpellChecker:
    def known(self, words):
        # Consider "mispelled" as unknown and every other word as known.
        return {word for word in words if word != "mispelled"}
    def correction(self, word):
        if word == "mispelled":
            return "misspelled"
        return word


class DummyNormaliser(Normaliser):
    def __init__(self):
        # Avoiding super().__init__ to avoid IO
        self.slang = {"brb": "be right back"}
        self.localisation = {"u": "you"}
        self.punctuation = {"...": ""}
        self.spell_check = DummySpellChecker()
        self._spell_cache = {}
        self.data = pd.DataFrame()



def test_text_transform():
    # Standard case: trims whitespace and lowercases
    assert text_transform("  HELLO World  ") == "hello world"
    # Already transformed string
    assert text_transform("test") == "test"
    # Empty string
    assert text_transform("   ") == ""


def test_emoji_replace():
    # No emoji: string remains unchanged
    assert emoji_replace("Hello world") == "Hello world"
    # With emoji: check that the descriptive text appears
    result = emoji_replace("Hello 😂")
    # With delimiters (" ", " "), emoji.demojize should yield something like " joy " without colons
    assert "joy" in result
    # Empty string.
    assert emoji_replace("") == ""

def test_replace_slang():
    normaliser = DummyNormaliser()
    # "brb" should be replaced by "be right back"
    result = normaliser.replace_slang("brb I will be there")
    assert "be right back" in result
    # Unmapped words remain unchanged
    assert "I" in result
    # Empty input
    assert normaliser.replace_slang("") == ""


def test_replace_localisation():
    normaliser = DummyNormaliser()
    result = normaliser.replace_localisation("u are here")
    # "u" should be replaced with "you"
    assert "you" in result
    # Empty input
    assert normaliser.replace_localisation("") == ""


def test_replace_punctuation():
    normaliser = DummyNormaliser()
    assert normaliser.replace_punctuation("Wait...") == "Wait..."
    # Here we check the mapping directly:
    assert normaliser.replace_punctuation("...") == ""
    # Also test empty input.
    assert normaliser.replace_punctuation("") == ""


def test_spellcheck():
    normaliser = DummyNormaliser()
    # Known word should not change
    assert normaliser.spellcheck("hello") == "hello"
    # "mispelled" should be corrected
    assert normaliser.spellcheck("mispelled") == "misspelled"
    # Mixed sentence
    result = normaliser.spellcheck("hello mispelled an")
    assert result == "hello misspelled an"
    # Empty input
    assert normaliser.spellcheck("") == ""


def test_clean_sentence():
    normaliser = DummyNormaliser()
    input_text = "  BRB 😂, u are mispelled...  "
    result = normaliser.clean_sentence(input_text)
    # Verify that all replacements happened.
    assert "be right back" in result  # slang replaced
    assert "joy" in result             # emoji replaced
    assert "you" in result             # localisation replaced
    assert result == result.strip()
    # "mispelled..." remains as is because punctuation stops spellcheck
    assert "mispelled" in result


def test_invalid_removal():
    normaliser = DummyNormaliser()
    # Create a dataframe with various sentences
    df = pd.DataFrame({
        "sentence": ["12345", "!!!", "abc", "","---","   ", "valid sentence"],
        "type": [0,0,0,0,0,0,0] # Not used
    })
    normaliser.data = df.copy()
    normaliser.invalid_removal()
    # Only rows with at least one alphabet character should remain.
    expected = ["abc", "valid sentence"]
    assert list(normaliser.data["sentence"]) == expected


def test_duplicate_removal():
    normaliser = DummyNormaliser()
    df = pd.DataFrame({
        "sentence": ["hello", "world", "hello", "test"],
        "type": [1, 0, 1, 0]
    })
    normaliser.data = df.copy()
    normaliser.duplicate_removal()
    # Check that duplicates are removed. Order is preserved
    unique_sentences = normaliser.data["sentence"].tolist()
    assert sorted(unique_sentences) == sorted(["hello", "world", "test"])


def test_write_csv(tmp_path):
    normaliser = DummyNormaliser()
    df = pd.DataFrame({
        "sentence": ["hello", "world"],
        "type": [1, 0]
    })
    normaliser.data = df.copy()
    output_file = tmp_path / "output.csv"
    normaliser.output = str(output_file)
    normaliser._write_csv()
    # Read back the CSV and check contents
    result_df = pd.read_csv(str(output_file), quoting=csv.QUOTE_ALL)
    # Ensure that the expected columns exist
    assert "sentence" in result_df.columns
    assert "is_type" in result_df.columns
    # is_type should be 1 where type > 0, else 0
    assert result_df["is_type"].tolist() == [1, 0]
