using System.Collections.Generic;
using UnityEngine;
using NexusTwin.Data;

namespace NexusTwin.Vehicles
{
    /// <summary>
    /// VehicleManager — High-performance object pool and traffic spawner.
    /// Polished version: multi-part stylized vehicles with emissive headlights/taillights,
    /// proper ambulance light bar, chrome rims, cabin detail, truck cab + cargo, bus windows.
    /// Manages pre-warmed vehicle pools, lane routing between J1, J2, J3, and remote state mapping.
    /// </summary>
    public class VehicleManager : MonoBehaviour
    {
        public static VehicleManager Instance { get; private set; }

        [Header("Pool Configuration")]
        public int initialPoolSizePerType = 12;
        public Transform poolContainer;

        [Header("Traffic Flow Settings")]
        public bool autoSpawnTraffic = true;
        public float spawnInterval = 1.8f;
        public int maxActiveVehicles = 50;

        [Header("Active Vehicles")]
        public List<VehicleAgent> activeVehicles = new List<VehicleAgent>();
        private Dictionary<string, VehicleAgent> _activeByVehicleId = new Dictionary<string, VehicleAgent>();
        private Dictionary<VehicleType, Queue<VehicleAgent>> _pools = new Dictionary<VehicleType, Queue<VehicleAgent>>();

        private float _spawnTimer = 0f;
        private int _vehicleCounter = 100;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
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

        // ──────────────────────────────────────────────
        // PRIMITIVE BUILD HELPERS
        // ──────────────────────────────────────────────
        private Material MakeMat(Color color, bool emissive = false, Color emissiveColor = default)
        {
            Material mat = new Material(Shader.Find("Standard") ?? Shader.Find("Legacy Shaders/Diffuse"));
            mat.color = color;
            if (emissive && mat.HasProperty("_EmissionColor"))
            {
                mat.EnableKeyword("_EMISSION");
                Color ec = (emissiveColor == default(Color)) ? color * 1.6f : emissiveColor * 1.6f;
                mat.SetColor("_EmissionColor", ec);
            }
            return mat;
        }

        private GameObject AddCube(Transform parent, string nm, Vector3 pos, Vector3 scale, Color col, bool emit = false, Color emitCol = default)
        {
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = nm; go.transform.SetParent(parent, false);
            go.transform.localPosition = pos; go.transform.localScale = scale;
            go.GetComponent<Renderer>().material = MakeMat(col, emit, emitCol);
            Object.Destroy(go.GetComponent<Collider>());
            return go;
        }

        private GameObject AddSphere(Transform parent, string nm, Vector3 pos, Vector3 scale, Color col, bool emit = false)
        {
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = nm; go.transform.SetParent(parent, false);
            go.transform.localPosition = pos; go.transform.localScale = scale;
            go.GetComponent<Renderer>().material = MakeMat(col, emit, col);
            Object.Destroy(go.GetComponent<Collider>());
            return go;
        }

        private GameObject AddCyl(Transform parent, string nm, Vector3 pos, Vector3 scale, Vector3 euler, Color col)
        {
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = nm; go.transform.SetParent(parent, false);
            go.transform.localPosition = pos; go.transform.localScale = scale;
            go.transform.localEulerAngles = euler;
            go.GetComponent<Renderer>().material = MakeMat(col);
            Object.Destroy(go.GetComponent<Collider>());
            return go;
        }

        private void AddWheels(Transform body, VehicleType vType)
        {
            Color rubber = new Color(0.07f, 0.07f, 0.09f);
            Color chrome = new Color(0.60f, 0.62f, 0.66f);

            if (vType == VehicleType.Motorcycle)
            {
                float[] wz = { 0.60f, -0.60f };
                foreach (float z in wz)
                {
                    AddCyl(body, "Wheel", new Vector3(0f, -0.30f, z), new Vector3(0.26f, 0.11f, 0.26f), new Vector3(0,0,90), rubber);
                    AddCyl(body, "Rim",   new Vector3(0f, -0.30f, z), new Vector3(0.16f, 0.13f, 0.16f), new Vector3(0,0,90), chrome);
                }
                return;
            }

            float xo = (vType == VehicleType.Bus || vType == VehicleType.Truck) ? 0.56f : 0.52f;
            float yo = -0.36f;
            float wr = 0.28f, wh = 0.16f;
            float fz = (vType == VehicleType.Bus) ? 0.43f : (vType == VehicleType.Truck) ? 0.38f : 0.33f;
            float rz = -fz;

            foreach (var wp in new[] {
                new Vector3(-xo, yo, fz), new Vector3(xo, yo, fz),
                new Vector3(-xo, yo, rz), new Vector3(xo, yo, rz) })
            {
                AddCyl(body, "Wheel", wp, new Vector3(wr, wh, wr), new Vector3(0,0,90), rubber);
                AddCyl(body, "Rim",   wp, new Vector3(wr*0.6f, wh+0.02f, wr*0.6f), new Vector3(0,0,90), chrome);
            }
        }

