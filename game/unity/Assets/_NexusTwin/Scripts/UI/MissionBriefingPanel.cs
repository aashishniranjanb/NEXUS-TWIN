using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// MissionBriefingPanel — Polished mission briefing screen.
    /// Features: animated entrance, typewriter situation text, pulsing threat badge,
    /// and SPACE/ENTER to start. Supports Mission 01 and 02.
    /// </summary>
    public class MissionBriefingPanel : MonoBehaviour
    {
        public GameObject panelRoot;
        public Text missionTitleText;
        public Text situationText;
        public Text objectiveText;
        public Text threatLevelText;
        public Button startMissionButton;
        public Image threatBadgeImage;

        // Animation
        private CanvasGroup _cg;
        private RectTransform _rect;
        private bool _briefingActive = false;

        private static readonly Color ThreatCritical = new Color(0.85f, 0.25f, 0.18f);
        private static readonly Color ThreatAdvanced = new Color(0.95f, 0.72f, 0.15f);

        private void Awake()
        {
            _cg   = panelRoot != null ? panelRoot.GetComponent<CanvasGroup>() : null;
            _rect = panelRoot != null ? panelRoot.GetComponent<RectTransform>() : null;
            if (panelRoot != null && _cg == null) _cg = panelRoot.AddComponent<CanvasGroup>();
        }

        private void Start()
        {
            if (startMissionButton != null)
                startMissionButton.onClick.AddListener(OnStartMissionClicked);
            EventBus.OnGameStateChanged += HandleGameStateChanged;
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void Update()
        {
            if (_briefingActive)
            {
                if (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return))
                    OnStartMissionClicked();
            }
        }

        public void SetupBriefing(int missionIndex)
        {
            if (missionIndex == 2)
            {
                if (missionTitleText != null)
                    missionTitleText.text = "MISSION 02: THE ESCAPE CORRIDOR";
                if (threatLevelText != null)
                    threatLevelText.text = "⚠  THREAT: ADVANCED — MULTIPLE EVENTS";
                if (threatBadgeImage != null)
                    threatBadgeImage.color = ThreatAdvanced;
                if (situationText != null)
                    situationText.text = "SITUATION\nDownstream traffic density rising rapidly. Secondary lane disruption near J3. Emergency vehicle crossing under conflicting constraints.";
                if (objectiveText != null)
                    objectiveText.text = "OBJECTIVE\nCoordinate corridor optimization vs direct Emergency Priority. Minimize delay while keeping ambulance transit within safety margins. Human approval required.";
            }
            else
            {
                if (missionTitleText != null)
                    missionTitleText.text = "MISSION 01: CLEAR THE EMERGENCY CORRIDOR";
                if (threatLevelText != null)
                    threatLevelText.text = "⚠  THREAT: CRITICAL — SIGNAL COMPROMISED";
                if (threatBadgeImage != null)
                    threatBadgeImage.color = ThreatCritical;
                if (situationText != null)
                    situationText.text = "SITUATION\nDeliberate traffic disruption detected at Junction J2. Signal tampering confirmed. Critical trauma ambulance (AMBULANCE_01) is en route. ETA: 4 minutes.";
                if (objectiveText != null)
                    objectiveText.text = "OBJECTIVE\nDeploy an AI-assisted adaptive traffic intervention. Evaluate Digital Twin counterfactual futures. Prevent gridlock. Secure zero-delay transit for the emergency vehicle.\n\n[SPACE] or [ENTER] to deploy →";
            }
        }

        private void HandleGameStateChanged(GameState state)
        {
            bool show = (state == GameState.Briefing);
            _briefingActive = show;

            if (show)
            {
                SetupBriefing(GameManager.Instance != null ? GameManager.Instance.currentMission : 1);
                if (panelRoot != null) panelRoot.SetActive(true);
                if (_rect != null && _cg != null)
                    StartCoroutine(UIAnimator.PopIn(_rect, _cg, 0.28f));
                if (threatBadgeImage != null)
                    StartCoroutine(UIAnimator.PulseHighlight(threatBadgeImage, Color.white, 0.5f, 4));
            }
            else
            {
                _briefingActive = false;
                if (panelRoot != null && _cg != null)
                    StartCoroutine(HideRoutine());
                else if (panelRoot != null)
                    panelRoot.SetActive(false);
            }
        }

        private IEnumerator HideRoutine()
        {
            yield return UIAnimator.FadeOut(_cg, 0.20f);
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnStartMissionClicked()
        {
            if (!_briefingActive) return;
            _briefingActive = false;
            SoundManager.Instance?.PlayClick();
            if (panelRoot != null && _cg != null)
                StartCoroutine(StartTransition());
            else
            {
                if (panelRoot != null) panelRoot.SetActive(false);
                GameManager.Instance?.SetState(GameState.Idle);
            }
        }

        private IEnumerator StartTransition()
        {
            yield return UIAnimator.FadeOut(_cg, 0.22f);
            if (panelRoot != null) panelRoot.SetActive(false);
            GameManager.Instance?.SetState(GameState.Idle);
        }
    }
}
