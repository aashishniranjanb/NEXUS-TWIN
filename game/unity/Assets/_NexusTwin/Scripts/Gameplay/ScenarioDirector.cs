using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;
using NexusTwin.Vehicles;
using NexusTwin.Traffic;
using NexusTwin.Scoring;
using NexusTwin.Networking;
using NexusTwin.UI;

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
            IncidentManager.Instance?.ResolveIncident(NexusIds.Junctions.J3);
            GameManager.Instance?.SetState(GameState.Briefing);
        }

        private IEnumerator ScenarioSequenceRoutine()
        {
            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;

            if (mission == 2)
            {
                Debug.Log("[ScenarioDirector] 00:00 - Mission 02 Active: Monitoring Escape Corridor J1-J2-J3");
                yield return new WaitForSeconds(4f);

                // Stage 2: First Alert (J2 Bottleneck)
                GameManager.Instance?.SetState(GameState.Event);
                incidentOccurred = true;
                IncidentManager.Instance?.TriggerIncident(NexusIds.Junctions.J2, IncidentType.Accident, new Vector3(2.5f, 0f, 0f));
                Debug.Log("[ScenarioDirector] 00:04 - Incident 1 triggered at J2");
                yield return new WaitForSeconds(4f);

                // Stage 3: Complication (J3 lane disruption)
                IncidentManager.Instance?.TriggerIncident(NexusIds.Junctions.J3, IncidentType.Closure, new Vector3(-2.5f, 0f, -60f));
                Debug.Log("[ScenarioDirector] 00:08 - Incident 2 triggered at J3 (lane closed)");
                yield return new WaitForSeconds(4f);

                // Stage 4: AI Alert with Uncertainty
                GameManager.Instance?.SetState(GameState.Analysis);
                predictionFired = true;
                _dataProvider.FetchAIPrediction(NexusIds.Junctions.J2, (alert) =>
                {
                    EventBus.RaiseAIPrediction(alert);
                });
                Debug.Log("[ScenarioDirector] 00:12 - AI predicts high congestion risk");
                yield return new WaitForSeconds(4f);

                // Stage 5: AI Recommendation & Decision
                GameManager.Instance?.SetState(GameState.Decision);
                recommendationFired = true;
                _dataProvider.FetchStrategies(NexusIds.Junctions.J2, (options) =>
                {
                    EventBus.RaiseStrategiesReady(options);
                    selectedStrategy = options[0]; // Coordinated Corridor is the AI Recommendation
                });
                yield return new WaitForSeconds(5f);

                // Stage 6: Digital Twin Simulation
                GameManager.Instance?.SetState(GameState.Simulation);
                Debug.Log("[ScenarioDirector] Digital Twin evaluating multi-junction futures...");
                yield return new WaitForSeconds(3f);

                GameManager.Instance?.SetState(GameState.Comparison);
                _dataProvider.SimulateFutures(NexusIds.Junctions.J2, selectedStrategy.type, (results) =>
                {
                    EventBus.RaiseSimulationComplete(results);
                });
                yield return new WaitForSeconds(3f);

                // Explanation
                GameManager.Instance?.SetState(GameState.Explanation);
                _dataProvider.FetchExplanation(selectedStrategy.type, (explanation) =>
                {
                    EventBus.RaiseExplanationReady(explanation);
                });
                yield return new WaitForSeconds(3f);

                // Stage 7: Decision Conflict / Approval
                GameManager.Instance?.SetState(GameState.Approval);
                Debug.Log("[ScenarioDirector] Awaiting operator priority decision...");

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

                // Stage 8: Execution & Consequences
                if (selectedStrategy.type == StrategyType.DoNothing && approved)
                {
                    yield return new WaitForSeconds(4f);
                    GameManager.Instance?.SetState(GameState.Failed);
                    EventBus.RaiseMissionFailed(new MissionFailureData
                    {
                        title = "Escape Corridor Collapse",
                        reason = "No Action resulted in compounding bottlenecks at J2 and J3. Emergency transit gridlocked.",
                        finalQueue = 78f,
                        ambulanceDelay = 32.5f
                    });
                    yield break;
                }

                // Points popup for human operator decision
                if (selectedStrategy.type == StrategyType.Diversion)
                {
                    ScorePopupFX.ShowPopup("+250 PTS — OPTIMAL AI ALIGNMENT!", new Vector2(0, 100), new Color(0.22f, 0.906f, 0.372f));
                }
                else if (selectedStrategy.type == StrategyType.EmergencyPriority)
                {
                    ScorePopupFX.ShowPopup("+180 PTS — EMERGENCY ROUTE SECURED!", new Vector2(0, 100), new Color(0.10f, 0.53f, 0.82f));
                }
                else
                {
                    ScorePopupFX.ShowPopup("+100 PTS — INTERVENTION APPLIED", new Vector2(0, 100), new Color(0.95f, 0.72f, 0.15f));
                }

                GameManager.Instance?.SetState(GameState.Apply);
                Debug.Log($"[ScenarioDirector] Applying strategy override: {selectedStrategy.label}");

                TrafficLightController[] allLights = FindObjectsByType<TrafficLightController>(FindObjectsSortMode.None);
                foreach (var light in allLights)
                {
                    light.ApplyStrategyOverride(selectedStrategy.strategyTypeString, 45f);
                }
                yield return new WaitForSeconds(2f);

                // Dispatch Ambulance
                ambulanceDispatched = true;
                _ambulanceAgent = VehicleManager.Instance?.SpawnEmergencyAmbulance();
                Debug.Log("[ScenarioDirector] Ambulance entering escape corridor");
                yield return new WaitForSeconds(9f);

                // Stage 9: Resolve & Result
                GameManager.Instance?.SetState(GameState.Result);
                IncidentManager.Instance?.ResolveIncident(NexusIds.Junctions.J2);
                IncidentManager.Instance?.ResolveIncident(NexusIds.Junctions.J3);
                yield return new WaitForSeconds(4f);

                // Stage 10: Debrief
                GameManager.Instance?.SetState(GameState.Score);
                scenarioCompleted = true;

                ScoreBreakdownData scoreData = new ScoreBreakdownData();
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
                    scoreData = new ScoreBreakdownData { trafficFlow = 290, emergencySafety = 330, queueControl = 210, decisionQuality = 150 };
                }

                EventBus.RaiseScoreUpdated(scoreData);
                EventBus.RaiseScenarioComplete(scoreData);
                yield break;
            }

            // Fallback to Mission 01 sequence if not mission 2
            Debug.Log("[ScenarioDirector] 00:00 - Mission 01 Active: Monitoring Corridor J1-J2-J3");
            yield return new WaitForSeconds(6f);

            GameManager.Instance?.SetState(GameState.Event);
            incidentOccurred = true;
            IncidentManager.Instance?.TriggerIncident(NexusIds.Junctions.J2, IncidentType.Accident, new Vector3(2.5f, 0f, 0f));
            yield return new WaitForSeconds(6f);

            GameManager.Instance?.SetState(GameState.Analysis);
            predictionFired = true;
            _dataProvider.FetchAIPrediction(NexusIds.Junctions.J2, (alert) =>
            {
                EventBus.RaiseAIPrediction(alert);
            });
            yield return new WaitForSeconds(5f);

            GameManager.Instance?.SetState(GameState.Decision);
            recommendationFired = true;
            _dataProvider.FetchStrategies(NexusIds.Junctions.J2, (options) =>
            {
                EventBus.RaiseStrategiesReady(options);
                selectedStrategy = options[0];
            });

            float waitSimM1 = 0f;
            while (!simulationRequested && waitSimM1 < 10f)
            {
                waitSimM1 += Time.deltaTime;
                yield return null;
            }

            if (!simulationRequested)
            {
                EventBus.RaiseSimulateRequested();
            }

            GameManager.Instance?.SetState(GameState.Simulation);
            yield return new WaitForSeconds(3f);

            GameManager.Instance?.SetState(GameState.Comparison);
            _dataProvider.SimulateFutures(NexusIds.Junctions.J2, selectedStrategy.type, (results) =>
            {
                EventBus.RaiseSimulationComplete(results);
            });
            yield return new WaitForSeconds(3f);

            GameManager.Instance?.SetState(GameState.Explanation);
            _dataProvider.FetchExplanation(selectedStrategy.type, (explanation) =>
            {
                EventBus.RaiseExplanationReady(explanation);
            });
            yield return new WaitForSeconds(2.5f);

            GameManager.Instance?.SetState(GameState.Approval);

            float waitApproveM1 = 0f;
            while (!decisionMade && waitApproveM1 < 12f)
            {
                waitApproveM1 += Time.deltaTime;
                yield return null;
            }

            if (!decisionMade)
            {
                EventBus.RaiseApproved();
            }

            if (selectedStrategy.type == StrategyType.DoNothing && approved)
            {
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

            GameManager.Instance?.SetState(GameState.Apply);
            TrafficLightController[] M1Lights = FindObjectsByType<TrafficLightController>(FindObjectsSortMode.None);
            foreach (var light in M1Lights)
            {
                light.ApplyStrategyOverride(selectedStrategy.strategyTypeString, 45f);
            }
            yield return new WaitForSeconds(2f);

            ambulanceDispatched = true;
            _ambulanceAgent = VehicleManager.Instance?.SpawnEmergencyAmbulance();
            yield return new WaitForSeconds(9f);

            GameManager.Instance?.SetState(GameState.Result);
            IncidentManager.Instance?.ResolveIncident(NexusIds.Junctions.J2);
            yield return new WaitForSeconds(4f);

            GameManager.Instance?.SetState(GameState.Score);
            scenarioCompleted = true;

            ScoreBreakdownData scoreDataM1 = new ScoreBreakdownData();
            if (ScoreController.Instance != null)
            {
                scoreDataM1 = new ScoreBreakdownData
                {
                    trafficFlow = ScoreController.Instance.trafficFlowScore,
                    emergencySafety = ScoreController.Instance.emergencySafetyScore,
                    queueControl = ScoreController.Instance.queueControlScore,
                    decisionQuality = ScoreController.Instance.decisionQualityScore
                };
            }
            else
            {
                scoreDataM1 = new ScoreBreakdownData { trafficFlow = 285, emergencySafety = 350, queueControl = 220, decisionQuality = 145 };
            }

            EventBus.RaiseScoreUpdated(scoreDataM1);
            EventBus.RaiseScenarioComplete(scoreDataM1);
        }

        private void HandleStrategySelected(StrategyOptionData option)
        {
            selectedStrategy = option;
            Debug.Log($"[ScenarioDirector] Player selected strategy: {option.label}");

            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;

            if (mission == 2)
            {
                if (option.type != StrategyType.DynamicLane && option.type != StrategyType.DoNothing)
                {
                    float delayDelta = (option.type == StrategyType.EmergencyPriority) ? 15.0f : 10.0f;
                    float emergencyDelta = (option.type == StrategyType.EmergencyPriority) ? -12.4f : -4.4f;
                    string tradeOff = (option.type == StrategyType.EmergencyPriority)
                        ? "Prioritizes immediate ambulance life safety, but overrides the coordinated corridor flow causing civilian gridlock."
                        : "Diverts traffic away from J2, but overloads the downstream bottleneck at J3.";

                    EventBus.RaiseDisagreementTriggered(new DisagreementData
                    {
                        playerAction = option.label,
                        aiRecommendation = "Coordinated Corridor System (optimize network flow)",
                        tradeOffReason = tradeOff,
                        networkDelayDeltaPct = delayDelta,
                        emergencyDelayDeltaS = emergencyDelta
                    });
                }
            }
            else
            {
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
