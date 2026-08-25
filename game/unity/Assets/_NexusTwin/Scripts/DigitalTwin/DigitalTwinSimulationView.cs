using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;
using NexusTwin.Vehicles;

namespace NexusTwin.DigitalTwin
{
    /// <summary>
    /// DigitalTwinSimulationView — Visually Undeniable Digital Twin Simulation.
    /// Phase C implementation:
    /// When "SIMULATE FUTURES" is triggered, splits/sweeps the city visually into 4 predicted counterfactual futures:
    /// - Future A (Divert Traffic): Translucent blue/green ghost vehicles along bypass routes.
    /// - Future B (Extend Green): Amber/green ghost stream through main corridor.
    /// - Future C (Emergency Priority): Red/white ambulance ghost with translucent green path line.
    /// - Future D (Do Nothing): Pulsing crimson queue density rings & gridlocked ghost vehicles.
    /// Includes translucent route projections, predicted queue markers, and holographic scan effects.
    /// </summary>
    public class DigitalTwinSimulationView : MonoBehaviour
    {
        public static DigitalTwinSimulationView Instance { get; private set; }

        [Header("Simulation State")]
        public bool isSimulationMode = false;
        public int activeFutureIndex = 0; // 0=A, 1=B, 2=C, 3=D

        [Header("Holographic Color Palette")]
        public Color ghostCyan     = new Color(0.10f, 0.70f, 0.95f, 0.55f); // Future A: Divert
        public Color ghostAmber    = new Color(0.95f, 0.72f, 0.15f, 0.55f); // Future B: Extend Green
        public Color ghostRed      = new Color(0.95f, 0.20f, 0.15f, 0.65f); // Future D: Do Nothing
        public Color ghostEmergency= new Color(0.20f, 0.95f, 0.40f, 0.65f); // Future C: Emergency Priority

        private List<GameObject> _ghostObjects = new List<GameObject>();
        private List<GameObject> _routeLineObjects = new List<GameObject>();
        private List<GameObject> _queueZoneObjects = new List<GameObject>();
        private Coroutine _sweepRoutine;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
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
            else if (state == GameState.Apply || state == GameState.Idle || state == GameState.Result || state == GameState.Score)
            {
                ExitSimulationMode();
            }
        }

        public void EnterSimulationMode()
        {
            if (isSimulationMode) return;
            isSimulationMode = true;
            Debug.Log("[DigitalTwinSimulationView] Entering Multi-Future Digital Twin Holographic Simulation");

            if (_sweepRoutine != null) StopCoroutine(_sweepRoutine);
            _sweepRoutine = StartCoroutine(RunMultiFutureSweepRoutine());
        }

        public void ExitSimulationMode()
        {
            if (!isSimulationMode) return;
            isSimulationMode = false;
            if (_sweepRoutine != null) StopCoroutine(_sweepRoutine);
            ClearAllSimulationVisuals();
            Debug.Log("[DigitalTwinSimulationView] Exiting Holographic Twin Simulation Mode -> Restoring Real World");
        }

        private void HandleSimulationComplete(ScenarioResultData[] results)
        {
            // Keep rendering active ghost state
            if (!isSimulationMode) EnterSimulationMode();
        }

        /// <summary>
        /// Sweeps sequentially through Future A, B, C, and D visual states to show
        /// the human operator all 4 counterfactual futures projected onto the physical city plane.
        /// </summary>
        private IEnumerator RunMultiFutureSweepRoutine()
        {
            // Sweep Future A -> B -> C -> D -> Show All Combined
            for (int future = 0; future < 4; future++)
            {
                activeFutureIndex = future;
                RenderFutureState(future);
                yield return new WaitForSeconds(0.75f);
            }

            // Finally, render composite state displaying all 4 futures side-by-side with translucent routes
            RenderAllFuturesComposite();
        }

