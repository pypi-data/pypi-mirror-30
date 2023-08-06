from __future__ import print_function
import requests
import json
import future

from . import metrics

# Optional imports
library_base_class = []
try:
    from sklearn.base import BaseEstimator
    library_base_class.append(BaseEstimator)
except ImportError:
    pass

try:
    from keras.models import Sequential
    from . import keras
    library_base_class.append(Sequential)
except ImportError:
    pass


__version__ = '0.2.1'


class ModelChimp:
    URL = "https://www.modelchimp.com/"

    def __init__(self, username, password, project_id):

        self._session = requests.Session()
        self._features = []
        self._model = None
        self._evaluation = {}
        self._algorithm = ""
        self._http_headers = {}
        self._project_id = ""
        self.__authenticate(username, password, project_id)

    def add(self, model, evaluation, features=None):
        '''
        Add feature list, model parameters and evaluation metrics
        that needs to be stored
        '''

        if not isinstance(features, list):
            raise ValueError("features should be a list")

        if len(features) == 0:
            features = None

        # Check the model belongs to a supported library
        for base in library_base_class:
            supported_flag = False
            if isinstance(model, base):
                supported_flag = True
                break

        if not supported_flag:
            raise ValueError("model should be an instance of sklearn or keras.")

        if not isinstance(evaluation, dict):
            raise ValueError("evaluation should be dict")

        # Check evaluation metrics are valid
        self.__validate_eval_metric(evaluation)

        # Assign the the features, evaluation and algorithm used
        self._features = features
        self._evaluation = self.__dict_to_kv(evaluation)
        self._algorithm = model.__class__.__name__

        module_name = model.__module__.split('.')[0]
        if module_name == 'sklearn':
            self._model = self.__dict_to_kv(model.get_params())
            self._deep_learning_parameters = []
            self._platform_library = self.PlatformLibraryType.SKLEARN
        elif module_name in ['keras', 'modelchimp']:
            model_params = keras._get_relevant_params(model.__dict__)
            self._model = self.__dict_to_kv(model_params)
            self._deep_learning_parameters = keras._get_layer_info(model.layers)
            self._platform_library = self.PlatformLibraryType.KERAS

    def show(self):
        '''
        Prints the details that is going to be synced to the cloud
        '''
        print("---Feature List---")
        for i, f in enumerate(self._features):
            print("%s. %s" % (i + 1, f))

        print("\n")
        print("---Model Parameter List---")
        for obj in self._model:
            model_text = "%s : %s" % (obj['key'], obj['value'])
            print(model_text)

        print("\n")
        print("---Evaluation List---")
        for obj in self._evaluation:
            evaluation_text = "%s : %s" % ( metrics.get_metric_name(obj['key']),
                                            obj['value'])
            print(evaluation_text)

    def save(self, name):
        '''
        Save the details to the ModelChimp cloud
        '''

        ml_model_url = ModelChimp.URL + 'api/ml-model/'
        result = {
            "name": name,
            "features": json.dumps(self._features),
            "model_parameters": json.dumps(self._model),
            "evaluation_parameters": json.dumps(self._evaluation),
            "deep_learning_parameters": json.dumps(self._deep_learning_parameters),
            "project": self._project_id,
            "algorithm": self._algorithm,
            "platform": "PYTHON",
            "platform_library": self._platform_library
        }

        save_request = self._session.post(
            ml_model_url, data=result, headers=self._http_headers)

        if save_request.status_code == 201:
            print("The data was successfully saved")
        else:
            print("The data could not be saved")

    def __authenticate(self, username, password, project_id):
        authentication_url = ModelChimp.URL + 'api-token-auth/'
        project_meta_url = ModelChimp.URL + 'api/project-meta/'
        auth_data = {"username": username, "password": password}

        request_auth = self._session.post(authentication_url, data=auth_data)

        # Check if the request got authenticated
        if request_auth.status_code == 400:
            raise requests.exceptions.RequestException(
                "username or password is not valid!")

        # Get the authenticated token and assign it to the header
        token = json.loads(request_auth.text)['token']
        self._http_headers = {'Authorization': 'Token ' + token}

        request_project = self._session.post(
            project_meta_url,
            data={'project_id': project_id},
            headers=self._http_headers)

        # Check if the user has permission for the project
        if request_project.status_code == 403:
            raise requests.exceptions.RequestException(
                "User is not a member of the project")
        elif request_project.status_code == 500:
            raise requests.exceptions.RequestException(
                "Project with the given project id does not exist")

        self._project_id = json.loads(request_project.text)['id']

    def __dict_to_kv(self, dict_val):
        result = [{'key': k, 'value': v} for k, v in dict_val.items()]
        result.sort(key=lambda e: e['key'])

        return result

    def __validate_eval_metric(self, eval):
        invalid_metric_message = '''Please provide a valid evaluation metric. \
Following is an example of choosing Log Loss as an evaluation metric:\n \
from modelchimp.metrics import LOG_LOSS
                '''
        for k, v in eval.items():
            try:
                if metrics.is_valid_metric(k):
                    continue
            except TypeError:
                pass

            raise ValueError(invalid_metric_message)

    class PlatformLibraryType(object):
        SKLEARN = '1'
        KERAS = '2'
        CHOICES = (
            (SKLEARN, 'Sklearn'),
            (KERAS, 'Keras')
        )
