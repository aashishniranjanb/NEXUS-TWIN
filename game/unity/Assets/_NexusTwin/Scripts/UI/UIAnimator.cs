using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace NexusTwin.UI
{
    /// <summary>
    /// UIAnimator — Provides smooth, polished UI transitions for all NEXUS-TWIN panels.
    /// Supports fade-in/out, slide-from-top, slide-from-bottom, slide-from-right,
    /// scale pop-in, and pulsing highlight. All animations use consistent easing curves
    /// matching the NEXUS-TWIN design language (fast in, gentle easeOut).
    /// </summary>
    public static class UIAnimator
    {
        // ─────────────────────────────────────────────────────────────────────────
        // Fade
        // ─────────────────────────────────────────────────────────────────────────
        public static IEnumerator FadeIn(CanvasGroup cg, float duration = 0.25f, System.Action onComplete = null)
        {
            if (cg == null) yield break;
            cg.alpha = 0f;
            cg.interactable = false;
            cg.blocksRaycasts = false;
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                cg.alpha = Mathf.SmoothStep(0f, 1f, t / duration);
                yield return null;
            }
            cg.alpha = 1f;
            cg.interactable = true;
            cg.blocksRaycasts = true;
            onComplete?.Invoke();
        }

        public static IEnumerator FadeOut(CanvasGroup cg, float duration = 0.20f, System.Action onComplete = null)
        {
            if (cg == null) yield break;
            cg.interactable = false;
            cg.blocksRaycasts = false;
            float startAlpha = cg.alpha;
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                cg.alpha = Mathf.SmoothStep(startAlpha, 0f, t / duration);
                yield return null;
            }
            cg.alpha = 0f;
            onComplete?.Invoke();
        }

        // ─────────────────────────────────────────────────────────────────────────
        // Slide + Fade (directional entrance)
        // ─────────────────────────────────────────────────────────────────────────
        public static IEnumerator SlideInFromTop(RectTransform rect, CanvasGroup cg, float slideDistance = 30f, float duration = 0.28f)
        {
            if (rect == null) yield break;
            Vector2 endPos = rect.anchoredPosition;
            Vector2 startPos = endPos + new Vector2(0f, slideDistance);
            if (cg != null) { cg.alpha = 0f; cg.blocksRaycasts = false; }
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float pct = EaseOutCubic(t / duration);
                rect.anchoredPosition = Vector2.Lerp(startPos, endPos, pct);
                if (cg != null) cg.alpha = pct;
                yield return null;
            }
            rect.anchoredPosition = endPos;
            if (cg != null) { cg.alpha = 1f; cg.blocksRaycasts = true; }
        }

        public static IEnumerator SlideInFromBottom(RectTransform rect, CanvasGroup cg, float slideDistance = 30f, float duration = 0.28f)
        {
            if (rect == null) yield break;
            Vector2 endPos = rect.anchoredPosition;
            Vector2 startPos = endPos - new Vector2(0f, slideDistance);
            if (cg != null) { cg.alpha = 0f; cg.blocksRaycasts = false; }
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float pct = EaseOutCubic(t / duration);
                rect.anchoredPosition = Vector2.Lerp(startPos, endPos, pct);
                if (cg != null) cg.alpha = pct;
                yield return null;
            }
            rect.anchoredPosition = endPos;
            if (cg != null) { cg.alpha = 1f; cg.blocksRaycasts = true; }
        }

        public static IEnumerator SlideInFromRight(RectTransform rect, CanvasGroup cg, float slideDistance = 40f, float duration = 0.28f)
        {
            if (rect == null) yield break;
            Vector2 endPos = rect.anchoredPosition;
            Vector2 startPos = endPos + new Vector2(slideDistance, 0f);
            if (cg != null) { cg.alpha = 0f; cg.blocksRaycasts = false; }
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float pct = EaseOutCubic(t / duration);
                rect.anchoredPosition = Vector2.Lerp(startPos, endPos, pct);
                if (cg != null) cg.alpha = pct;
                yield return null;
            }
            rect.anchoredPosition = endPos;
            if (cg != null) { cg.alpha = 1f; cg.blocksRaycasts = true; }
        }

        // ─────────────────────────────────────────────────────────────────────────
        // Scale Pop-In (used for cards and modals)
        // ─────────────────────────────────────────────────────────────────────────
        public static IEnumerator PopIn(RectTransform rect, CanvasGroup cg, float duration = 0.22f)
        {
            if (rect == null) yield break;
            if (cg != null) { cg.alpha = 0f; cg.blocksRaycasts = false; }
            rect.localScale = new Vector3(0.88f, 0.88f, 1f);
            float t = 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float pct = EaseOutBack(t / duration);
                float s = Mathf.Lerp(0.88f, 1f, pct);
                rect.localScale = new Vector3(s, s, 1f);
                if (cg != null) cg.alpha = Mathf.Clamp01(pct);
                yield return null;
            }
            rect.localScale = Vector3.one;
            if (cg != null) { cg.alpha = 1f; cg.blocksRaycasts = true; }
        }

        // ─────────────────────────────────────────────────────────────────────────
        // Pulse Highlight (used on "best" cards and approved state)
        // ─────────────────────────────────────────────────────────────────────────
        public static IEnumerator PulseHighlight(Image target, Color pulseColor, float duration = 0.6f, int pulses = 3)
        {
            if (target == null) yield break;
            Color originalColor = target.color;
            for (int i = 0; i < pulses; i++)
            {
                float t = 0f;
                float half = duration * 0.5f;
                while (t < half) { t += Time.deltaTime; target.color = Color.Lerp(originalColor, pulseColor, t / half); yield return null; }
                t = 0f;
                while (t < half) { t += Time.deltaTime; target.color = Color.Lerp(pulseColor, originalColor, t / half); yield return null; }
            }
            target.color = originalColor;
        }

        // ─────────────────────────────────────────────────────────────────────────
        // Typewriter text (cinematic and alert)
        // ─────────────────────────────────────────────────────────────────────────
        public static IEnumerator Typewriter(Text target, string fullText, float charsPerSecond = 40f)
        {
            if (target == null) yield break;
            target.text = "";
            int len = fullText.Length;
            float delay = 1f / charsPerSecond;
            for (int i = 0; i <= len; i++)
            {
                target.text = fullText.Substring(0, i);
                yield return new WaitForSeconds(delay);
            }
        }

        // ─────────────────────────────────────────────────────────────────────────
        // Easing functions
        // ─────────────────────────────────────────────────────────────────────────
        private static float EaseOutCubic(float t) => 1f - Mathf.Pow(1f - Mathf.Clamp01(t), 3f);

        private static float EaseOutBack(float t)
        {
            float c1 = 1.70158f;
            float c3 = c1 + 1f;
            t = Mathf.Clamp01(t);
            return 1f + c3 * Mathf.Pow(t - 1f, 3f) + c1 * Mathf.Pow(t - 1f, 2f);
        }
    }
}
