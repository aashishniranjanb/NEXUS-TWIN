using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using NexusTwin.Data;
using NexusTwin.Core;

namespace NexusTwin.Networking
{
    public enum ConnectionState
    {
        Disconnected,
        Connecting,
        Connected,
        Error
    }

    /// <summary>
    /// ApiClient — REST API client for communicating with FastAPI backend.
    /// Handles health checks, traffic state polling, AI predictions, and strategy evaluation/application.
    /// Implements Phase J specifications.
    /// </summary>
    public class ApiClient : MonoBehaviour
    {
        public static ApiClient Instance { get; private set; }

        [Header("Backend Configuration")]
        public string baseUrl = "http://localhost:8000";
        public ConnectionState connectionState = ConnectionState.Disconnected;
        public float healthCheckInterval = 5f;
        public int maxRetryAttempts = 3;

        private float _healthTimer = 0f;

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
            StartCoroutine(CheckHealthRoutine());
        }

        private void Update()
        {
            _healthTimer += Time.deltaTime;
            if (_healthTimer >= healthCheckInterval)
            {
                _healthTimer = 0f;
                StartCoroutine(CheckHealthRoutine());
            }
        }

        public IEnumerator CheckHealthRoutine(Action<bool> callback = null)
        {
            connectionState = ConnectionState.Connecting;
            using (UnityWebRequest req = UnityWebRequest.Get($"{baseUrl}/health"))
            {
                req.timeout = 3;
                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    connectionState = ConnectionState.Connected;
                    if (GameManager.Instance != null) GameManager.Instance.isBackendConnected = true;
                    callback?.Invoke(true);
                }
                else
                {
                    connectionState = ConnectionState.Error;
                    if (GameManager.Instance != null) GameManager.Instance.isBackendConnected = false;
                    callback?.Invoke(false);
                }
            }
        }

        public void GetTrafficState(Action<string> onSuccess, Action<string> onError = null)
        {
            StartCoroutine(GetRequestRoutine("/traffic/state", onSuccess, onError));
        }

        public void GetPrediction(string junctionId, Action<string> onSuccess, Action<string> onError = null)
        {
            StartCoroutine(GetRequestRoutine($"/traffic/prediction?junction_id={junctionId}", onSuccess, onError));
        }

        public void GetRecommendation(string junctionId, Action<string> onSuccess, Action<string> onError = null)
        {
            StartCoroutine(GetRequestRoutine($"/recommendation?junction_id={junctionId}", onSuccess, onError));
        }

        public void EvaluateStrategy(int horizonSeconds, string junctionId, string strategyType, float extSec, float divPct, Action<string> onSuccess, Action<string> onError = null)
        {
            string jsonBody = $"{{\"horizon_seconds\": {horizonSeconds}, \"junction_id\": \"{junctionId}\", \"strategy_type\": \"{strategyType}\", \"extension_seconds\": {extSec}, \"diversion_percent\": {divPct}}}";
            StartCoroutine(PostRequestRoutine("/strategy/evaluate", jsonBody, onSuccess, onError));
        }

        public void ApplyStrategy(string strategyId, string strategyType, string junctionId, Action<string> onSuccess, Action<string> onError = null)
        {
            string jsonBody = $"{{\"strategy_id\": \"{strategyId}\", \"strategy_type\": \"{strategyType}\", \"junction_id\": \"{junctionId}\"}}";
            StartCoroutine(PostRequestRoutine("/strategy/apply", jsonBody, onSuccess, onError));
        }

        public void TriggerIncident(string junctionId, string incidentType, Action<string> onSuccess, Action<string> onError = null)
        {
            string jsonBody = $"{{\"junction_id\": \"{junctionId}\", \"incident_type\": \"{incidentType}\", \"severity\": \"high\"}}";
            StartCoroutine(PostRequestRoutine("/incident/trigger", jsonBody, onSuccess, onError));
        }

        private IEnumerator GetRequestRoutine(string endpoint, Action<string> onSuccess, Action<string> onError)
        {
            using (UnityWebRequest req = UnityWebRequest.Get($"{baseUrl}{endpoint}"))
            {
                req.timeout = 4;
                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    onSuccess?.Invoke(req.downloadHandler.text);
                }
                else
                {
                    onError?.Invoke(req.error);
                }
            }
        }

        private IEnumerator PostRequestRoutine(string endpoint, string jsonPayload, Action<string> onSuccess, Action<string> onError)
        {
            using (UnityWebRequest req = new UnityWebRequest($"{baseUrl}{endpoint}", "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);
                req.uploadHandler = new UploadHandlerRaw(bodyRaw);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                req.timeout = 5;

                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    onSuccess?.Invoke(req.downloadHandler.text);
                }
                else
                {
                    onError?.Invoke(req.error);
                }
            }
        }
    }
}
