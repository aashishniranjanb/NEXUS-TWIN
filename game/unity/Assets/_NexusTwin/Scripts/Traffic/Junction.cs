using UnityEngine;
using NexusTwin.Data;

namespace NexusTwin.Traffic
{
    /// <summary>
    /// Junction — Represents one intersection in the 3D world.
    /// junctionId MUST match the backend TrafficState junction_id (J1/J2/J3).
    /// Per PHASE_4 §4.2.
    /// </summary>
    public class Junction : MonoBehaviour
    {
        [Header("Identity — Must match backend exactly")]
        public string junctionId; // "J1", "J2", "J3" — from NexusIds.Junctions

        [Header("Traffic Light Controllers — one per approach")]
        public TrafficLightController[] lights;

        [Header("Queue Visualization Zones")]
        public Transform[] queueZones; // used for vehicle queue density visualization

        [Header("Incident State")]
        public bool hasActiveIncident = false;
        public IncidentType activeIncidentType;

        /// <summary>Update all lights at this junction to a given phase.</summary>
        public void SetPhase(int phaseIndex, string phaseState)
        {
            for (int i = 0; i < lights.Length; i++)
            {
                if (lights[i] != null)
                {
                    // phaseState is SUMO-style string like "GGrrrrGGrrrr"
                    // Each character maps to one signal head
                    char signalChar = (i < phaseState.Length) ? phaseState[i] : 'r';
                    lights[i].SetSignal(signalChar);
                }
            }
        }

        /// <summary>Trigger an incident at this junction.</summary>
        public void TriggerIncident(IncidentType type)
        {
            hasActiveIncident = true;
            activeIncidentType = type;
            Debug.Log($"[Junction {junctionId}] Incident triggered: {type}");
        }

        /// <summary>Clear active incident at this junction.</summary>
        public void ResolveIncident()
        {
            hasActiveIncident = false;
            Debug.Log($"[Junction {junctionId}] Incident resolved");
        }
    }
}
