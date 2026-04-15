import os, sys
import yaml
import dill
import pickle
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

def read_yaml_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
def write_yaml_file(filepath: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(filepath):
                os.remove(filepath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def save_numpy_array_data(filepath: str, array: np.array):
    """
    Save numpy array data to file
    """
    try:
        dir_path = os.path.dirname(filepath)
        os.makedirs(dir_path, exist_ok=True)
        with open(filepath, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(filepath: str, obj: object) -> None:
    try:
        logging.info("Entered the save_object method of common utils class")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as file_obj:
            pickle.dump(obj, file=file_obj)
        logging.info("Exited the save_object method of common utils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(filepath: str) -> object:
    try:
        if not os.path.exists(filepath):
            raise Exception(f"The file: {filepath} doesnot exist")
        with open(filepath, "rb") as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
def load_numpy_array_data(filepath: str) -> np.array:
    try:
        with open(filepath, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def evaluate_models(X_train, y_train, X_test, y_test, models, params):
    try:
        report = {}

        for i in range(len(list(models))):
            model = list(models.values())[i]
            param = params[list(models.keys())[i]]

            gs = GridSearchCV(model, param_grid=param, cv=3)
            gs.fit(X_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)

            report[list(models.keys())[i]] = test_model_score
            return report
    except Exception as e:
        raise NetworkSecurityException(e, sys)