"""Handles Conversational Language Understanding (CLU) calls"""

from typing import Annotated
import requests
import json

import config


class CLUClient:
    """
    Conversational Language Understanding Client.
    Extracting intents and entities from a single utterance.
    """

    def __init__(self):
        self.language_endpoint = config.LANGUAGE_ENDPOINT
        self.clu_project_name = config.CLU_PROJECT_NAME
        self.clu_deployment_name = config.CLU_DEPLOYMENT_NAME
        self.aoai_key = config.AOAI_KEY
        self.api_version = "2023-04-01"
        # not all regions support Language service authoring
        self.authoring_language_endpoint = config.AUTHORING_LANGUAGE_ENDPOINT
        self.authoring_aoai_key = config.AUTHORING_AOAI_KEY

        self.path = f"/language/:analyze-conversations?api-version={self.api_version}"
        self.url = self.authoring_language_endpoint + self.path

        # defining request headers and body
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.authoring_aoai_key,
            "Content-Type": "application/json"
        }
        self.body = {
            "analysisInput": {
                "conversationItem": {
                    "id": "1",
                    "participantId": "user",
                    "text": None
                }
            },
            "parameters": {
                "projectName": self.clu_project_name,
                "deploymentName": self.clu_deployment_name,
            },
            "kind": "Conversation"
        }

    def get_clu_result(self, message: str) -> Annotated[dict, "CLU Result in JSON format"]:
        """
        Get CLU result for a given message.
        """
        self.body["analysisInput"]["conversationItem"]["text"] = message
        response = requests.post(
            self.url,
            headers=self.headers,
            data=json.dumps(self.body)
        )
        return response.json()

    def get_top_intend(self, clu_result: dict) -> Annotated[str, "Top intent from CLU result"]:
        """
        Get the top intent from the CLU result.
        """
        if "result" in clu_result and "prediction" in clu_result["result"]:
            predictions = clu_result["result"]["prediction"]
            if predictions and "topIntent" in predictions:
                return predictions["topIntent"]
        return None


# testing
if __name__ == "__main__":
    clu_client = CLUClient()
    utterance = "What is the refund policy for my order?"
    result = clu_client.get_clu_result(utterance)
    print(f"Intents and entities for '{utterance}':\n{result}")