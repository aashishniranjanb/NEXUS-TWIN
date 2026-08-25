using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// AIAlertPanel — Polished AI Congestion Risk alert panel.
    /// Features: animated entrance, pulsing risk bar, typewriter reveal, color-coded severity.
    /// Press [TAB] to dismiss.
    /// </summary>
    public class AIAlertPanel : MonoBehaviour
    {
        [Header("UI Text Fields")]
        public Text titleText;
        public Text junctionText;
        public Text probabilityText;
        public Text forecastText;
        public Text recommendationText;
        public Text mockBadgeText;

        [Header("Visual Container")]
        public GameObject panelRoot;
        public Image panelBackground;
        public Image accentBar;
        public Image riskBar;
        public Image riskBarFill;
        public Image warningIcon;

        // Color coding
        private static readonly Color LowRiskColor    = new Color(0.22f, 0.78f, 0.40f); // green
        private static readonly Color MedRiskColor    = new Color(0.95f, 0.72f, 0.15f); // amber
        private static readonly Color HighRiskColor   = new Color(0.85f, 0.25f, 0.18f); // red
        private static readonly Color CriticalColor   = new Color(0.95f, 0.10f, 0.10f); // bright red

        private CanvasGroup _cg;
        private RectTransform _rect;
        private Coroutine _pulseRoutine;

        private void Awake()
        {
            _cg = panelRoot != null ? panelRoot.GetComponent<CanvasGroup>() : null;
            _rect = panelRoot != null ? panelRoot.GetComponent<RectTransform>() : null;
            if (panelRoot != null && _cg == null) _cg = panelRoot.AddComponent<CanvasGroup>();
        }

        private void Start()
        {
            EventBus.OnAIPrediction += ShowAlert;
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnAIPrediction -= ShowAlert;
        }

        private void Update()
        {
            // Allow player to dismiss the alert manually
            if (panelRoot != null && panelRoot.activeSelf && Input.GetKeyDown(KeyCode.Tab))
            {
                Hide();
            }
        }

        public void ShowAlert(CongestionAlertData alert)
        {
            if (panelRoot == null) return;
            panelRoot.SetActive(true);

            // Determine severity
            float prob = alert.probability;
            Color riskColor = prob >= 0.85f ? CriticalColor :
                              prob >= 0.65f ? HighRiskColor :
                              prob >= 0.40f ? MedRiskColor  :
                                             LowRiskColor;

            string severityLabel = prob >= 0.85f ? "⚠ CRITICAL" :
                                   prob >= 0.65f ? "⚠ HIGH" :
                                   prob >= 0.40f ? "MODERATE" :
                                                   "LOW";

            // Text updates
            if (titleText != null)
                titleText.text = $"AI ALERT — CONGESTION RISK: {severityLabel}";
            if (junctionText != null)
                junctionText.text = $"JUNCTION: {alert.junctionId}  ·  CONFIDENCE: {Mathf.RoundToInt(alert.confidence * 100f)}%";
            if (probabilityText != null)
            {
                probabilityText.text = $"{Mathf.RoundToInt(prob * 100f)}%";
                probabilityText.color = riskColor;
            }
            if (forecastText != null)
                forecastText.text = $"Projected congestion in {alert.forecastMinutes} min";
            if (recommendationText != null)
                recommendationText.text = "ACTION REQUIRED → Select strategy below";

            bool isMock = (GameManager.Instance != null && GameManager.Instance.useMockData);
            if (mockBadgeText != null)
            {
                mockBadgeText.gameObject.SetActive(true);
                mockBadgeText.text = isMock ? "[DEMO MODE]" : "[LIVE AI]";
                mockBadgeText.color = isMock ? MedRiskColor : new Color(0.22f, 0.78f, 0.40f);
            }

            // Accent bar color — red for critical, amber for high
            if (accentBar != null) accentBar.color = riskColor;

            // Risk bar fill
            if (riskBarFill != null)
            {
                riskBarFill.color = riskColor;
                StartCoroutine(AnimateRiskBar(prob));
            }

            // Pulse the accent bar if critical
            if (_pulseRoutine != null) StopCoroutine(_pulseRoutine);
            if (prob >= 0.85f && accentBar != null)
            {
                _pulseRoutine = StartCoroutine(UIAnimator.PulseHighlight(accentBar, Color.white, 0.4f, 5));
            }

            // Animated entrance
            if (_rect != null && _cg != null)
                StartCoroutine(UIAnimator.SlideInFromTop(_rect, _cg, 20f, 0.25f));
        }

        private IEnumerator AnimateRiskBar(float targetFill)
        {
            if (riskBarFill == null) yield break;
            float startFill = 0f;
            RectTransform rt = riskBarFill.GetComponent<RectTransform>();
            if (rt == null) yield break;

            float duration = 0.6f;
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float pct = Mathf.SmoothStep(startFill, targetFill, t / duration);
                rt.anchorMax = new Vector2(pct, rt.anchorMax.y);
                yield return null;
            }
            rt.anchorMax = new Vector2(targetFill, rt.anchorMax.y);
        }

        public void Hide()
        {
            if (panelRoot == null) return;
            if (_cg != null)
                StartCoroutine(HideFade());
            else
                panelRoot.SetActive(false);
        }

        private IEnumerator HideFade()
        {
            yield return UIAnimator.FadeOut(_cg, 0.18f);
            panelRoot.SetActive(false);
        }
    }
}
