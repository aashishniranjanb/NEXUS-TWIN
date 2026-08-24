using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// StrategyPanel — Displays available traffic strategies and triggers Digital Twin simulation.
    /// Implements Phase G specifications.
    /// </summary>
    public class StrategyPanel : MonoBehaviour
    {
        [Header("Containers")]
        public GameObject panelRoot;
        public Transform optionsContainer;
        public Button simulateButton;
        public Text selectedStrategyLabel;

        private List<StrategyOptionData> _currentOptions = new List<StrategyOptionData>();
        private StrategyOptionData _selectedOption;

        private void Start()
        {
            EventBus.OnStrategiesReady += HandleStrategiesReady;
            if (simulateButton != null)
            {
                simulateButton.onClick.AddListener(OnSimulateClicked);
            }

            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnStrategiesReady -= HandleStrategiesReady;
        }

        private List<Button> _spawnedButtons = new List<Button>();

        public void HandleStrategiesReady(StrategyOptionData[] options)
        {
            if (panelRoot != null) panelRoot.SetActive(true);

            // Clear previous buttons
            foreach (var btn in _spawnedButtons)
            {
                if (btn != null) Destroy(btn.gameObject);
            }
            _spawnedButtons.Clear();

            _currentOptions = new List<StrategyOptionData>(options);

            if (optionsContainer != null)
            {
                for (int i = 0; i < _currentOptions.Count; i++)
                {
                    int index = i; // local copy for closure
                    var opt = _currentOptions[i];
                    GameObject btnObj = new GameObject($"OptBtn_{index}");
                    btnObj.transform.SetParent(optionsContainer, false);
                    RectTransform rect = btnObj.AddComponent<RectTransform>();
                    rect.anchorMin = new Vector2(0.5f, 1);
                    rect.anchorMax = new Vector2(0.5f, 1);
                    rect.pivot = new Vector2(0.5f, 1);
                    rect.sizeDelta = new Vector2(310, 22);
                    rect.anchoredPosition = new Vector2(0, -index * 25);

                    Image img = btnObj.AddComponent<Image>();
                    img.color = new Color(0.88f, 0.9f, 0.93f, 1f); // default unselected light grey/blue

                    Button btn = btnObj.AddComponent<Button>();
                    _spawnedButtons.Add(btn);

                    // Label inside button
                    GameObject labelObj = new GameObject("Label");
                    labelObj.transform.SetParent(btnObj.transform, false);
                    RectTransform lblRect = labelObj.AddComponent<RectTransform>();
                    lblRect.anchorMin = Vector2.zero;
                    lblRect.anchorMax = Vector2.one;
                    lblRect.sizeDelta = Vector2.zero;

                    Text t = labelObj.AddComponent<Text>();
                    t.text = opt.label;
                    t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf") ?? Resources.GetBuiltinResource<Font>("Arial.ttf");
                    t.fontSize = 11;
                    t.color = new Color(0.06f, 0.08f, 0.12f, 1f);
                    t.alignment = TextAnchor.MiddleCenter;

                    // Wire click event
                    btn.onClick.AddListener(() => SelectOption(opt));
                }
            }

            if (_currentOptions.Count > 0)
            {
                SelectOption(_currentOptions[0]);
            }
        }

        public void SelectOption(StrategyOptionData option)
        {
            _selectedOption = option;
            if (selectedStrategyLabel != null)
            {
                selectedStrategyLabel.text = $"Selected: {option.label}";
            }

            // Update button visual states (highlight active one)
            for (int i = 0; i < _currentOptions.Count; i++)
            {
                if (i < _spawnedButtons.Count && _spawnedButtons[i] != null)
                {
                    Image img = _spawnedButtons[i].GetComponent<Image>();
                    Text txt = _spawnedButtons[i].GetComponentInChildren<Text>();
                    if (_currentOptions[i].type == option.type)
                    {
                        img.color = new Color(0.1f, 0.53f, 0.82f, 1f); // Active blue/cyan accent
                        if (txt != null) txt.color = Color.white;
                    }
                    else
                    {
                        img.color = new Color(0.88f, 0.9f, 0.93f, 1f); // Inactive light grey/blue
                        if (txt != null) txt.color = new Color(0.06f, 0.08f, 0.12f, 1f); // Navy text
                    }
                }
            }

            EventBus.RaiseStrategySelected(option);
        }

        private void OnSimulateClicked()
        {
            Debug.Log("[StrategyPanel] SIMULATE button clicked by player");
            EventBus.RaiseSimulateRequested();
        }

        public void Hide()
        {
            if (panelRoot != null) panelRoot.SetActive(false);
        }
    }
}
