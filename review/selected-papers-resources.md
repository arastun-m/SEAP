## Selected Papers/Blogs highly-useful for the project

### 1. Anthropic - Building effective agents (2024)
[source](https://www.anthropic.com/engineering/building-effective-agents)
[cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents)

Key Ideas:
- outlines distinction: workflows and agents
- start simple, increase complexity when needed
    - tradeoff: latency cost vs task performance
    - e.g., a single augmented LLM (building block)
- understand underlying code of high-level/abstract frameworks
- workflow pattern examples: (1) prompt chaining, (2) routing, (3) parallelisation, (4) orchestrator-workers, (5) evaluator-optimiser
- three core principles:
    1. design simplicity
    2. transparency (show agent's planning steps)
    3. documentation and testing
- best practices for tool development


## Selected Resources highly-useful for the project

### 1. Camridge Building Energy & Environment Portal (CAMBEEP)
[source1](https://www.cambeep.eng.cam.ac.uk)

1. Building performance simulation (practical building physics and guide to simulation tools)
2. Building performance monitoring (handouts, toolkits and case studies)

* Digital Technology Group - Cambridge Weather

### 2. MIT NANDA: The Internet of AI Agents
[source2](https://nanda.media.mit.edu)

### 3. MCP Server Market
[market1](https://mcpmarket.com/leaderboards)

### 4. Microsoft's Phi (Small Language Model) Cookbook
[source3](https://github.com/microsoft/PhiCookBook?tab=readme-ov-file)
Relevance: small fast and cost-effective specialised (Phi family, fine-tuning) models for multi-agent systems

- Phi Family: Function Calling, Language & Advanced Reasoning, Vision & Audio, Mixture of Experts (MoE)
- Can we have a MoE agents (with specialised Phi models as client models) for a fast/efficiency conversational energy system?

### 5. Graphiti MCP Server | ZEP: A TEMPORAL KNOWLEDGE GRAPH ARCHITECTURE FOR AGENT MEMORY (2025)
[source4](https://arxiv.org/pdf/2501.13956)
[graphiti](https://github.com/getzep/graphiti)
Relevance: long-term memory storage (user chat history) to better manage user energy management preferences.

### 6. Azure Well-Architected Framework
[source5](https://learn.microsoft.com/en-us/azure/well-architected/)
[architecture gallery](https://learn.microsoft.com/en-us/azure/architecture/browse/)
Relevance: better designed system architecture + better design diagrams

### 7. Azure Language OpenAPI Conversational Agent Accelerator
[github](https://github.com/Azure-Samples/Azure-Language-OpenAI-Conversational-Agent-Accelerator)
[intend routing](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/agent-catalog/msft-agent-samples/foundry-agent-service-sdk/intent-routing-agent)
[blog](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/announcing-azure-ai-language-new-features-to-accelerate-your-agent-development/4415216)
Relevance: Azure AI Language for better conversational agents

- Fast and low-cost intent classification (routing) with CLU (Azure AI Language)
- CQA for pre-defined question answer pairs
- PII to protect user privacy / sensitive information
- fallback RAG
- simple UI with FastAPI and Uvicorn

### 8. Campus Energy Education Dashboard (UC Davis)
[web page](https://ceed.ucdavis.edu)
[TherMOOstat](https://facilities.ucdavis.edu/engineering/thermoostat) for feedback
[TherMOOstat paper](https://www.sciencedirect.com/science/article/pii/S0378778817309556)

- energy data and dashboard
- individual readings from each building
- user feedback system (to report conditions, e.g., track preferences)


## Selected Data Sources for the project
### 1. UNICON: An Open Dataset of Electricity, Gas and Water Consumption in a Large Multi-Campus University Setting (La Trobe University) (2022)
[data1](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9869498)
[dataset access](https://www.kaggle.com/datasets/cdaclab/unicon/data?select=building_submeter_consumption.csv)
Relevance: reference for synthetic data generation

Key Details:
- covers electricity consumption (kWh) at 15 mins of granularity + weather (temperature, humidity, wind speed and direction)
- building categories: teaching/labs, library, administrative, residental, sports
- data stored: (1) building (id, category, area, capacity) (2) calendar (date, weekend, holidays, semester) 
    (3) building consumption and weather data

other mentioned datasets:
- [HUE](https://pmc.ncbi.nlm.nih.gov/articles/PMC6660473/pdf/main.pdf) 
    (hourly energy usage + temperature, humidity, pressure), 
    [dataset access](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/N3HGRN)


### 2. A three-year dataset supporting research on building energy management and occupancy analytics (2022)
[data2](https://www.nature.com/articles/s41597-022-01257-x.pdf)
[dataset access](https://datadryad.org/dataset/doi:10.7941/D1N33Q)
Relevance: reference for synthetic data generation

Key Details:
- covers energy consumption, HVAC operating conditions, environmental parameters, occupant counts
- electricity data: miscellaneous, lighting, HVAC
- outdoor environmental: temperature, humidity, solar radiation
- indoor environmental: indoor temperature, cooling temperature, heating temperature
- occupancy counts
- HVAC operational data