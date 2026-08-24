using UnityEngine;
using NexusTwin.Data;
using NexusTwin.Core;

namespace NexusTwin.Camera
{
    /// <summary>
    /// StrategicCameraController — 3/4 elevated camera controller for NEXUS-TWIN.
    /// Supports Pan, Zoom, Smooth Orbit, Junction Focus (J1, J2, J3), and Incident Focus.
    /// Per DESIGN_GUIDELINES.md §7-8 and Phase B specifications.
    /// </summary>
    public class StrategicCameraController : MonoBehaviour
    {
        public static StrategicCameraController Instance { get; private set; }

        [Header("Movement Settings")]
        public float panSpeed = 25f;
        public float zoomSpeed = 40f;
        public float minZoomDist = 10f;
        public float maxZoomDist = 120f;
        public float smoothTime = 0.15f;

        [Header("Bounds")]
        public Vector2 xBounds = new Vector2(-150f, 150f);
        public Vector2 zBounds = new Vector2(-200f, 200f);

        [Header("Current Mode")]
        public CameraMode mode = CameraMode.Strategic;

        [Header("Focus Targets")]
        public Transform targetJ1;
        public Transform targetJ2;
        public Transform targetJ3;
        public Transform incidentTarget;

        private Vector3 _targetPosition;
        private float _currentZoom = 45f;
        private Vector3 _velocity = Vector3.zero;

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
            _targetPosition = transform.position;
            _currentZoom = transform.position.y;
            EventBus.OnIncidentTriggered += HandleIncidentTriggered;
        }

        private void OnDestroy()
        {
            EventBus.OnIncidentTriggered -= HandleIncidentTriggered;
        }

        private void Update()
        {
            if (mode == CameraMode.IncidentFocus && incidentTarget != null)
            {
                Vector3 desired = new Vector3(incidentTarget.position.x, 30f, incidentTarget.position.z - 25f);
                _targetPosition = Vector3.Lerp(_targetPosition, desired, Time.deltaTime * 3f);
            }
            else
            {
                HandlePan();
                HandleZoom();
                HandleKeyboardShortcuts();
            }

            // Smooth position update
            transform.position = Vector3.SmoothDamp(transform.position, _targetPosition, ref _velocity, smoothTime);
        }

        private void HandlePan()
        {
            float h = Input.GetAxis("Horizontal"); // A/D or Left/Right
            float v = Input.GetAxis("Vertical");   // W/S or Up/Down

            // Right click drag pan
            if (Input.GetMouseButton(1))
            {
                h = -Input.GetAxis("Mouse X") * 2f;
                v = -Input.GetAxis("Mouse Y") * 2f;
            }

            if (Mathf.Abs(h) > 0.01f || Mathf.Abs(v) > 0.01f)
            {
                mode = CameraMode.Strategic;
                Vector3 forward = new Vector3(transform.forward.x, 0f, transform.forward.z).normalized;
                Vector3 right = new Vector3(transform.right.x, 0f, transform.right.z).normalized;
                Vector3 move = (right * h + forward * v) * panSpeed * Time.deltaTime;
                _targetPosition += move;

                _targetPosition.x = Mathf.Clamp(_targetPosition.x, xBounds.x, xBounds.y);
                _targetPosition.z = Mathf.Clamp(_targetPosition.z, zBounds.x, zBounds.y);
            }
        }

        private void HandleZoom()
        {
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.001f)
            {
                _currentZoom -= scroll * zoomSpeed;
                _currentZoom = Mathf.Clamp(_currentZoom, minZoomDist, maxZoomDist);
                _targetPosition.y = _currentZoom;
            }
        }

        private void HandleKeyboardShortcuts()
        {
            // Focus hotkeys: 1 for J1, 2 for J2, 3 for J3, F for Frame All
            if (Input.GetKeyDown(KeyCode.Alpha1) && targetJ1 != null)
            {
                FocusOn(targetJ1.position);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha2) && targetJ2 != null)
            {
                FocusOn(targetJ2.position);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha3) && targetJ3 != null)
            {
                FocusOn(targetJ3.position);
            }
            else if (Input.GetKeyDown(KeyCode.F))
            {
                ResetStrategicView();
            }
            else if (Input.GetKeyDown(KeyCode.E))
            {
                FocusAmbulance();
            }
        }

        public void FocusAmbulance()
        {
            if (NexusTwin.Vehicles.VehicleManager.Instance != null)
            {
                foreach (var veh in NexusTwin.Vehicles.VehicleManager.Instance.activeVehicles)
                {
                    if (veh != null && (veh.isEmergency || veh.vehicleType == Data.VehicleType.Ambulance))
                    {
                        FocusOn(veh.transform.position);
                        return;
                    }
                }
            }
        }

        public void FocusOn(Vector3 worldPos)
        {
            mode = CameraMode.Strategic;
            _targetPosition = new Vector3(worldPos.x, 35f, worldPos.z - 30f);
        }

        public void FocusIncident(Transform target)
        {
            incidentTarget = target;
            mode = CameraMode.IncidentFocus;
        }

        public void ResetStrategicView()
        {
            mode = CameraMode.Strategic;
            _targetPosition = new Vector3(0f, 50f, -45f);
        }

        public void FocusJunction(string junctionId)
        {
            if (junctionId == "J1" && targetJ1 != null) FocusOn(targetJ1.position);
            else if (junctionId == "J2" && targetJ2 != null) FocusOn(targetJ2.position);
            else if (junctionId == "J3" && targetJ3 != null) FocusOn(targetJ3.position);
        }

        private void HandleIncidentTriggered(string junctionId, string incidentType)
        {
            Debug.Log($"[StrategicCamera] Incident detected at {junctionId}, auto-focusing");
            if (junctionId == NexusIds.Junctions.J1 && targetJ1 != null) FocusIncident(targetJ1);
            else if (junctionId == NexusIds.Junctions.J2 && targetJ2 != null) FocusIncident(targetJ2);
            else if (junctionId == NexusIds.Junctions.J3 && targetJ3 != null) FocusIncident(targetJ3);
        }
    }
}
