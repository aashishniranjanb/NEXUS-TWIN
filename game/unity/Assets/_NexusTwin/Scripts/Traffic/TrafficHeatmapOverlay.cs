using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Traffic;
using NexusTwin.Core;

namespace NexusTwin.Traffic
{
    /// <summary>
    /// TrafficHeatmapOverlay — Dynamically tints road segments and junction approaches
    /// based on live queue accumulation and congestion density.
    /// Provides immediate 3D situational awareness for the operator.
    /// </summary>
    public class TrafficHeatmapOverlay : MonoBehaviour
    {
        [Header("Heatmap Colors")]
        public Color flowGreen = new Color(0.223f, 0.906f, 0.372f, 0.35f);  // #39E75F
        public Color warnAmber = new Color(1.0f, 0.72f, 0.0f, 0.45f);        // #FFB800
        public Color alertRed = new Color(1.0f, 0.23f, 0.18f, 0.55f);        // #FF3B30

        [Header("Tuning Thresholds (meters)")]
        public float warnQueueThreshold = 15f;
        public float criticalQueueThreshold = 35f;

        private Renderer[] _roadRenderers;
        private Junction[] _junctions;

        private void Start()
        {
            _junctions = FindObjectsByType<Junction>(FindObjectsSortMode.None);
            FindRoadRenderers();
        }

        private void FindRoadRenderers()
        {
            WorldScaffold scaffold = FindFirstObjectByType<WorldScaffold>();
            if (scaffold != null)
            {
                _roadRenderers = scaffold.GetComponentsInChildren<Renderer>();
            }
        }

        private void Update()
        {
            UpdateHeatmapVisuals();
        }

        private void UpdateHeatmapVisuals()
        {
            if (_junctions == null || _junctions.Length == 0)
            {
                _junctions = FindObjectsByType<Junction>(FindObjectsSortMode.None);
                return;
            }

            foreach (var j in _junctions)
            {
                Color targetColor = flowGreen;

                if (j.hasActiveIncident)
                {
                    targetColor = alertRed;
                }
                else
                {
                    // Simulated queue density based on incident or vehicle counts near junction
                    int localVehCount = CountVehiclesNear(j.transform.position, 25f);
                    if (localVehCount > 10) targetColor = alertRed;
                    else if (localVehCount > 4) targetColor = warnAmber;
                    else targetColor = flowGreen;
                }

                // Apply color to junction center pad
                Renderer r = j.GetComponentInChildren<Renderer>();
                if (r != null)
                {
                    r.material.color = Color.Lerp(r.material.color, targetColor, Time.deltaTime * 3f);
                }
            }
        }

        private int CountVehiclesNear(Vector3 center, float radius)
        {
            Collider[] cols = Physics.OverlapSphere(center, radius);
            int count = 0;
            foreach (var c in cols)
            {
                if (c.CompareTag("Vehicle")) count++;
            }
            return count;
        }
    }
}
