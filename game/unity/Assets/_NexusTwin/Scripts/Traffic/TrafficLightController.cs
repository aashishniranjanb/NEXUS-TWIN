using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;

namespace NexusTwin.Traffic
{
    /// <summary>
    /// TrafficLightController — Manages traffic signal states and visual transitions.
    /// Controls Green/Yellow/Red lights with safe clearance intervals and player overrides.
    /// Implements Phase D requirements.
    /// </summary>
    public class TrafficLightController : MonoBehaviour
    {
        public enum SignalColor { Red, Yellow, Green }

        [Header("Identity")]
        public string junctionId = NexusIds.Junctions.J2;
        public int approachIndex = 0; // 0 = North, 1 = East, 2 = South, 3 = West

        [Header("Visual Elements")]
        public MeshRenderer redLightRenderer;
        public MeshRenderer yellowLightRenderer;
        public MeshRenderer greenLightRenderer;
        public Light spotLight;

        [Header("Current State")]
        public SignalColor currentSignal = SignalColor.Red;
        public float currentPhaseTimer = 0f;
        public float currentPhaseDuration = 25f;

        [Header("Materials / Colors")]
        public Color redOnColor = new Color(1f, 0.1f, 0.1f);
        public Color yellowOnColor = new Color(1f, 0.85f, 0.1f);
        public Color greenOnColor = new Color(0.2f, 0.95f, 0.35f);
        public Color offColor = new Color(0.15f, 0.15f, 0.15f);

        [Header("Override Settings")]
        public bool isOverridden = false;
        public string activeOverrideType = NexusIds.Strategies.DoNothing;
        public float overrideRemainingTime = 0f;

        private void Start()
        {
            UpdateVisuals();
        }

        private void Update()
        {
            if (isOverridden)
            {
                overrideRemainingTime -= Time.deltaTime;
                if (overrideRemainingTime <= 0f)
                {
                    ClearOverride();
                }
            }
            else
            {
                currentPhaseTimer += Time.deltaTime;
            }
        }

        /// <summary>
        /// Sets the signal from standard character code ('r', 'y', 'g', 'G').
        /// </summary>
        public void SetSignal(char signalChar)
        {
            switch (char.ToLower(signalChar))
            {
                case 'g':
                    SetSignalColor(SignalColor.Green);
                    break;
                case 'y':
                    SetSignalColor(SignalColor.Yellow);
                    break;
                case 'r':
                default:
                    SetSignalColor(SignalColor.Red);
                    break;
            }
        }

        /// <summary>
        /// Direct setter for signal color.
        /// </summary>
        public void SetSignalColor(SignalColor newColor)
        {
            currentSignal = newColor;
            UpdateVisuals();
        }

        /// <summary>
        /// Applies player strategy override (e.g. Green Extend, Emergency Green Wave).
        /// </summary>
        public void ApplyStrategyOverride(string strategyType, float durationSeconds)
        {
            isOverridden = true;
            activeOverrideType = strategyType;
            overrideRemainingTime = durationSeconds;

            if (strategyType == NexusIds.Strategies.GreenExtend || strategyType == NexusIds.Strategies.EmergencyPriority)
            {
                SetSignalColor(SignalColor.Green);
                Debug.Log($"[TrafficLightController] {junctionId} Approach {approachIndex} -> Override {strategyType} ({durationSeconds}s)");
            }
        }

        public void ClearOverride()
        {
            isOverridden = false;
            activeOverrideType = NexusIds.Strategies.DoNothing;
            overrideRemainingTime = 0f;
            Debug.Log($"[TrafficLightController] {junctionId} Approach {approachIndex} -> Override cleared");
        }

        /// <summary>
        /// Updates the emission and light colors on signal models.
        /// </summary>
        public void UpdateVisuals()
        {
            if (redLightRenderer != null && redLightRenderer.material != null)
            {
                redLightRenderer.material.color = (currentSignal == SignalColor.Red) ? redOnColor : offColor;
                if (redLightRenderer.material.HasProperty("_EmissionColor"))
                {
                    redLightRenderer.material.SetColor("_EmissionColor", (currentSignal == SignalColor.Red) ? redOnColor * 2f : Color.black);
                }
            }

            if (yellowLightRenderer != null && yellowLightRenderer.material != null)
            {
                yellowLightRenderer.material.color = (currentSignal == SignalColor.Yellow) ? yellowOnColor : offColor;
                if (yellowLightRenderer.material.HasProperty("_EmissionColor"))
                {
                    yellowLightRenderer.material.SetColor("_EmissionColor", (currentSignal == SignalColor.Yellow) ? yellowOnColor * 2f : Color.black);
                }
            }

            if (greenLightRenderer != null && greenLightRenderer.material != null)
            {
                greenLightRenderer.material.color = (currentSignal == SignalColor.Green) ? greenOnColor : offColor;
                if (greenLightRenderer.material.HasProperty("_EmissionColor"))
                {
                    greenLightRenderer.material.SetColor("_EmissionColor", (currentSignal == SignalColor.Green) ? greenOnColor * 2f : Color.black);
                }
            }

            if (spotLight != null)
            {
                switch (currentSignal)
                {
                    case SignalColor.Red:
                        spotLight.color = redOnColor;
                        spotLight.enabled = true;
                        break;
                    case SignalColor.Yellow:
                        spotLight.color = yellowOnColor;
                        spotLight.enabled = true;
                        break;
                    case SignalColor.Green:
                        spotLight.color = greenOnColor;
                        spotLight.enabled = true;
                        break;
                }
            }
        }
    }
}
