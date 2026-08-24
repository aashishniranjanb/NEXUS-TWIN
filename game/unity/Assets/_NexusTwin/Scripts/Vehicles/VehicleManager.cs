using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;

namespace NexusTwin.Vehicles
{
    /// <summary>
    /// VehicleManager — High performance object pool and traffic spawner.
    /// Manages pre-warmed vehicle pools, lane routing between J1, J2, J3, and remote state mapping.
    /// Implements Phase C requirements.
    /// </summary>
    public class VehicleManager : MonoBehaviour
    {
        public static VehicleManager Instance { get; private set; }

        [Header("Pool Configuration")]
        public int initialPoolSizePerType = 15;
        public Transform poolContainer;

        [Header("Traffic Flow Settings")]
        public bool autoSpawnTraffic = true;
        public float spawnInterval = 1.5f;
        public int maxActiveVehicles = 60;

        [Header("Active Vehicles")]
        public List<VehicleAgent> activeVehicles = new List<VehicleAgent>();
        private Dictionary<string, VehicleAgent> _activeByVehicleId = new Dictionary<string, VehicleAgent>();

        // Object pools grouped by VehicleType
        private Dictionary<VehicleType, Queue<VehicleAgent>> _pools = new Dictionary<VehicleType, Queue<VehicleAgent>>();

        private float _spawnTimer = 0f;
        private int _vehicleCounter = 100;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;

            if (poolContainer == null)
            {
                GameObject pc = new GameObject("VehiclePoolContainer");
                pc.transform.SetParent(transform);
                poolContainer = pc.transform;
            }

            InitializePools();
        }

        private void Update()
        {
            if (autoSpawnTraffic && activeVehicles.Count < maxActiveVehicles)
            {
                _spawnTimer += Time.deltaTime;
                if (_spawnTimer >= spawnInterval)
                {
                    _spawnTimer = 0f;
                    SpawnRandomTrafficVehicle();
                }
            }
        }

        private void InitializePools()
        {
            foreach (VehicleType vType in System.Enum.GetValues(typeof(VehicleType)))
            {
                _pools[vType] = new Queue<VehicleAgent>();
                for (int i = 0; i < initialPoolSizePerType; i++)
                {
                    VehicleAgent agent = CreateVehicleInstance(vType);
                    agent.gameObject.SetActive(false);
                    _pools[vType].Enqueue(agent);
                }
            }
        }

        private VehicleAgent CreateVehicleInstance(VehicleType vType)
        {
            GameObject obj = new GameObject($"Veh_{vType}_PoolItem");
            obj.transform.SetParent(poolContainer);
            obj.tag = "Vehicle";

            Vector3 scale = new Vector3(1.8f, 1.2f, 3.8f);
            Color baseColor = new Color(0.2f, 0.45f, 0.85f); // Cobalt Blue
            Color darkTrim = new Color(0.1f, 0.12f, 0.16f);

            switch (vType)
            {
                case VehicleType.Car:
                    scale = new Vector3(1.8f, 1.2f, 3.8f);
                    Color[] carColors = { new Color(0.18f, 0.45f, 0.85f), new Color(0.85f, 0.22f, 0.22f), new Color(0.25f, 0.28f, 0.32f), new Color(0.92f, 0.93f, 0.95f) };
                    baseColor = carColors[Random.Range(0, carColors.Length)];
                    break;
                case VehicleType.Bus:
                    scale = new Vector3(2.4f, 2.5f, 9.0f);
                    baseColor = new Color(0.95f, 0.65f, 0.1f); // Transit Amber/Yellow
                    break;
                case VehicleType.Truck:
                    scale = new Vector3(2.2f, 2.4f, 7.8f);
                    baseColor = new Color(0.35f, 0.38f, 0.45f); // Steel Grey
                    break;
                case VehicleType.Motorcycle:
                    scale = new Vector3(0.8f, 1.0f, 2.0f);
                    baseColor = new Color(0.15f, 0.85f, 0.75f); // Cyan
                    break;
                case VehicleType.Ambulance:
                    scale = new Vector3(2.1f, 2.0f, 5.0f);
                    baseColor = Color.white; // Pure Medical White
                    break;
            }

            // 1. Lower Chassis / Main Body
            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Cube);
            body.name = "Body";
            body.transform.SetParent(obj.transform, false);
            body.transform.localScale = scale;
            body.transform.localPosition = new Vector3(0f, scale.y * 0.5f, 0f);
            MeshRenderer bodyRend = body.GetComponent<MeshRenderer>();
            bodyRend.material.color = baseColor;

