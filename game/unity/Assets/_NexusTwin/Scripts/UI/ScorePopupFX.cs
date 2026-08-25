using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace NexusTwin.UI
{
    /// <summary>
    /// ScorePopupFX — Floating score popup feedback for rewarding human choices.
    /// Spawns animated text ("+150 PTS — AI ALIGNMENT!") that floats up and fades out.
    /// </summary>
    public class ScorePopupFX : MonoBehaviour
    {
        public static ScorePopupFX Instance { get; private set; }

        private Transform _canvasTransform;
        private Font _font;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            HUDController hud = HUDController.Instance;
            if (hud != null) _canvasTransform = hud.transform;
            _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf") ?? Resources.GetBuiltinResource<Font>("Arial.ttf");
        }

        public static void ShowPopup(string text, Vector2 screenPos, Color color)
        {
            if (Instance == null) return;
            Instance.Spawn(text, screenPos, color);
        }

        private void Spawn(string text, Vector2 pos, Color color)
        {
            if (_canvasTransform == null)
            {
                HUDController hud = HUDController.Instance;
                if (hud != null) _canvasTransform = hud.transform;
                else return;
            }

            GameObject popupObj = new GameObject("ScorePopup");
            popupObj.transform.SetParent(_canvasTransform, false);
            RectTransform rect = popupObj.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(0.5f, 0.5f);
            rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.pivot     = new Vector2(0.5f, 0.5f);
            rect.anchoredPosition = pos;
            rect.sizeDelta = new Vector2(400, 50);

            Text t = popupObj.AddComponent<Text>();
            t.text = text;
            t.font = _font;
            t.fontSize = 18;
            t.fontStyle = FontStyle.Bold;
            t.color = color;
            t.alignment = TextAnchor.MiddleCenter;

            CanvasGroup cg = popupObj.AddComponent<CanvasGroup>();
            StartCoroutine(AnimatePopup(rect, cg));
        }

        private IEnumerator AnimatePopup(RectTransform rect, CanvasGroup cg)
        {
            Vector2 startPos = rect.anchoredPosition;
            Vector2 endPos   = startPos + new Vector2(0f, 60f);

            float duration = 1.2f;
            float time = 0f;

            while (time < duration)
            {
                time += Time.deltaTime;
                float pct = time / duration;

                rect.anchoredPosition = Vector2.Lerp(startPos, endPos, pct);
                cg.alpha = Mathf.Lerp(1f, 0f, pct * pct);

                yield return null;
            }

            Destroy(rect.gameObject);
        }
    }
}
