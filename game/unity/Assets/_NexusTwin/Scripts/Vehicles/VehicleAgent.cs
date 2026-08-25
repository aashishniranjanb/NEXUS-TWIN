using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;

namespace NexusTwin.Vehicles
{
    /// <summary>
    /// VehicleAgent — Reusable vehicle agent supporting local pathfinding,
    /// traffic signal reaction, emergency priority, object pooling, and remote SUMO state sync.
    /// Implements Phase C requirements.
    /// </summary>
    public class VehicleAgent : MonoBehaviour
    {
        [Header("Identity & Specifications")]
        public string vehicleId;
        public VehicleType vehicleType = VehicleType.Car;
        public float maxSpeed = 14f; // ~50 km/h
        public float acceleration = 3.5f;
        public float braking = 6.0f;

        [Header("Telemetry State")]
        public float currentSpeed = 0f;
        public float waitingTime = 0f;
        public string currentLaneId = "";
        public bool isEmergency = false;
        public bool isStopped = false;
        public bool isGhost = false;

        [Header("Waypoint Path (Local Scripted Mode)")]
        public List<Vector3> waypoints = new List<Vector3>();
        public int currentWaypointIndex = 0;
        public float waypointRadius = 1.5f;

        [Header("Visuals")]
        public MeshRenderer vehicleRenderer;
        public GameObject emergencyFlashingLight;
        public Light headlightLeft;
        public Light headlightRight;
        public MeshRenderer taillightRenderer;
        public Material defaultMaterial;
        public Material ghostMaterial;

        [Header("Remote Sync (SUMO / WebSocket Mode)")]
        public bool isRemoteDriven = false;
        private Vector3 _targetRemotePos;
        private Quaternion _targetRemoteRot;
        private float _remoteSpeed = 0f;
        private float _lastRemoteUpdateTime = 0f;

        // Cached renderer refs for siren lights
        private MeshRenderer _sirenRedRend;
        private MeshRenderer _sirenBlueRend;
        private MeshRenderer _sirenWhiteRend;
        private bool _sirenCacheDone = false;

        private void Update()
        {
            if (isRemoteDriven)
            {
                transform.position = Vector3.Lerp(transform.position, _targetRemotePos, Time.deltaTime * 12f);
                transform.rotation = Quaternion.Slerp(transform.rotation, _targetRemoteRot, Time.deltaTime * 12f);
                currentSpeed = _remoteSpeed;
            }
            else
            {
                DriveAlongWaypoints();
            }

            // ── Ambulance alternating red/blue siren flash ───────────────────
            if (isEmergency && emergencyFlashingLight != null)
            {
                if (!_sirenCacheDone) CacheSirenRenderers();

                float t = Time.time * 5f;  // flash at 5 Hz
                int phase = Mathf.FloorToInt(t) % 4;

                // Phase 0,1 → RED on / BLUE off / WHITE off
                // Phase 2,3 → RED off / BLUE on / WHITE on (white strobe)
                bool redOn   = (phase == 0 || phase == 1);
                bool blueOn  = (phase == 2 || phase == 3);
                bool whiteOn = (phase == 1 || phase == 3);

                if (_sirenRedRend   != null) _sirenRedRend.enabled   = redOn;
                if (_sirenBlueRend  != null) _sirenBlueRend.enabled  = blueOn;
                if (_sirenWhiteRend != null) _sirenWhiteRend.enabled = whiteOn;

                // Also flash the overall light bar visibility
                emergencyFlashingLight.SetActive(true);
            }

            // ── Brake lights (emissive color shift) ─────────────────────────
            if (taillightRenderer != null)
            {
                bool braking = (currentSpeed < 1.0f || isStopped);
                Color tlColor = braking ? new Color(1f, 0.04f, 0.04f) : new Color(0.32f, 0.04f, 0.04f);
                taillightRenderer.material.color = tlColor;
                if (taillightRenderer.material.HasProperty("_EmissionColor"))
                {
                    if (braking)
                    {
                        taillightRenderer.material.EnableKeyword("_EMISSION");
                        taillightRenderer.material.SetColor("_EmissionColor", new Color(0.8f, 0f, 0f));
                    }
                    else
                    {
                        taillightRenderer.material.DisableKeyword("_EMISSION");
                    }
                }
            }

            waitingTime = (currentSpeed < 0.1f) ? waitingTime + Time.deltaTime : 0f;
        }

        private void CacheSirenRenderers()
        {
            if (emergencyFlashingLight == null) return;
            foreach (var mr in emergencyFlashingLight.GetComponentsInChildren<MeshRenderer>())
            {
                if (mr.name == "LB_Red")   _sirenRedRend   = mr;
                if (mr.name == "LB_Blue")  _sirenBlueRend  = mr;
                if (mr.name == "LB_White") _sirenWhiteRend = mr;
            }
            _sirenCacheDone = true;
        }

