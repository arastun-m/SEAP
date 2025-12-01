# Evaluation & Benchmarking

[Azure AI Evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/observability) SDK used for simulations and evaluations. Useful [samples](https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate).

Alternatives:
- LangChain [LangSmith](https://docs.smith.langchain.com)
- [OpenAI Evals](https://github.com/openai/evals)


## Table of Contents
1. [File Structure](#file-structure)
2. [Modular Evaluation](#modular-evaluation)
    - [CLU](#1-conversational-language-understanding-clu)
    - [CQA](#2-custom-question-answering-cqa)
    - [Fallback RAG](#3-fallback-retrieval-augmented-generation-rag)
    - [Specialised Agents](#4-specialised-agents)
3. [End-to-End System Evaluation](#end-to-end-system-evaluation)


## File Structure

- [`scripts/`](scripts/) - running evaluations (reproducibility)
- [`data/`](data/) - synthetic system content
- [`eval_truth/`](eval_truth/) - available ground truth
- [`eval_dataset/`](eval_dataset/) - evaluation dataset (queries, context, responses)
- [`eval_results/`](eval_results/) - raw evaluation results
- [`figures/`](figures/) - result visualisation


## Modular Evaluation
### 1. Conversational Language Understanding (CLU) 

Evaluating the accuracy of intent routing. Evaluation dataset generated using an LLM prompted with synthetic system data.

See files for [Ground Truth](eval_truth/clu_truth.jsonl), [Dataset](eval_dataset/clu_samples.jsonl), [Results](figures/clu_performance_breakdown.png)

### 2. Custom Question Answering (CQA)

Evaluating the accuracy of question answering matches. Evaluation dataset generated using an LLM prompted with synthetic FAQs data (faqs.md).

See files for [Ground Truth](eval_truth/cqa_truth.jsonl), [Dataset](eval_dataset/cqa_samples.jsonl), [Results](figures/cqa_performance_breakdown.png)

### 3. Fallback Retrieval-Augmented Generation (RAG)

Evaluating the varying aspects of Retrieval-Augmented Generation (RAG) setup. Including; relevance of retrieval results (retrieval), consistency of response with respect to retrieved results (grounding), relevance of the final response (relevance). None of these methods require ground truth (labelled data). The evaluation dataset (query, answer, context) is generated using the RAG client and azure.ai.evaluations.simulator.

See file for [Dataset](eval_dataset/rag_samples.jsonl), [Results](figures/rag_performance_breakdown.png)

### 4. Specialised Agents

Specialised agents are: (1) CampusInfo, (2) AdminInfo, (3) Feedback (4) ChartPlotter. Modular agent evaluation includes constructing local access to agent clients (AgentClients). This enables direct single-turn access to the agent. Client provides responses, tool definitions, and tool calls based on a given query.

Evaluating intend resolution, tool call accuracy, and task adherence specific to agentic workflows. Evaluating quality through general purpose evaluators including; coherence and fluency.

- For CampusInfo see [Ground Truth](eval_truth/campus_info_truth.jsonl), [Dataset](eval_dataset/campus_info_samples.jsonl), [Results](figures/campus_info_performance_breakdown.png)
- For Feedback see [Ground Truth](eval_truth/feedback_truth.jsonl), [Dataset](eval_dataset/feedback_samples.jsonl), [Results](figures/feedback_performance_breakdown.png)
- For AdminInfo see [Ground Truth](eval_truth/admin_info_truth.jsonl), [Dataset](eval_dataset/admin_info_samples.jsonl), [Results](figures/admin_info_performance_breakdown.png)


## End-to-End System Evaluation

To run the end-to-end evaluations:
```bash
python endtoend_eval.py
```