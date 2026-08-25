using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;
using NexusTwin.Gameplay;

namespace NexusTwin.UI
{
    /// <summary>
    /// HUDController — Primary Heads-Up Display orchestrator for NEXUS-TWIN.
    /// Polished features: live network health bar, animated score counter,
    /// state-aware top bar colors, junction status indicators,
    /// and animated state transitions across all workflow panels.
    /// </summary>
    public class HUDController : MonoBehaviour
    {
        public static HUDController Instance { get; private set; }

        [Header("Top Bar UI")]
        public GameObject topBarRoot;
        public Text titleText;
        public Text missionText;
        public Text timerText;
        public Text scoreText;
        public Text stateText;
        public Text healthText;
        public Text junctionText;
        public GameObject mockModeBanner;

        [Header("Network Health Bar")]
        public Image healthBarFill;
        public Image healthBarBg;

        [Header("Junction Status Indicators")]
        public Image j1Indicator;
        public Image j2Indicator;
        public Image j3Indicator;
        public Text j1Label;
        public Text j2Label;
        public Text j3Label;

        [Header("Top Bar Background")]
        public Image topBarBg;

        [Header("Primary Panels")]
        public MainMenuPanel mainMenuPanel;
        public IntroCinematicController introCinematic;
        public MissionBriefingPanel missionBriefingPanel;
        public AIAlertPanel alertPanel;
        public StrategyPanel strategyPanel;
        public CounterfactualCardPanel cardPanel;
        public ExplanationPanel explanationPanel;
        public DecisionButtons decisionButtons;
        public AIDisagreementModal disagreementModal;
        public FailurePanel failurePanel;
        public ScoreDebriefPanel scoreDebriefPanel;

        private float _sessionTimer = 0f;
        private int _currentScore = 0;
        private int _displayScore = 0;
        private Coroutine _scoreRoutine;

        // Color palette
        private static readonly Color TopBarNormal   = new Color(0.92f, 0.94f, 0.96f, 0.98f);
        private static readonly Color TopBarAlert     = new Color(0.14f, 0.06f, 0.05f, 0.97f);
        private static readonly Color TopBarApproval  = new Color(0.04f, 0.14f, 0.06f, 0.97f);
        private static readonly Color AccentBlue      = new Color(0.10f, 0.53f, 0.82f, 1f);
        private static readonly Color SuccessGreen    = new Color(0.22f, 0.906f, 0.372f, 1f);
        private static readonly Color WarningRed      = new Color(0.85f, 0.25f, 0.18f, 1f);
        private static readonly Color AmberYellow     = new Color(0.95f, 0.72f, 0.15f, 1f);
        private static readonly Color NavyDark        = new Color(0.06f, 0.08f, 0.12f, 1f);

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            EventBus.OnGameStateChanged += UpdateStateDisplay;
            EventBus.OnScoreUpdated     += UpdateScoreDisplay;
            EventBus.OnScenarioComplete += HandleScenarioComplete;

            if (mockModeBanner != null)
            {
                bool isMock = (GameManager.Instance != null && GameManager.Instance.useMockData);
                mockModeBanner.SetActive(isMock);
            }
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= UpdateStateDisplay;
            EventBus.OnScoreUpdated     -= UpdateScoreDisplay;
            EventBus.OnScenarioComplete -= HandleScenarioComplete;
        }

        private void Update()
        {
            if (GameManager.Instance != null && GameManager.Instance.currentState >= GameState.Idle)
            {
                _sessionTimer += Time.deltaTime;
                if (timerText != null)
                {
                    int min = Mathf.FloorToInt(_sessionTimer / 60f);
                    int sec = Mathf.FloorToInt(_sessionTimer % 60f);
                    timerText.text = $"TIME: {min:00}:{sec:00}";

                    // Color timer red when approaching 5 minutes
                    if (_sessionTimer > 240f)
                        timerText.color = WarningRed;
                    else if (_sessionTimer > 180f)
                        timerText.color = AmberYellow;
                }
            }

            // Animated score counter
            if (_displayScore != _currentScore)
            {
                _displayScore = (int)Mathf.MoveTowards(_displayScore, _currentScore, Time.deltaTime * 300f);
                if (scoreText != null)
                    scoreText.text = $"SCORE: {_displayScore}";
            }
        }

