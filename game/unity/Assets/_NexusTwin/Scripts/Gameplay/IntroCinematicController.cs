using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Audio;
using NexusTwin.Data;
using NexusTwin.Camera;

namespace NexusTwin.Gameplay
{
    public class IntroCinematicController : MonoBehaviour
    {
        public static IntroCinematicController Instance { get; private set; }

        public GameObject cinematicUIRoot;
        public CanvasGroup fadeCanvasGroup;
        public Text subtitleText;
        public Text hackerTerminalText;
        public GameObject hackerTerminalBox;
        public Button skipButton;

        private Coroutine _cinematicRoutine;
        private bool _isSkipped = false;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Start()
        {
            if (skipButton != null)
                skipButton.onClick.AddListener(SkipCinematic);

            EventBus.OnGameStateChanged += HandleGameStateChanged;
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void Update()
        {
            if (GameManager.Instance != null && GameManager.Instance.currentState == GameState.Cinematic)
            {
                if (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Escape))
                {
                    SkipCinematic();
                }
            }
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (state == GameState.Cinematic)
            {
                StartCinematic();
            }
            else
            {
                if (cinematicUIRoot != null) cinematicUIRoot.SetActive(false);
            }
        }

        public void StartCinematic()
        {
            if (cinematicUIRoot != null) cinematicUIRoot.SetActive(true);
            _isSkipped = false;
            if (_cinematicRoutine != null) StopCoroutine(_cinematicRoutine);
            _cinematicRoutine = StartCoroutine(CinematicSequence());
        }

        public void SkipCinematic()
        {
            if (_isSkipped) return;
            _isSkipped = true;
            SoundManager.Instance?.PlayClick();
            if (_cinematicRoutine != null) StopCoroutine(_cinematicRoutine);
            if (cinematicUIRoot != null) cinematicUIRoot.SetActive(false);
            GameManager.Instance?.SetState(GameState.Briefing);
        }

        private IEnumerator CinematicSequence()
        {
            // 1. Initial Black Screen + Ambience
            if (fadeCanvasGroup != null) fadeCanvasGroup.alpha = 1f;
            if (hackerTerminalBox != null) hackerTerminalBox.SetActive(false);
            SetSubtitle("EXT. METROPOLITAN CORRIDOR — 02:41 AM\n[POLICE RADIO: 'All units, 10-33 disruption reported near Sector J2...']");
            yield return new WaitForSeconds(3.5f);
            if (_isSkipped) yield break;

            // 2. Fade into City View
            float fadeTime = 2f;
            for (float t = 0; t < fadeTime; t += Time.deltaTime)
            {
                if (fadeCanvasGroup != null) fadeCanvasGroup.alpha = Mathf.Lerp(1f, 0f, t / fadeTime);
                yield return null;
            }
            if (fadeCanvasGroup != null) fadeCanvasGroup.alpha = 0f;

            // 3. The Heist / Suspicious Convoy
            SetSubtitle("A high-value heist convoy maneuvers into the central corridor.");
            StrategicCameraController.Instance?.FocusJunction("J1");
            yield return new WaitForSeconds(4f);
            if (_isSkipped) yield break;

            // 4. Hacker Intrusion Terminal Opens
            if (hackerTerminalBox != null) hackerTerminalBox.SetActive(true);
            SoundManager.Instance?.PlayAlert();
            if (hackerTerminalText != null)
            {
                hackerTerminalText.text = "> INTRUSION DETECTED: UNKNOWN ACTOR\n> ACCESSING TRAFFIC CONTROLLER J2...\n> OVERRIDE SIGNAL: FORCE GREEN NORTHBOUND\n> TRAFFIC DENSITY SPIKING: CRITICAL";
            }
            SetSubtitle("THE AI HACKER: Traffic signals hijacked at J2. Deliberate bottleneck forming.");
            StrategicCameraController.Instance?.FocusJunction("J2");
            yield return new WaitForSeconds(5.5f);
            if (_isSkipped) yield break;

            // 5. Emergency Siren Sounds
            if (hackerTerminalBox != null) hackerTerminalBox.SetActive(false);
            SoundManager.Instance?.StartSiren();
            SetSubtitle("🚨 EMERGENCY RESPONSE: AMBULANCE_01 EN ROUTE TO TRAUMA CENTER.\nCorridor blockage imminent!");
            StrategicCameraController.Instance?.FocusJunction("J3");
            yield return new WaitForSeconds(4.5f);
            SoundManager.Instance?.StopSiren();
            if (_isSkipped) yield break;

            // 6. Transition to Player Control Room
            SetSubtitle("NEXUS-TWIN OPERATOR ONLINE.\nYou are in command of the city digital twin network.");
            yield return new WaitForSeconds(3f);
            if (_isSkipped) yield break;

            if (cinematicUIRoot != null) cinematicUIRoot.SetActive(false);
            GameManager.Instance?.SetState(GameState.Briefing);
        }

        private void SetSubtitle(string text)
        {
            if (subtitleText != null)
            {
                subtitleText.text = text;
            }
        }
    }
}