        private void RenderFutureState(int futureIndex)
        {
            ClearAllSimulationVisuals();

            switch (futureIndex)
            {
                case 0: // Future A: Divert Traffic (Cyan/Green Bypass Stream)
                    SpawnGhostRouteLine(new Vector3(2.5f, 0.15f, 80f), new Vector3(2.5f, 0.15f, 60f), ghostCyan);
                    SpawnGhostRouteLine(new Vector3(2.5f, 0.15f, 60f), new Vector3(45f, 0.15f, 60f), ghostCyan);
                    SpawnGhostRouteLine(new Vector3(2.5f, 0.15f, 60f), new Vector3(-45f, 0.15f, 60f), ghostCyan);

                    for (int i = 0; i < 8; i++)
                    {
                        float x = (i % 2 == 0) ? (15f + i * 4f) : (-15f - i * 4f);
                        SpawnGhostVehicle(new Vector3(x, 0.6f, 60f), Quaternion.Euler(0f, 90f, 0f), ghostCyan, "Ghost_Divert_" + i);
                    }
                    SpawnQueueZone(new Vector3(0f, 0.05f, 0f), new Vector3(8f, 0.1f, 8f), new Color(0.2f, 0.8f, 0.3f, 0.25f));
                    break;

                case 1: // Future B: Extend Green (Amber Main Corridor Stream)
                    SpawnGhostRouteLine(new Vector3(2.5f, 0.15f, 80f), new Vector3(2.5f, 0.15f, -80f), ghostAmber);
                    for (int i = 0; i < 6; i++)
                    {
                        SpawnGhostVehicle(new Vector3(2.5f, 0.6f, 50f - i * 14f), Quaternion.Euler(0f, 180f, 0f), ghostAmber, "Ghost_GreenExtend_" + i);
                    }
                    // Side-street queue buildup
                    SpawnQueueZone(new Vector3(-25f, 0.05f, 0f), new Vector3(18f, 0.1f, 6f), new Color(0.95f, 0.70f, 0.10f, 0.35f));
                    break;

                case 2: // Future C: Emergency Priority (Bright Green EMS Wave + Red Clearance)
                    SpawnGhostRouteLine(new Vector3(2.5f, 0.20f, 85f), new Vector3(2.5f, 0.20f, -85f), ghostEmergency, width: 2.2f);
                    // Ambulance ghost
                    SpawnGhostVehicle(new Vector3(2.5f, 0.7f, 30f), Quaternion.Euler(0f, 180f, 0f), ghostEmergency, "Ghost_Ambulance_EMS", scale: new Vector3(2.1f, 2.1f, 5.2f));

                    // Stopped side traffic ghosts (Red)
                    SpawnGhostVehicle(new Vector3(-12f, 0.6f, 2.5f), Quaternion.Euler(0f, 90f, 0f), ghostRed, "Ghost_Stopped_W");
                    SpawnGhostVehicle(new Vector3(12f, 0.6f, -2.5f), Quaternion.Euler(0f, 270f, 0f), ghostRed, "Ghost_Stopped_E");
                    break;

                case 3: // Future D: Do Nothing (Pulsing Crimson Gridlock)
                    for (int i = 0; i < 12; i++)
                    {
                        float z = 20f - (i * 4f);
                        float x = (i % 2 == 0) ? 2.5f : 4.5f;
                        SpawnGhostVehicle(new Vector3(x, 0.6f, z), Quaternion.Euler(0f, 180f, 0f), ghostRed, "Ghost_Gridlock_" + i);
                    }
                    // Large crimson bottleneck queue zone at J2
                    SpawnQueueZone(new Vector3(0f, 0.05f, 0f), new Vector3(32f, 0.1f, 32f), new Color(0.85f, 0.10f, 0.10f, 0.45f));
                    break;
            }
        }

        private void RenderAllFuturesComposite()
        {
            ClearAllSimulationVisuals();

            // 1. Bypass diversion stream (Future A)
            SpawnGhostRouteLine(new Vector3(2.5f, 0.15f, 60f), new Vector3(45f, 0.15f, 60f), ghostCyan);
            for (int i = 0; i < 4; i++)
                SpawnGhostVehicle(new Vector3(18f + i * 6f, 0.6f, 60f), Quaternion.Euler(0f, 90f, 0f), ghostCyan, "Ghost_A_" + i);

            // 2. Emergency Priority route (Future C)
            SpawnGhostRouteLine(new Vector3(2.5f, 0.20f, 85f), new Vector3(2.5f, 0.20f, -85f), ghostEmergency, width: 2.4f);
            SpawnGhostVehicle(new Vector3(2.5f, 0.7f, 35f), Quaternion.Euler(0f, 180f, 0f), ghostEmergency, "Ghost_Ambulance", scale: new Vector3(2.1f, 2.1f, 5.2f));

            // 3. Gridlock Queue Zone at J2 (Future D baseline)
            SpawnQueueZone(new Vector3(0f, 0.05f, 0f), new Vector3(26f, 0.08f, 26f), new Color(0.85f, 0.15f, 0.15f, 0.30f));
        }

