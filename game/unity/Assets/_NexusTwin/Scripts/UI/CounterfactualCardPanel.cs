using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;

namespace NexusTwin.UI
{
    /// <summary>
    /// CounterfactualCardPanel — Polished 4-future Digital Twin comparison panel.
    /// Features: Staggered card pop-in animation, color-coded metric deltas (green/red),
    /// AI-recommended card highlighted with glowing border and pulsing badge,
    /// animated best-card reveal sequence.
    /// </summary>
    public class CounterfactualCardPanel : MonoBehaviour
    {
        [Header("Containers")]
        public GameObject panelRoot;
        public Transform cardsContainer;
        public Text summaryHeader;

        [Header("Card Texts (Fallback / Static binding)")]
        public Text card1Title;
        public Text card1Metrics;
        public Image card1Border;

        public Text card2Title;
        public Text card2Metrics;
        public Image card2Border;

        public Text card3Title;
        public Text card3Metrics;
        public Image card3Border;

        public Text card4Title;
        public Text card4Metrics;
        public Image card4Border;

        public Color bestGreenColor    = new Color(0.223f, 0.906f, 0.372f); // #39E75F
        public Color dangerRedColor    = new Color(0.85f, 0.25f, 0.18f);
        public Color warningAmberColor = new Color(0.95f, 0.72f, 0.15f);
        public Color defaultBorderColor = new Color(0.75f, 0.78f, 0.82f);
        public Color neutralGrey       = new Color(0.88f, 0.90f, 0.93f);

        // Card inner image references for glow pulse on best
        private Image[] _cardInnerBgs;
        private RectTransform[] _cardRects;
        private CanvasGroup _panelCg;

        private void Awake()
        {
            _panelCg = panelRoot != null ? panelRoot.GetComponent<CanvasGroup>() : null;
            if (panelRoot != null && _panelCg == null) _panelCg = panelRoot.AddComponent<CanvasGroup>();
        }

        private void Start()
        {
            EventBus.OnSimulationComplete += DisplayResults;
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnSimulationComplete -= DisplayResults;
        }

        public void DisplayResults(ScenarioResultData[] results)
        {
            if (panelRoot == null) return;
            panelRoot.SetActive(true);

            if (summaryHeader != null)
                summaryHeader.text = "DIGITAL TWIN — COUNTERFACTUAL FUTURES";

            if (results == null || results.Length == 0) return;

            var borders = new Image[] { card1Border, card2Border, card3Border, card4Border };
            var titles  = new Text[]  { card1Title,  card2Title,  card3Title,  card4Title  };
            var metrics = new Text[]  { card1Metrics, card2Metrics, card3Metrics, card4Metrics };

            // Collect card rects for staggered pop-in
            _cardRects = new RectTransform[4];
            _cardInnerBgs = new Image[4];
            for (int i = 0; i < 4; i++)
            {
                if (borders[i] != null) _cardRects[i] = borders[i].GetComponent<RectTransform>();
            }

            // Update card content
            for (int i = 0; i < 4 && i < results.Length; i++)
            {
                var r = results[i];
                if (titles[i] != null)
                {
                    titles[i].text = r.label;
                    titles[i].fontStyle = r.isBest ? FontStyle.Bold : FontStyle.Normal;
                }

                if (metrics[i] != null)
                    metrics[i].text = BuildMetricsText(r);

                if (borders[i] != null)
                    borders[i].color = r.isBest ? bestGreenColor : defaultBorderColor;
            }

            // Animate entrance
            StartCoroutine(StaggeredCardEntrance(results));
        }

        private string BuildMetricsText(ScenarioResultData r)
        {
            // Color-coded with rich prefix indicators
            string delayStr   = r.delayDeltaPct   <= 0f ? $"▼ {Mathf.Abs(r.delayDeltaPct):F1}% delay"   : $"▲ {r.delayDeltaPct:F1}% delay";
            string queueStr   = r.queueDeltaPct   <= 0f ? $"▼ {Mathf.Abs(r.queueDeltaPct):F1}% queue"   : $"▲ {r.queueDeltaPct:F1}% queue";
            string emergStr   = r.emergencyDelayS  <= 0f ? $"▼ {Mathf.Abs(r.emergencyDelayS):F0}s ETA"   : $"▲ {r.emergencyDelayS:F0}s ETA";
            string emissStr   = r.emissionsDeltaPct <= 0f ? $"▼ {Mathf.Abs(r.emissionsDeltaPct):F1}% CO₂" : $"▲ {r.emissionsDeltaPct:F1}% CO₂";

            return $"{delayStr}\n{queueStr}\n{emergStr}\n{emissStr}";
        }

        private IEnumerator StaggeredCardEntrance(ScenarioResultData[] results)
        {
            // Fade in panel header first
            if (_panelCg != null)
            {
                _panelCg.alpha = 0f;
                float t = 0f;
                while (t < 0.15f) { t += Time.deltaTime; _panelCg.alpha = t / 0.15f; yield return null; }
                _panelCg.alpha = 1f;
            }

            // Stagger each card pop-in
            var borders = new Image[] { card1Border, card2Border, card3Border, card4Border };
            for (int i = 0; i < 4 && i < results.Length; i++)
            {
                if (_cardRects[i] != null)
                {
                    CanvasGroup cardCg = borders[i]?.gameObject.GetComponent<CanvasGroup>();
                    if (cardCg == null && borders[i] != null) cardCg = borders[i].gameObject.AddComponent<CanvasGroup>();
                    StartCoroutine(UIAnimator.PopIn(_cardRects[i], cardCg, 0.20f));
                }
                yield return new WaitForSeconds(0.08f); // stagger delay
            }

            // After all cards are in, pulse the best card
            yield return new WaitForSeconds(0.3f);
            for (int i = 0; i < 4 && i < results.Length; i++)
            {
                if (results[i].isBest && borders[i] != null)
                {
                    StartCoroutine(UIAnimator.PulseHighlight(borders[i], Color.white, 0.35f, 3));
                    break;
                }
            }
        }

        public void Hide()
        {
            if (panelRoot == null) return;
            if (_panelCg != null)
                StartCoroutine(HideRoutine());
            else
                panelRoot.SetActive(false);
        }

        private IEnumerator HideRoutine()
        {
            yield return UIAnimator.FadeOut(_panelCg, 0.18f);
            panelRoot.SetActive(false);
        }
    }
}
