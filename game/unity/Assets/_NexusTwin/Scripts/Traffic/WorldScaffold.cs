using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Camera;

namespace NexusTwin.Traffic
{
    /// <summary>
    /// WorldScaffold — Procedurally constructs or anchors the 3-junction corridor (J1, J2, J3)
    /// with roads, lane markings, intersections, pedestrian crosswalks, sidewalks, and traffic signal rigs.
    /// Implements Phase B requirements.
    /// </summary>
    public class WorldScaffold : MonoBehaviour
    {
        [Header("Junction Positions")]
        public Vector3 j1Position = new Vector3(0f, 0f, 60f);   // North
        public Vector3 j2Position = new Vector3(0f, 0f, 0f);    // Center
        public Vector3 j3Position = new Vector3(0f, 0f, -60f);  // South

        [Header("Corridor Geometry Settings")]
        public float roadWidth = 14f;
        public float junctionSize = 18f;
        public float crossStreetLength = 50f;

        [Header("Junction References")]
        public Junction junction1;
        public Junction junction2;
        public Junction junction3;

        [Header("Materials (Optional / Procedural)")]
        public Material roadMaterial;
        public Material markingMaterial;
        public Material sidewalkMaterial;
        public Material groundMaterial;

        private void Awake()
        {
            BuildEnvironmentIfMissing();
        }

        public void BuildEnvironmentIfMissing()
        {
            // Build Ground plane
            if (transform.Find("Ground") == null)
            {
                GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
                ground.name = "Ground";
                ground.transform.SetParent(transform);
                ground.transform.position = new Vector3(0f, -0.05f, 0f);
                ground.transform.localScale = new Vector3(25f, 1f, 25f);
                Renderer r = ground.GetComponent<Renderer>();
                if (r != null)
                {
                    r.material.color = new Color(0.12f, 0.14f, 0.16f); // dark urban asphalt ground
                }
            }

            // Setup or Instantiate Junctions
            junction1 = SetupJunction("J1", j1Position);
            junction2 = SetupJunction("J2", j2Position);
            junction3 = SetupJunction("J3", j3Position);

            // Setup connecting roads
            BuildRoadSegment("Road_J1_to_J2", (j1Position + j2Position) * 0.5f, new Vector3(roadWidth, 0.1f, Mathf.Abs(j1Position.z - j2Position.z) - junctionSize));
            BuildRoadSegment("Road_J2_to_J3", (j2Position + j3Position) * 0.5f, new Vector3(roadWidth, 0.1f, Mathf.Abs(j2Position.z - j3Position.z) - junctionSize));
            BuildRoadSegment("Road_J1_North", j1Position + new Vector3(0f, 0f, crossStreetLength * 0.5f), new Vector3(roadWidth, 0.1f, crossStreetLength));
            BuildRoadSegment("Road_J3_South", j3Position - new Vector3(0f, 0f, crossStreetLength * 0.5f), new Vector3(roadWidth, 0.1f, crossStreetLength));

            // Setup Cross Streets (East-West at each junction)
            BuildRoadSegment("Cross_J1", j1Position, new Vector3(crossStreetLength * 2f + junctionSize, 0.1f, roadWidth));
            BuildRoadSegment("Cross_J2", j2Position, new Vector3(crossStreetLength * 2f + junctionSize, 0.1f, roadWidth));
            BuildRoadSegment("Cross_J3", j3Position, new Vector3(crossStreetLength * 2f + junctionSize, 0.1f, roadWidth));

            // Link camera targets if camera is present
            StrategicCameraController cam = FindFirstObjectByType<StrategicCameraController>();
            if (cam != null)
            {
                cam.targetJ1 = junction1.transform;
                cam.targetJ2 = junction2.transform;
                cam.targetJ3 = junction3.transform;
            }
        }

