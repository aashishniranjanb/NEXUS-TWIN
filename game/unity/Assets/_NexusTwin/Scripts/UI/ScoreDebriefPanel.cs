using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

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

        private void OnReplayClicked()
        {
            SoundManager.Instance?.PlayClick();
            if (panelRoot != null) panelRoot.SetActive(false);
            EventBus.RaiseMissionRestart();
        }

        private void OnNextMissionClicked()
        {
            SoundManager.Instance?.PlayClick();
            Debug.Log("[ScoreDebrief] Mission 02 selected — The Heist Escape Route");
            if (panelRoot != null) panelRoot.SetActive(false);
            EventBus.RaiseMissionRestart();
        }
    }
}
