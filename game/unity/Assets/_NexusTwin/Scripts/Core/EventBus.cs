using System;

namespace NexusTwin.Core
{
    /// <summary>
    /// Lightweight publish/subscribe event bus for decoupling game systems.
    /// Gameplay scripts raise events here; UI scripts listen.
    /// No direct coupling between gameplay logic and UI internals.
    /// </summary>
    public static class EventBus
    {
        // --- Traffic Events ---
        public static event Action<string, float> OnCongestionAlert;          // junctionId, probability
        public static event Action<string, string> OnIncidentTriggered;       // junctionId, incidentType
        public static event Action<string> OnIncidentResolved;                // junctionId

        // --- AI / Decision Events ---
        public static event Action<CongestionAlertData> OnAIPrediction;
        public static event Action<StrategyOptionData[]> OnStrategiesReady;
        public static event Action<ScenarioResultData[]> OnSimulationComplete;
        public static event Action<ExplanationData> OnExplanationReady;
        public static event Action<DisagreementData> OnDisagreementTriggered;

        // --- Player Action Events ---
        public static event Action<StrategyOptionData> OnStrategySelected;
        public static event Action OnSimulateRequested;
        public static event Action OnApproved;
        public static event Action OnRejected;
        public static event Action OnMissionRestart;
        public static event Action OnPlayClicked;

        // --- Score & Mission Events ---
        public static event Action<ScoreBreakdownData> OnScoreUpdated;
        public static event Action<ScoreBreakdownData> OnScenarioComplete;
        public static event Action<MissionFailureData> OnMissionFailed;

        // --- Game State Events ---
        public static event Action<Data.GameState> OnGameStateChanged;

        // --- Raise Methods ---
        public static void RaiseCongestionAlert(string junctionId, float probability)
            => OnCongestionAlert?.Invoke(junctionId, probability);

        public static void RaiseIncidentTriggered(string junctionId, string incidentType)
            => OnIncidentTriggered?.Invoke(junctionId, incidentType);

        public static void RaiseIncidentResolved(string junctionId)
            => OnIncidentResolved?.Invoke(junctionId);

        public static void RaiseAIPrediction(CongestionAlertData alert)
            => OnAIPrediction?.Invoke(alert);

        public static void RaiseStrategiesReady(StrategyOptionData[] options)
            => OnStrategiesReady?.Invoke(options);

        public static void RaiseSimulationComplete(ScenarioResultData[] results)
            => OnSimulationComplete?.Invoke(results);

        public static void RaiseExplanationReady(ExplanationData explanation)
            => OnExplanationReady?.Invoke(explanation);

        public static void RaiseDisagreementTriggered(DisagreementData disagreement)
            => OnDisagreementTriggered?.Invoke(disagreement);

        public static void RaiseStrategySelected(StrategyOptionData option)
            => OnStrategySelected?.Invoke(option);

        public static void RaiseSimulateRequested()
            => OnSimulateRequested?.Invoke();

        public static void RaiseApproved()
            => OnApproved?.Invoke();

        public static void RaiseRejected()
            => OnRejected?.Invoke();

        public static void RaiseMissionRestart()
            => OnMissionRestart?.Invoke();

        public static void RaisePlayClicked()
            => OnPlayClicked?.Invoke();

        public static void RaiseScoreUpdated(ScoreBreakdownData score)
            => OnScoreUpdated?.Invoke(score);

        public static void RaiseScenarioComplete(ScoreBreakdownData score)
            => OnScenarioComplete?.Invoke(score);

        public static void RaiseMissionFailed(MissionFailureData failure)
            => OnMissionFailed?.Invoke(failure);

        public static void RaiseGameStateChanged(Data.GameState state)
            => OnGameStateChanged?.Invoke(state);
    }

    // --- Event Data Structs ---

    [Serializable]
    public struct DisagreementData
    {
        public string playerAction;
        public string aiRecommendation;
        public string tradeOffReason;
        public float networkDelayDeltaPct;
        public float emergencyDelayDeltaS;
    }

    [Serializable]
    public struct MissionFailureData
    {
        public string title;
        public string reason;
        public float finalQueue;
        public float ambulanceDelay;
    }

    [Serializable]
    public struct CongestionAlertData
    {
        public string junctionId;
        public float probability;
        public int forecastMinutes;
    }

    [Serializable]
    public struct StrategyOptionData
    {
        public Data.StrategyType type;
        public string label;
        public string strategyTypeString; // backend-compatible string from NexusIds
        public float extensionSeconds;    // for green_extend
        public float diversionPercent;    // for diversion
    }

    [Serializable]
    public struct ScenarioResultData
    {
        public Data.StrategyType type;
        public string label;
        public float delayDeltaPct;
        public float queueDeltaPct;
        public float emissionsDeltaPct;
        public float emergencyDelayS;
        public bool isBest;
    }

    [Serializable]
    public struct ExplanationData
    {
        public string action;
        public string reason;
        public string evidence;
        public float confidence;
    }

    [Serializable]
    public struct ScoreBreakdownData
    {
        public int trafficFlow;
        public int emergencySafety;
        public int queueControl;
        public int decisionQuality;
        public int Total => trafficFlow + emergencySafety + queueControl + decisionQuality;
    }
}
