# AI-Based Urban Traffic Intelligence

## Problem Statement
Urban traffic is influenced by many interacting factors, including time, location, road layout, traffic flow, turning patterns, and intersection characteristics. The resulting congestion can affect travel time, fuel consumption, road efficiency, and the overall movement of people through a city.

Build an AI-powered system that uses the provided traffic data to understand, analyse, predict, simulate, or improve aspects of urban transportation.

The problem is intentionally open-ended. Teams may identify patterns in traffic behaviour, explore the causes of congestion, predict future conditions, detect unusual traffic situations, recommend possible interventions, simulate alternative scenarios, support transportation decisions, or develop another innovative application based on the data.

The AI approach is completely open. Teams may use machine learning, deep learning, generative AI, large language models, AI agents, optimization, simulation, or combinations of these techniques.

## Deliverable
A working AI-powered system that meaningfully uses the provided traffic dataset to produce useful traffic-related intelligence, analysis, predictions, recommendations, simulations, or other capabilities. The final objective, user experience, interface, and technical approach are open to the team.

## Dataset
### BigQuery-Geotab Intersection Congestion Dataset
* **Kaggle:** [BigQuery-Geotab Intersection Congestion](https://www.kaggle.com/competitions/bigquery-geotab-intersection-congestion)
* **Source:** Geotab / Kaggle

The dataset contains traffic observations from major intersections in Atlanta, Boston, Chicago, and Philadelphia. It includes information related to traffic movement and waiting behaviour at different intersections and times.

The dataset contains information such as:
- City and intersection
- Geographic location
- Time and day information
- Entry and exit directions
- Traffic movement through intersections
- Intersection characteristics
- Waiting time
- Distance to the first stopped vehicle
- Traffic stopping duration and related measurements

### Dataset Download Procedure
Follow these steps to download the dataset locally via the Kaggle CLI:

1. **Accept Competition Rules:**
   Go to [Kaggle Competition Rules](https://www.kaggle.com/competitions/bigquery-geotab-intersection-congestion/rules) and click **"I Understand and Accept"** to join the competition.

2. **Configure API Credentials:**
   Set up your Kaggle API Token in terminal:
   ```bash
   # Linux/macOS
   export KAGGLE_API_TOKEN="<your_kaggle_api_token>"
   
   # Windows (PowerShell)
   $env:KAGGLE_API_TOKEN="<your_kaggle_api_token>"
   ```

3. **Download & Extract Dataset:**
   Execute the download command and extract to the `data/` directory:
   ```bash
   kaggle competitions download -c bigquery-geotab-intersection-congestion -p ./data
   ```
   Extract `bigquery-geotab-intersection-congestion.zip` contents directly into the `./data` directory.


## Mandatory Requirement
The provided BigQuery-Geotab Intersection Congestion Dataset must be a meaningful and demonstrable component of the solution.

Teams must be able to clearly demonstrate:
**Provided traffic data → AI/ML processing or reasoning → meaningful traffic intelligence**

The dataset must influence the functionality of the submitted system and must not be used merely as a sample dataset or visual background.

## What Participants Can Explore
Participants may use the dataset to investigate any meaningful aspect of urban traffic. They could identify traffic patterns, study congestion behaviour, predict future conditions, detect unusual situations, explore intersection dynamics, optimize traffic movement, simulate different scenarios, or build AI-assisted transportation decision systems.

The technical approach is completely open. Teams may use machine learning, generative AI, AI agents, optimization, simulation, statistical modelling, or a combination of methods.

The final solution may be analytical, predictive, interactive, simulation-based, or decision-oriented. Teams are encouraged to identify their own problem within the broader challenge of understanding and improving urban mobility using real-world traffic data.

## Core Idea
> **“What useful intelligence can you create from real-world traffic behaviour?”**

Participants should use the common dataset as a foundation and decide for themselves what meaningful AI-powered capability they can build on top of it.
