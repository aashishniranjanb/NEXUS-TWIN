using UnityEngine;
using UnityEngine.UI;
using NexusTwin.Data;
using NexusTwin.Camera;
using NexusTwin.Traffic;
using NexusTwin.Vehicles;
using NexusTwin.Gameplay;
using NexusTwin.DigitalTwin;
using NexusTwin.Scoring;
using NexusTwin.Networking;
using NexusTwin.UI;

namespace NexusTwin.Core
{
    /// <summary>
    /// SceneBootstrapper — Turnkey initializer for NEXUS-TWIN.
    /// Polished version: wires in all animated UI panels, health bar, junction indicators,
    /// confidence bars, risk fill bars, decision button styling, and AI disagreement modal.
    /// </summary>
    [DefaultExecutionOrder(-100)]
    public class SceneBootstrapper : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void AutoBootstrap()
        {
            GameObject bootObj = new GameObject("[NEXUS_BOOTSTRAPPER]");
            bootObj.AddComponent<SceneBootstrapper>();
            DontDestroyOnLoad(bootObj);
        }

        private void Awake()
        {
            EnsureCoreManagers();
            EnsureWorldAndCamera();
            EnsureHUDCanvas();
        }

        // ──────────────────────────────────────────────
        // CORE MANAGERS
        // ──────────────────────────────────────────────
        private void EnsureCoreManagers()
        {
            if (FindFirstObjectByType<GameManager>() == null)
            { GameObject gm = new GameObject("GameManager"); gm.AddComponent<GameManager>(); }

            if (FindFirstObjectByType<ApiClient>() == null)
            { GameObject api = new GameObject("ApiClient"); api.AddComponent<ApiClient>(); }

            if (FindFirstObjectByType<WebSocketClient>() == null)
            { GameObject ws = new GameObject("WebSocketClient"); ws.AddComponent<WebSocketClient>(); }

            if (FindFirstObjectByType<VehicleManager>() == null)
            { GameObject vm = new GameObject("VehicleManager"); vm.AddComponent<VehicleManager>(); }

            if (FindFirstObjectByType<IncidentManager>() == null)
            { GameObject im = new GameObject("IncidentManager"); im.AddComponent<IncidentManager>(); }

            if (FindFirstObjectByType<NexusTwin.Audio.SoundManager>() == null)
            { GameObject sm = new GameObject("SoundManager"); sm.AddComponent<NexusTwin.Audio.SoundManager>(); }

            if (FindFirstObjectByType<ScoreController>() == null)
            { GameObject sc = new GameObject("ScoreController"); sc.AddComponent<ScoreController>(); }

            if (FindFirstObjectByType<DigitalTwinSimulationView>() == null)
            { GameObject dtv = new GameObject("DigitalTwinSimulationView"); dtv.AddComponent<DigitalTwinSimulationView>(); }

            if (FindFirstObjectByType<ScenarioDirector>() == null)
            { GameObject sd = new GameObject("ScenarioDirector"); sd.AddComponent<ScenarioDirector>(); }

            if (FindFirstObjectByType<SandboxModeController>() == null)
            { GameObject smc = new GameObject("SandboxModeController"); smc.AddComponent<SandboxModeController>(); }
        }

        // ──────────────────────────────────────────────
        // WORLD & CAMERA
        // ──────────────────────────────────────────────
        private void EnsureWorldAndCamera()
        {
            if (FindFirstObjectByType<WorldScaffold>() == null)
            { new GameObject("WorldScaffold").AddComponent<WorldScaffold>(); }

            if (FindFirstObjectByType<UrbanEnvironmentGenerator>() == null)
            { new GameObject("UrbanEnvironmentGenerator").AddComponent<UrbanEnvironmentGenerator>(); }

            if (FindFirstObjectByType<TrafficHeatmapOverlay>() == null)
            { new GameObject("TrafficHeatmapOverlay").AddComponent<TrafficHeatmapOverlay>(); }

            StrategicCameraController camCtrl = FindFirstObjectByType<StrategicCameraController>();
            if (camCtrl == null)
            {
                UnityEngine.Camera mainCam = UnityEngine.Camera.main;
                if (mainCam == null)
                {
                    GameObject camObj = new GameObject("Main Camera");
                    mainCam = camObj.AddComponent<UnityEngine.Camera>();
                    camObj.tag = "MainCamera";
                    camObj.AddComponent<AudioListener>();
                }
                mainCam.transform.position = new Vector3(0f, 45f, -40f);
                mainCam.transform.rotation = Quaternion.Euler(45f, 0f, 0f);
                camCtrl = mainCam.gameObject.AddComponent<StrategicCameraController>();
            }

            if (camCtrl != null)
            {
                Junction[] junctions = FindObjectsByType<Junction>(FindObjectsSortMode.None);
                foreach (var j in junctions)
                {
                    if (j.junctionId == "J1") camCtrl.targetJ1 = j.transform;
                    else if (j.junctionId == "J2") camCtrl.targetJ2 = j.transform;
                    else if (j.junctionId == "J3") camCtrl.targetJ3 = j.transform;
                }
            }
        }

        // ──────────────────────────────────────────────
        // HUD CANVAS — FULL POLISHED LAYOUT
        // ──────────────────────────────────────────────
        private void EnsureHUDCanvas()
        {
            if (FindFirstObjectByType<HUDController>() != null) return;

            // Canvas
            GameObject canvasObj = new GameObject("NEXUS_HUD_Canvas");
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 10;
            CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = 0.5f;
            canvasObj.AddComponent<GraphicRaycaster>();

            HUDController hud = canvasObj.AddComponent<HUDController>();

            // ── Color Palette ──────────────────────────────────────────────────
            Color panelLight   = new Color(0.96f, 0.97f, 0.98f, 0.97f);
            Color panelDark    = new Color(0.08f, 0.10f, 0.14f, 0.95f);
            Color panelOverlay = new Color(0.04f, 0.06f, 0.09f, 0.92f);
            Color navyText     = new Color(0.06f, 0.08f, 0.12f, 1f);
            Color accentBlue   = new Color(0.10f, 0.53f, 0.82f, 1f);
            Color successGreen = new Color(0.22f, 0.906f, 0.372f, 1f);
            Color warningRed   = new Color(0.85f, 0.25f, 0.18f, 1f);
            Color amberYellow  = new Color(0.95f, 0.72f, 0.15f, 1f);
            Color lightGrey    = new Color(0.75f, 0.78f, 0.82f, 1f);
            Color cardBg       = new Color(0.98f, 0.98f, 0.99f, 1f);

            Font uiFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")
                       ?? Resources.GetBuiltinResource<Font>("Arial.ttf");

            // ══════════════════════════════════════════
            // 1. TOP BAR  (H = 64px)
            // ══════════════════════════════════════════
            GameObject topBar = new GameObject("TopBar");
            topBar.transform.SetParent(canvasObj.transform, false);
            RectTransform tbRect = topBar.AddComponent<RectTransform>();
            tbRect.anchorMin = new Vector2(0, 1);
            tbRect.anchorMax = new Vector2(1, 1);
            tbRect.pivot     = new Vector2(0.5f, 1);
            tbRect.sizeDelta = new Vector2(0, 64);
            tbRect.anchoredPosition = Vector2.zero;
            Image tbBg = topBar.AddComponent<Image>();
            tbBg.color = new Color(0.92f, 0.94f, 0.96f, 0.98f);
            hud.topBarBg  = tbBg;
            hud.topBarRoot = topBar;
            AddAccentBar(topBar, accentBlue, false);   // blue bottom accent

            // Left: NEXUS-TWIN title
            hud.titleText = MakeText(topBar.transform, "TitleText", "NEXUS-TWIN",
                new Vector2(18, -12), new Vector2(160, 36),
                TextAnchor.MiddleLeft, uiFont, 20, accentBlue, FontStyle.Bold);

            // Mission label
            hud.missionText = MakeText(topBar.transform, "MissionText", "MISSION 01: EMERGENCY CORRIDOR",
                new Vector2(185, -12), new Vector2(360, 30),
                TextAnchor.MiddleLeft, uiFont, 12, navyText);

            // Right side: TIME / HEALTH / SCORE / STATE
            hud.timerText = MakeTextRight(topBar.transform, "TimerText", "TIME: 00:00",
                new Vector2(-470, -12), new Vector2(130, 30), uiFont, 12, navyText);

            // Health bar label
            hud.healthText = MakeTextRight(topBar.transform, "HealthText", "HEALTH: 94%",
                new Vector2(-290, -12), new Vector2(120, 30), uiFont, 12, successGreen);

            // Health bar (visual track + fill)
            GameObject hbTrack = MakeRect(topBar.transform, "HealthBarTrack", new Vector2(-290, -42), new Vector2(120, 7));
            Image hbTrackImg = hbTrack.AddComponent<Image>();
            hbTrackImg.color = new Color(0.80f, 0.82f, 0.85f);
            GameObject hbFill = MakeRect(hbTrack.transform, "HealthBarFill", Vector2.zero, Vector2.zero, fullStretch: true);
            Image hbFillImg = hbFill.AddComponent<Image>();
            hbFillImg.color = successGreen;
            RectTransform hbFillRt = hbFill.GetComponent<RectTransform>();
            hbFillRt.anchorMin = new Vector2(0, 0);
            hbFillRt.anchorMax = new Vector2(0.94f, 1);  // start at 94%
            hbFillRt.offsetMin = Vector2.zero;
            hbFillRt.offsetMax = Vector2.zero;
            hud.healthBarFill = hbFillImg;
            hud.healthBarBg   = hbTrackImg;

            // Score
            hud.scoreText = MakeTextRight(topBar.transform, "ScoreText", "SCORE: 0",
                new Vector2(-155, -12), new Vector2(130, 30), uiFont, 12, navyText);

            // State / Mode badge
            hud.stateText = MakeTextRight(topBar.transform, "StateText", "◎ DEMO MODE",
                new Vector2(-18, -12), new Vector2(135, 30), uiFont, 11, accentBlue);

            // Junction indicators (small colored dots)
            float jIndX = -485f;
            hud.j1Indicator = MakeIndicatorDot(topBar.transform, "J1_Dot", new Vector2(jIndX, -45), successGreen);
            hud.j1Label = MakeTextRight(topBar.transform, "J1_Label", "J1",
                new Vector2(jIndX + 16, -37), new Vector2(24, 16), uiFont, 9, successGreen);

            hud.j2Indicator = MakeIndicatorDot(topBar.transform, "J2_Dot", new Vector2(jIndX + 44, -45), amberYellow);
            hud.j2Label = MakeTextRight(topBar.transform, "J2_Label", "J2",
                new Vector2(jIndX + 60, -37), new Vector2(24, 16), uiFont, 9, amberYellow);

            hud.j3Indicator = MakeIndicatorDot(topBar.transform, "J3_Dot", new Vector2(jIndX + 88, -45), successGreen);
            hud.j3Label = MakeTextRight(topBar.transform, "J3_Label", "J3",
                new Vector2(jIndX + 104, -37), new Vector2(24, 16), uiFont, 9, successGreen);

            // ══════════════════════════════════════════
            // 2. MAIN MENU PANEL
            // ══════════════════════════════════════════
            GameObject menuObj = BuildFullscreenPanel(canvasObj.transform, "MainMenuPanel", panelOverlay);
            MainMenuPanel mainMenu = menuObj.AddComponent<MainMenuPanel>();
            mainMenu.panelRoot = menuObj;

            // Decorative top strip
            GameObject menuStrip = MakeRect(menuObj.transform, "MenuTopStrip", new Vector2(0, -80), new Vector2(640, 3));
            menuStrip.AddComponent<Image>().color = accentBlue;

            MakeTextCentered(menuObj.transform, "MenuTitle", "NEXUS-TWIN",
                new Vector2(0, -100), new Vector2(800, 70), uiFont, 46, accentBlue, FontStyle.Bold);
            MakeTextCentered(menuObj.transform, "MenuTagline", "CITY UNDER PRESSURE",
                new Vector2(0, -170), new Vector2(700, 32), uiFont, 18, new Color(0.78f, 0.82f, 0.88f));
            MakeTextCentered(menuObj.transform, "MenuSubtitle", "A Responsible AI Traffic Strategy Game",
                new Vector2(0, -204), new Vector2(700, 25), uiFont, 13, new Color(0.58f, 0.62f, 0.68f));

            // Divider
            GameObject div = MakeRect(menuObj.transform, "MenuDivider", new Vector2(0, -245), new Vector2(300, 1));
            div.AddComponent<Image>().color = new Color(0.3f, 0.35f, 0.45f);

            mainMenu.playButton     = BuildMenuButton(menuObj.transform, "PlayBtn",     "START MISSION",        new Vector2(0, -280), new Vector2(320, 52), accentBlue, uiFont, 14);
            mainMenu.missionsButton = BuildMenuButton(menuObj.transform, "MissionsBtn", "CAMPAIGN MISSIONS",    new Vector2(0, -344), new Vector2(320, 46), panelDark, uiFont, 13);
            mainMenu.settingsButton = BuildMenuButton(menuObj.transform, "SettingsBtn", "SYSTEM SETTINGS",      new Vector2(0, -400), new Vector2(320, 46), panelDark, uiFont, 13);
            mainMenu.exitButton     = BuildMenuButton(menuObj.transform, "ExitBtn",     "EXIT",                 new Vector2(0, -456), new Vector2(320, 46), new Color(0.35f, 0.12f, 0.10f), uiFont, 13);

            MakeTextCentered(menuObj.transform, "MenuFooter", "v2.0  ·  NEXUS-TWIN  ·  Responsible AI Track",
                new Vector2(0, 20), new Vector2(700, 20), uiFont, 10, new Color(0.40f, 0.44f, 0.50f));

            hud.mainMenuPanel = mainMenu;

            // ══════════════════════════════════════════
            // 3. INTRO CINEMATIC OVERLAY
            // ══════════════════════════════════════════
            GameObject cineObj = BuildFullscreenPanel(canvasObj.transform, "IntroCinematicOverlay", new Color(0f, 0f, 0f, 0.96f));
            CanvasGroup cineCg = cineObj.AddComponent<CanvasGroup>();
            IntroCinematicController cineCtrl = cineObj.AddComponent<IntroCinematicController>();
            cineCtrl.cinematicUIRoot = cineObj;
            cineCtrl.fadeCanvasGroup = cineCg;

            // Hacker terminal box
            GameObject hackBox = MakeRectAnchored(cineObj.transform, "HackerTerminalBox",
                new Vector2(0.5f, 0.62f), new Vector2(0.5f, 0.62f), new Vector2(580, 170));
            Image hackBg = hackBox.AddComponent<Image>();
            hackBg.color = new Color(0.02f, 0.03f, 0.05f, 0.97f);
            AddAccentBar(hackBox, warningRed, true);
            // Inner green scan line effect
            MakeRect(hackBox.transform, "ScanLine", new Vector2(0, -80), new Vector2(560, 1))
                .AddComponent<Image>().color = new Color(0.1f, 0.9f, 0.3f, 0.15f);
            cineCtrl.hackerTerminalBox  = hackBox;
            cineCtrl.hackerTerminalText = MakeText(hackBox.transform, "HackText", "",
                new Vector2(16, -16), new Vector2(548, 140),
                TextAnchor.UpperLeft, uiFont, 12, successGreen);

            // Subtitle bar at bottom
            GameObject subBar = MakeRectAnchored(cineObj.transform, "SubtitleBar",
                new Vector2(0, 0), new Vector2(1, 0), new Vector2(0, 90), pivot: new Vector2(0.5f, 0));
            subBar.AddComponent<Image>().color = new Color(0.04f, 0.05f, 0.07f, 0.94f);
            cineCtrl.subtitleText = MakeText(subBar.transform, "SubText", "",
                new Vector2(40, 0), new Vector2(-80, 86),
                TextAnchor.MiddleCenter, uiFont, 15, Color.white,
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));

            cineCtrl.skipButton = BuildButton(cineObj.transform, "SkipBtn", "SKIP  [SPACE]",
                new Vector2(-28, -80), new Vector2(160, 34),
                new Color(0.18f, 0.22f, 0.30f), Color.white,
                new Vector2(1, 1), new Vector2(1, 1), uiFont, 11);
            hud.introCinematic = cineCtrl;
            cineObj.SetActive(false);

            // ══════════════════════════════════════════
            // 4. MISSION BRIEFING PANEL
            // ══════════════════════════════════════════
            GameObject briefObj = MakeRectAnchored(canvasObj.transform, "MissionBriefingPanel",
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(660, 380));
            Image briefBg = briefObj.AddComponent<Image>();
            briefBg.color = panelLight;
            briefObj.AddComponent<CanvasGroup>();  // for pop-in animation
            AddAccentBar(briefObj, accentBlue, true);

            MissionBriefingPanel briefing = briefObj.AddComponent<MissionBriefingPanel>();
            briefing.panelRoot = briefObj;

            // Threat badge image (colored)
            GameObject threatBadge = MakeRect(briefObj.transform, "ThreatBadge", new Vector2(25, -58), new Vector2(300, 22));
            briefing.threatBadgeImage = threatBadge.AddComponent<Image>();
            briefing.threatBadgeImage.color = warningRed;

            briefing.missionTitleText = MakeText(briefObj.transform, "BriefTitle",
                "MISSION 01: CLEAR THE EMERGENCY CORRIDOR",
                new Vector2(25, -22), new Vector2(610, 30),
                TextAnchor.UpperLeft, uiFont, 15, accentBlue, FontStyle.Bold);

            briefing.threatLevelText = MakeText(threatBadge.transform, "ThreatText",
                "⚠  THREAT: CRITICAL — SIGNAL COMPROMISED",
                new Vector2(8, 0), new Vector2(-10, 22),
                TextAnchor.MiddleLeft, uiFont, 10, Color.white,
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));

            briefing.situationText = MakeText(briefObj.transform, "SitText",
                "SITUATION\nDeliberate traffic disruption detected at Junction J2. Signal tampering confirmed. Critical trauma ambulance (AMBULANCE_01) is en route.",
                new Vector2(25, -92), new Vector2(610, 70),
                TextAnchor.UpperLeft, uiFont, 12, navyText);

            briefing.objectiveText = MakeText(briefObj.transform, "ObjText",
                "OBJECTIVE\nDeploy an AI-assisted adaptive traffic intervention. Evaluate Digital Twin counterfactual futures. Prevent gridlock. Secure zero-delay transit for the emergency vehicle.\n\n[SPACE] or [ENTER] to deploy →",
                new Vector2(25, -174), new Vector2(610, 100),
                TextAnchor.UpperLeft, uiFont, 12, navyText);

            briefing.startMissionButton = BuildButton(briefObj.transform, "StartBtn",
                "DEPLOY →  [SPACE]",
                new Vector2(0, 24), new Vector2(280, 50),
                successGreen, Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 14, FontStyle.Bold);

            hud.missionBriefingPanel = briefing;
            briefObj.SetActive(false);

            // ══════════════════════════════════════════
            // 5. AI ALERT PANEL — left column
            // ══════════════════════════════════════════
            GameObject alertObj = MakeRectAnchored(canvasObj.transform, "AIAlertPanel",
                new Vector2(0f, 0.5f), new Vector2(0f, 0.5f), new Vector2(360, 240),
                anchoredPos: new Vector2(18, 50), pivot: new Vector2(0, 0.5f));
            Image alertBg = alertObj.AddComponent<Image>();
            alertBg.color = new Color(0.12f, 0.04f, 0.03f, 0.97f);
            alertObj.AddComponent<CanvasGroup>();
            Image alertAccent = AddAccentBar(alertObj, warningRed, true);

            AIAlertPanel alertPanel = alertObj.AddComponent<AIAlertPanel>();
            alertPanel.panelRoot   = alertObj;
            alertPanel.accentBar   = alertAccent;
            alertPanel.panelBackground = alertBg;

            alertPanel.titleText = MakeText(alertObj.transform, "AlertTitle", "AI ALERT — CONGESTION RISK",
                new Vector2(14, -18), new Vector2(332, 26), TextAnchor.UpperLeft, uiFont, 12, warningRed, FontStyle.Bold);

            alertPanel.junctionText = MakeText(alertObj.transform, "JunctionText", "JUNCTION: J2  ·  CONFIDENCE: 82%",
                new Vector2(14, -50), new Vector2(332, 22), TextAnchor.UpperLeft, uiFont, 11, new Color(0.78f, 0.82f, 0.88f));

            // Giant risk percentage
            alertPanel.probabilityText = MakeText(alertObj.transform, "ProbText", "87%",
                new Vector2(14, -76), new Vector2(120, 52), TextAnchor.UpperLeft, uiFont, 40, warningRed, FontStyle.Bold);

            alertPanel.forecastText = MakeText(alertObj.transform, "ForeText", "Projected congestion in 5 min",
                new Vector2(14, -132), new Vector2(332, 22), TextAnchor.UpperLeft, uiFont, 11, new Color(0.78f, 0.82f, 0.88f));

            // Risk bar track + fill
            GameObject riskTrack = MakeRect(alertObj.transform, "RiskBarTrack", new Vector2(14, -160), new Vector2(332, 8));
            riskTrack.AddComponent<Image>().color = new Color(0.25f, 0.10f, 0.10f);
            GameObject riskFill = MakeRect(riskTrack.transform, "RiskBarFill", Vector2.zero, Vector2.zero);
            Image riskFillImg = riskFill.AddComponent<Image>();
            riskFillImg.color = warningRed;
            RectTransform riskFillRt = riskFill.GetComponent<RectTransform>();
            riskFillRt.anchorMin = new Vector2(0, 0); riskFillRt.anchorMax = new Vector2(0, 1);
            riskFillRt.offsetMin = Vector2.zero; riskFillRt.offsetMax = Vector2.zero;
            alertPanel.riskBarFill = riskFillImg;

            alertPanel.recommendationText = MakeText(alertObj.transform, "RecommText", "ACTION REQUIRED → Select strategy",
                new Vector2(14, -178), new Vector2(332, 22), TextAnchor.UpperLeft, uiFont, 11, new Color(0.95f, 0.72f, 0.15f));

            alertPanel.mockBadgeText = MakeText(alertObj.transform, "BadgeText", "[DEMO MODE]",
                new Vector2(14, -210), new Vector2(332, 20), TextAnchor.UpperLeft, uiFont, 10, accentBlue);

            hud.alertPanel = alertPanel;
            alertObj.SetActive(false);

            // ══════════════════════════════════════════
            // 6. STRATEGY PANEL — right column
            // ══════════════════════════════════════════
            GameObject stratObj = MakeRectAnchored(canvasObj.transform, "StrategyPanel",
                new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(370, 280),
                anchoredPos: new Vector2(-18, 50), pivot: new Vector2(1, 0.5f));
            Image stratBg = stratObj.AddComponent<Image>();
            stratBg.color = new Color(0.08f, 0.10f, 0.14f, 0.97f);
            stratObj.AddComponent<CanvasGroup>();
            AddAccentBar(stratObj, accentBlue, true);

            StrategyPanel strategyPanel = stratObj.AddComponent<StrategyPanel>();
            strategyPanel.panelRoot = stratObj;

            strategyPanel.panelTitleText = MakeText(stratObj.transform, "StratHeader", "INTERVENTION STRATEGY",
                new Vector2(14, -18), new Vector2(342, 24), TextAnchor.UpperLeft, uiFont, 12, accentBlue, FontStyle.Bold);

            GameObject optContainer = new GameObject("OptionsContainer");
            optContainer.transform.SetParent(stratObj.transform, false);
            RectTransform optRect = optContainer.AddComponent<RectTransform>();
            optRect.anchorMin = new Vector2(0, 1); optRect.anchorMax = new Vector2(1, 1);
            optRect.pivot = new Vector2(0.5f, 1);
            optRect.sizeDelta = new Vector2(-28, 160);
            optRect.anchoredPosition = new Vector2(0, -50);
            strategyPanel.optionsContainer = optContainer.transform;

            strategyPanel.selectedStrategyLabel = MakeText(stratObj.transform, "SelectedLabel", "▶  Divert Traffic",
                new Vector2(14, -218), new Vector2(342, 24), TextAnchor.UpperLeft, uiFont, 11, new Color(0.22f, 0.906f, 0.372f));

            // SIMULATE button
            GameObject simBtnObj = new GameObject("SimulateBtn");
            simBtnObj.transform.SetParent(stratObj.transform, false);
            RectTransform simBtnRect = simBtnObj.AddComponent<RectTransform>();
            simBtnRect.anchorMin = new Vector2(0.5f, 0); simBtnRect.anchorMax = new Vector2(0.5f, 0);
            simBtnRect.pivot = new Vector2(0.5f, 0);
            simBtnRect.sizeDelta = new Vector2(280, 44);
            simBtnRect.anchoredPosition = new Vector2(0, 14);
            Image simImg = simBtnObj.AddComponent<Image>();
            simImg.color = accentBlue;
            Button simBtn = simBtnObj.AddComponent<Button>();
            MakeText(simBtnObj.transform, "Label", "◀▶  SIMULATE FUTURES  [S]",
                Vector2.zero, Vector2.zero, TextAnchor.MiddleCenter, uiFont, 12, Color.white, FontStyle.Bold,
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));
            strategyPanel.simulateButton = simBtn;

            hud.strategyPanel = strategyPanel;
            stratObj.SetActive(false);

            // ══════════════════════════════════════════
            // 7. COUNTERFACTUAL CARD PANEL — centered bottom half
            // ══════════════════════════════════════════
            GameObject cardObj = MakeRectAnchored(canvasObj.transform, "CounterfactualPanel",
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(780, 240),
                anchoredPos: new Vector2(0, -50));
            Image cardBgImg = cardObj.AddComponent<Image>();
            cardBgImg.color = new Color(0.10f, 0.12f, 0.16f, 0.97f);
            cardObj.AddComponent<CanvasGroup>();
            AddAccentBar(cardObj, accentBlue, true);

            CounterfactualCardPanel cardPanel = cardObj.AddComponent<CounterfactualCardPanel>();
            cardPanel.panelRoot = cardObj;
            cardPanel.summaryHeader = MakeText(cardObj.transform, "CardHeader", "DIGITAL TWIN — COUNTERFACTUAL FUTURES",
                new Vector2(0, -12), new Vector2(740, 24), TextAnchor.UpperCenter, uiFont, 12, accentBlue, FontStyle.Bold);

            // 4 cards
            float cardW = 170f; float cardH = 175f;
            float[] cardXs = { -282f, -94f, 94f, 282f };
            string[] cardLabels = { "Divert Traffic", "Extend Green", "Emergency Prio", "No Action" };
            Color[] cardColors = { successGreen, new Color(0.75f, 0.78f, 0.82f), new Color(0.75f, 0.78f, 0.82f), new Color(0.85f, 0.25f, 0.18f) };

            var c1 = BuildCounterfactualCard(cardObj.transform, "Card_1", cardLabels[0], "-37.6% delay\n-30.1% queue\n-24s ETA\n-14.2% CO₂",
                new Vector2(cardXs[0], -40), cardW, cardH, cardColors[0], cardBg, uiFont);
            cardPanel.card1Title = c1.title; cardPanel.card1Metrics = c1.metrics; cardPanel.card1Border = c1.border;

            var c2 = BuildCounterfactualCard(cardObj.transform, "Card_2", cardLabels[1], "-12.4% delay\n-18.2% queue\n+4s ETA\n-8.1% CO₂",
                new Vector2(cardXs[1], -40), cardW, cardH, cardColors[1], cardBg, uiFont);
            cardPanel.card2Title = c2.title; cardPanel.card2Metrics = c2.metrics; cardPanel.card2Border = c2.border;

            var c3 = BuildCounterfactualCard(cardObj.transform, "Card_3", cardLabels[2], "+8.0% delay\n+12.0% queue\n-31s ETA\n+5.0% CO₂",
                new Vector2(cardXs[2], -40), cardW, cardH, cardColors[2], cardBg, uiFont);
            cardPanel.card3Title = c3.title; cardPanel.card3Metrics = c3.metrics; cardPanel.card3Border = c3.border;

            var c4 = BuildCounterfactualCard(cardObj.transform, "Card_4", cardLabels[3], "+45.0% delay\n+62.0% queue\n+24s ETA\n+35.0% CO₂",
                new Vector2(cardXs[3], -40), cardW, cardH, cardColors[3], cardBg, uiFont);
            cardPanel.card4Title = c4.title; cardPanel.card4Metrics = c4.metrics; cardPanel.card4Border = c4.border;

            hud.cardPanel = cardPanel;
            cardObj.SetActive(false);

            // ══════════════════════════════════════════
            // 8. EXPLANATION PANEL — bottom strip
            // ══════════════════════════════════════════
            GameObject expObj = MakeRectAnchored(canvasObj.transform, "ExplanationPanel",
                new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(760, 160),
                anchoredPos: new Vector2(0, 26), pivot: new Vector2(0.5f, 0));
            Image expBg = expObj.AddComponent<Image>();
            expBg.color = new Color(0.06f, 0.12f, 0.08f, 0.97f);
            expObj.AddComponent<CanvasGroup>();
            Image expAccent = AddAccentBar(expObj, successGreen, true);

            ExplanationPanel expPanel = expObj.AddComponent<ExplanationPanel>();
            expPanel.panelRoot = expObj;
            expPanel.accentBar = expAccent;

            expPanel.panelHeader = MakeText(expObj.transform, "ExpHeader", "NEXUS-AI  EXPLANATION",
                new Vector2(16, -14), new Vector2(730, 20), TextAnchor.UpperLeft, uiFont, 11, successGreen, FontStyle.Bold);

            expPanel.actionText = MakeText(expObj.transform, "ExpAction", "ACTION",
                new Vector2(16, -40), new Vector2(730, 28), TextAnchor.UpperLeft, uiFont, 11, Color.white);

            expPanel.reasonText = MakeText(expObj.transform, "ExpReason", "WHY",
                new Vector2(16, -72), new Vector2(600, 24), TextAnchor.UpperLeft, uiFont, 11, new Color(0.75f, 0.80f, 0.85f));

            expPanel.evidenceText = MakeText(expObj.transform, "ExpEvidence", "EVIDENCE",
                new Vector2(16, -100), new Vector2(600, 24), TextAnchor.UpperLeft, uiFont, 10, new Color(0.65f, 0.70f, 0.75f));

            // Confidence score + bar
            expPanel.confidenceText = MakeText(expObj.transform, "ExpConf", "CONFIDENCE: 92%",
                new Vector2(16, -128), new Vector2(200, 22), TextAnchor.UpperLeft, uiFont, 11, successGreen, FontStyle.Bold);

            GameObject confTrack = MakeRect(expObj.transform, "ConfBarTrack", new Vector2(230, -131), new Vector2(230, 7));
            confTrack.AddComponent<Image>().color = new Color(0.15f, 0.22f, 0.16f);
            GameObject confFill = MakeRect(confTrack.transform, "ConfBarFill", Vector2.zero, Vector2.zero);
            Image confFillImg = confFill.AddComponent<Image>();
            confFillImg.color = successGreen;
            RectTransform confFillRt = confFill.GetComponent<RectTransform>();
            confFillRt.anchorMin = new Vector2(0, 0); confFillRt.anchorMax = new Vector2(0, 1);
            confFillRt.offsetMin = Vector2.zero; confFillRt.offsetMax = Vector2.zero;
            expPanel.confidenceBarFill = confFillImg;

            hud.explanationPanel = expPanel;
            expObj.SetActive(false);

            // ══════════════════════════════════════════
            // 9. DECISION BUTTONS — bottom right
            // ══════════════════════════════════════════
            GameObject decObj = MakeRectAnchored(canvasObj.transform, "DecisionButtons",
                new Vector2(1, 0), new Vector2(1, 0), new Vector2(240, 130),
                anchoredPos: new Vector2(-18, 26), pivot: new Vector2(1, 0));

            DecisionButtons decButtons = decObj.AddComponent<DecisionButtons>();
            decButtons.panelRoot = decObj;

            decButtons.approveButton = BuildButton(decObj.transform, "ApproveBtn", "✓  APPROVE  [A]",
                new Vector2(0, 72), new Vector2(224, 52), successGreen, Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 13, FontStyle.Bold);

            decButtons.rejectButton = BuildButton(decObj.transform, "RejectBtn", "✕  REJECT  [R]",
                new Vector2(0, 12), new Vector2(224, 50), new Color(0.28f, 0.12f, 0.10f), new Color(1f, 0.5f, 0.4f),
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 13);

            hud.decisionButtons = decButtons;
            decObj.SetActive(false);

            // ══════════════════════════════════════════
            // 10. AI DISAGREEMENT MODAL
            // ══════════════════════════════════════════
            GameObject disagObj = MakeRectAnchored(canvasObj.transform, "AIDisagreementModal",
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(560, 320));
            Image disagBg = disagObj.AddComponent<Image>();
            disagBg.color = new Color(0.12f, 0.10f, 0.04f, 0.98f);
            disagObj.AddComponent<CanvasGroup>();
            AddAccentBar(disagObj, amberYellow, true);

            AIDisagreementModal disagModal = disagObj.AddComponent<AIDisagreementModal>();
            disagModal.modalRoot = disagObj;
            disagModal.headerText = MakeText(disagObj.transform, "DisagHeader", "⚠  AI RECOMMENDATION MISMATCH",
                new Vector2(20, -22), new Vector2(520, 28), TextAnchor.UpperLeft, uiFont, 14, amberYellow, FontStyle.Bold);
            disagModal.playerChoiceText = MakeText(disagObj.transform, "PlayerChoice", "Your Strategy: Emergency Priority",
                new Vector2(20, -62), new Vector2(520, 24), TextAnchor.UpperLeft, uiFont, 12, new Color(0.9f, 0.8f, 0.6f));
            disagModal.aiRecommendationText = MakeText(disagObj.transform, "AIRecom", "AI Recommends: Divert Traffic",
                new Vector2(20, -92), new Vector2(520, 24), TextAnchor.UpperLeft, uiFont, 12, new Color(0.7f, 0.85f, 0.7f));
            disagModal.tradeOffsText = MakeText(disagObj.transform, "TradeOffs", "Trade-off: Your choice adds +8% general delay but saves 31s ambulance ETA. This is a valid Responsible AI override.",
                new Vector2(20, -126), new Vector2(520, 80), TextAnchor.UpperLeft, uiFont, 11, new Color(0.75f, 0.78f, 0.82f));

            disagModal.continueButton = BuildButton(disagObj.transform, "ContBtn", "CONFIRM OVERRIDE  [A]",
                new Vector2(140, 20), new Vector2(220, 44), successGreen, Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 12, FontStyle.Bold);
            disagModal.reconsiderButton = BuildButton(disagObj.transform, "ReconsBtn", "RECONSIDER  [R]",
                new Vector2(-150, 20), new Vector2(200, 44), new Color(0.28f, 0.30f, 0.38f), Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 12);

            hud.disagreementModal = disagModal;
            disagObj.SetActive(false);

            // ══════════════════════════════════════════
            // 11. FAILURE PANEL
            // ══════════════════════════════════════════
            GameObject failObj = MakeRectAnchored(canvasObj.transform, "FailurePanel",
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(580, 340));
            Image failBg = failObj.AddComponent<Image>();
            failBg.color = new Color(0.12f, 0.04f, 0.03f, 0.98f);
            failObj.AddComponent<CanvasGroup>();
            AddAccentBar(failObj, warningRed, true);

            FailurePanel failurePanel = failObj.AddComponent<FailurePanel>();
            failurePanel.panelRoot = failObj;
            failurePanel.failureTitleText = MakeText(failObj.transform, "FailTitle", "MISSION FAILED — NETWORK COLLAPSE",
                new Vector2(22, -22), new Vector2(536, 30), TextAnchor.UpperLeft, uiFont, 16, warningRed, FontStyle.Bold);
            failurePanel.reasonText = MakeText(failObj.transform, "FailReason",
                "Unmitigated traffic congestion resulted in total corridor gridlock. The emergency ambulance could not pass.",
                new Vector2(22, -64), new Vector2(536, 55), TextAnchor.UpperLeft, uiFont, 12, new Color(0.80f, 0.75f, 0.72f));
            failurePanel.metricsText = MakeText(failObj.transform, "FailMetrics", "",
                new Vector2(22, -128), new Vector2(536, 100), TextAnchor.UpperLeft, uiFont, 11, new Color(0.65f, 0.68f, 0.72f));
            failurePanel.tryAgainButton = BuildButton(failObj.transform, "TryAgainBtn", "TRY AGAIN  [SPACE]",
                new Vector2(0, 24), new Vector2(260, 50), warningRed, Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 14, FontStyle.Bold);

            hud.failurePanel = failurePanel;
            failObj.SetActive(false);

            // ══════════════════════════════════════════
            // 12. SCORE DEBRIEF PANEL
            // ══════════════════════════════════════════
            GameObject debriefObj = MakeRectAnchored(canvasObj.transform, "ScoreDebriefPanel",
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(720, 420));
            Image debriefBg = debriefObj.AddComponent<Image>();
            debriefBg.color = panelLight;
            debriefObj.AddComponent<CanvasGroup>();
            AddAccentBar(debriefObj, successGreen, true);

            ScoreDebriefPanel debriefPanel = debriefObj.AddComponent<ScoreDebriefPanel>();
            debriefPanel.panelRoot = debriefObj;
            debriefPanel.titleText = MakeText(debriefObj.transform, "DebriefTitle", "MISSION 01 COMPLETE — CORRIDOR SECURED",
                new Vector2(24, -22), new Vector2(672, 30), TextAnchor.UpperLeft, uiFont, 15, accentBlue, FontStyle.Bold);
            debriefPanel.totalScoreText = MakeText(debriefObj.transform, "TotalScore", "1000 / 1000 PTS",
                new Vector2(24, -60), new Vector2(672, 38), TextAnchor.UpperLeft, uiFont, 22, successGreen, FontStyle.Bold);
            debriefPanel.breakdownText = MakeText(debriefObj.transform, "Breakdown", "",
                new Vector2(24, -106), new Vector2(672, 100), TextAnchor.UpperLeft, uiFont, 12, navyText);
            debriefPanel.comparisonText = MakeText(debriefObj.transform, "Comparison", "",
                new Vector2(24, -214), new Vector2(672, 90), TextAnchor.UpperLeft, uiFont, 11, new Color(0.35f, 0.40f, 0.48f));

            debriefPanel.replayButton = BuildButton(debriefObj.transform, "ReplayBtn", "↺  REPLAY MISSION",
                new Vector2(-180, 24), new Vector2(240, 48), new Color(0.22f, 0.26f, 0.36f), Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 13);
            debriefPanel.nextMissionButton = BuildButton(debriefObj.transform, "NextBtn", "MISSION 02  →",
                new Vector2(180, 24), new Vector2(240, 48), successGreen, Color.white,
                new Vector2(0.5f, 0), new Vector2(0.5f, 0), uiFont, 13, FontStyle.Bold);

            hud.scoreDebriefPanel = debriefPanel;
            debriefObj.SetActive(false);
        }

        // ──────────────────────────────────────────────
        // HELPERS
        // ──────────────────────────────────────────────
        private Image AddAccentBar(GameObject parent, Color color, bool topEdge)
        {
            GameObject bar = new GameObject("AccentBar");
            bar.transform.SetParent(parent.transform, false);
            RectTransform rect = bar.AddComponent<RectTransform>();
            if (topEdge)
            {
                rect.anchorMin = new Vector2(0, 1); rect.anchorMax = new Vector2(1, 1);
                rect.pivot = new Vector2(0.5f, 1);
            }
            else
            {
                rect.anchorMin = new Vector2(0, 0); rect.anchorMax = new Vector2(1, 0);
                rect.pivot = new Vector2(0.5f, 0);
            }
            rect.anchoredPosition = Vector2.zero;
            rect.sizeDelta = new Vector2(0, 4f);
            Image img = bar.AddComponent<Image>();
            img.color = color;
            return img;
        }

        private GameObject BuildFullscreenPanel(Transform parent, string name, Color bgColor)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one;
            rect.offsetMin = Vector2.zero; rect.offsetMax = Vector2.zero;
            obj.AddComponent<Image>().color = bgColor;
            return obj;
        }

        private (Text title, Text metrics, Image border) BuildCounterfactualCard(
            Transform parent, string name, string titleStr, string metricsStr,
            Vector2 pos, float w, float h, Color borderColor, Color innerBg, Font font)
        {
            GameObject card = new GameObject(name);
            card.transform.SetParent(parent, false);
            RectTransform rect = card.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(0.5f, 1); rect.anchorMax = new Vector2(0.5f, 1);
            rect.pivot = new Vector2(0.5f, 1);
            rect.sizeDelta = new Vector2(w, h);
            rect.anchoredPosition = pos;
            card.AddComponent<CanvasGroup>();   // for stagger pop-in

            Image border = card.AddComponent<Image>();
            border.color = borderColor;

            // Inner panel
            GameObject inner = new GameObject("Inner");
            inner.transform.SetParent(card.transform, false);
            RectTransform innerRect = inner.AddComponent<RectTransform>();
            innerRect.anchorMin = Vector2.zero; innerRect.anchorMax = Vector2.one;
            innerRect.offsetMin = new Vector2(3, 3); innerRect.offsetMax = new Vector2(-3, -3);
            inner.AddComponent<Image>().color = new Color(0.10f, 0.12f, 0.16f);

            // Title strip
            GameObject titleStrip = new GameObject("TitleStrip");
            titleStrip.transform.SetParent(inner.transform, false);
            RectTransform tsRect = titleStrip.AddComponent<RectTransform>();
            tsRect.anchorMin = new Vector2(0, 1); tsRect.anchorMax = new Vector2(1, 1);
            tsRect.pivot = new Vector2(0.5f, 1);
            tsRect.sizeDelta = new Vector2(0, 28);
            tsRect.anchoredPosition = Vector2.zero;
            titleStrip.AddComponent<Image>().color = borderColor;

            Text titleText = MakeText(titleStrip.transform, "Title", titleStr,
                new Vector2(0, 0), Vector2.zero, TextAnchor.MiddleCenter, font, 11,
                new Color(0.06f, 0.08f, 0.10f), FontStyle.Bold,
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));

            Text metricsText = MakeText(inner.transform, "Metrics", metricsStr,
                new Vector2(0, -32), new Vector2(-12, -36),
                TextAnchor.UpperCenter, font, 11, new Color(0.80f, 0.84f, 0.88f),
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));

            return (titleText, metricsText, border);
        }

        private Button BuildMenuButton(Transform parent, string name, string label, Vector2 pos, Vector2 size, Color bgColor, Font font, int fontSize)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(0.5f, 1); rect.anchorMax = new Vector2(0.5f, 1);
            rect.pivot = new Vector2(0.5f, 1);
            rect.sizeDelta = size; rect.anchoredPosition = pos;
            obj.AddComponent<Image>().color = bgColor;
            Button btn = obj.AddComponent<Button>();
            // Left accent strip
            GameObject strip = new GameObject("Strip");
            strip.transform.SetParent(obj.transform, false);
            RectTransform stripRt = strip.AddComponent<RectTransform>();
            stripRt.anchorMin = new Vector2(0, 0); stripRt.anchorMax = new Vector2(0, 1);
            stripRt.sizeDelta = new Vector2(4, 0); stripRt.anchoredPosition = Vector2.zero;
            strip.AddComponent<Image>().color = new Color(0.1f, 0.53f, 0.82f);

            MakeText(obj.transform, "Label", label, new Vector2(16, 0), Vector2.zero,
                TextAnchor.MiddleLeft, font, fontSize, Color.white,
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));
            return btn;
        }

        private Button BuildButton(Transform parent, string name, string label, Vector2 pos, Vector2 size,
            Color bgColor, Color textColor, Vector2 minAnchor, Vector2 maxAnchor, Font font, int fontSize, FontStyle style = FontStyle.Normal)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = minAnchor; rect.anchorMax = maxAnchor;
            rect.pivot = new Vector2(0.5f, 0);
            rect.sizeDelta = size; rect.anchoredPosition = pos;
            obj.AddComponent<Image>().color = bgColor;
            Button btn = obj.AddComponent<Button>();
            MakeText(obj.transform, "Label", label, Vector2.zero, Vector2.zero,
                TextAnchor.MiddleCenter, font, fontSize, textColor, style,
                anchorMin: new Vector2(0, 0), anchorMax: new Vector2(1, 1));
            return btn;
        }

        private Image MakeIndicatorDot(Transform parent, string name, Vector2 pos, Color color)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(1, 1); rect.anchorMax = new Vector2(1, 1);
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(10, 10);
            rect.anchoredPosition = pos;
            Image img = obj.AddComponent<Image>();
            img.color = color;
            return img;
        }

        private GameObject MakeRect(Transform parent, string name, Vector2 pos, Vector2 size, bool fullStretch = false)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            if (fullStretch)
            {
                rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one;
                rect.offsetMin = Vector2.zero; rect.offsetMax = Vector2.zero;
            }
            else
            {
                rect.anchorMin = new Vector2(0, 1); rect.anchorMax = new Vector2(0, 1);
                rect.pivot = new Vector2(0, 1);
                rect.anchoredPosition = pos; rect.sizeDelta = size;
            }
            return obj;
        }

        private GameObject MakeRectAnchored(Transform parent, string name,
            Vector2 minA, Vector2 maxA, Vector2 size, Vector2 anchoredPos = default, Vector2 pivot = default)
        {
            if (pivot == default) pivot = new Vector2(0.5f, 0.5f);
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = minA; rect.anchorMax = maxA;
            rect.pivot = pivot;
            rect.sizeDelta = size;
            rect.anchoredPosition = anchoredPos;
            return obj;
        }

        private Text MakeText(Transform parent, string name, string text,
            Vector2 pos, Vector2 size, TextAnchor align, Font font, int fontSize, Color color,
            FontStyle style = FontStyle.Normal, Vector2? anchorMin = null, Vector2? anchorMax = null)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = anchorMin ?? new Vector2(0, 1);
            rect.anchorMax = anchorMax ?? new Vector2(0, 1);
            rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = pos;
            rect.sizeDelta = size;
            Text t = obj.AddComponent<Text>();
            t.text = text; t.font = font; t.fontSize = fontSize;
            t.color = color; t.alignment = align; t.fontStyle = style;
            t.resizeTextForBestFit = false;
            return t;
        }

        private Text MakeTextRight(Transform parent, string name, string text,
            Vector2 pos, Vector2 size, Font font, int fontSize, Color color)
        {
            return MakeText(parent, name, text, pos, size, TextAnchor.MiddleRight, font, fontSize, color,
                anchorMin: new Vector2(1, 1), anchorMax: new Vector2(1, 1));
        }

        private Text MakeTextCentered(Transform parent, string name, string text,
            Vector2 pos, Vector2 size, Font font, int fontSize, Color color, FontStyle style = FontStyle.Normal)
        {
            return MakeText(parent, name, text, pos, size, TextAnchor.UpperCenter, font, fontSize, color, style,
                anchorMin: new Vector2(0.5f, 1), anchorMax: new Vector2(0.5f, 1));
        }
    }
}
