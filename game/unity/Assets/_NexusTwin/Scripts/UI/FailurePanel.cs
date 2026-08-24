using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    public class FailurePanel : MonoBehaviour
    {
        public GameObject panelRoot;
        public Text failureTitleText;
        public Text reasonText;
        public Text metricsText;
        public Button tryAgainButton;

        private void Start()
        {
            if (tryAgainButton != null)
                tryAgainButton.onClick.AddListener(OnTryAgainClicked);

            EventBus.OnMissionFailed += ShowFailure;
            EventBus.OnGameStateChanged += HandleGameStateChanged;
        }

        private void OnDestroy()
        {
            EventBus.OnMissionFailed -= ShowFailure;
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void Update()
        {
            if (GameManager.Instance != null && GameManager.Instance.currentState == GameState.Failed)
            {
                if (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return))
                {
                    OnTryAgainClicked();
                }
            }
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(state == GameState.Failed);
            }
        }

        public void ShowFailure(MissionFailureData data)
        {
            if (panelRoot != null) panelRoot.SetActive(true);
            SoundManager.Instance?.PlayReject();

            if (failureTitleText != null)
                failureTitleText.text = $"MISSION FAILED — {data.title.ToUpper()}";

            if (reasonText != null)
                reasonText.text = data.reason;

            if (metricsText != null)
            {
                metricsText.text = $"<b>Final Network Metrics:</b>\n" +
                                   $"• Peak Queue Buildup: <color=#D94040><b>{data.finalQueue:F1} meters</b></color>\n" +
                                   $"• Ambulance Delay: <color=#D94040><b>+{data.ambulanceDelay:F1} sec</b></color>";
            }
        }

        private void OnTryAgainClicked()
        {
            SoundManager.Instance?.PlayClick();
            if (panelRoot != null) panelRoot.SetActive(false);
            EventBus.RaiseMissionRestart();
        }
    }
}
