using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;
using NexusTwin.Vehicles;
using NexusTwin.Traffic;
using NexusTwin.Scoring;
using NexusTwin.Networking;

namespace NexusTwin.Gameplay
{
    /// <summary>
    /// ScenarioDirector — Directs the primary mission:
    /// Accident at J2 + Approaching Ambulance + AI Prediction + Digital Twin Simulation + Responsible AI Decisions.
    /// Supports Main Menu, Narrative Cinematic, Mission Briefing, Failure, and Score Debriefing.
    /// </summary>
    public class ScenarioDirector : MonoBehaviour
    {
        public static ScenarioDirector Instance { get; private set; }

        [Header("Scenario Settings")]
        public float scenarioTimer = 0f;
        public StrategyType aiRecommendedType = StrategyType.Diversion;

        [Header("State Tracking")]
        public bool incidentOccurred = false;
        public bool predictionFired = false;
        public bool recommendationFired = false;
        public bool simulationRequested = false;
        public bool decisionMade = false;
        public bool ambulanceDispatched = false;
        public bool scenarioCompleted = false;

        [Header("Player Choices")]
        public StrategyOptionData selectedStrategy;
        public bool approved = false;

        private VehicleAgent _ambulanceAgent;
        private Coroutine _scenarioRoutine;
        private IGameDataProvider _dataProvider;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            if (GameManager.Instance != null && !GameManager.Instance.useMockData)
            {
                _dataProvider = new LiveGameDataProvider();
            }
            else
            {
                _dataProvider = new MockGameDataProvider();
            }
        }

