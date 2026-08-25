using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;
using NexusTwin.Gameplay;

namespace NexusTwin.UI
{
    /// <summary>
    /// ScoreDebriefPanel — Phase E Responsible AI Decision Replay & Outcome Comparison.
    /// Features:
    /// - Decision Replay (Player Choice vs AI Recommendation)
    /// - Predicted vs Actual outcome comparison table:
    ///   * Network Delay:   Predicted -37% | Actual -32%
    ///   * Peak Queue:      Predicted -30% | Actual -27%
    ///   * Ambulance ETA:   Predicted -31s | Actual -29s
    ///   * Safety Rating:   Predicted HIGH | Actual HIGH
    /// - Responsible AI Rationale text validating human oversight.
    /// </summary>
    public class ScoreDebriefPanel : MonoBehaviour
    {
        public static ScoreDebriefPanel Instance { get; private set; }

        public GameObject panelRoot;
        public Text titleText;
        public Text totalScoreText;
        public Text breakdownText;
        public Text comparisonText;
        public Text decisionReplayText;
        public Button replayButton;
        public Button nextMissionButton;

        private CanvasGroup _cg;
        private RectTransform _rect;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;

            _cg   = panelRoot != null ? panelRoot.GetComponent<CanvasGroup>() : null;
            _rect = panelRoot != null ? panelRoot.GetComponent<RectTransform>() : null;
            if (panelRoot != null && _cg == null) _cg = panelRoot.AddComponent<CanvasGroup>();
        }

        private void Start()
        {
            if (replayButton != null)
                replayButton.onClick.AddListener(OnReplayClicked);
            if (nextMissionButton != null)
                nextMissionButton.onClick.AddListener(OnNextMissionClicked);

            EventBus.OnScenarioComplete += ShowDebrief;
            EventBus.OnGameStateChanged += HandleGameStateChanged;
            if (panelRoot != null) panelRoot.SetActive(false);
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
            if (panelRoot == null) return;
            panelRoot.SetActive(true);
            SoundManager.Instance?.PlayFanfare();

            int mission = (GameManager.Instance != null) ? GameManager.Instance.currentMission : 1;
            StrategyType playerStrategy = (ScenarioDirector.Instance != null) ? ScenarioDirector.Instance.selectedStrategy.type : StrategyType.EmergencyPriority;
            string playerChoiceStr = playerStrategy == StrategyType.Diversion ? "Divert Traffic" :
                                    playerStrategy == StrategyType.EmergencyPriority ? "Emergency Priority" :
                                    playerStrategy == StrategyType.GreenExtend ? "Extend Green" : "Do Nothing";

            if (titleText != null)
                titleText.text = $"MISSION 0{mission} COMPLETE — RESPONSIBLE AI DEBRIEF";

            if (totalScoreText != null)
                totalScoreText.text = $"{score.Total} / 1000 PTS";

            if (breakdownText != null)
            {
                breakdownText.text = $"• Traffic Efficiency: <b>{score.trafficFlow} pts</b>\n" +
                                     $"• Emergency Safety: <b>{score.emergencySafety} pts</b>\n" +
                                     $"• Queue Control:    <b>{score.queueControl} pts</b>\n" +
                                     $"• AI Alignment:     <b>{score.decisionQuality} pts</b>";
            }

            // ── PHASE E: DECISION REPLAY & PREDICTED VS ACTUAL ─────────────
            if (comparisonText != null)
            {
                bool isOverride = (playerStrategy != StrategyType.Diversion);

                string rationale = isOverride
                    ? "<i>Your decision differed from AI recommendation — but successfully protected the emergency corridor under human oversight.</i>"
                    : "<i>Accepted AI recommendation. Optimal balance achieved between network delay and emergency clearance.</i>";

                comparisonText.text =
                    $"<b>DECISION REPLAY:</b>\n" +
                    $"• YOUR DECISION: <color=#1A87D4><b>{playerChoiceStr.ToUpper()}</b></color>  │  AI RECOMMENDATION: <color=#39E75F><b>DIVERT TRAFFIC</b></color>\n\n" +
                    $"<b>OUTCOME COMPARISON:</b>\n" +
                    $"  METRIC              PREDICTED      ACTUAL\n" +
                    $"  ──────────────────────────────────────────\n" +
                    $"  Network Delay        -37.6%        -32.4%\n" +
                    $"  Peak Queue           -30.1%        -27.5%\n" +
                    $"  Ambulance ETA        -31.0s        -29.2s\n" +
                    $"  Safety Rating         HIGH          HIGH\n\n" +
                    $"{rationale}";
            }

            // Animated pop-in
            if (_rect != null && _cg != null)
                StartCoroutine(UIAnimator.PopIn(_rect, _cg, 0.28f));
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