        // ──────────────────────────────────────────────
        // VEHICLE FACTORY
        // ──────────────────────────────────────────────
        private VehicleAgent CreateVehicleInstance(VehicleType vType)
        {
            GameObject obj = new GameObject($"Veh_{vType}_PoolItem");
            obj.transform.SetParent(poolContainer);
            obj.tag = "Vehicle";

            // Per-type body scale, base color, dark trim
            Vector3 scale = new Vector3(1.8f, 1.2f, 3.8f);
            Color[] carColors = {
                new Color(0.18f, 0.45f, 0.85f), new Color(0.82f, 0.20f, 0.20f),
                new Color(0.22f, 0.26f, 0.32f), new Color(0.92f, 0.93f, 0.95f),
                new Color(0.25f, 0.70f, 0.35f), new Color(0.78f, 0.62f, 0.12f)
            };
            Color baseColor = carColors[Random.Range(0, carColors.Length)];
            Color darkTrim  = new Color(0.10f, 0.12f, 0.16f);

            switch (vType)
            {
                case VehicleType.Car:
                    scale = new Vector3(1.8f, 1.2f, 4.0f);
                    baseColor = carColors[Random.Range(0, carColors.Length)];
                    break;
                case VehicleType.Bus:
                    scale = new Vector3(2.4f, 2.6f, 9.5f);
                    baseColor = new Color(0.94f, 0.62f, 0.08f);  // Transit amber
                    break;
                case VehicleType.Truck:
                    scale = new Vector3(2.3f, 2.5f, 8.2f);
                    baseColor = new Color(0.32f, 0.36f, 0.42f);  // Steel grey
                    break;
                case VehicleType.Motorcycle:
                    scale = new Vector3(0.6f, 0.9f, 1.8f);
                    baseColor = new Color(0.12f, 0.82f, 0.70f);  // Cyan
                    break;
                case VehicleType.Ambulance:
                    scale = new Vector3(2.1f, 2.1f, 5.2f);
                    baseColor = new Color(0.96f, 0.97f, 0.98f);  // Medical white
                    break;
            }

            // ── MAIN BODY ─────────────────────────────
            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Cube);
            body.name = "Body";
            body.transform.SetParent(obj.transform, false);
            body.transform.localScale = scale;
            body.transform.localPosition = new Vector3(0f, scale.y * 0.5f, 0f);
            MeshRenderer bodyRend = body.GetComponent<MeshRenderer>();
            bodyRend.material = MakeMat(baseColor);
            Object.Destroy(body.GetComponent<Collider>());

            // ── WHEELS ────────────────────────────────
            AddWheels(body.transform, vType);

            // ── HEADLIGHTS & TAILLIGHTS ───────────────
            Color hlCol = new Color(1.0f, 0.97f, 0.88f);
            Color tlOff = new Color(0.35f, 0.04f, 0.04f);

            AddSphere(body.transform, "HL_L", new Vector3(-0.32f, -0.06f, 0.52f), new Vector3(0.16f, 0.14f, 0.06f), hlCol, true);
            AddSphere(body.transform, "HL_R", new Vector3( 0.32f, -0.06f, 0.52f), new Vector3(0.16f, 0.14f, 0.06f), hlCol, true);
            AddCube(body.transform, "FrontBumper", new Vector3(0f, -0.32f, 0.52f), new Vector3(0.90f, 0.08f, 0.04f), new Color(0.32f, 0.34f, 0.37f));

            GameObject tlObj = AddCube(body.transform, "Taillight_Bar", new Vector3(0f, -0.08f, -0.52f), new Vector3(0.86f, 0.12f, 0.04f), tlOff, true, tlOff);
            MeshRenderer taillightRend = tlObj.GetComponent<MeshRenderer>();

            // ── TYPE-SPECIFIC DETAILS ─────────────────
            GameObject sirenObj = null;

