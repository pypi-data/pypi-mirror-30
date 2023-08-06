from __future__ import print_function
import requests
import json
from sklearn.base import BaseEstimator

class ModelChimp:
    URL = "https://www.modelchimp.com/"

    def __init__(self, username, password, project_id):
        self.session = requests.Session()
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

        if not isinstance(model, BaseEstimator):
            raise ValueError("model should be an instance of sklearn.")

        if not isinstance(evaluation, dict):
            raise ValueError("evaluation should be dict")

        self._features = features
        self._model = self._dict_to_kv(model.get_params())
        self._evaluation = self._dict_to_kv(evaluation)
        self._algorithm = model.__class__.__name__

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
            evaluation_text = "%s : %s" % (obj['key'], obj['value'])
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
            "project": self._project_id,
            "algorithm": self._algorithm,
            "platform": "PYTHON"
        }

        save_request = self.session.post(
            ml_model_url, data=result, headers=self._http_headers)

        if save_request.status_code == 201:
            print("The data was successfully saved")
        else:
            print("The data could not be saved")

    def __authenticate(self, username, password, project_id):
        authentication_url = ModelChimp.URL + 'api-token-auth/'
        project_meta_url = ModelChimp.URL + 'api/project-meta/'
        auth_data = {"username": username, "password": password}

        request_auth = self.session.post(authentication_url, data=auth_data)

        # Check if the request got authenticated
        if request_auth.status_code == 400:
            raise requests.exceptions.RequestException(
                "username or password is not valid!")

        # Get the authenticated token and assign it to the header
        token = json.loads(request_auth.text)['token']
        self._http_headers = {'Authorization': 'Token ' + token}

        request_project = self.session.post(
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

    def _dict_to_kv(self, dict_val):
        result = [{'key': k, 'value': v} for k, v in dict_val.items()]
        result.sort(key=lambda e: e['key'])

        return result
