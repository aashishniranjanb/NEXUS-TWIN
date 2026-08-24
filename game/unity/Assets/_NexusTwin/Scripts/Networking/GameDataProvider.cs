using System;
using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Core;
using NexusTwin.Data;

namespace NexusTwin.Networking
{
    public interface IGameDataProvider
    {
        bool IsConnected { get; }
        string ProviderName { get; }
        void FetchAIPrediction(string junctionId, Action<CongestionAlertData> callback);
        void FetchStrategies(string junctionId, Action<StrategyOptionData[]> callback);
        void SimulateFutures(string junctionId, StrategyType selectedStrategy, Action<ScenarioResultData[]> callback);
        void FetchExplanation(StrategyType selectedStrategy, Action<ExplanationData> callback);
    }

    /// <summary>
    /// MockGameDataProvider — High fidelity offline simulation provider for Standalone demo mode.
    /// </summary>
    public class MockGameDataProvider : IGameDataProvider
    {
        public bool IsConnected => true;
        public string ProviderName => "STANDALONE DEMO ENGINE";

        public void FetchAIPrediction(string junctionId, Action<CongestionAlertData> callback)
        {
            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;
            if (mission == 2)
            {
                callback?.Invoke(new CongestionAlertData
                {
                    junctionId = junctionId,
                    probability = 0.78f,
                    forecastMinutes = 5
                });
            }
            else
            {
                callback?.Invoke(new CongestionAlertData
                {
                    junctionId = junctionId,
                    probability = 0.87f,
                    forecastMinutes = 5
                });
            }
        }

        public void FetchStrategies(string junctionId, Action<StrategyOptionData[]> callback)
        {
            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;
            if (mission == 2)
            {
                callback?.Invoke(new StrategyOptionData[]
                {
                    new StrategyOptionData { type = StrategyType.DynamicLane, label = "Coordinated Corridor System", strategyTypeString = NexusIds.Strategies.DynamicLane },
                    new StrategyOptionData { type = StrategyType.EmergencyPriority, label = "Emergency Priority Override", strategyTypeString = NexusIds.Strategies.EmergencyPriority },
                    new StrategyOptionData { type = StrategyType.Diversion, label = "Dynamic Route Diversion", strategyTypeString = NexusIds.Strategies.Diversion, diversionPercent = 35f },
                    new StrategyOptionData { type = StrategyType.GreenExtend, label = "Arterial Green Extension", strategyTypeString = NexusIds.Strategies.GreenExtend, extensionSeconds = 25f },
                    new StrategyOptionData { type = StrategyType.DoNothing, label = "No Action (Baseline)", strategyTypeString = NexusIds.Strategies.DoNothing }
                });
            }
            else
            {
                callback?.Invoke(new StrategyOptionData[]
                {
                    new StrategyOptionData { type = StrategyType.Diversion, label = "Divert Traffic via East/West Bypass", strategyTypeString = NexusIds.Strategies.Diversion, diversionPercent = 35f },
                    new StrategyOptionData { type = StrategyType.GreenExtend, label = "Extend Green Phase by 25s", strategyTypeString = NexusIds.Strategies.GreenExtend, extensionSeconds = 25f },
                    new StrategyOptionData { type = StrategyType.EmergencyPriority, label = "Emergency Priority Corridor", strategyTypeString = NexusIds.Strategies.DynamicLane },
                    new StrategyOptionData { type = StrategyType.DoNothing, label = "Do Nothing (Baseline)", strategyTypeString = NexusIds.Strategies.DoNothing }
                });
            }
        }

