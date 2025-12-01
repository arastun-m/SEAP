"""Handles Custom Question Answering (CQA) calls"""

from typing import Annotated
import requests
import json

import config


class CQAClient:
    """
    Custom Question Answering Client.
    Returns a matching answers if any.
    """

    def __init__(self):
        self.language_endpoint = config.LANGUAGE_ENDPOINT
        self.cqa_project_name = config.CQA_PROJECT_NAME
        self.cqa_deployment_name = config.CQA_DEPLOYMENT_NAME
        self.cqa_confidence_threshold = config.CQA_CONFIDENCE_THRESHOLD
        self.aoai_key = config.AOAI_KEY
        self.api_version = "2023-04-01"

        self.path = f"/language/:query-knowledgebases?projectName={self.cqa_project_name}&deploymentName=\
            {self.cqa_deployment_name}&api-version={self.api_version}"
        self.url = self.language_endpoint + self.path

        # defining request headers and body
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.aoai_key,
            "Content-Type": "application/json"
        }
        self.body = {
            "question": None,
            "top": 5,
            "confidenceScoreThreshold": self.cqa_confidence_threshold,
            "rankerType": "Default",
            "projectName": self.cqa_project_name,
            "deploymentName": self.cqa_deployment_name
        }

    def get_cqa_result(self, question: str) -> Annotated[dict, "CQA Result in JSON format"]:
        """
        Get CQA result for a given question.
        """
        self.body["question"] = question
        response = requests.post(
            self.url,
            headers=self.headers,
            data=json.dumps(self.body)
        )
        return response.json()

    def get_top_answer(self, cqa_result: dict) -> Annotated[dict, "Top answer from CQA result"]:
        """
        Get the top answer from the CQA result.
        """
        if "answers" in cqa_result and cqa_result["answers"]:
            top_answer = cqa_result["answers"][0]
            return {
                "answer": top_answer.get("answer", ""),
                "confidence": top_answer.get("confidenceScore", 0.0),
                "source": top_answer.get("source", "")
            }
        return {"answer": "", "confidence": 0.0, "source": ""}
    

# testing
if __name__ == "__main__":
    cqa_client = CQAClient()
    question = "I wanted to know about the refund policy for my order?"
    result = cqa_client.get_cqa_result(question)
    print(json.dumps(result, indent=2))
    print("Top Answer:", cqa_client.get_top_answer(result))