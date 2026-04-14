import os
import sys

"""
Defining common constant variable for training pipeline
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME: str = "NetworkSecurity"
ARTIFACT_DIR: str = "Artifacts"
FILENAME: str = "phishingData.csv"

TRAIN_FILENAME: str = "train.csv"
TEST_FILENAME: str = "test.csv"

"""
Data Ingestion related constant start with DATA_INGESTION VAR NAME
"""
DATA_INGESTION_COLLECTION_NAME: str = "NetworkData"
DATA_INGESTION_DATABASE_NAME: str = "Bootcamp"
DATA_INGESTION_DIRNAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2