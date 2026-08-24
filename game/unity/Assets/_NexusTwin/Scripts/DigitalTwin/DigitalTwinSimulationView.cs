using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;
using NexusTwin.Vehicles;

namespace NexusTwin.DigitalTwin
{
    /// <summary>
    /// DigitalTwinSimulationView — Handles exploratory counterfactual visualization (Ghost Futures).
    /// Renders ghost vehicles to demonstrate simulated traffic outcomes before player approval.
    /// Implements Phase H specifications.
    /// </summary>
    public class DigitalTwinSimulationView : MonoBehaviour
    {
        public static DigitalTwinSimulationView Instance { get; private set; }

        [Header("Ghost Visualization Settings")]
        public bool isSimulationMode = false;
        public Color ghostFutureColor = new Color(0.2f, 0.8f, 1.0f, 0.45f); // Holographic Cyan Ghost
        public Color ghostBestColor = new Color(0.223f, 0.906f, 0.372f, 0.6f);  // #39E75F Best Green

        [Header("Ghost Vehicles")]
        private List<GameObject> _activeGhostObjects = new List<GameObject>();

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
            EventBus.OnGameStateChanged += HandleGameStateChanged;
            EventBus.OnSimulationComplete += HandleSimulationComplete;
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
            EventBus.OnSimulationComplete -= HandleSimulationComplete;
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (state == GameState.Simulation || state == GameState.Comparison)
            {
                EnterSimulationMode();
            }
            else if (state == GameState.Apply || state == GameState.Idle || state == GameState.Result)
            {
                ExitSimulationMode();
            }
        }

        public void EnterSimulationMode()
        {
            if (isSimulationMode) return;
            isSimulationMode = true;
            Debug.Log("[DigitalTwinSimulationView] Entering Holographic Twin Simulation Mode");
            RenderGhostFutures();
        }

        public void ExitSimulationMode()
        {
            if (!isSimulationMode) return;
            isSimulationMode = false;
            ClearGhosts();
            Debug.Log("[DigitalTwinSimulationView] Exiting Holographic Twin Simulation Mode -> Restoring Live View");
        }

        private void HandleSimulationComplete(ScenarioResultData[] results)
        {
            // Spawn ghost future paths based on results
            RenderGhostFutures();
        }

        private void RenderGhostFutures()
        {
            ClearGhosts();

            // Spawn 5-10 ghost vehicles along bypass diversion routes to visually illustrate Future A
            for (int i = 0; i < 6; i++)
            {
                GameObject ghost = GameObject.CreatePrimitive(PrimitiveType.Cube);
                ghost.name = $"Ghost_Veh_{i}";
                ghost.transform.localScale = new Vector3(1.8f, 1.2f, 3.8f);

                // Position along East/West bypass
                float x = -30f + i * 12f;
                float z = (i % 2 == 0) ? 15f : -15f;
                ghost.transform.position = new Vector3(x, 0.6f, z);
                ghost.transform.rotation = Quaternion.Euler(0f, 90f, 0f);

                Renderer r = ghost.GetComponent<Renderer>();
                if (r != null)
                {
                    r.material.color = ghostBestColor;
                }

                _activeGhostObjects.Add(ghost);
            }
        }

        private void ClearGhosts()
        {
            foreach (var g in _activeGhostObjects)
            {
                if (g != null) Destroy(g);
            }
            _activeGhostObjects.Clear();
        }
    }
}
