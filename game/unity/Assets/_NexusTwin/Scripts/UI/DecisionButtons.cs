using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Core;
using NexusTwin.Data;

namespace NexusTwin.UI
{
    /// <summary>
    /// DecisionButtons — Human-in-the-loop operator controls: Approve, Reject, Try Another.
    /// Implements Phase G specifications.
    /// </summary>
    public class DecisionButtons : MonoBehaviour
    {
        [Header("Containers")]
        public GameObject panelRoot;

        [Header("Buttons")]
        public Button approveButton;
        public Button rejectButton;
        public Button tryAnotherButton;

        private void Start()
        {
            if (approveButton != null) approveButton.onClick.AddListener(OnApproveClicked);
            if (rejectButton != null) rejectButton.onClick.AddListener(OnRejectClicked);
            if (tryAnotherButton != null) tryAnotherButton.onClick.AddListener(OnTryAnotherClicked);

            EventBus.OnGameStateChanged += HandleGameStateChanged;
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnDestroy()
        {
            EventBus.OnGameStateChanged -= HandleGameStateChanged;
        }

        private void HandleGameStateChanged(GameState state)
        {
            if (panelRoot == null) return;
            // Only show decision buttons when in Approval or Decision states
            bool shouldShow = (state == GameState.Approval || state == GameState.Explanation);
            panelRoot.SetActive(shouldShow);
        }

        private void OnApproveClicked()
        {
            Debug.Log("[DecisionButtons] Player clicked APPROVE");
            EventBus.RaiseApproved();
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnRejectClicked()
        {
            Debug.Log("[DecisionButtons] Player clicked REJECT");
            EventBus.RaiseRejected();
            if (panelRoot != null) panelRoot.SetActive(false);
        }

        private void OnTryAnotherClicked()
        {
            Debug.Log("[DecisionButtons] Player clicked TRY ANOTHER");
            GameManager.Instance?.SetState(GameState.Decision);
        }
    }
}
