using UnityEngine;

namespace NexusTwin.Traffic
{
    /// <summary>
    /// UrbanEnvironmentGenerator — Procedurally populates the 3D world with high-fidelity
    /// stylized architecture, sidewalks, curbs, lane markings, stop bars, crosswalks,
    /// and functional street lighting for a modern strategy game aesthetic.
    /// </summary>
    public class UrbanEnvironmentGenerator : MonoBehaviour
    {
        [Header("City Layout Settings")]
        public int buildingCountPerSide = 10;
        public float setbackDistance = 24f;
        public float corridorLength = 200f;

        [Header("Color Palette")]
        public Color asphaltColor = new Color(0.12f, 0.13f, 0.16f);
        public Color sidewalkColor = new Color(0.75f, 0.78f, 0.82f);
        public Color curbColor = new Color(0.55f, 0.58f, 0.62f);
        public Color[] buildingColors = new Color[]
        {
            new Color(0.14f, 0.16f, 0.22f),
            new Color(0.18f, 0.20f, 0.28f),
            new Color(0.22f, 0.25f, 0.35f),
            new Color(0.11f, 0.13f, 0.18f),
            new Color(0.25f, 0.28f, 0.38f)
        };

        public Color windowGlowCyan = new Color(0.25f, 0.80f, 0.95f, 0.9f);
        public Color windowGlowWarm = new Color(1.0f, 0.85f, 0.55f, 0.9f);
        public Color streetLightColor = new Color(1f, 0.95f, 0.82f);
        public Color markingColor = new Color(0.92f, 0.93f, 0.95f, 0.95f);
        public Color doubleYellowColor = new Color(1.0f, 0.75f, 0.1f);

        private void Start()
        {
            GenerateGroundPlanes();
            GenerateSidewalksAndCurbs();
            GenerateCityBlocks();
            GenerateStreetLights();
            GenerateRoadMarkings();
        }

        private void GenerateGroundPlanes()
        {
            Transform groundRoot = transform.Find("GroundPlanes");
            if (groundRoot != null) return;

            groundRoot = new GameObject("GroundPlanes").transform;
            groundRoot.SetParent(transform);

            // Main Corridor Asphalt (North-South)
            GameObject nsRoad = GameObject.CreatePrimitive(PrimitiveType.Cube);
            nsRoad.name = "Asphalt_Corridor_NS";
            nsRoad.transform.SetParent(groundRoot);
            nsRoad.transform.position = new Vector3(0f, -0.05f, 0f);
            nsRoad.transform.localScale = new Vector3(12f, 0.1f, corridorLength);
            nsRoad.GetComponent<Renderer>().material.color = asphaltColor;

            // Cross Streets at J1, J2, J3
            float[] junctionZs = { 60f, 0f, -60f };
            foreach (float jz in junctionZs)
            {
                GameObject ewRoad = GameObject.CreatePrimitive(PrimitiveType.Cube);
                ewRoad.name = $"Asphalt_CrossStreet_Z{jz}";
                ewRoad.transform.SetParent(groundRoot);
                ewRoad.transform.position = new Vector3(0f, -0.05f, jz);
                ewRoad.transform.localScale = new Vector3(120f, 0.1f, 12f);
                ewRoad.GetComponent<Renderer>().material.color = asphaltColor;
            }
        }

        private void GenerateSidewalksAndCurbs()
        {
            Transform swRoot = transform.Find("Sidewalks");
            if (swRoot != null) return;

            swRoot = new GameObject("Sidewalks").transform;
            swRoot.SetParent(transform);

            // Sidewalk strips along NS corridor (East and West sides)
            float[] xSides = { -7.5f, 7.5f };
            foreach (float x in xSides)
            {
                for (int seg = -1; seg <= 1; seg++)
                {
                    float centerZ = seg * 60f + 30f;
                    if (Mathf.Abs(centerZ) > 85f) continue;

                    GameObject sw = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    sw.name = $"Sidewalk_NS_{x}_{seg}";
                    sw.transform.SetParent(swRoot);
                    sw.transform.position = new Vector3(x + (x > 0 ? 1.5f : -1.5f), 0.08f, centerZ);
                    sw.transform.localScale = new Vector3(3.0f, 0.16f, 40f);
                    sw.GetComponent<Renderer>().material.color = sidewalkColor;

                    // Curb edge
                    GameObject curb = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    curb.name = "Curb";
                    curb.transform.SetParent(sw.transform);
                    curb.transform.localPosition = new Vector3(x > 0 ? -0.48f : 0.48f, 0.02f, 0f);
                    curb.transform.localScale = new Vector3(0.1f, 1.05f, 1.0f);
                    curb.GetComponent<Renderer>().material.color = curbColor;
                }
            }
        }

