""" Sets up agents (config.json) in Azure AI Foundry Agents project """

import json
import os
import re
from dotenv import load_dotenv
load_dotenv()

from azure.ai.agents import AgentsClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential


def bind_parameters(input_string: str, parameters: dict) -> str:
    """
    Replace occurrences of '${key}' in the input string with the value of the key in the parameters dictionary.

    :param input_string: The string containing keys of value to replace.
    :param parameters: A dictionary containing the values to substitute in the input string.
    :return: The modified string with parameters replaced.
    """
    if parameters is None:
        return input_string

    # Define the regex pattern to match '${key}'
    parameter_binding_regex = re.compile(r"\$\{([^}]+)\}")

    # Replace matches with corresponding values from the dictionary
    return parameter_binding_regex.sub(
        lambda match: parameters.get(match.group(1), match.group(0)),
        input_string
    )

def load_prompt_string(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Prompt file not found: {file_path}")
        return None


class AgentSetup():
    """
    Sets up the Azure AI Agents:
    (1) General Campus Information Agent
    (2) User Feedback Collector Agent
    (3) Admin Info Agent
    (4) Chart Plotter Agent
    """

    def __init__(self):
        self.model_name = os.environ['AOAI_DEPLOYMENT']
        self.endpoint = os.environ['AGENTS_PROJECT_ENDPOINT']
        self.delete_old_agents = os.environ.get("DELETE_OLD_AGENTS", "true").lower() == "true"
        self.credential = DefaultAzureCredential()
        self.client = AgentsClient(self.endpoint, self.credential, api_version="2025-05-15-preview")
        # set up the config file
        self.config_dir = os.environ.get("CONFIG_DIR", ".")
        self.config_file = os.path.join(self.config_dir, "config.json")

        # set up agent details
        self.agent_names = ["CampusInfo", "Feedback", "AdminInfo", "ChartPlotter"]
        prompts_dir = 'src/backend/src/prompts/'
        self.agent_instruction_paths = {
            "CampusInfo": os.path.join(prompts_dir, "campus_info.txt"),
            "Feedback": os.path.join(prompts_dir, "user_feedback.txt"),
            "AdminInfo": os.path.join(prompts_dir, "admin_info.txt"),
            "ChartPlotter": os.path.join(prompts_dir, "chart_plotter.txt"),
        }

    def cleanup_agents(self):
        """
        Create an instance of the AgentsClient.
        """
        # If DELETE_OLD_AGENTS is set to true, delete all existing agents in the project
        if self.delete_old_agents:
            print("Deleting all existing agents in the project...")
            agents = self.client.list_agents()
            while agents:
                try: 
                    agent = agents.next()
                    print(f"Deleting agent: {agent.name} with ID: {agent.id}")
                    self.client.delete_agent(agent.id)
                except StopIteration: return
                except ResourceNotFoundError: continue

    def setup_agents(self):
        """
        Set up the agents in the Azure AI Agents project and write their IDs to a config file.
        """
        agent_ids = {}
        for agent_name in self.agent_names:
            # Load the instructions from the corresponding file
            instructions = load_prompt_string(self.agent_instruction_paths[agent_name])
            if not instructions:
                print(f"Skipping agent {agent_name} due to missing instructions.")
                continue
            
            # Create the agent
            agent_definition = self.client.create_agent(
                model=self.model_name,
                name=agent_name,
                instructions=instructions,
            )
            agent_ids[agent_name] = agent_definition.id
            print(f"Created agent: {agent_name} with ID: {agent_definition.id}")

        # Write to config.json file
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(agent_ids, f, indent=2)
            print(f"Agent IDs written to {self.config_file}")
            print(json.dumps(agent_ids, indent=2))
                
        except Exception as e:
            print(f"Error writing to {self.config_file}: {e}")
            print(json.dumps(agent_ids, indent=2)) 


if __name__ == "__main__":
    agent_setup = AgentSetup()
    with agent_setup.client:
        agent_setup.cleanup_agents()
        agent_setup.setup_agents()
    print("Agent setup completed.")