using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// AIAlertPanel — Displays AI Congestion Risk alerts with confidence & forecast time.
    /// Implements Phase G specifications.
    /// </summary>
    public class AIAlertPanel : MonoBehaviour
    {
        [Header("UI Text Fields")]
        public Text titleText;
        public Text junctionText;
        public Text probabilityText;
        public Text forecastText;
        public Text mockBadgeText;

        [Header("Visual Container")]
        public GameObject panelRoot;
        public Image warningIcon;

        private void Start()
        {
            EventBus.OnAIPrediction += ShowAlert;
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnAIPrediction -= ShowAlert;
        }

        public void ShowAlert(CongestionAlertData alert)
        {
            if (panelRoot != null) panelRoot.SetActive(true);

            if (titleText != null) titleText.text = "AI ALERT: HIGH CONGESTION RISK";
            if (junctionText != null) junctionText.text = $"JUNCTION: {alert.junctionId}";
            if (probabilityText != null) probabilityText.text = $"RISK PROBABILITY: {Mathf.RoundToInt(alert.probability * 100f)}%";
            if (forecastText != null) forecastText.text = $"FORECAST HORIZON: {alert.forecastMinutes} MIN";

            bool isMock = (GameManager.Instance != null && GameManager.Instance.useMockData);
            if (mockBadgeText != null)
            {
                mockBadgeText.gameObject.SetActive(isMock);
                mockBadgeText.text = isMock ? "[DEMO / MOCK DATA]" : "[LIVE AI PREDICTOR]";
            }
        }

        public void Hide()
        {
            if (panelRoot != null) panelRoot.SetActive(false);
        }
    }
}
