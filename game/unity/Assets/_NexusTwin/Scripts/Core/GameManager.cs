using UnityEngine;
using NexusTwin.Data;

namespace NexusTwin.Core
{
    /// <summary>
    /// GameManager — Singleton that persists across scenes.
    /// Manages session lifecycle and routes between game states.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Session")]
        public string playerName = "Commander";
        public string currentMode = "free_play";
        public string difficulty = "normal";

        [Header("Runtime State")]
        public GameState currentState = GameState.MainMenu;
        public bool isBackendConnected = false;
        public bool useMockData = true; // Stage A: true. Stage B (step 17): false.
        public int currentMission = 1;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Transition to a new game state with validation.
        /// Invalid transitions are logged and rejected.
        /// </summary>
        public void SetState(GameState newState)
        {
            if (!IsValidTransition(currentState, newState))
            {
                Debug.LogWarning($"[GameManager] Invalid state transition: {currentState} -> {newState}");
                return;
            }

            Debug.Log($"[GameManager] State: {currentState} -> {newState}");
            currentState = newState;
            EventBus.RaiseGameStateChanged(newState);
        }

        /// <summary>
        /// State machine transition validation per GAME_STATE_MACHINE.md.
        /// </summary>
        private bool IsValidTransition(GameState from, GameState to)
        {
            if (from == to) return true;

            switch (from)
            {
                case GameState.MainMenu:   return to == GameState.Cinematic || to == GameState.Briefing || to == GameState.Idle;
                case GameState.Cinematic:  return to == GameState.Briefing || to == GameState.Idle || to == GameState.MainMenu;
                case GameState.Briefing:   return to == GameState.Idle || to == GameState.MainMenu;
                case GameState.Idle:       return to == GameState.Event || to == GameState.MainMenu || to == GameState.Briefing;
                case GameState.Event:      return to == GameState.Analysis || to == GameState.Failed;
                case GameState.Analysis:   return to == GameState.Decision || to == GameState.Failed;
                case GameState.Decision:   return to == GameState.Simulation || to == GameState.Approval || to == GameState.Failed;
                case GameState.Simulation: return to == GameState.Comparison || to == GameState.Failed;
                case GameState.Comparison: return to == GameState.Explanation || to == GameState.Approval || to == GameState.Failed;
                case GameState.Explanation:return to == GameState.Approval || to == GameState.Decision || to == GameState.Failed;
                case GameState.Approval:   return to == GameState.Apply || to == GameState.Decision || to == GameState.Failed; // reject loops back or fails
                case GameState.Apply:      return to == GameState.Result || to == GameState.Failed;
                case GameState.Result:     return to == GameState.Score || to == GameState.Failed;
                case GameState.Score:      return to == GameState.Idle || to == GameState.Briefing || to == GameState.MainMenu || to == GameState.NextEvent;
                case GameState.Failed:     return to == GameState.Idle || to == GameState.Briefing || to == GameState.MainMenu || to == GameState.Cinematic;
                case GameState.NextEvent:  return to == GameState.Event || to == GameState.Idle || to == GameState.MainMenu;
                default: return true;
            }
        }
    }
}
