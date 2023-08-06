from __future__ import print_function
import requests
import json
import future
import six
from six.moves import cPickle as pickle
import zlib
import sys

from . import metrics

# Optional imports
library_base_class = []
try:
    from sklearn.base import BaseEstimator
    library_base_class.append(BaseEstimator)
except ImportError:
    pass

try:
    from keras.models import Sequential, Embedding
    from . import keras
    library_base_class.append(Sequential)
    library_base_class.append(Embedding)
except ImportError:
    pass


__version__ = '0.2.2'


class ModelChimp:
    URL = "https://www.modelchimp.com/"

    def __init__(self, username, password, project_id):
        self.project_id = project_id
        self._session = requests.Session()
        self._features = []
        self._model = None
        self._model_obj = {}
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
            self._model_obj = model
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


    def save(self, name, model_object_save=False):
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

        # Check model is sklearn and get a compresesd pickle __version__
        if model_object_save:
            if result["platform_library"] != self.PlatformLibraryType.SKLEARN:
                raise TypeError("Only Sklearn models can be uploaded for now.")
            files = {'ml_model': self.__get_compressed_picke(self._model_obj)}
            save_request = self._session.post(ml_model_url, data=result,
                            files=files, headers=self._http_headers)
        else:
            save_request = self._session.post(ml_model_url, data=result,
                            headers=self._http_headers)

        if save_request.status_code == 201:
            print("The data was successfully saved")
        else:
            print("The data could not be saved")


    def pull_model(self, model_id=None):
        if model_id is None:
            raise Exception('Please provide the Model ID.')

        pull_model_url = ModelChimp.URL + 'api/get-model-object/'
        payload =  {
            "project_id": self._project_id,
            "model_id": model_id
        }

        save_request = self._session.post(pull_model_url, data=payload,
                            headers=self._http_headers)

        if save_request.status_code == 406:
            print("Incorrect Model ID was given.")
        elif save_request.status_code == 403:
            print("You don't have permission to the project.")
        elif save_request.status_code == 404:
            print("Either the given model does not exist under the current project %s or the model does not exist at all." % self.project_id)

        model_object = save_request.content
        model_object = zlib.decompress(model_object, 31)
        model_object = pickle.loads(model_object)

        return model_object


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


    def __get_compressed_picke(self, model_object):
        pickled_obj = pickle.dumps(model_object,-1)
        z = zlib.compressobj(-1,zlib.DEFLATED,31)
        gzip_compressed_pickle = z.compress(pickled_obj) + z.flush()

        # A limit of 10mb for a model
        if sys.getsizeof(gzip_compressed_pickle) > 10000000:
            raise ValueError("Compressed model has a limit of 10MB.")

        return gzip_compressed_pickle


    class PlatformLibraryType(object):
        SKLEARN = '1'
        KERAS = '2'
        CHOICES = (
            (SKLEARN, 'Sklearn'),
            (KERAS, 'Keras')
        )
