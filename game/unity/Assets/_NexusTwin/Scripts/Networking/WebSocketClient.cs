using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using NexusTwin.Vehicles;
using NexusTwin.Traffic;
using NexusTwin.Data;

namespace NexusTwin.Networking
{
    [Serializable]
    public class RemoteVehicleData
    {
        public string id;
        public string type;
        public float x;
        public float y;
        public float z;
        public float speed_mps;
        public float angle_deg;
        public string lane_id;
    }

    [Serializable]
    public class RemoteSignalData
    {
        public string junction_id;
        public int phase_index;
        public string phase_state;
        public float remaining_duration_s;
    }

    [Serializable]
    public class RemoteTrafficPacket
    {
        public string type;
        public int step;
        public float timestamp;
        public List<RemoteVehicleData> vehicles;
        public List<RemoteSignalData> signals;
    }

    /// <summary>
    /// WebSocketClient — Real-time telemetry receiver for SUMO/FastAPI bridge.
    /// Streams vehicle coordinates and signal phases directly into Unity scene with smooth interpolation.
    /// Implements Phase J, L specifications.
    /// </summary>
    public class WebSocketClient : MonoBehaviour
    {
        public static WebSocketClient Instance { get; private set; }

        [Header("Connection Settings")]
        public string wsUrl = "ws://localhost:8000/ws/traffic";
        public bool autoConnect = true;
        public bool isConnected = false;
        public float reconnectDelay = 3f;

        private ClientWebSocket _webSocket;
        private CancellationTokenSource _cts;
        private readonly Queue<string> _incomingMessages = new Queue<string>();
        private readonly object _lock = new object();

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
            if (autoConnect)
            {
                Connect();
            }
        }

        private void OnDestroy()
        {
            Disconnect();
        }

        private void Update()
        {
            // Process queued network messages on main Unity thread
            lock (_lock)
            {
                while (_incomingMessages.Count > 0)
                {
                    string json = _incomingMessages.Dequeue();
                    ProcessMessage(json);
                }
            }
        }

        public async void Connect()
        {
            if (_webSocket != null && _webSocket.State == WebSocketState.Open) return;

            try
            {
                _cts = new CancellationTokenSource();
                _webSocket = new ClientWebSocket();
                Uri serverUri = new Uri(wsUrl);

                Debug.Log($"[WebSocketClient] Connecting to {wsUrl}...");
                await _webSocket.ConnectAsync(serverUri, _cts.Token);

                if (_webSocket.State == WebSocketState.Open)
                {
                    isConnected = true;
                    Debug.Log("[WebSocketClient] WebSocket connection established successfully");
                    _ = ReceiveLoop();
                }
            }
            catch (Exception ex)
            {
                isConnected = false;
                Debug.LogWarning($"[WebSocketClient] Connection failed: {ex.Message}. Will retry in {reconnectDelay}s");
                Invoke(nameof(Connect), reconnectDelay);
            }
        }

        private async Task ReceiveLoop()
        {
            byte[] buffer = new byte[8192];
            try
            {
                while (_webSocket != null && _webSocket.State == WebSocketState.Open)
                {
                    WebSocketReceiveResult result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                        break;
                    }

                    string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    lock (_lock)
                    {
                        _incomingMessages.Enqueue(message);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[WebSocketClient] Receive error: {ex.Message}");
            }
            finally
            {
                isConnected = false;
                Invoke(nameof(Connect), reconnectDelay);
            }
        }

        private void ProcessMessage(string json)
        {
            try
            {
                RemoteTrafficPacket packet = JsonUtility.FromJson<RemoteTrafficPacket>(json);
                if (packet == null) return;

                // Sync Vehicles
                if (packet.vehicles != null && VehicleManager.Instance != null)
                {
                    foreach (var vData in packet.vehicles)
                    {
                        VehicleAgent agent = VehicleManager.Instance.GetActiveVehicle(vData.id);
                        if (agent == null)
                        {
                            VehicleType vType = ParseVehicleType(vData.type);
                            agent = VehicleManager.Instance.Spawn(vData.id, vType, null, vType == VehicleType.Ambulance);
                        }

                        Vector3 unityPos = new Vector3(vData.x, vData.y, vData.z);
                        agent.SetRemoteState(unityPos, vData.angle_deg, vData.speed_mps, vData.lane_id);
                    }
                }

                // Sync Signals
                if (packet.signals != null)
                {
                    TrafficLightController[] allLights = FindObjectsByType<TrafficLightController>(FindObjectsSortMode.None);
                    foreach (var sData in packet.signals)
                    {
                        foreach (var light in allLights)
                        {
                            if (light.junctionId == sData.junction_id)
                            {
                                char sigChar = (light.approachIndex < sData.phase_state.Length) ? sData.phase_state[light.approachIndex] : 'r';
                                light.SetSignal(sigChar);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[WebSocketClient] Parse error: {ex.Message}");
            }
        }

        private VehicleType ParseVehicleType(string typeStr)
        {
            switch (typeStr?.ToLower())
            {
                case "ambulance": return VehicleType.Ambulance;
                case "bus": return VehicleType.Bus;
                case "truck": return VehicleType.Truck;
                case "motorcycle": return VehicleType.Motorcycle;
                case "police": return VehicleType.Police;
                case "fire": return VehicleType.Fire;
                default: return VehicleType.Car;
            }
        }

        public async void Disconnect()
        {
            try
            {
                if (_cts != null)
                {
                    _cts.Cancel();
                    _cts.Dispose();
                    _cts = null;
                }

                if (_webSocket != null)
                {
                    if (_webSocket.State == WebSocketState.Open)
                    {
                        await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Client disconnect", CancellationToken.None);
                    }
                    _webSocket.Dispose();
                    _webSocket = null;
                }
            }
            catch (Exception) { }
            finally
            {
                isConnected = false;
            }
        }
    }
}