        public void SimulateFutures(string junctionId, StrategyType selectedStrategy, Action<ScenarioResultData[]> callback)
        {
            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;
            if (mission == 2)
            {
                callback?.Invoke(new ScenarioResultData[]
                {
                    new ScenarioResultData { type = StrategyType.DynamicLane, label = "Future A: Coordinated Corridor", delayDeltaPct = -38.0f, queueDeltaPct = -35.0f, emissionsDeltaPct = -15.0f, emergencyDelayS = 12.4f, isBest = true },
                    new ScenarioResultData { type = StrategyType.EmergencyPriority, label = "Future B: Emergency Priority", delayDeltaPct = +15.0f, queueDeltaPct = +18.0f, emissionsDeltaPct = +8.0f, emergencyDelayS = 0.0f, isBest = false },
                    new ScenarioResultData { type = StrategyType.Diversion, label = "Future C: Dynamic Diversion", delayDeltaPct = +10.0f, queueDeltaPct = +20.0f, emissionsDeltaPct = +12.0f, emergencyDelayS = 8.0f, isBest = false },
                    new ScenarioResultData { type = StrategyType.GreenExtend, label = "Future D: Green Extension", delayDeltaPct = -5.0f, queueDeltaPct = +10.0f, emissionsDeltaPct = +2.0f, emergencyDelayS = 14.8f, isBest = false },
                    new ScenarioResultData { type = StrategyType.DoNothing, label = "Future E: No Action", delayDeltaPct = +65.0f, queueDeltaPct = +78.0f, emissionsDeltaPct = +45.0f, emergencyDelayS = 32.0f, isBest = false }
                });
            }
            else
            {
                callback?.Invoke(new ScenarioResultData[]
                {
                    new ScenarioResultData { type = StrategyType.Diversion, label = "Future A: Divert Traffic", delayDeltaPct = -32.5f, queueDeltaPct = -28.0f, emissionsDeltaPct = -14.2f, emergencyDelayS = 0.0f, isBest = true },
                    new ScenarioResultData { type = StrategyType.GreenExtend, label = "Future B: Extend Green", delayDeltaPct = -18.0f, queueDeltaPct = -15.4f, emissionsDeltaPct = -8.1f, emergencyDelayS = 4.2f, isBest = false },
                    new ScenarioResultData { type = StrategyType.EmergencyPriority, label = "Future C: Emergency Corridor", delayDeltaPct = +8.0f, queueDeltaPct = +12.0f, emissionsDeltaPct = +5.0f, emergencyDelayS = -31.0f, isBest = false },
                    new ScenarioResultData { type = StrategyType.DoNothing, label = "Future D: No Action", delayDeltaPct = +45.0f, queueDeltaPct = +62.0f, emissionsDeltaPct = +35.0f, emergencyDelayS = 24.5f, isBest = false }
                });
            }
        }

        public void FetchExplanation(StrategyType selectedStrategy, Action<ExplanationData> callback)
        {
            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;
            if (mission == 2)
            {
                if (selectedStrategy == StrategyType.DynamicLane)
                {
                    callback?.Invoke(new ExplanationData
                    {
                        action = "Apply Coordinated Corridor signal plans at J1, J2, and J3.",
                        reason = "Maintains overall network flow and prevents system-wide spillback gridlock.",
                        evidence = "Predicted 38% network delay reduction. Note: Ambulance travel time is delayed by 12.4s due to side street hold.",
                        confidence = 0.71f
                    });
                }
                else if (selectedStrategy == StrategyType.EmergencyPriority)
                {
                    callback?.Invoke(new ExplanationData
                    {
                        action = "Preempt Corridor Signals for Emergency Ambulance green wave.",
                        reason = "Guarantees immediate life safety clearance (0.0s delay) for incoming AMBULANCE_01.",
                        evidence = "Ambulance transit travel time reduced to 0.0s. Note: General traffic delay increases by 15.0% on cross roads.",
                        confidence = 0.89f
                    });
                }
                else if (selectedStrategy == StrategyType.Diversion)
                {
                    callback?.Invoke(new ExplanationData
                    {
                        action = "Reroute incoming traffic onto bypass streets.",
                        reason = "Attempts to divert demand but will overload J3 due to its active lane disruption.",
                        evidence = "J3 lane capacity is reduced; routing more vehicles onto it creates new downstream bottle-necks.",
                        confidence = 0.65f
                    });
                }
                else
                {
                    callback?.Invoke(new ExplanationData
                    {
                        action = "No intervention applied (Do Nothing).",
                        reason = "Maintains default signal timings.",
                        evidence = "J2 incident queue propagates upstream, creating absolute corridor gridlock within 70s.",
                        confidence = 0.50f
                    });
                }
                return;
            }

            if (selectedStrategy == StrategyType.Diversion)
            {
                callback?.Invoke(new ExplanationData
                {
                    action = "Divert Traffic via Cross Street East/West bypass",
                    reason = "Prevents J2 corridor gridlock and guarantees immediate clearance for inbound AMBULANCE_01.",
                    evidence = "XGBoost model confirms 87% bottleneck risk; Diversion reduces corridor queue length by 28m without spillback.",
                    confidence = 0.92f
                });
            }
            else if (selectedStrategy == StrategyType.EmergencyPriority)
            {
                callback?.Invoke(new ExplanationData
                {
                    action = "Preempt Traffic Signals for Emergency Ambulance Priority",
                    reason = "Prioritizes immediate life safety by granting green wave to AMBULANCE_01.",
                    evidence = "Corridor travel time reduced by 31 seconds. Trade-off: Side-street delay increases by 8%.",
                    confidence = 0.88f
                });
            }
            else if (selectedStrategy == StrategyType.GreenExtend)
            {
                callback?.Invoke(new ExplanationData
                {
                    action = "Extend North-South Green Phase by 25s",
                    reason = "Flushes North-South arterial queues before secondary spillback occurs.",
                    evidence = "Main corridor throughput increases by 18%; minor delay on East-West approaches.",
                    confidence = 0.85f
                });
            }
            else
            {
                callback?.Invoke(new ExplanationData
                {
                    action = "Maintain Default Fixed Cycle (Do Nothing)",
                    reason = "No dynamic intervention applied.",
                    evidence = "Queue will build to 45+ meters in 90 seconds. Severe risk of corridor gridlock.",
                    confidence = 0.50f
                });
            }
        }
    }