        private void UpdateStateDisplay(GameState state)
        {
            // Live/demo badge
            if (stateText != null)
            {
                bool isLive = (GameManager.Instance != null && !GameManager.Instance.useMockData && GameManager.Instance.isBackendConnected);
                string modeLabel = isLive ? "◉ LIVE AI" : "◎ DEMO MODE";
                stateText.text = modeLabel;
                stateText.color = isLive ? SuccessGreen : AccentBlue;
            }

            // Mission label
            if (missionText != null && GameManager.Instance != null)
            {
                missionText.text = (GameManager.Instance.currentMission == 2)
                    ? "MISSION 02: ESCAPE CORRIDOR"
                    : "MISSION 01: EMERGENCY CORRIDOR";
            }

            // Top bar visibility
            if (topBarRoot != null)
                topBarRoot.SetActive(state != GameState.MainMenu && state != GameState.Cinematic);

            // Top bar tint by game state
            if (topBarBg != null)
            {
                Color barColor = TopBarNormal;
                if (state == GameState.Analysis || state == GameState.Event)
                    barColor = TopBarAlert;
                else if (state == GameState.Approval)
                    barColor = TopBarApproval;
                topBarBg.color = barColor;
            }

            // Health bar update
            UpdateHealthBar(state);

            // Panel orchestration
            switch (state)
            {
                case GameState.MainMenu:
                    SetPanel(mainMenuPanel?.panelRoot, true);
                    SetPanel(missionBriefingPanel?.panelRoot, false);
                    SetPanel(failurePanel?.panelRoot, false);
                    SetPanel(scoreDebriefPanel?.panelRoot, false);
                    HideWorkflowPanels();
                    break;

                case GameState.Cinematic:
                    SetPanel(mainMenuPanel?.panelRoot, false);
                    SetPanel(missionBriefingPanel?.panelRoot, false);
                    SetPanel(failurePanel?.panelRoot, false);
                    SetPanel(scoreDebriefPanel?.panelRoot, false);
                    HideWorkflowPanels();
                    break;

                case GameState.Briefing:
                    SetPanel(mainMenuPanel?.panelRoot, false);
                    SetPanel(missionBriefingPanel?.panelRoot, true);
                    SetPanel(failurePanel?.panelRoot, false);
                    SetPanel(scoreDebriefPanel?.panelRoot, false);
                    HideWorkflowPanels();
                    break;

                case GameState.Idle:
                case GameState.Event:
                case GameState.Apply:
                case GameState.Result:
                    SetPanel(mainMenuPanel?.panelRoot, false);
                    SetPanel(missionBriefingPanel?.panelRoot, false);
                    SetPanel(failurePanel?.panelRoot, false);
                    SetPanel(scoreDebriefPanel?.panelRoot, false);
                    HideWorkflowPanels();
                    break;

                case GameState.Analysis:
                    SetPanel(alertPanel?.panelRoot, true);
                    strategyPanel?.Hide();
                    cardPanel?.Hide();
                    explanationPanel?.Hide();
                    SetPanel(decisionButtons?.panelRoot, false);
                    break;

                case GameState.Decision:
                case GameState.Simulation:
                    SetPanel(alertPanel?.panelRoot, true);
                    SetPanel(strategyPanel?.panelRoot, true);
                    cardPanel?.Hide();
                    explanationPanel?.Hide();
                    SetPanel(decisionButtons?.panelRoot, false);
                    break;

                case GameState.Comparison:
                    SetPanel(alertPanel?.panelRoot, true);
                    strategyPanel?.Hide();
                    SetPanel(cardPanel?.panelRoot, true);
                    explanationPanel?.Hide();
                    SetPanel(decisionButtons?.panelRoot, false);
                    break;

                case GameState.Explanation:
                case GameState.Approval:
                    SetPanel(alertPanel?.panelRoot, true);
                    strategyPanel?.Hide();
                    SetPanel(cardPanel?.panelRoot, true);
                    SetPanel(explanationPanel?.panelRoot, true);
                    SetPanel(decisionButtons?.panelRoot, true);
                    break;

                case GameState.Score:
                    HideWorkflowPanels();
                    SetPanel(scoreDebriefPanel?.panelRoot, true);
                    break;

                case GameState.Failed:
                    HideWorkflowPanels();
                    SetPanel(failurePanel?.panelRoot, true);
                    break;
            }
        }

