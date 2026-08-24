using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    public class MissionBriefingPanel : MonoBehaviour
    {
        public GameObject panelRoot;
        public Text missionTitleText;
        public Text situationText;
        public Text objectiveText;
        public Text threatLevelText;
        public Button startMissionButton;

        private void Start()
        {
            if (startMissionButton != null)
                startMissionButton.onClick.AddListener(OnStartMissionClicked);

            EventBus.OnGameStateChanged += HandleGameStateChanged;
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void Update()
        {
            if (GameManager.Instance != null && GameManager.Instance.currentState == GameState.Briefing)
            {
                if (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return))
                {
                    OnStartMissionClicked();
                }
            }
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(state == GameState.Briefing);
            }
        }

        private void OnStartMissionClicked()
        {
            SoundManager.Instance?.PlayClick();
            if (panelRoot != null) panelRoot.SetActive(false);
            GameManager.Instance?.SetState(GameState.Idle);
        }
    }
}
