from enums import BlameType, ComparativeJustificationType, DenialType, DownplayingType, EmotionalConnectionType, \
    EmotionalLeverageType, ExpectationType, InvalidationType, MemoryDistortionType, PowerImbalanceType, ThreatType

ELEMENT_PATHS = {
    BlameType: "blame",
    ComparativeJustificationType: "comparative_justification",
    DenialType: "denial",
    DownplayingType: "downplaying",
    EmotionalConnectionType: "emotional_connection",
    EmotionalLeverageType: "emotional_leverage",
    ExpectationType: "expectation",
    InvalidationType: "invalidation",
    MemoryDistortionType: "memory_distortion",
    PowerImbalanceType: "power_imbalance",
    ThreatType: "threat"
}

RAW_PATH = "./data/element/raw/"
AUGMENT_PATH = "./data/element/augmented/paraphrase/"
NORMALISATION_PATH = "./data/element/normalised/"

SLANG_PATH = "./data/datasets/slang/slang.json"
LOCALISATION_PATH = "./data/datasets/localisation/localisation.json"
PUNCTUATION_PATH = "./data/datasets/punctuation/punctuation.json"
