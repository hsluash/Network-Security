""""
Steps:
1. Load numpy array data from train and test npy files
2. train array : X_train and y_train and same for test
3. run various models and get the best model on train set and save the 
best model as pickle file and save the metric artifact on train data
4. use that best model and calculate metric on test data and store the metric artifact
"""
import os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.metrics import r2_score
import mlflow
from urllib.parse import urlparse

from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.common import load_object, save_object, load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
'''
os.environ['MLFLOW_TRACKING_URI'] = "https://dagshub.com/AishwaryaK/datascienceproject.mlflow"
os.environ['MLFLOW_TRACKING_USERNAME'] = "AishwaryaK"
os.environ['MLFLOW_TRACKING_PASSWORD'] = "22c5c718ae343642b1bdef12f72f113ba1a3e081"
'''

class ModelTrainer:
    def __init__(self, model_training_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_training_config = model_training_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self,best_model,classificationmetric):
        #mlflow.set_registry_uri("https://dagshub.com/AishwaryaK/datascienceproject.mlflow")
        #tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score

            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model")
            """
            # Model registry does not work with file store
            if tracking_url_type_store != "file":

                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model)
            else:
                mlflow.sklearn.log_model(best_model, "model")
        """

    def train_model(self, x_train, y_train, x_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
        }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }
        model_report: dict = evaluate_models(X_train=x_train, y_train=y_train, 
                                             X_test=x_test, y_test=y_test, 
                                             models=models, params=params)
        
        ## To get best model score from dict
        best_model_score = max(sorted(model_report.values()))
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]

        y_train_pred = best_model.predict(x_train)
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
        self.track_mlflow(best_model,classification_train_metric)


        y_test_pred = best_model.predict(x_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        ## Track the mlflow
        self.track_mlflow(best_model,classification_test_metric)

        preprocessor = load_object(filepath=self.data_transformation_artifact.transformed_object_filepath)
        model_dir_path = os.path.dirname(self.model_training_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_training_config.trained_model_file_path, obj=network_model)

        ## Model Trainer Artifact
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file=self.model_training_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )
        logging.info(f"Model Trainer Artifact: {model_trainer_artifact}")
        return model_trainer_artifact

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_filepath
            test_file_path = self.data_transformation_artifact.transformed_test_filepath

            # loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
