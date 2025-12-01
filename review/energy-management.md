# Smart Energy Management Papers
1. Smart Energy Management with AI-Agents (no LLMs)
2. Smart Energy Management with traditional AI approaches (no agents or LLMs)
3. Smart Energy Management other approaches
4. Smart Energy Management with LLMs

## 1. Smart Energy Management with AI-Agents
NOTE: a lot of these papers use MAS with traditional AI techniques and control algorithms, not LLMs (as this is a fairly new concept).

### A.1. AI-Layered with Multi-Agent Systems Architecture - Prognostics Health Management of Smart Energy Transformers (2022)
[energy-agent-1](https://www.mdpi.com/1996-1073/15/19/7217) 

Key ideas: multi-agent system, hybrid artificial intelligence, prognostics health management, smart transformers, online and offline monitoring, health index estimation, machine learning models, data fusion, smart grid integration

#### Agents:
- Smart Energy Management Agent: decision regarding load management, power factor control, maintenance scheduling
- Other Agents: Data Acquisition, Data Management, AI Analysis (ML models), Monitoring, Expert Analysis, Prognostic

- field agent: collect real-time sensor data, monitor transformer parameters, detect anomalies
- data acquisition agent: aggregate sensor inputs, ensure data integrity, manage communication protocols
- data management agent: preprocess data, clean datasets, label data with expert input
- hybrid ai agent: analyze data using machine learning models, classify faults, estimate health index and life loss
- health index agent: compute overall health score, assess component degradation, monitor maintenance history
- prognostic agent: predict future failures, estimate transformer lifespan, support maintenance planning
- monitoring agent: visualize key performance indicators, generate alerts, provide user interface for system status
- smart energy management agent: optimize load distribution, adjust power factor, schedule preventive maintenance


### A.2. Multi-agent Topology for an Energy-efficient Building Management and Information System (BMIS) (2020)
[energy-agent-2](https://www.tandfonline.com/doi/pdf/10.1080/03772063.2020.1847701)

Key ideas: master agent and zone/function specific helper agents, monitoring+adjusting building systems

#### Agents:
System Arhitecture:
- Sensing layer: sensors monitoring environmental parameters
- Control layer: actuators adjusting building systems (e.g., HVAC, lighting) driven by AI-Agents
- Decision layer: each agent reponsible for specific zones or functions within the building

- Master Agent: coordination and supervision
- Other Agents: Thermal Comfort, Illumination, Air Quality, Occupancy, Energy Monitoring, Communication


### A.3. Multi Agent System (MAS) Approach for Autonomous Energy Management in a Microgrid (2021)
[energy-agent-3](https://www.tandfonline.com/doi/pdf/10.1080/15325008.2021.1937390)

Key ideas: multi-agent system, autonomous energy management, distributed control, forecasting, real-time correction, agent coordination, scalability, microgrid optimization, simulation using stateflow

#### Agents:
- Forecasting agent: predict future energy demand, predict renewable energy generation, analyze historical data
- Real-time correction agent: monitor real-time performance, adjust forecast errors, update control actions dynamically
- Control agent: manage distributed generators, control energy storage systems, balance local energy demand and supply
- Coordination agent: facilitate communication between agents, resolve conflicts, ensure system-wide optimization and stability


### A.4. Modular Nano Grid Energy Management using Multi-Agent AI Arhictecture (2024)
[energy-agent-4](https://www.sciencedirect.com/science/article/pii/S0045790624000405#bib0019)

Key ideas: modular nanogrids, multi-agent systems, hierarchical control, decentralized energy management, real-time optimization, energy coordination, sustainability

#### Agents:
- Device agent: monitor local devices, manage local energy production and storage, report device status
- Nanogrid agent: balance internal energy loads, coordinate energy flow within nanogrid, forecast demand
- Intergrid agent: negotiate energy exchange between nanogrids, optimize global energy distribution, ensure system-wide efficiency


### A.5. Energy Management in Distributed Microgrids using Multi-Agent Systems (2019)
[energy-agent-5](https://www.sciencedirect.com/science/article/pii/S2210670718315233)

Key ideas: distributed microgrids, multi-agent systems, decentralized control, renewable energy integration, hierarchical energy management, energy optimization, real-time decision making

#### Agents:
- Device agent: monitor energy devices, manage local generation units, control battery storage
- MicrogridAgent: balance energy supply and demand, optimize internal energy flows, maintain grid stability
- Intergrid agent: coordinate energy exchange between microgrids, enhance system-wide efficiency, handle inter-microgrid communication


### A.6. Energy Management of Residential Hybrid Enegry System using Multi-Agent Deep Reinforcement Learning (2024)
[energy-agent-6](https://www.sciencedirect.com/science/article/pii/S0306261924007979?casa_token=Yl5RjEpGUj8AAAAA:wqvhKvqWY0AFB6xBk4FY5nw3TnHb4EeJLrZ406QB372q1WFyN14QomRb9m-j8JQ_vTIpT-VVDw#bb0230)

Key ideas: residential hybrid energy systems, multi-agent deep reinforcement learning, scalable energy management, centralized training decentralized execution, pv self-consumption, hvac control, battery storage optimization, energy cost reduction

#### Agents:
- HVAC agent: maintain indoor temperature, minimize hvac energy consumption, learn thermal comfort strategies
- Battery agent: manage battery charging and discharging, align storage with consumption and pv generation, reduce grid dependency
- PV (solar energy) agent: maximize solar energy self-consumption, coordinate pv energy distribution, optimize renewable utilization


### A.7. Energy Management of Multi-Energy Industrial Park using Multi-Agent Deep Reinforcement Learning (2021)
[energy-agent-7](https://www.sciencedirect.com/science/article/pii/S0306261922001064?casa_token=KmSSktfs9nwAAAAA:3hrVdvdi0KajEDDhw0IILJBlFLWQoaQncX1ZBWF_C3lHhre_PZETkXU63yPwYlV0cD6zfvYBKw)

Key ideas: multi-energy industrial park, multi-agent deep reinforcement learning, decentralized execution, centralized training, soft actor-critic, counterfactual baseline, attention mechanism, energy cost minimization, energy storage constraints, renewable energy integration

#### Agents:
- Battery agent: manage charging and discharging cycles, ensure energy storage within capacity constraints, optimize battery usage for cost efficiency
- CHP (Combined Heat and Power) agent: control combined heat and power unit operations, balance electricity and heat generation, coordinate with other agents for optimal energy distribution
- Boiler agent: regulate boiler functions, manage heat production, collaborate with CHPAgent to meet thermal demands efficiently
- Renewable agent: monitor renewable energy generation, forecast energy availability, integrate renewable sources into the energy mix effectively
- Load agent: predict energy demand, adjust consumption patterns, interact with supply agents to maintain demand-supply balance


### A.8. Home Energy Management using Multi-Agent Reinforcement Learning-Based Data-Driven Method (2020)
[energy-agent-8](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8981876&casa_token=GJNLKTfz0QwAAAAA:6FvB6prjSnORP52PRek1HuvgOHsp9waltH3w5DxvLotlIpGozORKsAzYdAOJx1cYxxm4Uo50)

Key ideas: home energy management, multi-agent reinforcement learning, data-driven scheduling, finite markov decision process, q-learning, neural networks, extreme learning machine, demand response, electricity cost minimization, user comfort optimization

#### Agents:
- Appliance agent: schedule operation times for household appliances, minimize electricity costs, reduce demand response-induced discomfort
- EV (electric vehicle) agent: manage electric vehicle charging schedules, align charging with low-cost periods, balance user mobility needs with energy efficiency
- PV (solar energy) agent: predict solar photovoltaic generation, optimize utilization of renewable energy, coordinate with other agents for energy distribution


### A.9. Article: Fetch.AIs Real-time Autonomous Energy Management System (@ Uni of Warwick) (2020)
[energy-agent-9](https://medium.com/fetch-ai/fetch-ais-real-time-autonomous-energy-management-system-delivers-major-cost-savings-23462727c7bf)

Multi-Agent AI Framework:
- agents manage individual enery assets (HVAC, battery storage units, renewable enery sources)
- "Virtual Twin": to simulate and implement the energy management strategy (18% reduction in energy costs)


### A.10. Optimised Energy Trading (Microgrid Networks) with Multi-Agent Deep Reinforcement Learning (2024)
[energy-agent-10](https://link.springer.com/article/10.1007/s13369-024-09754-4)

Employs Multi-agent deep reinforcement learning (MADRL) to:
- enhance device scheduling
- peer-to-peer (P2P) energy trading
- battery storage
- electric vehicles (EVs)

MADRL design:
- Each agent represents an individual household or energy asset
- Learning optimal strategies through interactions with environment
- Real-time pricing
- Demand response signals
- Decentralised control and optimisation


### A.11. Review and Evaluation of Multi-Agent Control Applications for Energy Management in Buildings (2024)
[energy-agent-11](https://www.mdpi.com/1996-1073/17/19/4835)

Key ideas: multi-agent control, integrated building energy management systems, decentralized control, model predictive control, reinforcement learning, hybrid control approaches, building energy subsystems (hvac, dhw, lighting, res, ess, evs), agent interactions, simulation tools, commercial building focus, residential deployment gap, real-world implementation challenges





<hr style="border:2px solid gray">


## 2. Smart Energy Management with other integrated AI approaches
### B.1. AI-based Home Energy Management System (*) (2022)
[energy-ai-1](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9514553)

Energy control strategies:
- Outing-based: proactive adjustments based on system predictions that the home will be unoccupied
- Occupancy-based: real-time adjustements based on current occupancy
- Comfort-based: maintains indoor temperatures within the comfort range derived by the ANN
- Sleep-based: saving energy during predicted sleep time


### B.2. AI-based & IoT-neabled Home Energy Management System (HEMS) (2021)
[energy-ai-2](https://www.sciencedirect.com/science/article/pii/S2352484721005497)

Key ideas: renewable energy integration, energy efficiency improvement, supply-side management, demand-side management, multi-objective optimization, user comfort, real-time control, smart grid interaction

#### Agents:
- supply-side management agent: schedule power dispatch among generation, consumption, and storage, optimize energy flow based on grid price and pv forecasts
- demand-side management agent: schedule and control flexible appliances, modulate load profiles to align with user preferences and energy availability
- optimization agent: implement ai-based multi-objective optimization to minimize costs and maximize comfort levels
- monitoring agent: assess system performance, provide user interface for real-time feedback and alerts


### B.3. Review on AI-Enabled Smart Building Management Systems (SBMS) (2024)
[energy-ai-3](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5190519)

AI-based integrations:
- Predictive Maintenance: reduced downtime and maintenance costs
- Energy Consumption Forecasting: ML algorithms to predict/optimise usage patterns
- Occupancy Detection: adjusting systems based on real0time occupancy data
- Temperature, humidity, lightning conditions

Challenges: data privacy and security (sensitive data), interoperability (integrating AI solutions with diverse systems), skill requirements (maintaining AI systems)


### B.4. Review of Deep Reinforcement Learning (DRL) for Smart Building Energy Management (SBEM) (2021)
[energy-ai-4](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9426901&casa_token=AzkF3PY_544AAAAA:kZ9aj1m5z_3jHUtloWir4cwzCLZ6z0AknW58GF805z5foN-MUP3weBSxn7H-cuD_EV0p0Hb9&tag=1)

Key Applications of DRL:
- HVAC Control: balance consumption with occupant comfort
- Ligthning Systems: optimise based on occupancy and natural light availability
- Integrated Control: DRL coordinates multiple subsystems
- Energy Storage Management
- Energy Trading: between buildings and grid
- Demand Reponse: adjust energy consumption in response to grid signals (grid stability)


### B.5. Literature Review of Energy Management Models in Smart Homes (2025)
[energy-ai-5](https://link.springer.com/article/10.1007/s41660-025-00506-x)

Key Insights on Multi-Agent Approaches:
- Decentralized Coordination and Control: manage specific components; HVAC, lighting, and appliances
- AI integrations: reinforcement learning, deep learning (adapt to user behavior and preferences)

Outlined Challenges:
- Lack of standardized communication protocols (but now we can use MCP)
- Need for standardised frameworks for MAS implementation (e.g., AutoGen, Semantic Kernel): for better adaptability, security.


### B.6. AI agents envisioning the future: Forecast-based Operation of Renewable Energy Storage Systems (with DRL) (2021)
[energy-ai-6](https://www.sciencedirect.com/science/article/pii/S0196890422001972)

DRL-based energy management system that learns optimal operational strategies for hydrogen production and storage. DRL agent's observation space includes energy price forecasts.
- Real-time data for decision making
- Dynamic energy environemnts

Challenges:
- Self-learning algorithms (DRL) face significant obstacle in meeting multiple divergent objectives (e.g., hyrodgen generation and volatile market prices) 
- High variability of the daily targets set by Rule-Based (RB) approach (hinders training)


### B.7. Hybrid Approach for Digital Twins (DT) in the Built Environment (Berkeley, Princeton, Siemens) (2021)
[energy-ai-7](https://dl.acm.org/doi/pdf/10.1145/3447555.3466585)

- physics-informed machine learning (PIML)
- challenge: it may be difficult to transform existing buildings to Zero Energy Building (ZEBs) standard.
- Digital twins (DT): monitor existing buildings and further increase their energy efficiency.

- Room focused hybrid methodology that incorporates physics-based and machine learning to create a digital twin.
- aim: to capture the dynamic behavior of the building’s HVAC system for energy efficiency and occupant satisfaction.
- KPIs: preliminary cooling energy comparison between the physical test and the digital twin model.


### B.8. Digital Twins (DT) and AI for energy efficiency in historic buildings (2021)
[energy-ai-8](https://iopscience.iop.org/article/10.1088/1755-1315/863/1/012041/pdf)

- factors affecting building energy consumption: e.g., weather, occupancy
- ANN is one of the most popular algorithms for energy consumption prediction
- utilises cloud-based digitalisation framework 
    - enough storage space and computing resources for energy monitoring data
    - enables ubiquitous, convenient, on-demand network acess to a shared pool of computing resources
    - Microsoft Azure is used as the cloud computing platform
- Data collection: indoor environment, HVAC and lighting, Energy consumption metering, outdoor weather, energy prices
- Ways of data collection: sensors, queries from BMS, weather stations and APIs
- framework evaluation metrics: (1) stability and portability, (2) prediction performance, optimal energy consumption, time saved


### B.9 Benchmarking energy consumption in universities: A review (2023)
[energy-ai-9](https://www.sciencedirect.com/science/article/pii/S2352710223023653#bib61)

- KPIs: universities lack well-defined, targeted KPIs, which would help them clearly/consistenly report their energy/sustainability performance
- Sustainability of a university campus is complex, can be measured by different metrics


<hr style="border:2px solid gray">


## 3. Smart Energy Management with other approaches
### C.1. Digitalisation of Energy: An Energy Futures Lab (Briefing Paper) (Rhodes, Aidan) (2020)
[energy-other-1](https://spiral.imperial.ac.uk/server/api/core/bitstreams/cdca31be-e9c1-4107-bd33-64d8c709bd51/content)

Considers 4 areas of digitalisation: big data, ML and AI, IoT, and bitcoin.


### C.2. Is IoT monitoring key to improve building energy efficiency? Case study of a smart campus in Spain (2023)
[energy-other-2](https://www.sciencedirect.com/science/article/pii/S0378778823001123?casa_token=F2DcEASZKTUAAAAA:SlQmpNUuulNCRQzG7oP5jvSbv3cSRIVDjnk-Sib1TpfMDCyddX1z10sKJlcHA2sKy5o53XvdxA#da005)

- A continuous, real-time monitoring system to support decisions in managing building energy systems.
- Demonstrated the system’s impact in reducing excessive heating and energy waste through temperature monitoring.
- The CO₂-based control method showed potential to save 40–70% of HVAC energy consumption.
- The methodology is scalable to a campus-wide smart system.


### C.3. Thesis: Understanding building and urban environment interactions: An integrated framework for building occupancy modelling (2022)
[energy-other-3](https://spiral.imperial.ac.uk/entities/publication/f189abfd-b227-4547-bc3c-4ac9596e1239)

Includes data collection method for campus occupancy:
Occupancy:
- Wi-Fi logs: implicit and low-cost source of occupancy data from existing campus infrastructure.
Air Quality:
- External air temperature: collected from online sources like Weather Underground and the UK Met Office.

APIs and Web Scraping: Urban variables (e.g., weather, transport, events) were gathered using scripted API calls in R.


### C.4. Developing a dynamic digital twin at building and city levels: A case study of the West Cambridge campus (2022)
[energy-other-4](https://www.repository.cam.ac.uk/items/eb7c345e-660c-4693-ba70-4eaf9bf6b711)

This dynamic digital twin implementation includes energy management.

In Data Acquisition Layer:
- design of a data acquisition approach is challenging, especially when considering the type, format, source and content of the data.
- components: IoT devices, Random Collection Devices, Building Management Data, Real-time Sensor Data
- example of data collection techniques; contactless (e.g., image-based), sensor systems, mobile access (WiFi environment)
- West Cambridge DT data is acquried from : building management system (BMS), asset managmenet system (AMS), space management system (SMS) used in Cambridge.


### C.5. Digital Twins’ Applications for Building Energy Efficiency: A Review (2022)
[energy-other-5](https://www.repository.cam.ac.uk/items/7266eaa4-3b23-48af-9048-a6bed2a97d38)

The concept of energy efficiency refers to the ratio between the output of performance, service, good, or energy, and the input of energy, according to the European Parliament [6].

Includes literature review on: (1) Occupant's comfort, (2) Energy consumption simulation
1. Room temperature parameter can characterise thermal comfort and satisfaction of tenants.


### C.6. Smart City Digital Twin–Enabled Energy Management: Toward Real-Time Building Energy Benchmarking (Georgia Tech) (2020)
[energy-other-6](https://ascelibrary.org/doi/pdf/10.1061/%28ASCE%29ME.1943-5479.0000741)

Why are Digital Twins (DT) useful:
- DT-based real energy monitoring can bridge the gap between building energy performance (as simulated by diagnosis) and actual building performance
- The Georgia Institute of Technology (GT) university campus was selected to quantify building energy-efficiency scores
- Building energy consumption data proivded by Georgia Tech Facilities Management Office (Jessica Rose)



<hr style="border:2px solid gray">


## 4. Energy related approaches with LLMs
### D.1 DrAgent: An Agentic Approach to Fault Analysis in Power Grids Using Large Language Models (2025)
[energy-llm-1](https://ieeexplore.ieee.org/abstract/document/10920654)

- Aim: using an LLM worflow to analyse power-grid fault records for operators
- Idea: in future, LLMs may be integrated into MAS to handle natural-language queries ("how can we reduce energy use in Lab A?")


### D.2 Exploring automated energy optimization with unstructured building data: A multi-agent based framework leveraging large language models (2024)
[energy-llm-2](https://www.researchgate.net/publication/383364013_Exploring_automated_energy_optimization_with_unstructured_building_data_A_multi-agent_based_framework_leveraging_large_language_models)

- Idea: encode expert knowledge into control agents
- Modern energy systems are becoming increasingly complex
- LLMs are gaining significance for expert guidance