using UnityEngine;
using NexusTwin.Data;

namespace NexusTwin.Gameplay
{
    /// <summary>
    /// IncidentTrigger — Attached to locations or timers to trigger incidents during scenarios.
    /// Implements Phase F requirements.
    /// </summary>
    public class IncidentTrigger : MonoBehaviour
    {
        public string junctionId = NexusIds.Junctions.J2;
        public IncidentType incidentType = IncidentType.Accident;
        public float triggerTimeSeconds = 20.0f;
        public bool hasTriggered = false;

        private float _elapsed = 0f;

        private void Update()
        {
            if (hasTriggered) return;

            _elapsed += Time.deltaTime;
            if (_elapsed >= triggerTimeSeconds)
            {
                Trigger();
            }
        }

        public void Trigger()
        {
            if (hasTriggered) return;
            hasTriggered = true;

            IncidentManager.Instance?.TriggerIncident(junctionId, incidentType, transform.position);
            Debug.Log($"[IncidentTrigger] Fired {incidentType} at {junctionId} (T={_elapsed:F1}s)");
        }
    }
}