        private void GenerateCityBlocks()
        {
            Transform cityRoot = transform.Find("CityBlocks");
            if (cityRoot != null) return;

            cityRoot = new GameObject("CityBlocks").transform;
            cityRoot.SetParent(transform);

            float[] xOffsets = { -setbackDistance, setbackDistance };

            foreach (float x in xOffsets)
            {
                for (int i = 0; i < buildingCountPerSide; i++)
                {
                    float z = -corridorLength * 0.45f + (i * (corridorLength / buildingCountPerSide)) + Random.Range(-2f, 2f);

                    // Skip intersections (Z near 60, 0, -60)
                    if (Mathf.Abs(z - 60f) < 16f || Mathf.Abs(z) < 16f || Mathf.Abs(z + 60f) < 16f) continue;

                    float width = Random.Range(12f, 20f);
                    float depth = Random.Range(14f, 22f);
                    float height = Random.Range(18f, 55f);

                    GameObject bldg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    bldg.name = $"Building_{(x > 0 ? "E" : "W")}_{i}";
                    bldg.transform.SetParent(cityRoot);
                    bldg.transform.position = new Vector3(x + (x > 0 ? depth * 0.5f : -depth * 0.5f), height * 0.5f, z);
                    bldg.transform.localScale = new Vector3(depth, height, width);

                    Renderer r = bldg.GetComponent<Renderer>();
                    if (r != null)
                    {
                        Color baseColor = buildingColors[Random.Range(0, buildingColors.Length)];
                        r.material.color = baseColor;
                    }

                    // Window strip bands
                    int bands = Mathf.FloorToInt(height / 8f);
                    for (int b = 1; b <= bands; b++)
                    {
                        GameObject windowBand = GameObject.CreatePrimitive(PrimitiveType.Cube);
                        windowBand.name = $"Windows_{b}";
                        windowBand.transform.SetParent(bldg.transform);
                        float normY = -0.45f + (float)b / (bands + 1);
                        windowBand.transform.localPosition = new Vector3(0f, normY, 0f);
                        windowBand.transform.localScale = new Vector3(1.02f, 0.08f, 1.02f);

                        Renderer wr = windowBand.GetComponent<Renderer>();
                        if (wr != null)
                        {
                            wr.material.color = (Random.value < 0.6f) ? windowGlowCyan : windowGlowWarm;
                        }
                    }

                    // Rooftop architecture (Helipad or HVAC/Antenna)
                    if (Random.value < 0.4f)
                    {
                        GameObject antenna = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                        antenna.name = "RoofAntenna";
                        antenna.transform.SetParent(bldg.transform);
                        antenna.transform.localPosition = new Vector3(0f, 0.58f, 0f);
                        antenna.transform.localScale = new Vector3(0.04f, 0.16f, 0.04f);
                        antenna.GetComponent<Renderer>().material.color = Color.red;
                    }
                }
            }
        }

        private void GenerateStreetLights()
        {
            Transform lightRoot = transform.Find("StreetLights");
            if (lightRoot != null) return;

            lightRoot = new GameObject("StreetLights").transform;
            lightRoot.SetParent(transform);

            for (float z = -85f; z <= 85f; z += 22f)
            {
                CreateStreetLight(lightRoot, new Vector3(-6.8f, 0f, z), 90f);
                CreateStreetLight(lightRoot, new Vector3(6.8f, 0f, z), -90f);
            }
        }

