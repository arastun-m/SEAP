## Base Agents (and extensions/alternatives)
LLM + Prompt (instructions, few-shot examples, hints/knowledge)

The base agent refers to the fundamental architecture or implementation of the agent that controls how the LLM operates in an autonomous setting. It’s like the agent "engine", the baseline structure upon which more specialized or task-specific agents can be built.

### Table of Contents
1. [Act](#base1-act-language-models-as-zero-shot-planners-extracting-actionable-knowledge-for-embodied-agents-2022)
2. [ReAct](#base2-react-synergizing-reasoning-and-acting-in-language-models-2023)
3. [CoT](#base3-chain-of-thought-prompting-elicits-reasoning-in-large-language-models-2022)
4. [StateAct](#base4-stateact-enhancing-llm-base-agents-via-self-prompting-and-state-tracking-2025)
5. [AdaPlanner](#base5-adaplanner-adaptive-planning-from-feedback-with-language-models-2023)
6. [Reflexion](#base6-reflexion-an-autonomous-agent-with-dynamic-memory-and-self-reflection)


### Base1. Act: Language Models as Zero-Shot Planners: Extracting Actionable Knowledge for Embodied Agents (2022)
[paper](https://proceedings.mlr.press/v162/huang22a/huang22a.pdf),
relevance: LLMs acting in interactive environments (used directly as agents)

- among the first to use LLMs directly to act in an interactive environment
- Do LLMs already cointain enough informataion, not just for linguistic tasks, but to make goal-drive decisions
- decompose high-level natural language tasks into conrete sequence of actions using semantic translation
- Evaluation metrics: Executability and Correctness
- Ablations of design decisions

### Base2. ReAct: Synergizing reasoning and acting in language models. (2023)
[paper](https://arxiv.org/pdf/2210.03629),
relevance: ReAct is the base agent of modern state-of-the-art approaches

- Explores 4 prompting methods (a) Standard, (b) Chain-of-thought, (c) Act-only, (d) ReAct
    - Contains example prompts in the appendix
- Problem solving process demonstrated by ReAct is more factual and grounded
- CoT is more accurate in formulating reasoning structure but can easily suffer from hallucinated facts or thoughts.

### Base3: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (2022)
[paper](https://proceedings.neurips.cc/paper_files/paper/2022/file/9d5609613524ecf4f15af0f7b31abca4-Paper-Conference.pdf)

- explores learning via chain-of-thought prompting.
- extends on the traditional few-shot prompting methods.
    - works poorly on tasks that require reasoning abilities.
    - few-shot prompting:
        - [source: Language Models are Few-Shot Learners](https://arxiv.org/pdf/2005.14165)
        - source shows that: scaling up language models greatly improves task-agnostic few-shot performance

### Base4. StateAct: Enhancing LLM Base Agents via Self-prompting and State-tracking (2025)
[paper](https://arxiv.org/pdf/2410.02810v3),
relevance: notion of base agents and extensions

- discusses the notion of base agents and its extensions (RAG, fine-tuning, tools, hand-crafted rules, multi-agent)
- StateAct: for long-context reasoning and goal adherence through (1) self-prompting, (2) chain-of-states
- discusses more costly extensions to the base agent; fine-tuning, test-time scaling, distillation

### Base5. AdaPlanner: Adaptive Planning from Feedback with Language Models (2023)
[paper](https://arxiv.org/pdf/2305.16653),
relevance: code-based prompts, open-loop/closed-loop LLM agent systems

- plan generation via code-based LLM prompting (improves conditional reasoning)
    - using code-based prompts instead of natural language prompts for LLMs reduces ambiguity and misinterpretation
- proposes a skill discovery mechanism that leverages successful plans as few-shot exemplars
- the notion of open-loop (rely on pre-determined plans) and closed-loop (incorporate environment feedback) systems for LLM agents
    - plus a table of past methods

### Base6. Reflexion: an autonomous agent with dynamic memory and self-reflection (2023)
[paper](https://web3.arxiv.org/pdf/2303.11366v1),
[also](https://proceedings.neurips.cc/paper_files/paper/2023/file/1b44b878bb782e6954cd888628510e90-Paper-Conference.pdf),
relevance: another base-agent approach utlilising emergent properties in LLMs

- endows an agent with dynamic memory and self-reflection capabilities
    - self-optimisation grounded in natural language
- leverages ReAct

### AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation (2023)
[paper](https://arxiv.org/pdf/2308.08155)
relevance: a notable multi-agent framework

- multiple agents that can converse with each other to accomplish tasks.
- they can (1) incorporate feedback (through conversationad or a human-in-the-loop), (2) exhibit a broad range of capabilities, (3) break complex tasks into manageable simpler subtasks.

### Base7. Knowagent: Knowledge-augmented planning for llm-based agents (2024)
### Base8. React meets actre: When language agents enjoy training data autonomy (2024)
### Base9. Stateflow: Enhancing llm task-solving through state-driven workflows (2024)

### Base10. 
