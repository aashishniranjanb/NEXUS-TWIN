using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;

namespace NexusTwin.UI
{
    /// <summary>
    /// ExplanationPanel — Displays Explainable AI (XAI) rationale:
    /// Action, Reason, Evidence, and Confidence Score.
    /// Implements Phase G specifications.
    /// </summary>
    public class ExplanationPanel : MonoBehaviour
    {
        [Header("Containers")]
        public GameObject panelRoot;

        [Header("Text Fields")]
        public Text actionText;
        public Text reasonText;
        public Text evidenceText;
        public Text confidenceText;

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
            if (panelRoot != null) panelRoot.SetActive(true);

            if (actionText != null) actionText.text = $"ACTION: {explanation.action}";
            if (reasonText != null) reasonText.text = $"WHY: {explanation.reason}";
            if (evidenceText != null) evidenceText.text = $"EVIDENCE: {explanation.evidence}";
            if (confidenceText != null) confidenceText.text = $"CONFIDENCE: {Mathf.RoundToInt(explanation.confidence * 100f)}%";
        }

        public void Hide()
        {
            if (panelRoot != null) panelRoot.SetActive(false);
        }
    }
}
