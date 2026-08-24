using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;
using NexusTwin.Gameplay;

namespace NexusTwin.UI
{
    public class ScoreDebriefPanel : MonoBehaviour
    {
        public GameObject panelRoot;
        public Text titleText;
        public Text totalScoreText;
        public Text breakdownText;
        public Text comparisonText;
        public Button replayButton;
        public Button nextMissionButton;

        private void Start()
        {
            if (replayButton != null)
                replayButton.onClick.AddListener(OnReplayClicked);
            if (nextMissionButton != null)
                nextMissionButton.onClick.AddListener(OnNextMissionClicked);

            EventBus.OnScenarioComplete += ShowDebrief;
            EventBus.OnGameStateChanged += HandleGameStateChanged;
        }

        private void OnDestroy()
        {
            EventBus.OnScenarioComplete -= ShowDebrief;
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(state == GameState.Score);
            }
        }

        public void ShowDebrief(ScoreBreakdownData score)
        {
            if (panelRoot != null) panelRoot.SetActive(true);
            SoundManager.Instance?.PlayFanfare();

            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;

            if (mission == 2)
            {
                if (titleText != null)
                    titleText.text = "MISSION 02 COMPLETE — THE ESCAPE CORRIDOR RESOLVED";

                if (totalScoreText != null)
                    totalScoreText.text = $"{score.Total} / 1000 PTS";

                if (breakdownText != null)
                {
                    breakdownText.text = $"• Coordinated Traffic Flow: <b>{score.trafficFlow} pts</b>\n" +
                                         $"• Emergency Corridor Priority: <b>{score.emergencySafety} pts</b>\n" +
                                         $"• Multi-Junction Spillback: <b>{score.queueControl} pts</b>\n" +
                                         $"• AI Trade-Off Alignment: <b>{score.decisionQuality} pts</b>";
                }

                if (comparisonText != null)
                {
                    StrategyType sType = (ScenarioDirector.Instance != null) ? ScenarioDirector.Instance.selectedStrategy.type : StrategyType.DynamicLane;
                    if (sType == StrategyType.EmergencyPriority)
                    {
                        comparisonText.text = $"<b>Corridor Impact Summary (Emergency Priority):</b>\n" +
                                              $"• Mean Corridor Queue: <b>35m → 42m (+20%)</b>\n" +
                                              $"• Average Network Delay: <b>0.28s → 0.32s (+15%)</b>\n" +
                                              $"• Ambulance Transit: <color=#39E75F><b>SAFE ARRIVAL (0.0s delay)</b></color>\n" +
                                              $"<i>Human Choice overridden AI recommended network flow optimization.</i>";
                    }
                    else if (sType == StrategyType.DynamicLane)
                    {
                        comparisonText.text = $"<b>Corridor Impact Summary (Coordinated Corridor):</b>\n" +
                                              $"• Mean Corridor Queue: <b>35m → 22m (-35%)</b>\n" +
                                              $"• Average Network Delay: <b>0.28s → 0.17s (-38%)</b>\n" +
                                              $"• Ambulance Transit: <color=#F2B84B><b>TRANSIT STALLED (12.4s delay)</b></color>\n" +
                                              $"<i>Accepted AI recommendation. Optimized network delay but delayed emergency response.</i>";
                    }
                    else
                    {
                        comparisonText.text = $"<b>Corridor Impact Summary (Suboptimal Choice):</b>\n" +
                                              $"• Mean Corridor Queue: <b>35m → 38m (+8%)</b>\n" +
                                              $"• Average Network Delay: <b>0.28s → 0.26s (-5%)</b>\n" +
                                              $"• Ambulance Transit: <color=#D94040><b>TRANSIT DELAYED (14.8s delay)</b></color>";
                    }
                }
            }
            else
            {
                if (titleText != null)
                    titleText.text = "MISSION 01 COMPLETE — EMERGENCY CORRIDOR SECURED";

                if (totalScoreText != null)
                    totalScoreText.text = $"{score.Total} / 1000 PTS";

                if (breakdownText != null)
                {
                    breakdownText.text = $"• Traffic Flow Efficiency: <b>{score.trafficFlow} pts</b>\n" +
                                         $"• Emergency Corridor Safety: <b>{score.emergencySafety} pts</b>\n" +
                                         $"• Queue Spillback Control: <b>{score.queueControl} pts</b>\n" +
                                         $"• AI Decision Quality: <b>{score.decisionQuality} pts</b>";
                }

                if (comparisonText != null)
                {
                    comparisonText.text = $"<b>Corridor Impact Summary:</b>\n" +
                                          $"• Mean Corridor Queue: <b>45m → 12m (-73%)</b>\n" +
                                          $"• Average Network Delay: <b>0.35s → 0.18s (-48%)</b>\n" +
                                          $"• Ambulance Transit: <color=#39E75F><b>SAFE ARRIVAL (0.0s delay)</b></color>";
                }
            }
        }

        private void OnReplayClicked()
        {
            SoundManager.Instance?.PlayClick();
            if (panelRoot != null) panelRoot.SetActive(false);
            EventBus.RaiseMissionRestart();
        }

        private void OnNextMissionClicked()
        {
            SoundManager.Instance?.PlayClick();
            if (GameManager.Instance != null)
            {
                GameManager.Instance.currentMission = (GameManager.Instance.currentMission == 1) ? 2 : 1;
            }
            if (panelRoot != null) panelRoot.SetActive(false);
            EventBus.RaiseMissionRestart();
        }
    }
}
