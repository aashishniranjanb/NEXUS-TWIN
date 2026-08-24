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

        public void SetupBriefing(int missionIndex)
        {
            if (missionIndex == 2)
            {
                if (missionTitleText != null) missionTitleText.text = "MISSION 02: THE ESCAPE CORRIDOR";
                if (threatLevelText != null) threatLevelText.text = "THREAT LEVEL: <color=#F2B84B>ADVANCED (MULTIPLE CONGESTION EVENTS)</color>";
                if (situationText != null) situationText.text = "<b>SITUATION:</b>\nDownstream traffic density is increasing rapidly. A secondary bottleneck lane-disruption has occurred near J3. An emergency response vehicle must cross the network under conflicting constraints.";
                if (objectiveText != null) objectiveText.text = "<b>OBJECTIVE:</b>\nCompare Coordinated Corridor system optimizations versus direct Emergency Priority waves. Minimize total delay while keeping the ambulance transit below safety margins.";
            }
            else
            {
                if (missionTitleText != null) missionTitleText.text = "MISSION 01: CLEAR THE EMERGENCY CORRIDOR";
                if (threatLevelText != null) threatLevelText.text = "THREAT LEVEL: <color=#D94040>CRITICAL (BOTTLENECK DETECTED)</color>";
                if (situationText != null) situationText.text = "<b>SITUATION:</b>\nDeliberate traffic disruption and signal tampering identified at Junction J2. A critical trauma ambulance (AMBULANCE_01) is en route to the hospital through the main corridor.";
                if (objectiveText != null) objectiveText.text = "<b>OBJECTIVE:</b>\nUtilize the NEXUS AI and Counterfactual Digital Twin to deploy an adaptive traffic intervention. Prevent gridlock and secure zero-delay transit for the emergency ambulance.";
            }
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (state == GameState.Briefing)
            {
                SetupBriefing(GameManager.Instance != null ? GameManager.Instance.currentMission : 1);
            }
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
