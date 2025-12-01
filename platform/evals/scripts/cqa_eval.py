import time

from azure.ai.evaluation import evaluate, F1ScoreEvaluator

from eval_config import (
    GROUND_TRUTH_PATHS, DATASET_PATHS, RESULT_PATHS,
    CQAClient
)
from eval_utils import EvalDataHandling, ExactMatchEvaluator, AnswerLengthEvaluator, answer_length


class CQAEval:
    """ CQA Evaluation Class 
    1. Generates an evaluation dataset using ground truth and CQA client.
    2. Runs CQA evaluation on the evaluation data and stores results.
    """

    def __init__(self, cqa_client : CQAClient):
        self.cqa_client = cqa_client
        self.eval_data_handler = EvalDataHandling()
        self.ground_truth_path = GROUND_TRUTH_PATHS["cqa"]
        self.dataset_path = DATASET_PATHS["cqa"]
        self.results_path = RESULT_PATHS["cqa"]
    
    def generate_dataset(self) -> None:
        """ Generates evaluation dataset using given queries, ground truth, and CQA client. 
        Also adds response level metric results: latency and answer length.
        """
        ground_truth_data = self.eval_data_handler.get_eval_dataset(self.ground_truth_path)
        eval_data = []

        for line in ground_truth_data:
            start_time = time.time()
            cqa_result = self.cqa_client.get_cqa_result(line["query"])
            top_answer = self.cqa_client.get_top_answer(cqa_result)["answer"]
            end_time = time.time()

            top_answer_length = len(top_answer)
            eval_data.append({
                "query": line["query"],
                "context": "", # no context from CQA
                "response": top_answer,
                "ground_truth": line["ground_truth"],
                "answer_length": top_answer_length,
                "latency": end_time - start_time
            })
        self.eval_data_handler.write_eval_dataset(eval_data, self.dataset_path)
        print(f"Generated benchmark data with {len(eval_data)} entries, saved to {self.dataset_path}")

    def evaluate(self) -> None:
        """ Run CQA evaluation on the benchmark data and store results. """
        benchmark_data = self.eval_data_handler.get_eval_dataset(self.dataset_path)
        if not benchmark_data:
            raise ValueError("Benchmark data is empty. Please generate benchmark data first.")

        # Evaluate using F1 Score
        evaluate(
            data=self.dataset_path,
            evaluators={
                "f1_score": F1ScoreEvaluator(threshold=1.0), # complete match
            },
            # column mapping
            evaluator_config={
                "default": {
                    "column_mapping": {
                        "query": "${data.query}",
                        "ground_truth": "${data.ground_truth}",
                        "response": "${data.response}",
                    } 
                }
            },
            output_path=self.results_path,
        )
        print(f"Evaluation completed. Results saved to {self.results_path}")


# CQA Eval Pipeline
if __name__ == "__main__":
    cqa_client = CQAClient()
    cqa_eval = CQAEval(cqa_client)
    cqa_eval.generate_dataset()
    cqa_eval.evaluate()