        private void DriveAlongWaypoints()
        {
            if (waypoints == null || waypoints.Count == 0 || currentWaypointIndex >= waypoints.Count)
            {
                // Reached end of path -> return to pool
                VehicleManager.Instance?.Despawn(this);
                return;
            }

            Vector3 target = waypoints[currentWaypointIndex];
            Vector3 diff = target - transform.position;
            diff.y = 0f; // Stay on road plane
            float dist = diff.magnitude;

            if (dist < waypointRadius)
            {
                currentWaypointIndex++;
                return;
            }

            // Obstacle & Signal check ahead (Raycast)
            bool shouldStop = CheckObstaclesAndSignals();
            if (shouldStop)
            {
                currentSpeed = Mathf.MoveTowards(currentSpeed, 0f, braking * Time.deltaTime);
                isStopped = true;
            }
            else
            {
                currentSpeed = Mathf.MoveTowards(currentSpeed, maxSpeed, acceleration * Time.deltaTime);
                isStopped = false;
            }

            // Rotate towards next waypoint
            if (diff != Vector3.zero)
            {
                Quaternion desiredRot = Quaternion.LookRotation(diff);
                transform.rotation = Quaternion.RotateTowards(transform.rotation, desiredRot, 180f * Time.deltaTime);
            }

            transform.position += transform.forward * currentSpeed * Time.deltaTime;
        }

        private bool CheckObstaclesAndSignals()
        {
            // Emergency vehicles ignore normal stops unless directly blocked
            if (isEmergency) return false;

            RaycastHit hit;
            Vector3 origin = transform.position + Vector3.up * 0.5f;
            if (Physics.Raycast(origin, transform.forward, out hit, 6.0f))
            {
                // Check if vehicle ahead or red light stop zone
                if (hit.collider.CompareTag("Vehicle") || hit.collider.CompareTag("TrafficStop"))
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Called when spawned from object pool.
        /// </summary>
        public void OnSpawn(string id, VehicleType type, List<Vector3> pathWaypoints, bool emergency = false)
        {
            vehicleId = id;
            vehicleType = type;
            waypoints = (pathWaypoints != null) ? new List<Vector3>(pathWaypoints) : new List<Vector3>();
            currentWaypointIndex = 0;
            currentSpeed = 0f;
            waitingTime = 0f;
            isEmergency = emergency || (type == VehicleType.Ambulance || type == VehicleType.Police || type == VehicleType.Fire);
            isRemoteDriven = false;
            isGhost = false;

            if (waypoints.Count > 0)
            {
                transform.position = waypoints[0];
                if (waypoints.Count > 1)
                {
                    Vector3 look = waypoints[1] - waypoints[0];
                    if (look != Vector3.zero) transform.rotation = Quaternion.LookRotation(look);
                }
            }

            SetVisualAppearance();
            gameObject.SetActive(true);
        }

        /// <summary>
        /// Called when returned to pool.
        /// </summary>
        public void OnDespawn()
        {
            gameObject.SetActive(false);
            waypoints.Clear();
            currentWaypointIndex = 0;
            currentSpeed = 0f;
            waitingTime = 0f;
            isRemoteDriven = false;
            if (emergencyFlashingLight != null) emergencyFlashingLight.SetActive(false);
        }

        /// <summary>
        /// Updates vehicle state received from SUMO / WebSocket.
        /// </summary>
        public void SetRemoteState(Vector3 pos, float angleDeg, float speedMps, string laneId)
        {
            isRemoteDriven = true;
            _targetRemotePos = pos;
            _targetRemoteRot = Quaternion.Euler(0f, angleDeg, 0f);
            _remoteSpeed = speedMps;
            currentLaneId = laneId;
            _lastRemoteUpdateTime = Time.time;
        }

        /// <summary>
        /// Configures ghost material for Digital Twin counterfactual visualization.
        /// </summary>
        public void SetGhostMode(bool ghost, Color ghostColor)
        {
            isGhost = ghost;
            if (vehicleRenderer != null)
            {
                if (ghost)
                {
                    vehicleRenderer.material.color = new Color(ghostColor.r, ghostColor.g, ghostColor.b, 0.45f);
                }
                else
                {
                    SetVisualAppearance();
                }
            }
        }

        private void SetVisualAppearance()
        {
            if (vehicleRenderer == null)
            {
                vehicleRenderer = GetComponentInChildren<MeshRenderer>();
            }

            if (vehicleRenderer != null)
            {
                Color c = Color.white;
                switch (vehicleType)
                {
                    case VehicleType.Car:
                        c = new Color(0.2f, 0.55f, 0.9f); // Blue
                        break;
                    case VehicleType.Bus:
                        c = new Color(0.95f, 0.75f, 0.1f); // Yellow/Orange
                        break;
                    case VehicleType.Truck:
                        c = new Color(0.35f, 0.7f, 0.35f); // Green
                        break;
                    case VehicleType.Motorcycle:
                        c = new Color(0.8f, 0.3f, 0.8f); // Purple
                        break;
                    case VehicleType.Ambulance:
                        c = new Color(1f, 1f, 1f); // Crisp White with Red Cross
                        break;
                    case VehicleType.Police:
                        c = new Color(0.1f, 0.1f, 0.2f); // Navy Dark
                        break;
                    case VehicleType.Fire:
                        c = new Color(0.95f, 0.15f, 0.1f); // Red
                        break;
                }
                vehicleRenderer.material.color = c;
            }

            if (emergencyFlashingLight != null)
            {
                emergencyFlashingLight.SetActive(isEmergency);
            }
        }
    }
}