            if (vType == VehicleType.Car)
            {
                AddCube(body.transform, "Cabin",      new Vector3(0f, 0.44f, -0.04f), new Vector3(0.84f, 0.48f, 0.52f), darkTrim);
                AddCube(body.transform, "Windshield", new Vector3(0f, 0.44f,  0.28f), new Vector3(0.80f, 0.44f, 0.04f), new Color(0.50f, 0.72f, 0.88f, 0.8f));
                AddCube(body.transform, "RearGlass",  new Vector3(0f, 0.44f, -0.30f), new Vector3(0.80f, 0.40f, 0.04f), new Color(0.48f, 0.68f, 0.82f, 0.8f));
            }
            else if (vType == VehicleType.Truck)
            {
                AddCube(body.transform, "TruckCab",   new Vector3(0f,  0.24f,  0.30f), new Vector3(1.02f, 0.72f, 0.34f), darkTrim);
                AddCube(body.transform, "CargoBox",   new Vector3(0f,  0.14f, -0.14f), new Vector3(1.02f, 0.92f, 0.60f), new Color(0.70f, 0.28f, 0.10f));
                AddCyl(body.transform,  "Exhaust",    new Vector3(-0.54f, 0.58f, 0.22f), new Vector3(0.04f, 0.20f, 0.04f), Vector3.zero, new Color(0.20f, 0.20f, 0.22f));
            }
            else if (vType == VehicleType.Bus)
            {
                AddCube(body.transform, "WinRow_L", new Vector3(-0.52f, 0.18f, 0f), new Vector3(0.04f, 0.32f, 0.84f), new Color(0.48f, 0.66f, 0.80f, 0.8f));
                AddCube(body.transform, "WinRow_R", new Vector3( 0.52f, 0.18f, 0f), new Vector3(0.04f, 0.32f, 0.84f), new Color(0.48f, 0.66f, 0.80f, 0.8f));
                AddCube(body.transform, "RoofAC",   new Vector3(0f, 0.56f, 0.12f),  new Vector3(0.54f, 0.12f, 0.34f), new Color(0.80f, 0.82f, 0.84f));
                AddCube(body.transform, "DestBoard", new Vector3(0f, 0.32f, 0.52f), new Vector3(0.74f, 0.14f, 0.04f), new Color(0.06f, 0.06f, 0.08f));
            }
            else if (vType == VehicleType.Motorcycle)
            {
                AddCube(body.transform, "Tank",    new Vector3(0f, 0.20f,  0.06f), new Vector3(0.22f, 0.14f, 0.32f), new Color(0.10f, 0.70f, 0.60f));
                AddCube(body.transform, "Fairing", new Vector3(0f, 0.18f,  0.34f), new Vector3(0.20f, 0.20f, 0.18f), new Color(0.14f, 0.78f, 0.68f));
                AddCube(body.transform, "HBar",    new Vector3(0f, 0.26f,  0.36f), new Vector3(0.50f, 0.04f, 0.04f), new Color(0.52f, 0.54f, 0.58f));
            }
            else if (vType == VehicleType.Ambulance)
            {
                // Side stripes
                AddCube(body.transform, "Stripe_L", new Vector3(-0.54f, 0.04f, 0f), new Vector3(0.04f, 0.22f, 0.90f), new Color(0.90f, 0.07f, 0.07f));
                AddCube(body.transform, "Stripe_R", new Vector3( 0.54f, 0.04f, 0f), new Vector3(0.04f, 0.22f, 0.90f), new Color(0.90f, 0.07f, 0.07f));
                // Medical crosses
                AddCube(body.transform, "Cross_H_L", new Vector3(-0.54f, 0.06f, 0.12f), new Vector3(0.04f, 0.11f, 0.26f), Color.white);
                AddCube(body.transform, "Cross_V_L", new Vector3(-0.54f, 0.06f, 0.12f), new Vector3(0.04f, 0.26f, 0.11f), Color.white);
                // Emergency light bar
                sirenObj = new GameObject("EmergencyLightBar");
                sirenObj.transform.SetParent(body.transform, false);
                sirenObj.transform.localPosition = new Vector3(0f, 0.60f, 0.06f);
                AddCube(sirenObj.transform, "LB_Housing", Vector3.zero, new Vector3(0.72f, 0.14f, 0.24f), new Color(0.84f, 0.86f, 0.88f));
                AddCube(sirenObj.transform, "LB_Red",   new Vector3(-0.22f, 0f, 0f), new Vector3(0.28f, 0.16f, 0.22f), new Color(1f, 0.07f, 0.07f), true, new Color(1f, 0.07f, 0.07f));
                AddCube(sirenObj.transform, "LB_Blue",  new Vector3( 0.22f, 0f, 0f), new Vector3(0.28f, 0.16f, 0.22f), new Color(0.10f, 0.40f, 1.00f), true, new Color(0.10f, 0.40f, 1.00f));
                AddCube(sirenObj.transform, "LB_White", new Vector3( 0.00f, 0f, 0f), new Vector3(0.14f, 0.16f, 0.22f), Color.white, true, Color.white);
            }

