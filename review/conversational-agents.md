## 1. Conversational (LLM-based) AI agent systems
### Conv1. Graph-Based Grounding in a Conversational Clinical Decision Support System (Johns Hopkins APL) (2024)
[conv-agent-1](https://ieeexplore.ieee.org/document/10765950),
[also an blog on the paper](https://www.jhuapl.edu/news/news-releases/230817a-cpg-ai-battlefield-medical-assistance),
Relevance: conversational agent in a technical domain

Key Idea:
- graph-based method for grounding LLMs in technical domains, prevents premature diagnosis.
- applicable to any technical domain where: flow-chart like structured sequence of patterns have been captured

System Design:
- two grounding mechanisms: RAG and Graph-grounding
    (1) RAG of curated library of clinical practice guidelines (CPG)
    (2) Graph navigation system to maintain an index into the TCCC (Tactical Combat Causality Care) diagrams
- Processes: Dialogue manager, Navigator (graph navigation), Information retriever (RAG)
    - Dialogue manager combines Navigator and IR output to form a single coherent response
- Intrinsic (synthetic data) and Extrinsic (uses human interaction) evaluation


### Conv2. Autonomous Evaluation and Refinement of Digital Agents (Berkeley) (2024)
[conv-agent-2](https://arxiv.org/pdf/2404.06474),
[github repo](https://github.com/Berkeley-NLP/Agent-Eval-Refine),
Relevance: improves agent performance, safe real-world deployment, no-need for additional supervision/data

Key Idea:
- domain-general evaluation models that improve agent performance for web navigation and device control.
    - via inference-time guidance (self-correction via Reflexion); 29% improvement on WebArena benchmark
    - via fine-tuning/retraining (filtered training data); 75% improvement in device control settings
- leverages a Vision Language Model (VLM); processes screenshots, actions and instructions
- evaluation models are not perfect (74.4 and 92.9% agreement with oracle evaluation metrics)


### Conv3. Chatlaw: A Multi-Agent Legal Assistant with Knowledge Graph Enhanced Mixture-of-Experts LLM
[conv-agent-3](https://arxiv.org/pdf/2306.16092)
relevance: conversational multi-agent system in law

Key Idea:
- Conversational Multi-Agent Legal Assistant System
- Utilises MoE and a MAS system to enhance reliability and accuracy
- High quality legal dataset with knowledge graphs
- Standardised Operation Procedures (SOP) modelled after real law firm workflows (reduce errors and hallucinations)


<hr style="border:2px solid gray">


## 2. LLM-based agentic frameworks/projects
### AG1. CowPilot: A Framework for Autonomous and Human-Agent Collaborative Web Navigation (2025)
[paper](https://arxiv.org/pdf/2501.16609)
relevance: agentic system for web navigation

- human agent collaborative web navigation

### AG5. SWE-agent: Agent-computer interfaces enable automated software engineering (2024)
[paper](https://arxiv.org/pdf/2405.15793)
relevance: agentic system for software engineering

- SWE-agent autonomoulsy using computers to solve software engineering tasks
- through a custom Agent-Computer Interface (ACI) designed to enhance agent's ability

### AG6. MARG: Multi-Agent Review Generation for Scientific Papers (2024)
[paper](https://arxiv.org/pdf/2401.04259)
relevance: agentic system for scientific research

- explores LLMs ability to generate feedback for scientific papers
- distributes paper text across agents (to overcome input token size limitation)
- subtasks specialised for different comment types (clarity, experiments, impact)


<hr style="border:2px solid gray">


## 3. Concepts/Challenges/Ideas - Conversational LLMs
### LLM1. On LLMs-Driven Synthetic Data Generation, Curation, and Evaluation: A Survey (Zhejiang University) (2024)
[paper](https://arxiv.org/pdf/2406.15126?),
Relevance: synthetic energy data generation, curation and evaluation

Key Idea:
- human-generated idea: challenging, high-cost, suspectible to biases and errors
- does not create datasets from scratch, performs data augmentation with small nubmer of seed samples
- challenges: data faithfulness (logics and grammatics, domain-specific data) and diversity (should mimic real-world data)
- mentions: data generation agents (HuggingGPT, MetaGPT)
- synergies for data generation: LM-LLMs, Human-Model

Proposed 3 Stage Workflow:
1. Data generation: prompt engineering (context, controls, examples) and multi-step generation (break-down complex data)
2. Data curation: filtering and label enhancement
3. Data evaluation: direct (textual aspects) and indirect (train or fine-tune models with data)

### LLM2. On the Origin of Hallucinations in Conversational Models: Is it the Datasets or the Models? (Alberta, IBM) (2022)
[paper](https://arxiv.org/pdf/2204.07931)
Relevance: hallucinations in (1) user query handling, (2) adjusting energy settings, (3) synthetic data

Key Idea:
- Widely used benchmarks (gold responses) are rife with hallucinations
- knowledge-grounded conversational models hallucinate through subjective information and unsupported factual information
- halucination evalation: response classification taxonomy (entailment, hallucination, partial hallucination, generic, uncooperative)
- hallucination is a reflection of training data issues and model weakness

### LLM3. Agentic retrieval-augmented generation: A survey on agentic rag (2025)
[paper](https://arxiv.org/pdf/2501.09136)
relevance: outlines difference between agents using traditional RAG systems, and Agentic RAG

- traditional RAG setups are constrained by static workflows, lack adaptability for multi-step reasoning, and lack contextual integration
- traditional RAG paradigms include; naive RAG, advanced RAG, Modular RAG, Graph RAG
- Unlike traditional RAG, agentic RAG employs autnomous agents to orhcestrate retrieval, filter relevant information and refine responses they excell in scenarious requiring precision and adatability.

### LLM4. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (2020)
[paper](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf)
relevance: introduction of RAG

- a general-purpose fine-tuning recipe for retrieval-augmented generation (RAG)
- combining pre-trained parametric and non-parametric memory for language generation.

### LLM5. Restgpt: Connecting large language models with real-world restful apis (2023)
[paper](https://arxiv.org/pdf/2306.06624)
relevance: LLM as controllers, feeding tool instructions and few-shot examples through prompts

### LLM6. Easytool: Enhancing llm-based agents with concise tool instruction (2024)
[paper](https://arxiv.org/pdf/2401.06201)
relevance: agent tool use through concise instructions

- tool documentations can be diverse, redundant, or incomplete
- EasyTool: high quality tool instructions from tool documentation
    - through standard tool descriptions, and tool functionality guidelines with few-shot examples
    - can significantly reduce token consumption, and improve tool utilisation performance

### LLM7. Meta-Reasoning Improves Tool Use in Large Language Models (2024)
[paper](https://arxiv.org/pdf/2411.04535)
relevance: TECTON, more advanced method to improve tol usage by LLMs

- instead of commonly used inference-time tool selection made by naive greedy decoding this method:
    - (1) through custom fine-tuned language modelling head; reasons over the task and gathers candidate tools
    - (2) meta-reasons over the previous output and makes the final choice

### LLM8. CRITIC: Large language models can self-correct with tool-interactive critiquing (2023)
[paper](https://arxiv.org/pdf/2305.11738)
relevance: another prompt engineering technique to improve LLM performance through tool-based critiques

- follows the n iterations of: generate output->call tools->generate critiques (based on tool results)->rectify output
- CRITIC helps LLMs verfiy and rectify their own output through human-like interaction with external tools.
    - uses external tools to self-reflect and amend the output based on given critique (verify-then-correct)

### LLM9. Toolformer: Language Models Can Teach Themselves to Use Tools (2023)
[paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/d842425e4bf79ba039352da0f658a906-Paper-Conference.pdf)
relevance: tool calling through LLM fine-tuning

### LLM10. Defeating Prompt Injections by Design (2025)
[paper](https://arxiv.org/pdf/2503.18813)
relevance: safety against prompt injections

### LLM11. The prompt report: a systematic survey of prompt engineering techniques (2024)
[paper](https://arxiv.org/pdf/2406.06608?)
relevance: to date, most comprehensive report on prompt and prompt engineering (incl in agentic context, and security)