        private void UpdateHealthBar(GameState state)
        {
            float health = 0.94f; // Default healthy
            Color healthColor = SuccessGreen;

            if (state == GameState.Analysis || state == GameState.Event)
            {
                health = 0.62f;
                healthColor = AmberYellow;
            }
            else if (state == GameState.Failed)
            {
                health = 0.18f;
                healthColor = WarningRed;
            }
            else if (state >= GameState.Score)
            {
                health = 0.96f;
                healthColor = SuccessGreen;
            }

            if (healthText != null)
            {
                healthText.text = $"HEALTH: {Mathf.RoundToInt(health * 100f)}%";
                healthText.color = healthColor;
            }

            if (healthBarFill != null)
            {
                healthBarFill.color = healthColor;
                StartCoroutine(AnimateHealthBar(health));
            }
        }

        private IEnumerator AnimateHealthBar(float target)
        {
            if (healthBarFill == null) yield break;
            RectTransform rt = healthBarFill.GetComponent<RectTransform>();
            if (rt == null) yield break;
            float start = rt.anchorMax.x;
            float t = 0f;
            while (t < 0.4f)
            {
                t += Time.deltaTime;
                rt.anchorMax = new Vector2(Mathf.SmoothStep(start, target, t / 0.4f), rt.anchorMax.y);
                yield return null;
            }
            rt.anchorMax = new Vector2(target, rt.anchorMax.y);
        }

        private void SetPanel(GameObject panel, bool active)
        {
            if (panel != null) panel.SetActive(active);
        }

        private void HideWorkflowPanels()
        {
            alertPanel?.Hide();
            strategyPanel?.Hide();
            cardPanel?.Hide();
            explanationPanel?.Hide();
            SetPanel(decisionButtons?.panelRoot, false);
            SetPanel(disagreementModal?.modalRoot, false);
        }

        private void UpdateScoreDisplay(ScoreBreakdownData score)
        {
            _currentScore = score.Total;
            // Animated counter runs in Update()
        }

        private void HandleScenarioComplete(ScoreBreakdownData score)
        {
            Debug.Log($"[HUDController] Mission Complete — Score: {score.Total}");
        }

        /// <summary>Sets junction indicator color. Call from ScenarioDirector on incident events.</summary>
        public void SetJunctionStatus(string junctionId, JunctionStatus status)
        {
            Image indicator = junctionId == "J1" ? j1Indicator : junctionId == "J2" ? j2Indicator : j3Indicator;
            Text label = junctionId == "J1" ? j1Label : junctionId == "J2" ? j2Label : j3Label;
            if (indicator == null) return;

            Color c = status == JunctionStatus.Normal   ? SuccessGreen :
                      status == JunctionStatus.Warning  ? AmberYellow  :
                      status == JunctionStatus.Critical ? WarningRed   :
                                                         new Color(0.5f, 0.5f, 0.6f);
            indicator.color = c;
            if (label != null) label.color = c;
            if (status == JunctionStatus.Critical)
                StartCoroutine(UIAnimator.PulseHighlight(indicator, Color.white, 0.4f, 3));
        }
    }

    public enum JunctionStatus { Normal, Warning, Critical, Closed }
}