            // 2. Cabin / Upper Glass Deck (for Car, Bus, Truck, Ambulance)
            if (vType == VehicleType.Car)
            {
                GameObject cabin = GameObject.CreatePrimitive(PrimitiveType.Cube);
                cabin.name = "Cabin";
                cabin.transform.SetParent(body.transform, false);
                cabin.transform.localPosition = new Vector3(0f, 0.45f, -0.05f);
                cabin.transform.localScale = new Vector3(0.85f, 0.55f, 0.55f);
                cabin.GetComponent<Renderer>().material.color = darkTrim;
            }
            else if (vType == VehicleType.Truck)
            {
                // Cargo Container on rear bed
                GameObject cargo = GameObject.CreatePrimitive(PrimitiveType.Cube);
                cargo.name = "CargoBox";
                cargo.transform.SetParent(body.transform, false);
                cargo.transform.localPosition = new Vector3(0f, 0.15f, -0.2f);
                cargo.transform.localScale = new Vector3(1.02f, 1.05f, 0.65f);
                cargo.GetComponent<Renderer>().material.color = new Color(0.85f, 0.35f, 0.15f);
            }
            else if (vType == VehicleType.Ambulance)
            {
                // Red Cross Decals on Left & Right
                GameObject crossH = GameObject.CreatePrimitive(PrimitiveType.Cube);
                crossH.name = "RedCross_H";
                crossH.transform.SetParent(body.transform, false);
                crossH.transform.localPosition = new Vector3(0f, 0.05f, 0f);
                crossH.transform.localScale = new Vector3(1.03f, 0.25f, 0.65f);
                crossH.GetComponent<Renderer>().material.color = Color.red;

                GameObject crossV = GameObject.CreatePrimitive(PrimitiveType.Cube);
                crossV.name = "RedCross_V";
                crossV.transform.SetParent(body.transform, false);
                crossV.transform.localPosition = new Vector3(0f, 0.05f, 0f);
                crossV.transform.localScale = new Vector3(1.03f, 0.65f, 0.25f);
                crossV.GetComponent<Renderer>().material.color = Color.red;
            }

            // 3. Emergency Dual Siren (Red & Blue Flashing)
            GameObject siren = null;
            if (vType == VehicleType.Ambulance)
            {
                siren = new GameObject("EmergencyLightBar");
                siren.transform.SetParent(body.transform, false);
                siren.transform.localPosition = new Vector3(0f, 0.58f, 0.2f);

                GameObject sirenRed = GameObject.CreatePrimitive(PrimitiveType.Cube);
                sirenRed.name = "Siren_Red";
                sirenRed.transform.SetParent(siren.transform, false);
                sirenRed.transform.localPosition = new Vector3(-0.35f, 0f, 0f);
                sirenRed.transform.localScale = new Vector3(0.35f, 0.2f, 0.25f);
                sirenRed.GetComponent<Renderer>().material.color = Color.red;

                GameObject sirenBlue = GameObject.CreatePrimitive(PrimitiveType.Cube);
                sirenBlue.name = "Siren_Blue";
                sirenBlue.transform.SetParent(siren.transform, false);
                sirenBlue.transform.localPosition = new Vector3(0.35f, 0f, 0f);
                sirenBlue.transform.localScale = new Vector3(0.35f, 0.2f, 0.25f);
                sirenBlue.GetComponent<Renderer>().material.color = new Color(0.1f, 0.5f, 1.0f);
            }