        private void Start()
        {
            EventBus.OnStrategySelected += HandleStrategySelected;
            EventBus.OnSimulateRequested += HandleSimulateRequested;
            EventBus.OnApproved += HandleApproved;
            EventBus.OnRejected += HandleRejected;
            EventBus.OnMissionRestart += HandleMissionRestart;
            EventBus.OnGameStateChanged += HandleGameStateChanged;

            // Initialize in MainMenu
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SetState(GameState.MainMenu);
            }
        }

        private void OnDestroy()
        {
            EventBus.OnStrategySelected -= HandleStrategySelected;
            EventBus.OnSimulateRequested -= HandleSimulateRequested;
            EventBus.OnApproved -= HandleApproved;
            EventBus.OnRejected -= HandleRejected;
            EventBus.OnMissionRestart -= HandleMissionRestart;
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void Update()
        {
            if (!scenarioCompleted && GameManager.Instance != null && GameManager.Instance.currentState >= GameState.Idle)
            {
                scenarioTimer += Time.deltaTime;
            }
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (state == GameState.Idle && _scenarioRoutine == null)
            {
                _scenarioRoutine = StartCoroutine(ScenarioSequenceRoutine());
            }
        }

        private void HandleMissionRestart()
        {
            if (_scenarioRoutine != null) StopCoroutine(_scenarioRoutine);
            _scenarioRoutine = null;

            scenarioTimer = 0f;
            incidentOccurred = false;
            predictionFired = false;
            recommendationFired = false;
            simulationRequested = false;
            decisionMade = false;
            ambulanceDispatched = false;
            scenarioCompleted = false;
            approved = false;

            IncidentManager.Instance?.ResolveIncident(NexusIds.Junctions.J2);
            GameManager.Instance?.SetState(GameState.Briefing);
        }

        private IEnumerator ScenarioSequenceRoutine()
        {
            Debug.Log("[ScenarioDirector] 00:00 - Mission 01 Active: Monitoring Corridor J1-J2-J3");
            yield return new WaitForSeconds(6f);

            // 00:15 - Accident occurs at J2 (EVENT)
            GameManager.Instance?.SetState(GameState.Event);
            incidentOccurred = true;
            IncidentManager.Instance?.TriggerIncident(NexusIds.Junctions.J2, IncidentType.Accident, new Vector3(2.5f, 0f, 0f));
            Debug.Log("[ScenarioDirector] 00:15 - ACCIDENT OCCURRED AT J2!");
            yield return new WaitForSeconds(6f);

            // 00:30 - AI Predicts High Congestion (ANALYSIS)
            GameManager.Instance?.SetState(GameState.Analysis);
            predictionFired = true;
            _dataProvider.FetchAIPrediction(NexusIds.Junctions.J2, (alert) =>
            {
                EventBus.RaiseAIPrediction(alert);
            });
            Debug.Log("[ScenarioDirector] 00:30 - AI Predicts 87% Congestion Risk at J2");
            yield return new WaitForSeconds(5f);

            // 00:45 - AI Recommends Strategy Options (DECISION)
            GameManager.Instance?.SetState(GameState.Decision);
            recommendationFired = true;

            _dataProvider.FetchStrategies(NexusIds.Junctions.J2, (options) =>
            {
                EventBus.RaiseStrategiesReady(options);
                selectedStrategy = options[0]; // default select recommendation
            });
            Debug.Log("[ScenarioDirector] 00:45 - AI Strategy Recommendation displayed");

            // Wait for player to simulate or timeout
            float waitSim = 0f;
            while (!simulationRequested && waitSim < 10f)
            {
                waitSim += Time.deltaTime;
                yield return null;
            }

            if (!simulationRequested)
            {
                EventBus.RaiseSimulateRequested();
            }

            // 01:00 - Digital Twin Simulation (SIMULATION -> COMPARISON)
            GameManager.Instance?.SetState(GameState.Simulation);
            Debug.Log("[ScenarioDirector] 01:00 - Digital Twin evaluating counterfactual futures...");
            yield return new WaitForSeconds(3f);

            GameManager.Instance?.SetState(GameState.Comparison);
            _dataProvider.SimulateFutures(NexusIds.Junctions.J2, selectedStrategy.type, (results) =>
            {
                EventBus.RaiseSimulationComplete(results);
            });
            yield return new WaitForSeconds(3f);

            // 01:15 - Explanation Stage (EXPLANATION)
            GameManager.Instance?.SetState(GameState.Explanation);
            _dataProvider.FetchExplanation(selectedStrategy.type, (explanation) =>
            {
                EventBus.RaiseExplanationReady(explanation);
            });
            yield return new WaitForSeconds(2.5f);

            // 01:30 - Player Approval Stage (APPROVAL)
            GameManager.Instance?.SetState(GameState.Approval);
            Debug.Log("[ScenarioDirector] Awaiting Player Approval / Trade-off review...");

            float waitApprove = 0f;
            while (!decisionMade && waitApprove < 12f)
            {
                waitApprove += Time.deltaTime;
                yield return null;
            }

            if (!decisionMade)
            {
                EventBus.RaiseApproved();
            }

            // Check if player selected DoNothing or rejected necessary intervention
            if (selectedStrategy.type == StrategyType.DoNothing && approved)
            {
                // Unmitigated gridlock -> Mission Failure
                yield return new WaitForSeconds(4f);
                GameManager.Instance?.SetState(GameState.Failed);
                EventBus.RaiseMissionFailed(new MissionFailureData
                {
                    title = "Network Gridlock",
                    reason = "Unmitigated corridor congestion blocked all approaches. Emergency vehicle failed to reach destination.",
                    finalQueue = 58.5f,
                    ambulanceDelay = 38.2f
                });
                yield break;
            }

            // 01:50 - Apply Strategy (APPLY)
            GameManager.Instance?.SetState(GameState.Apply);
            Debug.Log($"[ScenarioDirector] Applying strategy: {selectedStrategy.label}");

            TrafficLightController[] allLights = FindObjectsByType<TrafficLightController>(FindObjectsSortMode.None);
            foreach (var light in allLights)
            {
                light.ApplyStrategyOverride(selectedStrategy.strategyTypeString, 45f);
            }
            yield return new WaitForSeconds(2f);

            // 02:10 - Ambulance Dispatched
            ambulanceDispatched = true;
            _ambulanceAgent = VehicleManager.Instance?.SpawnEmergencyAmbulance();
            Debug.Log("[ScenarioDirector] 02:10 - AMBULANCE_01 dispatched through corridor");
            yield return new WaitForSeconds(9f);

            // 02:30 - Resolve & Result
            GameManager.Instance?.SetState(GameState.Result);
            IncidentManager.Instance?.ResolveIncident(NexusIds.Junctions.J2);
            Debug.Log("[ScenarioDirector] 02:30 - Incident resolved, corridor normalized");
            yield return new WaitForSeconds(4f);

            // 02:45 - Score Breakdown
            GameManager.Instance?.SetState(GameState.Score);
            scenarioCompleted = true;

            ScoreBreakdownData scoreData;
            if (ScoreController.Instance != null)
            {
                scoreData = new ScoreBreakdownData
                {
                    trafficFlow = ScoreController.Instance.trafficFlowScore,
                    emergencySafety = ScoreController.Instance.emergencySafetyScore,
                    queueControl = ScoreController.Instance.queueControlScore,
                    decisionQuality = ScoreController.Instance.decisionQualityScore
                };
            }
            else
            {
                scoreData = new ScoreBreakdownData
                {
                    trafficFlow = 285,
                    emergencySafety = 350,
                    queueControl = 220,
                    decisionQuality = 145
                };
            }

            EventBus.RaiseScoreUpdated(scoreData);
            EventBus.RaiseScenarioComplete(scoreData);
            Debug.Log($"[ScenarioDirector] Mission Complete! Score: {scoreData.Total} pts");
        }

        private void HandleStrategySelected(StrategyOptionData option)
        {
            selectedStrategy = option;
            Debug.Log($"[ScenarioDirector] Player selected strategy: {option.label}");

            // Responsible AI Disagreement Check
            if (option.type != aiRecommendedType && option.type != StrategyType.DoNothing)
            {
                float delayDelta = (option.type == StrategyType.EmergencyPriority) ? 8.0f : -18.0f;
                float emergencyDelta = (option.type == StrategyType.EmergencyPriority) ? -31.0f : 4.2f;
                string tradeOff = (option.type == StrategyType.EmergencyPriority)
                    ? "Grants priority green wave to the ambulance at the expense of side-street civilian delay."
                    : "Extends main arterial green times without rerouting incoming bottleneck volume.";

                EventBus.RaiseDisagreementTriggered(new DisagreementData
                {
                    playerAction = option.label,
                    aiRecommendation = "Divert Traffic via Cross Street East/West bypass",
                    tradeOffReason = tradeOff,
                    networkDelayDeltaPct = delayDelta,
                    emergencyDelayDeltaS = emergencyDelta
                });
            }
        }

        private void HandleSimulateRequested()
        {
            simulationRequested = true;
        }

        private void HandleApproved()
        {
            approved = true;
            decisionMade = true;
        }

        private void HandleRejected()
        {
            approved = false;
            decisionMade = true;
        }
    }
}
