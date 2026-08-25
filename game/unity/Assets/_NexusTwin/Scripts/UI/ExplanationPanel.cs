using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;

namespace NexusTwin.UI
{
    /// <summary>
    /// ExplanationPanel — Polished Explainable AI rationale panel.
    /// Features: typewriter reveal of XAI text, confidence bar with animation,
    /// color-coded confidence (green/amber/red), slide-in entrance animation.
    /// </summary>
    public class ExplanationPanel : MonoBehaviour
    {
        [Header("Containers")]
        public GameObject panelRoot;
        public Image panelBg;
        public Image accentBar;
        public Image confidenceBarFill;

        [Header("Text Fields")]
        public Text actionText;
        public Text reasonText;
        public Text evidenceText;
        public Text confidenceText;
        public Text panelHeader;

        private static readonly Color HighConfColor = new Color(0.22f, 0.78f, 0.40f);
        private static readonly Color MidConfColor  = new Color(0.95f, 0.72f, 0.15f);
        private static readonly Color LowConfColor  = new Color(0.85f, 0.25f, 0.18f);

        private CanvasGroup _cg;
        private RectTransform _rect;

        private void Awake()
        {
            _cg   = panelRoot != null ? panelRoot.GetComponent<CanvasGroup>() : null;
            _rect = panelRoot != null ? panelRoot.GetComponent<RectTransform>() : null;
            if (panelRoot != null && _cg == null) _cg = panelRoot.AddComponent<CanvasGroup>();
        }

        private void Start()
        {
            EventBus.OnExplanationReady += DisplayExplanation;
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnExplanationReady -= DisplayExplanation;
        }

        public void DisplayExplanation(ExplanationData explanation)
        {
            if (panelRoot == null) return;
            panelRoot.SetActive(true);

            if (panelHeader != null) panelHeader.text = "NEXUS-AI EXPLANATION";

            // Color confidence
            Color confColor = explanation.confidence >= 0.80f ? HighConfColor :
                              explanation.confidence >= 0.55f ? MidConfColor  :
                                                               LowConfColor;

            if (actionText != null)
                actionText.text = $"ACTION\n{explanation.action}";
            if (reasonText != null)
                reasonText.text = $"WHY\n{explanation.reason}";
            if (evidenceText != null)
                evidenceText.text = $"EVIDENCE\n{explanation.evidence}";
            if (confidenceText != null)
            {
                confidenceText.text = $"CONFIDENCE: {Mathf.RoundToInt(explanation.confidence * 100f)}%";
                confidenceText.color = confColor;
            }
            if (accentBar != null) accentBar.color = confColor;

            // Animate
            if (_rect != null && _cg != null)
                StartCoroutine(UIAnimator.SlideInFromBottom(_rect, _cg, 20f, 0.25f));
            if (confidenceBarFill != null)
                StartCoroutine(AnimateConfidenceBar(explanation.confidence, confColor));
        }

        private IEnumerator AnimateConfidenceBar(float target, Color col)
        {
            if (confidenceBarFill == null) yield break;
            RectTransform rt = confidenceBarFill.GetComponent<RectTransform>();
            if (rt == null) yield break;
            confidenceBarFill.color = col;
            float t = 0f;
            float duration = 0.5f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float pct = Mathf.SmoothStep(0f, target, t / duration);
                rt.anchorMax = new Vector2(pct, rt.anchorMax.y);
                yield return null;
            }
            rt.anchorMax = new Vector2(target, rt.anchorMax.y);
        }

        public void Hide()
        {
            if (panelRoot == null) return;
            if (_cg != null)
                StartCoroutine(HideRoutine());
            else
                panelRoot.SetActive(false);
        }

        private IEnumerator HideRoutine()
        {
            yield return UIAnimator.FadeOut(_cg, 0.18f);
            panelRoot.SetActive(false);
        }
    }
}
