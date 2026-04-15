from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    trained_filepath: str
    test_filepath: str

@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_filepath: str
    valid_test_filepath: str
    invalid_train_filepath: str
    invalid_test_filepath: str
    drift_report_filepath: str