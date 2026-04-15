"""
Steps:
1. Same schema = same no. of features
2. Data Drift = change in distribution of data
3. validate no. of columns, numerical column exists or not ..
"""
import sys
import os
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import SCHEMA_FILEPATH
from networksecurity.utils.common import read_yaml_file, write_yaml_file

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILEPATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(filepath: str) -> pd.DataFrame:
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            total_cols = len(self._schema_config)
            logging.info(f"Required number of columns: {total_cols}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len(dataframe.columns) == total_cols:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def detect_database_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report.update({column:{
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status": is_found
                }})
            
            drift_report_filepath = self.data_validation_config.drift_report_file_path

            dir_path = os.path.dirname(drift_report_filepath)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(content=report, filepath=drift_report_filepath)

        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def inititate_data_validation(self):
        try:
            # read the train and test files
            train_file_path = self.data_ingestion_artifact.trained_filepath
            test_filepath = self.data_ingestion_artifact.test_filepath

            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_filepath)

            # validate no. of columns
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message="Train dataframe does not contain all columns.\n"
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message="Test dataframe does not contain all columns.\n"

            # check if numerical column exist
            numerical_cols = train_dataframe.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) == 0:
                error_message="Train dataframe does not have numerical columns.\n"
            logging.info("Train dataframe has numerical columns")

            # check data drift
            status = self.detect_database_drift(base_df=train_dataframe, current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_filepath=self.data_ingestion_artifact.trained_filepath,
                valid_test_filepath=self.data_ingestion_artifact.test_filepath,
                invalid_train_filepath=None,
                invalid_test_filepath=None,
                drift_report_filepath=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)