        private void CreateStreetLight(Transform parent, Vector3 pos, float rotationY)
        {
            GameObject lamp = new GameObject("StreetLamp");
            lamp.transform.SetParent(parent);
            lamp.transform.position = pos;
            lamp.transform.rotation = Quaternion.Euler(0f, rotationY, 0f);

            // Pole
            GameObject pole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pole.name = "Pole";
            pole.transform.SetParent(lamp.transform);
            pole.transform.localPosition = new Vector3(0f, 3.8f, 0f);
            pole.transform.localScale = new Vector3(0.12f, 3.8f, 0.12f);
            pole.GetComponent<Renderer>().material.color = new Color(0.25f, 0.27f, 0.32f);

            // Arm
            GameObject arm = GameObject.CreatePrimitive(PrimitiveType.Cube);
            arm.name = "Arm";
            arm.transform.SetParent(lamp.transform);
            arm.transform.localPosition = new Vector3(1.2f, 7.4f, 0f);
            arm.transform.localScale = new Vector3(2.2f, 0.10f, 0.12f);
            arm.GetComponent<Renderer>().material.color = new Color(0.25f, 0.27f, 0.32f);

            // Bulb fixture
            GameObject fixture = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            fixture.name = "Bulb";
            fixture.transform.SetParent(lamp.transform);
            fixture.transform.localPosition = new Vector3(2.1f, 7.2f, 0f);
            fixture.transform.localScale = new Vector3(0.35f, 0.18f, 0.35f);
            fixture.GetComponent<Renderer>().material.color = streetLightColor;

            // Spot Light
            GameObject lightObj = new GameObject("SpotLight");
            lightObj.transform.SetParent(lamp.transform);
            lightObj.transform.localPosition = new Vector3(2.1f, 7.1f, 0f);
            lightObj.transform.rotation = Quaternion.Euler(90f, 0f, 0f);

            Light l = lightObj.AddComponent<Light>();
            l.type = LightType.Spot;
            l.color = streetLightColor;
            l.range = 16f;
            l.spotAngle = 70f;
            l.intensity = 2.2f;
        }

        private void GenerateRoadMarkings()
        {
            Transform marksRoot = transform.Find("RoadMarkings");
            if (marksRoot != null) return;

            marksRoot = new GameObject("RoadMarkings").transform;
            marksRoot.SetParent(transform);

            // Double Yellow Center Lines along Corridor
            for (float z = -90f; z <= 90f; z += 5f)
            {
                if (Mathf.Abs(z - 60f) < 12f || Mathf.Abs(z) < 12f || Mathf.Abs(z + 60f) < 12f) continue;

                CreateLineMarking(marksRoot, new Vector3(-0.15f, 0.08f, z), new Vector3(0.10f, 0.02f, 4.2f), doubleYellowColor);
                CreateLineMarking(marksRoot, new Vector3(0.15f, 0.08f, z), new Vector3(0.10f, 0.02f, 4.2f), doubleYellowColor);
            }

            // White Shoulder Solid Lines (Left & Right road edges)
            for (float z = -90f; z <= 90f; z += 10f)
            {
                if (Mathf.Abs(z - 60f) < 12f || Mathf.Abs(z) < 12f || Mathf.Abs(z + 60f) < 12f) continue;

                CreateLineMarking(marksRoot, new Vector3(-5.2f, 0.08f, z), new Vector3(0.15f, 0.02f, 8.5f), markingColor);
                CreateLineMarking(marksRoot, new Vector3(5.2f, 0.08f, z), new Vector3(0.15f, 0.02f, 8.5f), markingColor);
            }

            // Junction Stop Bars & Zebra Crossings at J1, J2, J3
            float[] junctionZs = { 60f, 0f, -60f };
            foreach (float jz in junctionZs)
            {
                // Stop bars
                CreateLineMarking(marksRoot, new Vector3(2.5f, 0.08f, jz + 11.5f), new Vector3(4.8f, 0.02f, 0.5f), Color.white);
                CreateLineMarking(marksRoot, new Vector3(-2.5f, 0.08f, jz - 11.5f), new Vector3(4.8f, 0.02f, 0.5f), Color.white);

                // Zebra Crosswalks
                CreateCrosswalk(marksRoot, new Vector3(0f, 0.08f, jz + 9.5f));
                CreateCrosswalk(marksRoot, new Vector3(0f, 0.08f, jz - 9.5f));
            }
        }

        private void CreateLineMarking(Transform parent, Vector3 pos, Vector3 scale, Color col)
        {
            GameObject mark = GameObject.CreatePrimitive(PrimitiveType.Cube);
            mark.name = "Marking";
            mark.transform.SetParent(parent, false);
            mark.transform.position = pos;
            mark.transform.localScale = scale;
            Renderer r = mark.GetComponent<Renderer>();
            if (r != null) r.material.color = col;
        }

        private void CreateCrosswalk(Transform parent, Vector3 centerPos)
        {
            GameObject cw = new GameObject("Crosswalk");
            cw.transform.SetParent(parent);
            cw.transform.position = centerPos;

            for (float x = -5.0f; x <= 5.0f; x += 1.4f)
            {
                GameObject stripe = GameObject.CreatePrimitive(PrimitiveType.Cube);
                stripe.name = "Stripe";
                stripe.transform.SetParent(cw.transform);
                stripe.transform.localPosition = new Vector3(x, 0f, 0f);
                stripe.transform.localScale = new Vector3(0.85f, 0.02f, 2.4f);
                Renderer r = stripe.GetComponent<Renderer>();
                if (r != null) r.material.color = Color.white;
            }
        }
    }
}
