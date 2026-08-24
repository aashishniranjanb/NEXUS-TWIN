using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;

namespace NexusTwin.UI
{
    /// <summary>
    /// CounterfactualCardPanel — Visualizes multiple parallel future scenarios.
    /// Highlights the optimal strategy with #39E75F and shows key deltas (delay, queue, emissions).
    /// Implements Phase H specifications.
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

        public Color bestGreenColor = new Color(0.223f, 0.906f, 0.372f); // #39E75F
        public Color defaultBorderColor = new Color(0.75f, 0.78f, 0.82f);

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
            if (panelRoot != null) panelRoot.SetActive(true);

            if (summaryHeader != null)
            {
                summaryHeader.text = "DIGITAL TWIN: COUNTERFACTUAL FUTURES EVALUATION";
            }

            if (results == null || results.Length == 0) return;

            // Bind Card 1
            if (results.Length > 0 && card1Title != null)
            {
                card1Title.text = results[0].label;
                card1Metrics.text = $"Delay: {results[0].delayDeltaPct:+0.0;-0.0}%\nQueue: {results[0].queueDeltaPct:+0.0;-0.0}%\nEmissions: {results[0].emissionsDeltaPct:+0.0;-0.0}%\nEmerg Delay: {results[0].emergencyDelayS:F1}s";
                if (card1Border != null) card1Border.color = results[0].isBest ? bestGreenColor : defaultBorderColor;
            }

            // Bind Card 2
            if (results.Length > 1 && card2Title != null)
            {
                card2Title.text = results[1].label;
                card2Metrics.text = $"Delay: {results[1].delayDeltaPct:+0.0;-0.0}%\nQueue: {results[1].queueDeltaPct:+0.0;-0.0}%\nEmissions: {results[1].emissionsDeltaPct:+0.0;-0.0}%\nEmerg Delay: {results[1].emergencyDelayS:F1}s";
                if (card2Border != null) card2Border.color = results[1].isBest ? bestGreenColor : defaultBorderColor;
            }

            // Bind Card 3
            if (results.Length > 2 && card3Title != null)
            {
                card3Title.text = results[2].label;
                card3Metrics.text = $"Delay: {results[2].delayDeltaPct:+0.0;-0.0}%\nQueue: {results[2].queueDeltaPct:+0.0;-0.0}%\nEmissions: {results[2].emissionsDeltaPct:+0.0;-0.0}%\nEmerg Delay: {results[2].emergencyDelayS:F1}s";
                if (card3Border != null) card3Border.color = results[2].isBest ? bestGreenColor : defaultBorderColor;
            }

            // Bind Card 4
            if (results.Length > 3 && card4Title != null)
            {
                card4Title.text = results[3].label;
                card4Metrics.text = $"Delay: {results[3].delayDeltaPct:+0.0;-0.0}%\nQueue: {results[3].queueDeltaPct:+0.0;-0.0}%\nEmissions: {results[3].emissionsDeltaPct:+0.0;-0.0}%\nEmerg Delay: {results[3].emergencyDelayS:F1}s";
                if (card4Border != null) card4Border.color = results[3].isBest ? bestGreenColor : defaultBorderColor;
            }
        }

        public void Hide()
        {
            if (panelRoot != null) panelRoot.SetActive(false);
        }
    }
}
