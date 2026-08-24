using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    public class MainMenuPanel : MonoBehaviour
    {
        public GameObject panelRoot;
        public Button playButton;
        public Button missionsButton;
        public Button settingsButton;
        public Button exitButton;
        public Text playButtonText;

        private void Start()
        {
            if (playButton != null)
            {
                playButton.onClick.AddListener(OnPlayClicked);
                playButtonText = playButton.GetComponentInChildren<Text>();
            }
            if (missionsButton != null)
                missionsButton.onClick.AddListener(OnMissionsClicked);
            if (settingsButton != null)
                settingsButton.onClick.AddListener(OnSettingsClicked);
            if (exitButton != null)
                exitButton.onClick.AddListener(OnExitClicked);

            EventBus.OnGameStateChanged += HandleGameStateChanged;
            UpdatePlayButtonText();
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(state == GameState.MainMenu);
            }
            if (state == GameState.MainMenu)
            {
                UpdatePlayButtonText();
            }
        }

        private void OnPlayClicked()
        {
            SoundManager.Instance?.PlayClick();
            EventBus.RaisePlayClicked();
            GameManager.Instance?.SetState(GameState.Cinematic);
        }

        private void OnMissionsClicked()
        {
            SoundManager.Instance?.PlayClick();
            if (GameManager.Instance != null)
            {
                GameManager.Instance.currentMission = (GameManager.Instance.currentMission == 1) ? 2 : 1;
            }
            UpdatePlayButtonText();
            Debug.Log($"[MainMenu] Selected Mission: {GameManager.Instance?.currentMission}");
        }

        private void UpdatePlayButtonText()
        {
            if (playButtonText != null && GameManager.Instance != null)
            {
                playButtonText.text = $"PLAY: MISSION {GameManager.Instance.currentMission:00}";
            }
        }

        private void OnSettingsClicked()
        {
            SoundManager.Instance?.PlayClick();
            Debug.Log("[MainMenu] Settings opened");
        }

        private void OnExitClicked()
        {
            SoundManager.Instance?.PlayClick();
            Application.Quit();
            #if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
            #endif
        }
    }
}
