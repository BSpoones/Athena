
MAX_PER_REQUEST = 25

JSON_PRECURSOR = """Return the output **strictly as a JSON array of strings**, with no explanations or extra text"""
PARAPHRASING_PRECURSOR = """
Generate up to 5 paraphrased versions of each sentence while keeping the original meaning
If you are unable to generate 5 paraphrased versions, please return a minimum of 3
"""
PRONOUN_SWAP_PRECURSOR = """
Generate versions of each sentence with relevant pronouns swapped
"""
TENSE_SHIFT_PRECURSOR = """
Generate versions of each sentence to change the tense. Each example should be changed to cover past, present, future,
and perfect tense. Where this is not appropriate, do as many tenses as you can
"""
CONVO_FILTER_PRECURSOR = """
Generate at least 3 variations of each sentence, adding conversational fillers and emphasis wording to add additional meaning to
each sentence
"""
DEFINITENESS_CHANGES_PRECURSOR = """
Generate at least 3 versions of each sentence with changes to the definiteness of the sentence. This can include changing the certainty
levels. 
"""


class Augmentation:
    
    def __init__(self):
        ...
        
        
    def paraphrase(self):
        ...

    def pronoun_swap(self):
        ...

    def tense_shift(self):
        ...

    def convo_fillers(self):
        ...

    def definiteness_changes(self):
        ...

    def _request(self):
        ...
    
