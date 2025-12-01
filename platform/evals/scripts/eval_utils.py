"""Evaluation Utilities"""

import json


# --------------------- Custom Evaluators ---------------------
class ExactMatchEvaluator:
    """ Evaluator that checks if the response matches the ground truth exactly. 
    Use case: CLU, CQA
    """
    def __init__(self):
        self.name = "exact_match"

    def __call__(self, *, response: str, ground_truth: str, **kwargs) -> str:
        """ Evaluate the response against the ground truth. """
        return str(response.strip() == ground_truth.strip())

class AnswerLengthEvaluator:
    def __init__(self):
        pass
    # A class is made callable by implementing the special method __call__
    def __call__(self, *, response: str, **kwargs):
        return {"answer_length": len(response)}
    

async def answer_length(*, data, **kwargs):
  return len(data.get("answer"))

  # # when you return multiple results
  # return {
  #   "answer_length": len(data.get("answer")),
  #   "answer_length_div100": len(data.get("answer")) / 100
  # }


# --------------------- Data Loading Functions ---------------------
class EvalDataHandling:
    """ Static functions for evaluation data loading and handling. 
    
    1. get_synthetic_data: Load unstructured synthetic system data from .md files.
    2. get_benchmark_data: Load ground truth or benchmark data from JSONL files.
    3. write_benchmark_data: Write benchmark data to JSONL files.
    4. write_simulation_data: Write simulator results to JSON files.
    5. get_evaluation_results: Load evaluation results from JSON files.
    """

    def get_synthetic_data(self, file_path: str) -> list:
        """
        Load unstructured synthetic data from a .md file.
        :param file_name: Name of the .md file to load.
        :return: List of strings representing the synthetic data.
        """
        try:
            with open(file_path, 'r') as file:
                data = file.readlines()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return []
        return [line.strip() for line in data if line.strip()]

    def get_eval_dataset(self, file_path: str) -> list:
        """
        Loads evaluation dataset from a JSONL file.
        e.g., {"query": "", "ground_truth": ""}
        e.g., {"query": "", "context": "", "response": "", "ground_truth": ""}
        """
        try:
            with open(file_path, 'r') as file:
                data = [json.loads(line.strip()) for line in file if line.strip()]
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return []
        return data

    def write_eval_dataset(self, data: dict, file_path: str) -> None:
        """
        Write evaluation dataset to a JSONL file.
        :param data: A list of dictionaries containing benchmark data.
        :param file_name: Name of the file to write the data to.
        """
        with open(file_path, 'w') as file:
            for item in data:
                file.write(json.dumps(item) + '\n')
    
    def write_simulation_data(self, data: dict, file_path: str) -> None:
        """
        Write simulator results to a JSON file
        :param data: A list of dictionaries containing simulation results.
        :param file_name: Name of the file to write the data to.
        """
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    def to_eval_qr_json_lines(self, data: dict, latencies: list, output_path) -> None:
        """
        Convert the output to a query-and-response output format (eval dataset format)
        Example input (JSON): 
        [
            {"messages": [{"role": "user", "content": "query"}, {"role": "assistant", "content": "response", "context": "context"}, ...]},
            ...
        ]
        Example output (JSONL):
        {"query: "user query", "context": "assistant context", "response": "assistant response"}
        """
        with open(output_path, "w", encoding="utf-8") as f_out:
            for example in data:
                messages = example.get("messages", [])
                it = iter(messages) # iterate through each multi-turn conversation
                for msg in it:
                    if msg.get("role") == "user": # append user query
                        query = msg.get("content", "")
                        try:
                            next_msg = next(it)
                        except StopIteration:
                            continue
                        if next_msg.get("role") != "assistant":
                            continue # continue if no assistant response found
                        response = next_msg.get("content", "") # append assistant response
                        context = next_msg.get("context", "") or ""
                        line = {
                            "query": query,
                            "context": context,
                            "response": response,
                            "answer_length": len(response),
                            "latency": latencies.pop(0) if latencies else 0, # pop latency for each response
                        }
                        f_out.write(json.dumps(line, ensure_ascii=False) + "\n")

    def get_eval_results(self, file_path: str) -> list:
        """
        Load evaluation results from a JSON file.
        e.g., {"rows": [{}, {}, ...], "metrics": {"f1_score": {"f1_score": 0.0, "f1_result": "fail", "f1_threshold": 0.5}}}
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return []
        return data
