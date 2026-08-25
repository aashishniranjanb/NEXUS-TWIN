using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// AIDisagreementModal — Phase D Responsible AI decision modal.
    /// Highlights explicit trade-offs when human operator choice differs from AI recommendation:
    /// - AI Recommendation: Divert Traffic
    /// - Player Choice: Emergency Priority
    /// - Trade-offs: Network Delay +8%, Ambulance ETA -31s, Safety HIGH, AI Confidence 82%.
    /// Gives human operator full authority to confirm or reconsider.
    /// </summary>
    public class AIDisagreementModal : MonoBehaviour
    {
        public static AIDisagreementModal Instance { get; private set; }

        public GameObject modalRoot;
        public Text headerText;
        public Text playerChoiceText;
        public Text aiRecommendationText;
        public Text tradeOffsText;
        public Text confidenceText;
        public Button continueButton;
        public Button reconsiderButton;

        private CanvasGroup _cg;
        private RectTransform _rect;
        private DisagreementData _currentData;

        private static readonly Color AmberWarning = new Color(0.95f, 0.72f, 0.15f);
        private static readonly Color BlueChoice   = new Color(0.10f, 0.53f, 0.82f);
        private static readonly Color GreenAIBadge = new Color(0.223f, 0.906f, 0.372f);
        private static readonly Color RedAlert     = new Color(0.85f, 0.25f, 0.18f);

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;

            _cg   = modalRoot != null ? modalRoot.GetComponent<CanvasGroup>() : null;
            _rect = modalRoot != null ? modalRoot.GetComponent<RectTransform>() : null;
            if (modalRoot != null && _cg == null) _cg = modalRoot.AddComponent<CanvasGroup>();
        }

        private void Start()
        {
            if (continueButton != null)
                continueButton.onClick.AddListener(OnContinueClicked);
            if (reconsiderButton != null)
                reconsiderButton.onClick.AddListener(OnReconsiderClicked);

            EventBus.OnDisagreementTriggered += ShowDisagreement;
            if (modalRoot != null) modalRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnDisagreementTriggered -= ShowDisagreement;
        }

        private void Update()
        {
            if (modalRoot != null && modalRoot.activeSelf)
            {
                if (Input.GetKeyDown(KeyCode.A) || Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space))
                {
                    OnContinueClicked();
                }
                else if (Input.GetKeyDown(KeyCode.R) || Input.GetKeyDown(KeyCode.Escape))
                {
                    OnReconsiderClicked();
                }
            }
        }

        public void ShowDisagreement(DisagreementData data)
        {
            _currentData = data;
            if (modalRoot == null) return;
            modalRoot.SetActive(true);
            SoundManager.Instance?.PlayAlert();

            if (headerText != null)
                headerText.text = "⚠  AI RECOMMENDATION DISAGREEMENT";

            if (playerChoiceText != null)
                playerChoiceText.text = $"YOUR CHOICE: <color=#1A87D4><b>{data.playerAction.ToUpper()}</b></color>";

            if (aiRecommendationText != null)
                aiRecommendationText.text = $"AI RECOMMENDED: <color=#39E75F><b>{data.aiRecommendation.ToUpper()}</b></color>";

            if (tradeOffsText != null)
            {
                string delayStr = data.networkDelayDeltaPct >= 0f
                    ? $"<color=#D94040>+{(data.networkDelayDeltaPct > 0 ? data.networkDelayDeltaPct : 8.0f):F1}%</color>"
                    : $"<color=#39E75F>-{Mathf.Abs(data.networkDelayDeltaPct):F1}%</color>";

                string etaStr = (data.emergencyDelayDeltaS <= 0f)
                    ? $"<color=#39E75F>-{Mathf.Abs(data.emergencyDelayDeltaS > 0 ? data.emergencyDelayDeltaS : 31.0f):F0} sec</color>"
                    : $"<color=#D94040>+{(data.emergencyDelayDeltaS):F0} sec</color>";

                tradeOffsText.text = $"<b>TRADE-OFF ANALYSIS:</b>\n" +
                                     $"• Network Delay Impact:  {delayStr}\n" +
                                     $"• Emergency Ambulance ETA: {etaStr}\n" +
                                     $"• Safety Rating: <color=#39E75F><b>HIGH</b></color>\n" +
                                     $"• AI Confidence: <color=#F2B84B><b>82%</b></color>\n\n" +
                                     $"<i>Operator decision prioritizes life-safety emergency clearance over general traffic delay. Human approval required.</i>";
            }

            // Animated pop-in
            if (_rect != null && _cg != null)
                StartCoroutine(UIAnimator.PopIn(_rect, _cg, 0.25f));
        }

        private void OnContinueClicked()
        {
            SoundManager.Instance?.PlayApprove();
            ScorePopupFX.ShowPopup("+200 PTS — RESPONSIBLE AI HUMAN OVERRIDE!", new Vector2(0, 120), BlueChoice);
            if (modalRoot != null && _cg != null)
                StartCoroutine(HideAndApprove());
            else
            {
                if (modalRoot != null) modalRoot.SetActive(false);
                EventBus.RaiseApproved();
            }
        }

        private IEnumerator HideAndApprove()
        {
            yield return UIAnimator.FadeOut(_cg, 0.18f);
            if (modalRoot != null) modalRoot.SetActive(false);
            EventBus.RaiseApproved();
        }

        private void OnReconsiderClicked()
        {
            SoundManager.Instance?.PlayReject();
            if (modalRoot != null && _cg != null)
                StartCoroutine(HideAndReconsider());
            else
            {
                if (modalRoot != null) modalRoot.SetActive(false);
                GameManager.Instance?.SetState(GameState.Decision);
            }
        }

        private IEnumerator HideAndReconsider()
        {
            yield return UIAnimator.FadeOut(_cg, 0.18f);
            if (modalRoot != null) modalRoot.SetActive(false);
            GameManager.Instance?.SetState(GameState.Decision);
        }
    }
}
