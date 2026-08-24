using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Traffic;
using NexusTwin.Vehicles;
using NexusTwin.Core;
using NexusTwin.Audio;

namespace NexusTwin.Gameplay
{
    /// <summary>
    /// SandboxModeController — Free Play / Interactive Sandbox mode controller.
    /// Allows the human operator to manually click traffic lights to toggle phases,
    /// trigger custom incidents with right-click, dispatch emergency vehicles, and test AI.
    /// </summary>
    public class SandboxModeController : MonoBehaviour
    {
        public static SandboxModeController Instance { get; private set; }

        [Header("Mode Configuration")]
        public bool isSandboxActive = true;
        public LayerMask clickableLayer;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Update()
        {
            if (!isSandboxActive) return;

            HandleMouseInteraction();
            HandleHotkeyTriggers();
        }

        private void HandleMouseInteraction()
        {
            // Left click to toggle traffic signal phase
            if (Input.GetMouseButtonDown(0))
            {
                Ray ray = UnityEngine.Camera.main.ScreenPointToRay(Input.mousePosition);
                if (Physics.Raycast(ray, out RaycastHit hit, 200f))
                {
                    TrafficLightController tlc = hit.collider.GetComponentInParent<TrafficLightController>();
                    if (tlc != null)
                    {
                        ToggleSignal(tlc);
                        SoundManager.Instance?.PlayClick();
                    }
                }
            }

            // Right click to spawn incident at click location
            if (Input.GetMouseButtonDown(1) && Input.GetKey(KeyCode.LeftShift))
            {
                Ray ray = UnityEngine.Camera.main.ScreenPointToRay(Input.mousePosition);
                if (Physics.Raycast(ray, out RaycastHit hit, 200f))
                {
                    SpawnCustomIncident(hit.point);
                }
            }
        }

        private void HandleHotkeyTriggers()
        {
            // Hotkey 'E': Dispatch Emergency Ambulance
            if (Input.GetKeyDown(KeyCode.E))
            {
                VehicleManager.Instance?.SpawnEmergencyAmbulance();
                SoundManager.Instance?.StartSiren();
                Debug.Log("[SandboxMode] Dispatched Emergency Ambulance via Hotkey [E]");
            }

            // Hotkey 'I': Spawn Accident at J2
            if (Input.GetKeyDown(KeyCode.I))
            {
                SpawnCustomIncident(new Vector3(2.5f, 0f, 0f));
            }

            // Hotkey 'C': Force AI Predictor analysis
            if (Input.GetKeyDown(KeyCode.C))
            {
                CongestionAlertData alert = new CongestionAlertData
                {
                    junctionId = NexusIds.Junctions.J2,
                    probability = 0.91f,
                    forecastMinutes = 5
                };
                EventBus.RaiseAIPrediction(alert);
                SoundManager.Instance?.PlayAlert();
                Debug.Log("[SandboxMode] Triggered AI Congestion Forecast via Hotkey [C]");
            }
        }

        private void ToggleSignal(TrafficLightController tlc)
        {
            if (tlc.currentSignal == TrafficLightController.SignalColor.Green)
            {
                tlc.SetSignalColor(TrafficLightController.SignalColor.Red);
            }
            else
            {
                tlc.SetSignalColor(TrafficLightController.SignalColor.Green);
            }
            Debug.Log($"[SandboxMode] Manually toggled signal {tlc.junctionId} Approach {tlc.approachIndex} -> {tlc.currentSignal}");
        }

        private void SpawnCustomIncident(Vector3 location)
        {
            IncidentManager.Instance?.TriggerIncident(NexusIds.Junctions.J2, IncidentType.Accident, location);
            SoundManager.Instance?.PlayAlert();
            Debug.Log($"[SandboxMode] Custom Incident spawned at {location}");
        }
    }
}