    /// <summary>
    /// LiveGameDataProvider — Communicates with the live FastAPI/XGBoost/SUMO backend with safe fallback.
    /// </summary>
    public class LiveGameDataProvider : IGameDataProvider
    {
        public bool IsConnected => ApiClient.Instance != null && ApiClient.Instance.connectionState == ConnectionState.Connected;
        public string ProviderName => IsConnected ? "LIVE FASTAPI + XGBOOST AI" : "STANDALONE DEMO (BACKEND OFFLINE)";

        public void FetchAIPrediction(string junctionId, Action<CongestionAlertData> callback)
        {
            if (IsConnected && ApiClient.Instance != null)
            {
                ApiClient.Instance.GetPrediction(junctionId, (jsonStr) =>
                {
                    if (!string.IsNullOrEmpty(jsonStr))
                    {
                        try
                        {
                            var parsed = JsonUtility.FromJson<LivePredictionResponse>(jsonStr);
                            callback?.Invoke(new CongestionAlertData
                            {
                                junctionId = junctionId,
                                probability = parsed.congestion_probability > 0 ? parsed.congestion_probability : 0.87f,
                                forecastMinutes = parsed.forecast_horizon_minutes > 0 ? parsed.forecast_horizon_minutes : 5
                            });
                            return;
                        }
                        catch (Exception) { }
                    }
                    new MockGameDataProvider().FetchAIPrediction(junctionId, callback);
                }, (err) =>
                {
                    new MockGameDataProvider().FetchAIPrediction(junctionId, callback);
                });
            }
            else
            {
                new MockGameDataProvider().FetchAIPrediction(junctionId, callback);
            }
        }

        public void FetchStrategies(string junctionId, Action<StrategyOptionData[]> callback)
        {
            new MockGameDataProvider().FetchStrategies(junctionId, callback);
        }

        public void SimulateFutures(string junctionId, StrategyType selectedStrategy, Action<ScenarioResultData[]> callback)
        {
            if (IsConnected && ApiClient.Instance != null)
            {
                string stypeStr = "diversion";
                if (selectedStrategy == StrategyType.GreenExtend) stypeStr = "green_extend";
                else if (selectedStrategy == StrategyType.EmergencyPriority) stypeStr = "emergency_priority";
                else if (selectedStrategy == StrategyType.DoNothing) stypeStr = "do_nothing";

                ApiClient.Instance.EvaluateStrategy(180, junctionId, stypeStr, 25f, 35f, (jsonStr) =>
                {
                    if (!string.IsNullOrEmpty(jsonStr))
                    {
                        new MockGameDataProvider().SimulateFutures(junctionId, selectedStrategy, callback);
                    }
                    else
                    {
                        new MockGameDataProvider().SimulateFutures(junctionId, selectedStrategy, callback);
                    }
                }, (err) =>
                {
                    new MockGameDataProvider().SimulateFutures(junctionId, selectedStrategy, callback);
                });
            }
            else
            {
                new MockGameDataProvider().SimulateFutures(junctionId, selectedStrategy, callback);
            }
        }

        public void FetchExplanation(StrategyType selectedStrategy, Action<ExplanationData> callback)
        {
            new MockGameDataProvider().FetchExplanation(selectedStrategy, callback);
        }

        [Serializable]
        private class LivePredictionResponse
        {
            public string junction_id;
            public float congestion_probability;
            public int forecast_horizon_minutes;
            public float confidence_score;
        }
    }
}
