using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;
using NexusTwin.Traffic;

namespace NexusTwin.Gameplay
{
    /// <summary>
    /// IncidentManager — Tracks and visualizes active traffic incidents across the network.
    /// Spawns physical accident scenes with disabled vehicles, flashing hazard lights,
    /// and reflective safety cones to force realistic queue propagation.
    /// </summary>
    public class IncidentManager : MonoBehaviour
    {
        public static IncidentManager Instance { get; private set; }

        private Dictionary<string, GameObject> _activeHazardMarkers = new Dictionary<string, GameObject>();

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
            EventBus.OnIncidentTriggered += HandleIncidentTriggered;
            EventBus.OnIncidentResolved += HandleIncidentResolved;
        }

        private void OnDestroy()
        {
            EventBus.OnIncidentTriggered -= HandleIncidentTriggered;
            EventBus.OnIncidentResolved -= HandleIncidentResolved;
        }

        public void TriggerIncident(string junctionId, IncidentType type, Vector3 location)
        {
            Debug.Log($"[IncidentManager] Triggered {type} at {junctionId} (pos: {location})");

            if (!_activeHazardMarkers.ContainsKey(junctionId))
            {
                GameObject marker = CreateAccidentScene(location, type);
                _activeHazardMarkers[junctionId] = marker;
            }

            Junction j = FindJunction(junctionId);
            if (j != null)
            {
                j.TriggerIncident(type);
            }

            EventBus.RaiseIncidentTriggered(junctionId, type.ToString().ToLower());
        }

        public void ResolveIncident(string junctionId)
        {
            Debug.Log($"[IncidentManager] Resolved incident at {junctionId}");

            if (_activeHazardMarkers.TryGetValue(junctionId, out GameObject marker))
            {
                Destroy(marker);
                _activeHazardMarkers.Remove(junctionId);
            }

            Junction j = FindJunction(junctionId);
            if (j != null)
            {
                j.ResolveIncident();
            }

            EventBus.RaiseIncidentResolved(junctionId);
        }

        private GameObject CreateAccidentScene(Vector3 pos, IncidentType type)
        {
            GameObject sceneRoot = new GameObject($"AccidentScene_{type}");
            sceneRoot.transform.position = pos;

            // 1. Damaged Vehicle (Tilted dark sedan)
            GameObject car = GameObject.CreatePrimitive(PrimitiveType.Cube);
            car.name = "DamagedVehicle";
            car.tag = "Vehicle"; // Raycast obstacle for active vehicles
            car.transform.SetParent(sceneRoot.transform, false);
            car.transform.localPosition = new Vector3(0f, 0.6f, 0f);
            car.transform.localRotation = Quaternion.Euler(0f, 35f, 8f);
            car.transform.localScale = new Vector3(1.8f, 1.2f, 3.8f);
            car.GetComponent<Renderer>().material.color = new Color(0.2f, 0.22f, 0.28f);

            // Car roof / cabin
            GameObject cabin = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cabin.name = "Cabin";
            cabin.transform.SetParent(car.transform, false);
            cabin.transform.localPosition = new Vector3(0f, 0.5f, -0.1f);
            cabin.transform.localScale = new Vector3(0.9f, 0.65f, 0.55f);
            cabin.GetComponent<Renderer>().material.color = new Color(0.12f, 0.14f, 0.18f);

            // 2. Warning Cones with reflective stripes
            Vector3[] coneOffsets = new Vector3[]
            {
                new Vector3(-1.2f, 0f, 3.0f),
                new Vector3(1.2f, 0f, 3.2f),
                new Vector3(-1.4f, 0f, -3.2f),
                new Vector3(1.4f, 0f, -3.0f)
            };

            foreach (var offset in coneOffsets)
            {
                GameObject cone = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                cone.name = "SafetyCone";
                cone.tag = "Vehicle";
                cone.transform.SetParent(sceneRoot.transform, false);
                cone.transform.localPosition = new Vector3(offset.x, 0.35f, offset.z);
                cone.transform.localScale = new Vector3(0.45f, 0.35f, 0.45f);
                cone.GetComponent<Renderer>().material.color = new Color(1.0f, 0.45f, 0.05f); // Fluorescent Orange

                // Reflective white band
                GameObject band = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                band.name = "ReflectiveBand";
                band.transform.SetParent(cone.transform, false);
                band.transform.localPosition = new Vector3(0f, 0.2f, 0f);
                band.transform.localScale = new Vector3(1.02f, 0.3f, 1.02f);
                band.GetComponent<Renderer>().material.color = Color.white;
            }

            // 3. Pulsing Amber Hazard Light Beacon
            GameObject lightObj = new GameObject("HazardBeacon");
            lightObj.transform.SetParent(sceneRoot.transform, false);
            lightObj.transform.localPosition = new Vector3(0f, 1.8f, 0f);
            Light l = lightObj.AddComponent<Light>();
            l.color = new Color(1.0f, 0.6f, 0.1f);
            l.range = 14f;
            l.intensity = 3.0f;

            return sceneRoot;
        }

        private Junction FindJunction(string id)
        {
            Junction[] junctions = FindObjectsByType<Junction>(FindObjectsSortMode.None);
            foreach (Junction j in junctions)
            {
                if (j.junctionId == id) return j;
            }
            return null;
        }

        private void HandleIncidentTriggered(string junctionId, string incidentType) { }
        private void HandleIncidentResolved(string junctionId) { }
    }
}
