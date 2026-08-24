using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;
using NexusTwin.Gameplay;

namespace NexusTwin.UI
{
    /// <summary>
    /// HUDController — Primary Heads-Up Display orchestrator.
    /// Manages TopBar, MainMenu, Cinematic, Briefing, AI Alert, Strategy, Counterfactual Cards,
    /// Explanation, AI Disagreement, Failure, and Score Debriefing panels.
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

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Start()
        {
            EventBus.OnGameStateChanged += UpdateStateDisplay;
            EventBus.OnScoreUpdated += UpdateScoreDisplay;
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
            EventBus.OnScoreUpdated -= UpdateScoreDisplay;
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
                }
            }
        }

        private void UpdateStateDisplay(GameState state)
        {
            if (stateText != null)
            {
                bool isLive = (GameManager.Instance != null && !GameManager.Instance.useMockData && GameManager.Instance.isBackendConnected);
                string modeLabel = isLive ? "LIVE AI" : "DEMO MODE";
                stateText.text = $"[{modeLabel}] {state.ToString().ToUpper()}";
            }

            if (topBarRoot != null)
            {
                // Only show top bar during active gameplay or debriefing
                topBarRoot.SetActive(state != GameState.MainMenu && state != GameState.Cinematic);
            }

            // Centralized GameState UI Layout Manager
            switch (state)
            {
                case GameState.MainMenu:
                    if (mainMenuPanel != null && mainMenuPanel.panelRoot != null) mainMenuPanel.panelRoot.SetActive(true);
                    if (missionBriefingPanel != null && missionBriefingPanel.panelRoot != null) missionBriefingPanel.panelRoot.SetActive(false);
                    if (failurePanel != null && failurePanel.panelRoot != null) failurePanel.panelRoot.SetActive(false);
                    if (scoreDebriefPanel != null && scoreDebriefPanel.panelRoot != null) scoreDebriefPanel.panelRoot.SetActive(false);
                    HideWorkflowPanels();
                    break;

                case GameState.Cinematic:
                    if (mainMenuPanel != null && mainMenuPanel.panelRoot != null) mainMenuPanel.panelRoot.SetActive(false);
                    if (missionBriefingPanel != null && missionBriefingPanel.panelRoot != null) missionBriefingPanel.panelRoot.SetActive(false);
                    if (failurePanel != null && failurePanel.panelRoot != null) failurePanel.panelRoot.SetActive(false);
                    if (scoreDebriefPanel != null && scoreDebriefPanel.panelRoot != null) scoreDebriefPanel.panelRoot.SetActive(false);
                    HideWorkflowPanels();
                    break;

                case GameState.Briefing:
                    if (mainMenuPanel != null && mainMenuPanel.panelRoot != null) mainMenuPanel.panelRoot.SetActive(false);
                    if (missionBriefingPanel != null && missionBriefingPanel.panelRoot != null) missionBriefingPanel.panelRoot.SetActive(true);
                    if (failurePanel != null && failurePanel.panelRoot != null) failurePanel.panelRoot.SetActive(false);
                    if (scoreDebriefPanel != null && scoreDebriefPanel.panelRoot != null) scoreDebriefPanel.panelRoot.SetActive(false);
                    HideWorkflowPanels();
                    break;

                case GameState.Idle:
                case GameState.Event:
                case GameState.Apply:
                case GameState.Result:
                    if (mainMenuPanel != null && mainMenuPanel.panelRoot != null) mainMenuPanel.panelRoot.SetActive(false);
                    if (missionBriefingPanel != null && missionBriefingPanel.panelRoot != null) missionBriefingPanel.panelRoot.SetActive(false);
                    if (failurePanel != null && failurePanel.panelRoot != null) failurePanel.panelRoot.SetActive(false);
                    if (scoreDebriefPanel != null && scoreDebriefPanel.panelRoot != null) scoreDebriefPanel.panelRoot.SetActive(false);
                    HideWorkflowPanels();
                    break;

                case GameState.Analysis:
                    if (alertPanel != null && alertPanel.panelRoot != null) alertPanel.panelRoot.SetActive(true);
                    if (strategyPanel != null) strategyPanel.Hide();
                    if (cardPanel != null) cardPanel.Hide();
                    if (explanationPanel != null) explanationPanel.Hide();
                    if (decisionButtons != null && decisionButtons.panelRoot != null) decisionButtons.panelRoot.SetActive(false);
                    break;

                case GameState.Decision:
                case GameState.Simulation:
                    if (alertPanel != null && alertPanel.panelRoot != null) alertPanel.panelRoot.SetActive(true);
                    if (strategyPanel != null && strategyPanel.panelRoot != null) strategyPanel.panelRoot.SetActive(true);
                    if (cardPanel != null) cardPanel.Hide();
                    if (explanationPanel != null) explanationPanel.Hide();
                    if (decisionButtons != null && decisionButtons.panelRoot != null) decisionButtons.panelRoot.SetActive(false);
                    break;

                case GameState.Comparison:
                    if (alertPanel != null && alertPanel.panelRoot != null) alertPanel.panelRoot.SetActive(true);
                    if (strategyPanel != null) strategyPanel.Hide();
                    if (cardPanel != null && cardPanel.panelRoot != null) cardPanel.panelRoot.SetActive(true);
                    if (explanationPanel != null) explanationPanel.Hide();
                    if (decisionButtons != null && decisionButtons.panelRoot != null) decisionButtons.panelRoot.SetActive(false);
                    break;

                case GameState.Explanation:
                case GameState.Approval:
                    if (alertPanel != null && alertPanel.panelRoot != null) alertPanel.panelRoot.SetActive(true);
                    if (strategyPanel != null) strategyPanel.Hide();
                    if (cardPanel != null && cardPanel.panelRoot != null) cardPanel.panelRoot.SetActive(true);
                    if (explanationPanel != null && explanationPanel.panelRoot != null) explanationPanel.panelRoot.SetActive(true);
                    if (decisionButtons != null && decisionButtons.panelRoot != null) decisionButtons.panelRoot.SetActive(true);
                    break;

                case GameState.Score:
                    HideWorkflowPanels();
                    if (scoreDebriefPanel != null && scoreDebriefPanel.panelRoot != null) scoreDebriefPanel.panelRoot.SetActive(true);
                    break;

                case GameState.Failed:
                    HideWorkflowPanels();
                    if (failurePanel != null && failurePanel.panelRoot != null) failurePanel.panelRoot.SetActive(true);
                    break;
            }
        }

        private void HideWorkflowPanels()
        {
            if (alertPanel != null) alertPanel.Hide();
            if (strategyPanel != null) strategyPanel.Hide();
            if (cardPanel != null) cardPanel.Hide();
            if (explanationPanel != null) explanationPanel.Hide();
            if (decisionButtons != null && decisionButtons.panelRoot != null) decisionButtons.panelRoot.SetActive(false);
            if (disagreementModal != null && disagreementModal.modalRoot != null) disagreementModal.modalRoot.SetActive(false);
        }

        private void UpdateScoreDisplay(ScoreBreakdownData score)
        {
            _currentScore = score.Total;
            if (scoreText != null)
            {
                scoreText.text = $"SCORE: {_currentScore}";
            }
        }

        private void HandleScenarioComplete(ScoreBreakdownData score)
        {
            Debug.Log($"[HUDController] Scenario Complete — Final Score: {score.Total}");
        }
    }
}
