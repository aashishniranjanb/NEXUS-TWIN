using UnityEngine;
using NexusTwin.Core;
using NexusTwin.Data;
using NexusTwin.Gameplay;
using NexusTwin.Vehicles;

namespace NexusTwin.Scoring
{
    /// <summary>
    /// ScoreController — Tracks, calculates, and publishes network performance scores.
    /// Evaluates traffic flow, emergency safety, queue reduction, delay reduction, and decision quality.
    /// Implements Phase M specifications.
    /// </summary>
    public class ScoreController : MonoBehaviour
    {
        public static ScoreController Instance { get; private set; }

        [Header("Metric Baselines")]
        public float initialMeanQueue = 35.0f;
        public float initialAvgDelay = 0.28f;

        [Header("Current Live Metrics")]
        public float currentMeanQueue = 35.0f;
        public float currentAvgDelay = 0.28f;
        public float emergencyDelaySeconds = 0.0f;

        [Header("Scores")]
        public int trafficFlowScore = 0;
        public int emergencySafetyScore = 0;
        public int queueControlScore = 0;
        public int decisionQualityScore = 0;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Update()
        {
            if (VehicleManager.Instance != null)
            {
                var active = VehicleManager.Instance.activeVehicles;
                int stoppedCount = 0;
                float totalSpeed = 0f;
                int count = active.Count;

                VehicleAgent ambulance = null;
                for (int i = 0; i < count; i++)
                {
                    var v = active[i];
                    if (v != null)
                    {
                        if (v.isStopped) stoppedCount++;
                        totalSpeed += v.currentSpeed;
                        if (v.vehicleType == VehicleType.Ambulance && v.isEmergency)
                        {
                            ambulance = v;
                        }
                    }
                }

                if (count > 0)
                {
                    currentMeanQueue = stoppedCount * 6.5f;
                    currentAvgDelay = (count - (totalSpeed / 14f)) * 0.1f;
                }

                // Dynamic emergency delays (ambulance blocked)
                if (ambulance != null)
                {
                    if (ambulance.currentSpeed < 2.0f)
                    {
                        emergencyDelaySeconds += Time.deltaTime;
                    }
                }
            }
        }

        private void Start()
        {
            EventBus.OnApproved += CalculatePostApprovalScore;
        }

        private void OnDestroy()
        {
            EventBus.OnApproved -= CalculatePostApprovalScore;
        }

        public ScoreBreakdownData ComputeScore(float delayReductionPct, float queueReductionPct, float emergencyDelay, bool optimalDecision)
        {
            // Traffic Flow: up to 300 pts based on delay reduction
            trafficFlowScore = Mathf.Clamp(Mathf.RoundToInt(200f + delayReductionPct * 3.0f), 50, 350);

            // Emergency Safety: 350 pts if emergency delay is 0, penalized if delayed
            emergencySafetyScore = Mathf.Max(0, Mathf.RoundToInt(350f - emergencyDelay * 20f));

            // Queue Control: up to 250 pts based on queue reduction
            queueControlScore = Mathf.Clamp(Mathf.RoundToInt(150f + queueReductionPct * 2.5f), 20, 280);

            // Decision Quality: 150 pts if player chose the top AI strategy
            decisionQualityScore = optimalDecision ? 150 : 50;

            ScoreBreakdownData breakdown = new ScoreBreakdownData
            {
                trafficFlow = trafficFlowScore,
                emergencySafety = emergencySafetyScore,
                queueControl = queueControlScore,
                decisionQuality = decisionQualityScore
            };

            EventBus.RaiseScoreUpdated(breakdown);
            return breakdown;
        }

        private void CalculatePostApprovalScore()
        {
            if (ScenarioDirector.Instance == null)
            {
                ComputeScore(32.5f, 28.0f, 0.0f, true);
                return;
            }

            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;
            bool approved = ScenarioDirector.Instance.approved;
            StrategyType sType = ScenarioDirector.Instance.selectedStrategy.type;

            if (mission == 2)
            {
                if (!approved)
                {
                    ComputeScore(-65.0f, -78.0f, 32.0f, false);
                }
                else
                {
                    switch (sType)
                    {
                        case StrategyType.DynamicLane:
                            ComputeScore(38.0f, 35.0f, 12.4f, true);
                            break;
                        case StrategyType.EmergencyPriority:
                            ComputeScore(-15.0f, -18.0f, 0.0f, false);
                            break;
                        case StrategyType.Diversion:
                            ComputeScore(-10.0f, -20.0f, 8.0f, false);
                            break;
                        case StrategyType.GreenExtend:
                            ComputeScore(5.0f, -10.0f, 14.8f, false);
                            break;
                        case StrategyType.DoNothing:
                            ComputeScore(-65.0f, -78.0f, 32.0f, false);
                            break;
                        default:
                            ComputeScore(0.0f, 0.0f, 0.0f, false);
                            break;
                    }
                }
            }
            else
            {
                if (!approved)
                {
                    ComputeScore(-45.0f, -62.0f, 24.5f, false);
                }
                else
                {
                    switch (sType)
                    {
                        case StrategyType.Diversion:
                            ComputeScore(32.5f, 28.0f, 0.0f, true);
                            break;
                        case StrategyType.GreenExtend:
                            ComputeScore(18.0f, 15.4f, 4.2f, false);
                            break;
                        case StrategyType.DynamicLane:
                            ComputeScore(6.5f, 4.0f, 6.8f, false);
                            break;
                        case StrategyType.DoNothing:
                            ComputeScore(-45.0f, -62.0f, 24.5f, false);
                            break;
                        default:
                            ComputeScore(0.0f, 0.0f, 0.0f, false);
                            break;
                    }
                }
            }
        }
    }
}
