import os
import json
from dotenv import load_dotenv
load_dotenv()

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def get_azure_credential():
    use_mi_auth = os.environ.get('USE_MI_AUTH', 'false').lower() == 'true'
    if use_mi_auth:
        mi_client_id = os.environ['MI_CLIENT_ID']
        return ManagedIdentityCredential(
            client_id=mi_client_id
        )
    return DefaultAzureCredential()


class CLUSetup:
    """
    Sets up Conversational Language Understanding (CLU) project.
    (1) import project data, (2) train model, and (3) deploy model.
    """

    def __init__(self):
        self.import_file = 'infra/data/clu_import.json'
        self.project_name = os.environ['CLU_PROJECT_NAME']
        self.model_name = os.environ['CLU_MODEL_NAME']
        self.deployment_name = os.environ['CLU_DEPLOYMENT_NAME']

        self.endpoint = os.environ['LANGUAGE_ENDPOINT']
        self.credential = get_azure_credential()
        self.client = ConversationAuthoringClient(self.endpoint, self.credential)

        # not all regions support Language service authoring
        self.authoring_endpoint = os.environ.get('AUTHORING_LANGUAGE_ENDPOINT', self.endpoint)
        self.authoring_client = ConversationAuthoringClient(self.authoring_endpoint, self.credential)
    
    def import_project_data(self):
        """
        Import CLU project data from a JSON file.
        """
        print('Importing CLU project...')

        with open(self.import_file, 'r') as fp:
            project_json = json.load(fp)
        project_json['metadata']['projectName'] = self.project_name

        poller = self.authoring_client.begin_import_project(
            project_name=self.project_name,
            project=project_json
        )
        response = poller.result()
        print(response)
    
    def train_model(self):
        """
        Train the CLU model if it is not already trained.
        """
        print('Checking trained CLU models...')

        models = self.authoring_client.list_trained_models(
            project_name=self.project_name
        )
        model_names = [model['label'] for model in models]
        model_names = []

        if self.model_name not in model_names:
            print('Training CLU model...')
            poller = self.authoring_client.begin_train(
                project_name=self.project_name,
                configuration={
                    'modelLabel': self.model_name,
                    'trainingMode': 'standard'
                }
            )
            response = poller.result()
            print(response)
        else:
            print(f"Model {self.model_name} already trained.")
        
    def deploy_model(self):
        """
        Deploy the CLU model if it is not already deployed.
        """
        print('Checking CLU deployments...')

        deployments = self.authoring_client.list_deployments(
            project_name=self.project_name
        )
        deployment_names = [dep['deploymentName'] for dep in deployments]
        deployment_names = []

        if self.deployment_name not in deployment_names:
            print('Deploying CLU model...')
            poller = self.authoring_client.begin_deploy_project(
                project_name=self.project_name,
                deployment_name=self.deployment_name,
                deployment={
                    'trainedModelLabel': self.model_name
                }
            )
            response = poller.result()
            print(response)
        else:
            print(f"Deployment {self.deployment_name} already deployed.")


if __name__ == "__main__":
    clu_setup = CLUSetup()
    clu_setup.import_project_data()
    clu_setup.train_model()
    clu_setup.deploy_model()
