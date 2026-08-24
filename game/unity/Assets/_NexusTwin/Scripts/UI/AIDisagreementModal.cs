using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    public class AIDisagreementModal : MonoBehaviour
    {
        public GameObject modalRoot;
        public Text headerText;
        public Text playerChoiceText;
        public Text aiRecommendationText;
        public Text tradeOffsText;
        public Button continueButton;
        public Button reconsiderButton;

        private DisagreementData _currentData;

        private void Start()
        {
            if (continueButton != null)
                continueButton.onClick.AddListener(OnContinueClicked);
            if (reconsiderButton != null)
                reconsiderButton.onClick.AddListener(OnReconsiderClicked);

            EventBus.OnDisagreementTriggered += ShowDisagreement;
        }

        private void OnDestroy()
        {
            EventBus.OnDisagreementTriggered -= ShowDisagreement;
        }

        public void ShowDisagreement(DisagreementData data)
        {
            _currentData = data;
            if (modalRoot != null) modalRoot.SetActive(true);
            SoundManager.Instance?.PlayAlert();

            if (headerText != null)
                headerText.text = "⚠ AI RECOMMENDATION DISAGREEMENT";

            if (playerChoiceText != null)
                playerChoiceText.text = $"Your Strategy: <color=#0055FF><b>{data.playerAction}</b></color>";

            if (aiRecommendationText != null)
                aiRecommendationText.text = $"AI Recommended: <color=#39E75F><b>{data.aiRecommendation}</b></color>";

            if (tradeOffsText != null)
            {
                tradeOffsText.text = $"<b>Trade-off Analysis:</b>\n" +
                                     $"{data.tradeOffReason}\n" +
                                     $"• Network Delay Impact: <b>{(data.networkDelayDeltaPct >= 0 ? "+" : "")}{data.networkDelayDeltaPct:F1}%</b>\n" +
                                     $"• Emergency Clearance: <b>{(data.emergencyDelayDeltaS <= 0 ? "" : "+")}{data.emergencyDelayDeltaS:F1} sec</b>";
            }
        }

        private void OnContinueClicked()
        {
            SoundManager.Instance?.PlayApprove();
            if (modalRoot != null) modalRoot.SetActive(false);
            EventBus.RaiseApproved();
        }

        private void OnReconsiderClicked()
        {
            SoundManager.Instance?.PlayReject();
            if (modalRoot != null) modalRoot.SetActive(false);
            GameManager.Instance?.SetState(GameState.Decision);
        }
    }
}
