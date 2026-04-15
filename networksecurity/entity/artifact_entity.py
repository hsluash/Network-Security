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

@dataclass
class DataTransformationArtifact:
    transformed_object_filepath: str
    transformed_train_filepath: str
    transformed_test_filepath: str

@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float

@dataclass
class ModelTrainerArtifact:
    trained_model_file: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact