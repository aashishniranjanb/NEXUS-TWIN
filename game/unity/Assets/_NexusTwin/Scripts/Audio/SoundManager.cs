using UnityEngine;

namespace NexusTwin.Audio
{
    /// <summary>
    /// SoundManager — Procedural and clip-based audio synthesizer for NEXUS-TWIN.
    /// Generates distinct auditory feedback for UI clicks, AI alerts, emergency sirens,
    /// simulation hums, and victory fanfares without requiring external audio assets.
    /// </summary>
    public class SoundManager : MonoBehaviour
    {
        public static SoundManager Instance { get; private set; }

        [Header("Audio Sources")]
        public AudioSource sfxSource;
        public AudioSource sirenSource;
        public AudioSource ambientSource;

        private AudioClip _clickClip;
        private AudioClip _alertClip;
        private AudioClip _approveClip;
        private AudioClip _rejectClip;
        private AudioClip _sirenClip;
        private AudioClip _fanfareClip;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);

            InitializeAudioSources();
            GenerateProceduralClips();
        }

        private void InitializeAudioSources()
        {
            sfxSource = gameObject.AddComponent<AudioSource>();
            sfxSource.playOnAwake = false;
            sfxSource.volume = 0.7f;

            sirenSource = gameObject.AddComponent<AudioSource>();
            sirenSource.playOnAwake = false;
            sirenSource.loop = true;
            sirenSource.volume = 0.5f;

            ambientSource = gameObject.AddComponent<AudioSource>();
            ambientSource.playOnAwake = false;
            ambientSource.loop = true;
            ambientSource.volume = 0.25f;
        }

        private AudioClip _ambientClip;
        public bool isMuted = false;

        private void Start()
        {
            PlayAmbient();
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.M))
            {
                ToggleMute();
            }
        }

        public void ToggleMute()
        {
            isMuted = !isMuted;
            AudioListener.volume = isMuted ? 0f : 1f;
            Debug.Log($"[SoundManager] Audio Mute = {isMuted}");
        }

        private void GenerateProceduralClips()
        {
            _clickClip = CreateTone(880f, 0.08f, 0.5f);        // High crisp click (A5)
            _alertClip = CreateDualTone(587f, 880f, 0.35f);    // Warning chime (D5 + A5)
            _approveClip = CreateChime(new float[] { 523f, 659f, 784f }, 0.4f); // C Major chord
            _rejectClip = CreateTone(220f, 0.25f, 0.6f);       // Low buzz (A3)
            _sirenClip = CreateSiren(0.8f);                    // Modulated emergency siren
            _fanfareClip = CreateChime(new float[] { 523f, 659f, 784f, 1046f }, 0.8f); // Victory chord
            _ambientClip = CreateAmbientDrone(4.0f);            // City rumble
        }

        public void PlayAmbient()
        {
            if (ambientSource != null && _ambientClip != null && !ambientSource.isPlaying)
            {
                ambientSource.clip = _ambientClip;
                ambientSource.Play();
            }
        }

        public void PlayClick()
        {
            if (sfxSource != null && _clickClip != null) sfxSource.PlayOneShot(_clickClip, 0.6f);
        }

        public void PlayAlert()
        {
            if (sfxSource != null && _alertClip != null) sfxSource.PlayOneShot(_alertClip, 0.85f);
        }

        public void PlayApprove()
        {
            if (sfxSource != null && _approveClip != null) sfxSource.PlayOneShot(_approveClip, 0.8f);
        }

        public void PlayReject()
        {
            if (sfxSource != null && _rejectClip != null) sfxSource.PlayOneShot(_rejectClip, 0.7f);
        }

        public void PlayFanfare()
        {
            if (sfxSource != null && _fanfareClip != null) sfxSource.PlayOneShot(_fanfareClip, 0.9f);
        }

        public void StartSiren()
        {
            if (sirenSource != null && _sirenClip != null && !sirenSource.isPlaying)
            {
                sirenSource.clip = _sirenClip;
                sirenSource.Play();
            }
        }

        public void StopSiren()
        {
            if (sirenSource != null && sirenSource.isPlaying)
            {
                sirenSource.Stop();
            }
        }

        // --- Procedural Synthesis Helpers ---

        private AudioClip CreateTone(float frequency, float duration, float volume)
        {
            int sampleRate = 44100;
            int sampleCount = Mathf.CeilToInt(sampleRate * duration);
            float[] samples = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / sampleRate;
                float envelope = 1f - (t / duration); // Exponential decay
                samples[i] = Mathf.Sin(2f * Mathf.PI * frequency * t) * envelope * volume;
            }

            AudioClip clip = AudioClip.Create($"Tone_{frequency}", sampleCount, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        private AudioClip CreateDualTone(float f1, float f2, float duration)
        {
            int sampleRate = 44100;
            int sampleCount = Mathf.CeilToInt(sampleRate * duration);
            float[] samples = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / sampleRate;
                float env = Mathf.Sin(Mathf.PI * (t / duration));
                float wave = (Mathf.Sin(2f * Mathf.PI * f1 * t) + Mathf.Sin(2f * Mathf.PI * f2 * t)) * 0.5f;
                samples[i] = wave * env * 0.6f;
            }

            AudioClip clip = AudioClip.Create("DualTone", sampleCount, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        private AudioClip CreateChime(float[] freqs, float duration)
        {
            int sampleRate = 44100;
            int sampleCount = Mathf.CeilToInt(sampleRate * duration);
            float[] samples = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / sampleRate;
                float env = 1f - Mathf.Pow(t / duration, 0.7f);
                float wave = 0f;
                for (int f = 0; f < freqs.Length; f++)
                {
                    wave += Mathf.Sin(2f * Mathf.PI * freqs[f] * t);
                }
                samples[i] = (wave / freqs.Length) * env * 0.6f;
            }

            AudioClip clip = AudioClip.Create("Chime", sampleCount, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        private AudioClip CreateSiren(float duration)
        {
            int sampleRate = 44100;
            int sampleCount = Mathf.CeilToInt(sampleRate * duration);
            float[] samples = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / sampleRate;
                float mod = (Mathf.Sin(2f * Mathf.PI * 1.5f * t) + 1f) * 0.5f;
                float freq = Mathf.Lerp(600f, 1100f, mod);
                samples[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * 0.45f;
            }

            AudioClip clip = AudioClip.Create("Siren", sampleCount, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        private AudioClip CreateAmbientDrone(float duration)
        {
            int sampleRate = 44100;
            int sampleCount = Mathf.CeilToInt(sampleRate * duration);
            float[] samples = new float[sampleCount];

            for (int i = 0; i < sampleCount; i++)
            {
                float t = (float)i / sampleRate;
                float noise = (Mathf.Sin(2f * Mathf.PI * 55f * t) + Mathf.Sin(2f * Mathf.PI * 110f * t) * 0.5f) * 0.15f;
                samples[i] = noise;
            }

            AudioClip clip = AudioClip.Create("AmbientDrone", sampleCount, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }
    }
}
