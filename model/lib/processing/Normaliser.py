class Normaliser:
    
    def __init__(self, file: str):
        self.file = file
        self.data = None
        self.output = None
        
    @classmethod
    def from_file(cls, path: str) -> "Normaliser":
        ...
    
    def load(self):
        # Loads file and returns a dataframe
        ...
        
    def text_transformation(self):
        # Convert text to lowercase
        # Remove non-alphanumeric / punctiation characters
        # Regex to remove multiple spcaes
        # Remove trailing spaces
        # Converting emoji to :joy:
        ...
    
    def remove_contractions(self):
        # Remove contractions (it's -> it is)
        ...
        
    def standardise_punctuation(self):
        # Standardise punctiation e.g ... -> .
        ...
        
    def character_normalisation(self):
        # Standardise special characters e.g % -> percent
        ...
        
    def art_normalisation(self):
        # E.g converting :) -> smiley_face
        ...
        
    def lemmitisation(self):
        # E.g running -> run
        ...
        
    def spellcheck(self):
        # Fix common spelling mistakes
        ...
        
    def slang_conversion(self):
        # Normalise slang e.g u -> you
        ...
        
    def remove_duplicates(self):
        ...