        // ──────── Visual Spawners ────────
        private GameObject SpawnGhostVehicle(Vector3 pos, Quaternion rot, Color col, string name, Vector3? scale = null)
        {
            GameObject ghost = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ghost.name = name;
            ghost.transform.SetParent(transform, false);
            ghost.transform.position = pos;
            ghost.transform.rotation = rot;
            ghost.transform.localScale = scale ?? new Vector3(1.8f, 1.2f, 3.8f);

            Renderer r = ghost.GetComponent<Renderer>();
            if (r != null)
            {
                Material mat = new Material(Shader.Find("Standard") ?? Shader.Find("Legacy Shaders/Diffuse"));
                mat.color = col;
                if (mat.HasProperty("_EmissionColor"))
                {
                    mat.EnableKeyword("_EMISSION");
                    mat.SetColor("_EmissionColor", col * 1.5f);
                }
                r.material = mat;
            }
            Destroy(ghost.GetComponent<Collider>());
            _ghostObjects.Add(ghost);
            return ghost;
        }

        private void SpawnGhostRouteLine(Vector3 start, Vector3 end, Color col, float width = 1.6f)
        {
            GameObject lineObj = new GameObject("GhostRouteLine");
            lineObj.transform.SetParent(transform, false);

            Vector3 mid = (start + end) * 0.5f;
            Vector3 diff = end - start;
            float len = diff.magnitude;

            lineObj.transform.position = mid;
            lineObj.transform.rotation = Quaternion.LookRotation(diff);
            lineObj.transform.localScale = new Vector3(width, 0.06f, len);

            GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cube.transform.SetParent(lineObj.transform, false);
            cube.transform.localPosition = Vector3.zero;
            cube.transform.localScale = Vector3.one;

            Renderer r = cube.GetComponent<Renderer>();
            if (r != null)
            {
                Material mat = new Material(Shader.Find("Standard") ?? Shader.Find("Legacy Shaders/Diffuse"));
                mat.color = col;
                if (mat.HasProperty("_EmissionColor"))
                {
                    mat.EnableKeyword("_EMISSION");
                    mat.SetColor("_EmissionColor", col * 2.0f);
                }
                r.material = mat;
            }
            Destroy(cube.GetComponent<Collider>());
            _routeLineObjects.Add(lineObj);
        }

        private void SpawnQueueZone(Vector3 pos, Vector3 size, Color col)
        {
            GameObject qObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            qObj.name = "PredictedQueueZone";
            qObj.transform.SetParent(transform, false);
            qObj.transform.position = pos;
            qObj.transform.localScale = size;

            Renderer r = qObj.GetComponent<Renderer>();
            if (r != null)
            {
                Material mat = new Material(Shader.Find("Standard") ?? Shader.Find("Legacy Shaders/Diffuse"));
                mat.color = col;
                if (mat.HasProperty("_EmissionColor"))
                {
                    mat.EnableKeyword("_EMISSION");
                    mat.SetColor("_EmissionColor", col * 1.8f);
                }
                r.material = mat;
            }
            Destroy(qObj.GetComponent<Collider>());
            _queueZoneObjects.Add(qObj);
        }

        private void ClearAllSimulationVisuals()
        {
            foreach (var g in _ghostObjects) if (g != null) Destroy(g);
            foreach (var r in _routeLineObjects) if (r != null) Destroy(r);
            foreach (var q in _queueZoneObjects) if (q != null) Destroy(q);
            _ghostObjects.Clear();
            _routeLineObjects.Clear();
            _queueZoneObjects.Clear();
        }
    }
}
