import os
import json
from dotenv import load_dotenv
load_dotenv()

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient


def get_azure_credential():
    use_mi_auth = os.environ.get('USE_MI_AUTH', 'false').lower() == 'true'

    if use_mi_auth:
        mi_client_id = os.environ['MI_CLIENT_ID']
        return ManagedIdentityCredential(
            client_id=mi_client_id
        )

    return DefaultAzureCredential()


class CQASetup:
    """
    Sets up Custom Question Answering (CQA) project.
    (1) create the project, (2) import project data, and (3) deploy the project.
    """

    def __init__(self):
        self.import_file = 'infra/data/cqa_import.json'
        self.project_name = os.environ['CQA_PROJECT_NAME']
        self.deployment_name = os.environ['CQA_DEPLOYMENT_NAME']
        
        self.endpoint = os.environ['LANGUAGE_ENDPOINT']
        self.credential = get_azure_credential()
        self.client = AuthoringClient(self.endpoint, self.credential)

        # not all regions support Language service authoring
        self.authoring_endpoint = os.environ.get('AUTHORING_LANGUAGE_ENDPOINT', self.endpoint)
        self.authoring_client = AuthoringClient(self.endpoint, self.credential)
    
    def create_project(self):
        """
        Create a CQA project if it does not already exist.
        """
        print('Creating CQA project...')

        projects = self.authoring_client.list_projects()
        project_names = [p['projectName'] for p in projects]
        if self.project_name not in project_names:
            project = self.client.create_project(
                project_name=self.project_name,
                options={
                    'description': '',
                    'language': 'en',
                    'multilingualResource': False,
                    'settings': {
                        'defaultAnswer': 'No answer found'
                    }
                }
            )
            print(project)
        else:
            print(f'Project {self.project_name} already created.')
        
    def import_project_data(self):
        """
        Import CQA project data from a JSON file.
        """
        print('Importing CQA project...')

        with open(self.import_file, 'r') as fp:
            project_json = json.load(fp)
        poller = self.authoring_client.begin_import_assets(
            project_name=self.project_name,
            options=project_json
        )
        response = poller.result()
        print(response)
    
    def deploy_project(self):
        """
        Deploy the CQA project if it does not already exist.
        """
        print("Checking CQA deployments...")

        deployments = self.authoring_client.list_deployments(project_name=self.project_name)
        deployment_names = [d['deploymentName'] for d in deployments]

        if self.deployment_name not in deployment_names:
            print("Deploying knowledge base...")
            poller = self.authoring_client.begin_deploy_project(
                project_name=self.project_name,
                deployment_name=self.deployment_name
            )
            response = poller.result()
            print(response)
        else:
            print(f"Deployment {self.deployment_name} already deployed.")


if __name__ == "__main__":
    cqa_setup = CQASetup()
    cqa_setup.create_project()
    cqa_setup.import_project_data()
    cqa_setup.deploy_project()
