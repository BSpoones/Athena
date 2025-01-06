import matplotlib.pyplot as plt
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, lit, rand
from pyspark.ml.tuning import ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import DataFrame
from .GaslightType import GaslightType
from ..RelationType import RelationType
from ..ResponseType import ResponseType
from ..RoleType import RoleType
from ..SourceType import SourceType
import contractions

GASLIGHT_CONTEXT_FILE = ""
CONVERSATION_ID, SENDER_ROLE, RECIEVER_ROLE, MESSAGE_POSITION, PREVIOUS_RELATION, MESSAGE, IS_MANIPULATIVE, MANIPULATION_TYPE, SENTIMENT_SCORE, RESPONSE_TYPE, POWER_IMBALANCE, SOURCE_TYPE, HAS_VICTIM = \
    "","","","","","","","","",""


class GaslightingData:
    def __init__(self):
        self.SPARK = ""
        
    def read_file(
        self,
        file: str,
        *cols: str
        ) -> DataFrame:
        """
        Allows for any space separated text file to be loaded as a 
        spark dataframe, using *args to load column names
        """

        return self.SPARK.read \
            .option("delimiter", " ") \
            .csv(file, inferSchema=True, header=False) \
            .toDF(*cols)
        
    def load_single() -> DataFrame:
        ...
        
    def load_context(self) -> DataFrame:
        return self.load(
            # File location
            GASLIGHT_CONTEXT_FILE,
            # Column names
            CONVERSATION_ID, SENDER_ROLE, RECIEVER_ROLE, MESSAGE_POSITION, 
            PREVIOUS_RELATION, MESSAGE, IS_MANIPULATIVE, MANIPULATION_TYPE, 
            SENTIMENT_SCORE, RESPONSE_TYPE, POWER_IMBALANCE, SOURCE_TYPE, HAS_VICTIM
        )
        
    def sanitise_single(self, data: DataFrame) -> DataFrame:
        """
        Sanitises the gaslighting single dataset, removing any of the following
         - Rows where the RelationType is invalid
         - Rows where the ResponseType is invalid
         - Rows where the RoleType is invalid
         - Rows where the SourceType is invalid
         - Rows where the GaslightType is invalid
         - Any rows with missing data in any column
         - Ensuring the data types are valid (e.g IDs are int, trust state is a boolean)
         - Ensuring none of the applicable columns are negative
        """
        
        print("Sanitising the Single Gaslighting Dataset\n")
        
        row_count = data.count()
        print(f"Initial rows: {row_count:,}")
                
        # Removing all missing data
        trust_df = trust_df.dropna()
        row_after_missing = trust_df.count()
        
        print(f"Missing rows removed: {row_count - row_after_missing}")
        row_count = row_after_missing
    
        # Data type validation
        trust_df = trust_df.filter(
            (col(MANIPULATION_TYPE) >= GaslightType.min()) & (col(MANIPULATION_TYPE) <= GaslightType.max()) &
            (col(PREVIOUS_RELATION) >= RelationType.min()) & (col(PREVIOUS_RELATION) <= RelationType.max()) &
            (col(RESPONSE_TYPE) >= ResponseType.min()) & (col(RESPONSE_TYPE) <= ResponseType.max()) &
            (col(SENDER_ROLE) >= RoleType.min()) & (col(SENDER_ROLE) <= RoleType.max()) &
            (col(RECIEVER_ROLE) >= RoleType.min()) & (col(RECIEVER_ROLE) <= RoleType.max()) &
            (col(SOURCE_TYPE) >= SourceType.min()) & (col(SOURCE_TYPE) <= SourceType.max()) &
            
            # Ensuring correct data type
            (col(MANIPULATION_TYPE).cast("int").isNotNull()) &
            (col(PREVIOUS_RELATION).cast("int").isNotNull()) &
            (col(RESPONSE_TYPE).cast("int").isNotNull()) &
            (col(SENDER_ROLE).cast("int").isNotNull()) &
            (col(RECIEVER_ROLE).cast("int").isNotNull()) 
        )
        row_after_data = trust_df.count()
        print(f"Invalid data removed: {row_count - row_after_data}")
        row_count = row_after_data
        
        print(f"Sanitisation complete! Total clean records: {row_count:,}")
        
        return trust_df
    
            
    def normalise_text(self, data: DataFrame) -> DataFrame:
        text_col = data.select(MESSAGE)
        
        # Remove contractions (it's -> it is) for clarity
        text_col = contractions.fix(text_col)
        
        # TODO -> Replace informal words (u -> you)
        # TODO -> Regex for multiple spaces
        # TODO -> Remove trailing spaces
        # TODO -> Emoji? Remove / Convert?