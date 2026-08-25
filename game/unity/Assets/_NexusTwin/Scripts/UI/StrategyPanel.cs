using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// StrategyPanel — Polished strategy selection panel with animated entrance,
    /// hover-glow button states, selection confirmation animation, and
    /// AI recommendation badge highlighting.
    /// </summary>
    public class StrategyPanel : MonoBehaviour
    {
        [Header("Containers")]
        public GameObject panelRoot;
        public Transform optionsContainer;
        public Button simulateButton;
        public Text selectedStrategyLabel;
        public Text panelTitleText;

        // Color palette
        private static readonly Color ActiveBlueDark = new Color(0.08f, 0.46f, 0.78f);
        private static readonly Color AIRecommendGreen = new Color(0.223f, 0.906f, 0.372f);
        private static readonly Color DefaultBtn  = new Color(0.88f, 0.90f, 0.93f);
        private static readonly Color NavyText    = new Color(0.06f, 0.08f, 0.12f);
        private static readonly Color InactiveBtn = new Color(0.22f, 0.26f, 0.34f);

        private List<StrategyOptionData> _currentOptions = new List<StrategyOptionData>();
        private StrategyOptionData _selectedOption;
        private List<Button> _spawnedButtons = new List<Button>();
        private CanvasGroup _panelCg;
        private RectTransform _panelRect;

        private void Awake()
        {
            _panelCg = panelRoot != null ? panelRoot.GetComponent<CanvasGroup>() : null;
            if (panelRoot != null && _panelCg == null) _panelCg = panelRoot.AddComponent<CanvasGroup>();
            _panelRect = panelRoot != null ? panelRoot.GetComponent<RectTransform>() : null;
        }

        private void Start()
        {
            EventBus.OnStrategiesReady += HandleStrategiesReady;
            if (simulateButton != null) simulateButton.onClick.AddListener(OnSimulateClicked);
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnStrategiesReady -= HandleStrategiesReady;
        }

        public void HandleStrategiesReady(StrategyOptionData[] options)
        {
            if (panelRoot == null) return;
            panelRoot.SetActive(true);

            // Clear previous
            foreach (var btn in _spawnedButtons)
                if (btn != null) Destroy(btn.gameObject);
            _spawnedButtons.Clear();

            _currentOptions = new List<StrategyOptionData>(options);

            if (panelTitleText != null)
                panelTitleText.text = "SELECT INTERVENTION STRATEGY";

            if (optionsContainer != null)
            {
                for (int i = 0; i < _currentOptions.Count; i++)
                {
                    int index = i;
                    var opt = _currentOptions[i];
                    bool isAIRecommended = (opt.type == StrategyType.Diversion);

                    // Outer button container
                    GameObject btnObj = new GameObject($"StratBtn_{index}");
                    btnObj.transform.SetParent(optionsContainer, false);
                    RectTransform rect = btnObj.AddComponent<RectTransform>();
                    rect.anchorMin = new Vector2(0.5f, 1);
                    rect.anchorMax = new Vector2(0.5f, 1);
                    rect.pivot = new Vector2(0.5f, 1);
                    rect.sizeDelta = new Vector2(340, 36);
                    rect.anchoredPosition = new Vector2(0, -index * 42);

                    // Background image
                    Image img = btnObj.AddComponent<Image>();
                    img.color = InactiveBtn;

                    // Left accent strip
                    GameObject strip = new GameObject("AccentStrip");
                    strip.transform.SetParent(btnObj.transform, false);
                    RectTransform stripRect = strip.AddComponent<RectTransform>();
                    stripRect.anchorMin = new Vector2(0, 0);
                    stripRect.anchorMax = new Vector2(0, 1);
                    stripRect.sizeDelta = new Vector2(4, 0);
                    stripRect.anchoredPosition = Vector2.zero;
                    Image stripImg = strip.AddComponent<Image>();
                    stripImg.color = isAIRecommended ? AIRecommendGreen : new Color(0.35f, 0.40f, 0.50f);

                    Button btn = btnObj.AddComponent<Button>();
                    _spawnedButtons.Add(btn);

                    // Main label
                    GameObject labelObj = new GameObject("Label");
                    labelObj.transform.SetParent(btnObj.transform, false);
                    RectTransform lblRect = labelObj.AddComponent<RectTransform>();
                    lblRect.anchorMin = new Vector2(0.02f, 0);
                    lblRect.anchorMax = new Vector2(0.78f, 1);
                    lblRect.sizeDelta = Vector2.zero;
                    Text t = labelObj.AddComponent<Text>();
                    t.text = opt.label;
                    t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf") ?? Resources.GetBuiltinResource<Font>("Arial.ttf");
                    t.fontSize = 12;
                    t.fontStyle = FontStyle.Normal;
                    t.color = Color.white;
                    t.alignment = TextAnchor.MiddleLeft;

                    // AI badge for recommended strategy
                    if (isAIRecommended)
                    {
                        GameObject badge = new GameObject("AIBadge");
                        badge.transform.SetParent(btnObj.transform, false);
                        RectTransform badgeRect = badge.AddComponent<RectTransform>();
                        badgeRect.anchorMin = new Vector2(0.80f, 0.15f);
                        badgeRect.anchorMax = new Vector2(0.99f, 0.85f);
                        badgeRect.sizeDelta = Vector2.zero;
                        Image badgeBg = badge.AddComponent<Image>();
                        badgeBg.color = AIRecommendGreen;
                        Text badgeText = badge.AddComponent<Text>();
                        badgeText.text = "AI ★";
                        badgeText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                        badgeText.fontSize = 10;
                        badgeText.fontStyle = FontStyle.Bold;
                        badgeText.color = new Color(0.04f, 0.08f, 0.04f);
                        badgeText.alignment = TextAnchor.MiddleCenter;
                    }

                    btn.onClick.AddListener(() => SelectOption(opt));
                }
            }

            if (_currentOptions.Count > 0) SelectOption(_currentOptions[0]);

            // Animate entrance
            if (_panelRect != null && _panelCg != null)
                StartCoroutine(UIAnimator.SlideInFromRight(_panelRect, _panelCg, 30f, 0.25f));
        }

        public void SelectOption(StrategyOptionData option)
        {
            _selectedOption = option;
            if (selectedStrategyLabel != null)
                selectedStrategyLabel.text = $"▶  {option.label}";

            for (int i = 0; i < _currentOptions.Count; i++)
            {
                if (i >= _spawnedButtons.Count || _spawnedButtons[i] == null) continue;
                Image img = _spawnedButtons[i].GetComponent<Image>();
                Text txt = _spawnedButtons[i].GetComponentInChildren<Text>();
                bool isSelected = (_currentOptions[i].type == option.type);

                if (isSelected)
                {
                    img.color = ActiveBlueDark;
                    if (txt != null) txt.color = Color.white;
                    if (txt != null) txt.fontStyle = FontStyle.Bold;
                    StartCoroutine(SelectionFlash(img));
                }
                else
                {
                    img.color = InactiveBtn;
                    if (txt != null) txt.color = new Color(0.80f, 0.82f, 0.85f);
                    if (txt != null) txt.fontStyle = FontStyle.Normal;
                }
            }

            EventBus.RaiseStrategySelected(option);
        }

        private IEnumerator SelectionFlash(Image img)
        {
            Color flash = Color.white;
            Color target = ActiveBlueDark;
            float t = 0f;
            while (t < 0.12f)
            {
                t += Time.deltaTime;
                img.color = Color.Lerp(flash, target, t / 0.12f);
                yield return null;
            }
            img.color = target;
        }

        private void OnSimulateClicked()
        {
            if (simulateButton != null)
                StartCoroutine(ButtonClickFeedback(simulateButton.GetComponent<Image>()));
            Debug.Log("[StrategyPanel] SIMULATE triggered by player");
            EventBus.RaiseSimulateRequested();
        }

        private IEnumerator ButtonClickFeedback(Image img)
        {
            if (img == null) yield break;
            Color orig = img.color;
            img.color = Color.white;
            yield return new WaitForSeconds(0.08f);
            img.color = orig;
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