            // 4. Wheels
            float wheelRadius = 0.35f;
            float wheelWidth = 0.25f;
            Vector3[] wheelPositions = (vType == VehicleType.Motorcycle)
                ? new Vector3[] { new Vector3(0f, -0.3f, 0.7f), new Vector3(0f, -0.3f, -0.7f) }
                : new Vector3[] {
                    new Vector3(-0.52f, -0.35f, 0.32f),
                    new Vector3(0.52f, -0.35f, 0.32f),
                    new Vector3(-0.52f, -0.35f, -0.32f),
                    new Vector3(0.52f, -0.35f, -0.32f)
                };

            foreach (var wPos in wheelPositions)
            {
                GameObject wheel = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                wheel.name = "Wheel";
                wheel.transform.SetParent(body.transform, false);
                wheel.transform.localPosition = wPos;
                wheel.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);
                wheel.transform.localScale = new Vector3(wheelRadius, wheelWidth, wheelRadius);
                wheel.GetComponent<Renderer>().material.color = new Color(0.12f, 0.12f, 0.14f);
            }

            // 5. Headlights
            GameObject hlLeft = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            hlLeft.name = "Headlight_L";
            hlLeft.transform.SetParent(body.transform, false);
            hlLeft.transform.localPosition = new Vector3(-0.35f, -0.1f, 0.5f);
            hlLeft.transform.localScale = new Vector3(0.18f, 0.18f, 0.08f);
            hlLeft.GetComponent<Renderer>().material.color = new Color(1f, 0.95f, 0.8f);

            GameObject hlRight = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            hlRight.name = "Headlight_R";
            hlRight.transform.SetParent(body.transform, false);
            hlRight.transform.localPosition = new Vector3(0.35f, -0.1f, 0.5f);
            hlRight.transform.localScale = new Vector3(0.18f, 0.18f, 0.08f);
            hlRight.GetComponent<Renderer>().material.color = new Color(1f, 0.95f, 0.8f);

            // 6. Taillights Bar
            GameObject tl = GameObject.CreatePrimitive(PrimitiveType.Cube);
            tl.name = "Taillight_Bar";
            tl.transform.SetParent(body.transform, false);
            tl.transform.localPosition = new Vector3(0f, -0.05f, -0.5f);
            tl.transform.localScale = new Vector3(0.85f, 0.15f, 0.05f);
            MeshRenderer tlRend = tl.GetComponent<MeshRenderer>();
            tlRend.material.color = new Color(0.35f, 0.05f, 0.05f);

            VehicleAgent agent = obj.AddComponent<VehicleAgent>();
            agent.vehicleType = vType;
            agent.vehicleRenderer = bodyRend;
            agent.emergencyFlashingLight = siren;
            agent.taillightRenderer = tlRend;

            // BoxCollider for raycast obstacle avoidance
            BoxCollider col = obj.AddComponent<BoxCollider>();
            col.size = scale;
            col.center = new Vector3(0f, scale.y * 0.5f, 0f);

            return agent;
        }

        public VehicleAgent Spawn(string id, VehicleType type, List<Vector3> route, bool isEmergency = false)
        {
            if (!_pools.ContainsKey(type) || _pools[type].Count == 0)
            {
                // Expand pool dynamically
                VehicleAgent newAgent = CreateVehicleInstance(type);
                _pools[type].Enqueue(newAgent);
            }

            VehicleAgent agent = _pools[type].Dequeue();
            agent.OnSpawn(id, type, route, isEmergency);
            activeVehicles.Add(agent);
            _activeByVehicleId[id] = agent;
            return agent;
        }

        public void Despawn(VehicleAgent agent)
        {
            if (agent == null) return;

            activeVehicles.Remove(agent);
            if (!string.IsNullOrEmpty(agent.vehicleId))
            {
                _activeByVehicleId.Remove(agent.vehicleId);
            }

            agent.OnDespawn();
            _pools[agent.vehicleType].Enqueue(agent);
        }

        public void DespawnAll()
        {
            for (int i = activeVehicles.Count - 1; i >= 0; i--)
            {
                Despawn(activeVehicles[i]);
            }
        }

        public VehicleAgent GetActiveVehicle(string id)
        {
            _activeByVehicleId.TryGetValue(id, out VehicleAgent agent);
            return agent;
        }

        private void SpawnRandomTrafficVehicle()
        {
            _vehicleCounter++;
            string id = $"veh_{_vehicleCounter}";

            // Weighted random type: mostly cars, some trucks, buses, motorcycles
            float r = Random.value;
            VehicleType type = VehicleType.Car;
            if (r > 0.85f) type = VehicleType.Bus;
            else if (r > 0.70f) type = VehicleType.Truck;
            else if (r > 0.60f) type = VehicleType.Motorcycle;

            // Route selection: 0 = Southbound (J1->J2->J3), 1 = Northbound (J3->J2->J1), 2 = Cross Street Eastbound, 3 = Cross Street Westbound
            int routeType = Random.Range(0, 4);
            List<Vector3> route = GenerateRoute(routeType);

            Spawn(id, type, route, false);
        }

        public List<Vector3> GenerateRoute(int routeType)
        {
            List<Vector3> path = new List<Vector3>();
            float laneOffset = 2.5f;

            bool isDiverting = (Gameplay.ScenarioDirector.Instance != null && 
                                Gameplay.ScenarioDirector.Instance.approved && 
                                Gameplay.ScenarioDirector.Instance.selectedStrategy.type == StrategyType.Diversion);

            switch (routeType)
            {
                case 0: // Southbound Corridor (J1 to J3)
                    path.Add(new Vector3(laneOffset, 0f, 90f));
                    path.Add(new Vector3(laneOffset, 0f, 60f));   // J1
                    if (isDiverting)
                    {
                        // Turn East or West cross street at J1 to bypass J2 accident zone
                        float targetX = (Random.value < 0.5f) ? 50f : -50f;
                        path.Add(new Vector3(targetX, 0f, 60f));
                    }
                    else
                    {
                        path.Add(new Vector3(laneOffset, 0f, 0f));    // J2
                        path.Add(new Vector3(laneOffset, 0f, -60f));  // J3
                        path.Add(new Vector3(laneOffset, 0f, -90f));
                    }
                    break;

                case 1: // Northbound Corridor (J3 to J1)
                    path.Add(new Vector3(-laneOffset, 0f, -90f));
                    path.Add(new Vector3(-laneOffset, 0f, -60f));  // J3
                    if (isDiverting)
                    {
                        // Turn East or West cross street at J3 to bypass J2 accident zone
                        float targetX = (Random.value < 0.5f) ? 50f : -50f;
                        path.Add(new Vector3(targetX, 0f, -60f));
                    }
                    else
                    {
                        path.Add(new Vector3(-laneOffset, 0f, 0f));    // J2
                        path.Add(new Vector3(-laneOffset, 0f, 60f));   // J1
                        path.Add(new Vector3(-laneOffset, 0f, 90f));
                    }
                    break;

                case 2: // Cross Street at J2 (West to East)
                    path.Add(new Vector3(-50f, 0f, laneOffset));
                    path.Add(new Vector3(0f, 0f, laneOffset));     // J2
                    path.Add(new Vector3(50f, 0f, laneOffset));
                    break;

                case 3: // Cross Street at J2 (East to West)
                    path.Add(new Vector3(50f, 0f, -laneOffset));
                    path.Add(new Vector3(0f, 0f, -laneOffset));    // J2
                    path.Add(new Vector3(-50f, 0f, -laneOffset));
                    break;
            }

            return path;
        }

        public VehicleAgent SpawnEmergencyAmbulance()
        {
            List<Vector3> route = new List<Vector3>
            {
                new Vector3(2.5f, 0f, 85f),
                new Vector3(2.5f, 0f, 60f),  // J1
                new Vector3(2.5f, 0f, 0f),   // J2
                new Vector3(2.5f, 0f, -60f), // J3
                new Vector3(2.5f, 0f, -85f)
            };

            VehicleAgent amb = Spawn("AMBULANCE_01", VehicleType.Ambulance, route, true);
            amb.maxSpeed = 18f; // Fast emergency speed
            Debug.Log("[VehicleManager] Emergency AMBULANCE_01 dispatched along J1-J2-J3 corridor!");
            return amb;
        }
    }
}