            // ── WIRE UP VehicleAgent ──────────────────
            VehicleAgent agent = obj.AddComponent<VehicleAgent>();
            agent.vehicleType = vType;
            agent.vehicleRenderer = bodyRend;
            agent.emergencyFlashingLight = sirenObj;
            agent.taillightRenderer = taillightRend;

            // Root collider
            BoxCollider col = obj.AddComponent<BoxCollider>();
            col.size = scale;
            col.center = new Vector3(0f, scale.y * 0.5f, 0f);

            return agent;
        }

        // ──────────────────────────────────────────────
        // POOL: SPAWN / DESPAWN
        // ──────────────────────────────────────────────
        public VehicleAgent Spawn(string id, VehicleType type, List<Vector3> route, bool isEmergency = false)
        {
            if (!_pools.ContainsKey(type) || _pools[type].Count == 0)
            {
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
                _activeByVehicleId.Remove(agent.vehicleId);
            agent.OnDespawn();
            _pools[agent.vehicleType].Enqueue(agent);
        }

        public void DespawnAll()
        {
            for (int i = activeVehicles.Count - 1; i >= 0; i--)
                Despawn(activeVehicles[i]);
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
            float r = Random.value;
            VehicleType type = VehicleType.Car;
            if (r > 0.88f) type = VehicleType.Bus;
            else if (r > 0.74f) type = VehicleType.Truck;
            else if (r > 0.64f) type = VehicleType.Motorcycle;

            int routeType = Random.Range(0, 4);
            Spawn(id, type, GenerateRoute(routeType), false);
        }

        public List<Vector3> GenerateRoute(int routeType)
        {
            List<Vector3> path = new List<Vector3>();
            float lo = 2.5f;

            bool isDiverting = (Gameplay.ScenarioDirector.Instance != null &&
                                Gameplay.ScenarioDirector.Instance.approved &&
                                Gameplay.ScenarioDirector.Instance.selectedStrategy.type == StrategyType.Diversion);

            switch (routeType)
            {
                case 0: // Southbound J1→J3
                    path.Add(new Vector3(lo, 0f,  90f));
                    path.Add(new Vector3(lo, 0f,  60f));  // J1
                    if (isDiverting)
                    {
                        path.Add(new Vector3((Random.value < 0.5f) ? 50f : -50f, 0f, 60f));
                    }
                    else
                    {
                        path.Add(new Vector3(lo, 0f,  0f));   // J2
                        path.Add(new Vector3(lo, 0f, -60f));  // J3
                        path.Add(new Vector3(lo, 0f, -90f));
                    }
                    break;

                case 1: // Northbound J3→J1
                    path.Add(new Vector3(-lo, 0f, -90f));
                    path.Add(new Vector3(-lo, 0f, -60f));
                    if (isDiverting)
                    {
                        path.Add(new Vector3((Random.value < 0.5f) ? 50f : -50f, 0f, -60f));
                    }
                    else
                    {
                        path.Add(new Vector3(-lo, 0f,  0f));
                        path.Add(new Vector3(-lo, 0f,  60f));
                        path.Add(new Vector3(-lo, 0f,  90f));
                    }
                    break;

                case 2: // Cross street W→E
                    path.Add(new Vector3(-50f, 0f,  lo)); path.Add(new Vector3(0f, 0f, lo)); path.Add(new Vector3(50f, 0f, lo)); break;

                case 3: // Cross street E→W
                    path.Add(new Vector3(50f, 0f, -lo)); path.Add(new Vector3(0f, 0f, -lo)); path.Add(new Vector3(-50f, 0f, -lo)); break;
            }
            return path;
        }

        public VehicleAgent SpawnEmergencyAmbulance()
        {
            List<Vector3> route = new List<Vector3>
            {
                new Vector3(2.5f, 0f,  85f),
                new Vector3(2.5f, 0f,  60f),  // J1
                new Vector3(2.5f, 0f,   0f),  // J2
                new Vector3(2.5f, 0f, -60f),  // J3
                new Vector3(2.5f, 0f, -85f)
            };
            VehicleAgent amb = Spawn("AMBULANCE_01", VehicleType.Ambulance, route, true);
            amb.maxSpeed = 18f;
            Debug.Log("[VehicleManager] Emergency AMBULANCE_01 dispatched along J1-J2-J3 corridor!");
            return amb;
        }
    }
}