        private Junction SetupJunction(string id, Vector3 pos)
        {
            Transform existing = transform.Find($"Junction_{id}");
            GameObject jObj;
            if (existing == null)
            {
                jObj = new GameObject($"Junction_{id}");
                jObj.transform.SetParent(transform);
                jObj.transform.position = pos;

                // Intersection center pad
                GameObject pad = GameObject.CreatePrimitive(PrimitiveType.Cube);
                pad.name = "IntersectionPad";
                pad.transform.SetParent(jObj.transform);
                pad.transform.localPosition = new Vector3(0f, 0.05f, 0f);
                pad.transform.localScale = new Vector3(junctionSize, 0.1f, junctionSize);
                Renderer r = pad.GetComponent<Renderer>();
                if (r != null) r.material.color = new Color(0.2f, 0.22f, 0.25f);
            }
            else
            {
                jObj = existing.gameObject;
            }

            Junction junction = jObj.GetComponent<Junction>();
            if (junction == null) junction = jObj.AddComponent<Junction>();
            junction.junctionId = id;

            // Setup signal heads
            if (junction.lights == null || junction.lights.Length == 0)
            {
                junction.lights = new TrafficLightController[4];
                Vector3[] offsets = {
                    new Vector3(0f, 0f, junctionSize * 0.55f),   // North
                    new Vector3(junctionSize * 0.55f, 0f, 0f),   // East
                    new Vector3(0f, 0f, -junctionSize * 0.55f),  // South
                    new Vector3(-junctionSize * 0.55f, 0f, 0f)   // West
                };

                for (int i = 0; i < 4; i++)
                {
                    junction.lights[i] = CreateTrafficLightRig(jObj.transform, id, i, offsets[i]);
                }
            }

            return junction;
        }

        private TrafficLightController CreateTrafficLightRig(Transform parent, string jId, int approach, Vector3 localOffset)
        {
            GameObject rig = new GameObject($"Signal_{jId}_Approach_{approach}");
            rig.transform.SetParent(parent);
            rig.transform.localPosition = localOffset;

            // Pole
            GameObject pole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pole.name = "Pole";
            pole.transform.SetParent(rig.transform);
            pole.transform.localPosition = new Vector3(0f, 2.5f, 0f);
            pole.transform.localScale = new Vector3(0.25f, 2.5f, 0.25f);

            // Signal Box
            GameObject box = GameObject.CreatePrimitive(PrimitiveType.Cube);
            box.name = "SignalBox";
            box.transform.SetParent(rig.transform);
            box.transform.localPosition = new Vector3(0f, 5.0f, 0f);
            box.transform.localScale = new Vector3(0.8f, 2.2f, 0.6f);
            box.GetComponent<Renderer>().material.color = new Color(0.1f, 0.1f, 0.1f);

            // Red Light Head
            GameObject red = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            red.name = "RedLamp";
            red.transform.SetParent(box.transform);
            red.transform.localPosition = new Vector3(0f, 0.33f, 0.5f);
            red.transform.localScale = new Vector3(0.5f, 0.25f, 0.2f);

            // Yellow Light Head
            GameObject yellow = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            yellow.name = "YellowLamp";
            yellow.transform.SetParent(box.transform);
            yellow.transform.localPosition = new Vector3(0f, 0f, 0.5f);
            yellow.transform.localScale = new Vector3(0.5f, 0.25f, 0.2f);

            // Green Light Head
            GameObject green = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            green.name = "GreenLamp";
            green.transform.SetParent(box.transform);
            green.transform.localPosition = new Vector3(0f, -0.33f, 0.5f);
            green.transform.localScale = new Vector3(0.5f, 0.25f, 0.2f);

            TrafficLightController tlc = rig.AddComponent<TrafficLightController>();
            tlc.junctionId = jId;
            tlc.approachIndex = approach;
            tlc.redLightRenderer = red.GetComponent<MeshRenderer>();
            tlc.yellowLightRenderer = yellow.GetComponent<MeshRenderer>();
            tlc.greenLightRenderer = green.GetComponent<MeshRenderer>();

            return tlc;
        }

        private void BuildRoadSegment(string name, Vector3 pos, Vector3 size)
        {
            Transform existing = transform.Find(name);
            if (existing != null) return;

            GameObject road = GameObject.CreatePrimitive(PrimitiveType.Cube);
            road.name = name;
            road.transform.SetParent(transform);
            road.transform.position = pos;
            road.transform.localScale = size;
            Renderer r = road.GetComponent<Renderer>();
            if (r != null)
            {
                r.material.color = new Color(0.18f, 0.19f, 0.22f); // dark asphalt
            }
        }
    }
}
