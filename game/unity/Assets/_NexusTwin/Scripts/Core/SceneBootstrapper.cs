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
    /// Ensures all singleton systems, world geometry, camera, vehicle pools,
    /// network clients, audio, and all UI panels (MainMenu, Cinematic, Briefing,
    /// Alert, Strategy, Counterfactual, Explanation, Disagreement, Failure, Score)
    /// exist and are seamlessly connected.
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

        private void EnsureCoreManagers()
        {
            if (FindFirstObjectByType<GameManager>() == null)
            {
                GameObject gm = new GameObject("GameManager");
                gm.AddComponent<GameManager>();
            }

            if (FindFirstObjectByType<ApiClient>() == null)
            {
                GameObject api = new GameObject("ApiClient");
                api.AddComponent<ApiClient>();
            }

            if (FindFirstObjectByType<WebSocketClient>() == null)
            {
                GameObject ws = new GameObject("WebSocketClient");
                ws.AddComponent<WebSocketClient>();
            }

            if (FindFirstObjectByType<VehicleManager>() == null)
            {
                GameObject vm = new GameObject("VehicleManager");
                vm.AddComponent<VehicleManager>();
            }

            if (FindFirstObjectByType<IncidentManager>() == null)
            {
                GameObject im = new GameObject("IncidentManager");
                im.AddComponent<IncidentManager>();
            }

            if (FindFirstObjectByType<NexusTwin.Audio.SoundManager>() == null)
            {
                GameObject sm = new GameObject("SoundManager");
                sm.AddComponent<NexusTwin.Audio.SoundManager>();
            }

            if (FindFirstObjectByType<ScoreController>() == null)
            {
                GameObject sc = new GameObject("ScoreController");
                sc.AddComponent<ScoreController>();
            }

            if (FindFirstObjectByType<DigitalTwinSimulationView>() == null)
            {
                GameObject dtv = new GameObject("DigitalTwinSimulationView");
                dtv.AddComponent<DigitalTwinSimulationView>();
            }

            if (FindFirstObjectByType<ScenarioDirector>() == null)
            {
                GameObject sd = new GameObject("ScenarioDirector");
                sd.AddComponent<ScenarioDirector>();
            }

            if (FindFirstObjectByType<SandboxModeController>() == null)
            {
                GameObject smc = new GameObject("SandboxModeController");
                smc.AddComponent<SandboxModeController>();
            }
        }

        private void EnsureWorldAndCamera()
        {
            if (FindFirstObjectByType<WorldScaffold>() == null)
            {
                GameObject scaffoldObj = new GameObject("WorldScaffold");
                scaffoldObj.AddComponent<WorldScaffold>();
            }

            if (FindFirstObjectByType<UrbanEnvironmentGenerator>() == null)
            {
                GameObject urbanObj = new GameObject("UrbanEnvironmentGenerator");
                urbanObj.AddComponent<UrbanEnvironmentGenerator>();
            }

            if (FindFirstObjectByType<TrafficHeatmapOverlay>() == null)
            {
                GameObject heatmapObj = new GameObject("TrafficHeatmapOverlay");
                heatmapObj.AddComponent<TrafficHeatmapOverlay>();
            }

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

        private void EnsureHUDCanvas()
        {
            if (FindFirstObjectByType<HUDController>() != null) return;

            GameObject canvasObj = new GameObject("NEXUS_HUD_Canvas");
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObj.AddComponent<CanvasScaler>();
            canvasObj.AddComponent<GraphicRaycaster>();

            HUDController hud = canvasObj.AddComponent<HUDController>();

            // Palette
            Color lightPanelBg = new Color(0.95f, 0.96f, 0.98f, 0.96f);
            Color darkNavyText = new Color(0.06f, 0.08f, 0.12f, 1f);
            Color accentBlue = new Color(0.1f, 0.53f, 0.82f, 1f);
            Color successGreen = new Color(0.223f, 0.906f, 0.372f, 1f); // #39E75F
            Color warningRed = new Color(0.85f, 0.25f, 0.25f, 1f);
            Color darkOverlayBg = new Color(0.04f, 0.06f, 0.09f, 0.92f);

            // ==========================================
            // 1. TOP BAR
            // ==========================================
            GameObject topBar = new GameObject("TopBar");
            topBar.transform.SetParent(canvasObj.transform, false);
            RectTransform tbRect = topBar.AddComponent<RectTransform>();
            tbRect.anchorMin = new Vector2(0, 1);
            tbRect.anchorMax = new Vector2(1, 1);
            tbRect.pivot = new Vector2(0.5f, 1);
            tbRect.sizeDelta = new Vector2(0, 60);
            tbRect.anchoredPosition = Vector2.zero;

            Image tbBg = topBar.AddComponent<Image>();
            tbBg.color = new Color(0.92f, 0.94f, 0.96f, 0.98f);
            AddAccentBar(topBar, accentBlue, false);
            hud.topBarRoot = topBar;

            hud.titleText = CreateText(topBar.transform, "TitleText", "NEXUS-TWIN", new Vector2(20, -15), new Vector2(140, 30), TextAnchor.MiddleLeft, color: accentBlue);
            hud.missionText = CreateText(topBar.transform, "MissionText", "MISSION 01: EMERGENCY CORRIDOR", new Vector2(170, -15), new Vector2(300, 30), TextAnchor.MiddleLeft, color: darkNavyText);
            hud.timerText = CreateText(topBar.transform, "TimerText", "TIME: 00:00", new Vector2(-420, -15), new Vector2(120, 30), TextAnchor.MiddleRight, new Vector2(1, 1), new Vector2(1, 1), color: darkNavyText);
            hud.healthText = CreateText(topBar.transform, "HealthText", "HEALTH: 94%", new Vector2(-280, -15), new Vector2(130, 30), TextAnchor.MiddleRight, new Vector2(1, 1), new Vector2(1, 1), color: successGreen);
            hud.scoreText = CreateText(topBar.transform, "ScoreText", "SCORE: 0", new Vector2(-150, -15), new Vector2(120, 30), TextAnchor.MiddleRight, new Vector2(1, 1), new Vector2(1, 1), color: darkNavyText);
            hud.stateText = CreateText(topBar.transform, "StateText", "STANDALONE", new Vector2(-20, -15), new Vector2(120, 30), TextAnchor.MiddleRight, new Vector2(1, 1), new Vector2(1, 1), color: accentBlue);

            // ==========================================
            // 2. MAIN MENU PANEL
            // ==========================================
            GameObject menuObj = new GameObject("MainMenuPanel");
            menuObj.transform.SetParent(canvasObj.transform, false);
            RectTransform menuRect = menuObj.AddComponent<RectTransform>();
            menuRect.anchorMin = Vector2.zero;
            menuRect.anchorMax = Vector2.one;
            menuRect.offsetMin = Vector2.zero;
            menuRect.offsetMax = Vector2.zero;

            Image menuBg = menuObj.AddComponent<Image>();
            menuBg.color = darkOverlayBg;

            MainMenuPanel mainMenu = menuObj.AddComponent<MainMenuPanel>();
            mainMenu.panelRoot = menuObj;

            CreateText(menuObj.transform, "MenuTitle", "NEXUS-TWIN", new Vector2(0, -120), new Vector2(800, 60), TextAnchor.MiddleCenter, new Vector2(0.5f, 1), new Vector2(0.5f, 1), color: accentBlue);
            CreateText(menuObj.transform, "MenuSubtitle", "CITY UNDER PRESSURE — A RESPONSIBLE AI STRATEGY GAME", new Vector2(0, -180), new Vector2(800, 30), TextAnchor.MiddleCenter, new Vector2(0.5f, 1), new Vector2(0.5f, 1), color: Color.white);

            mainMenu.playButton = CreateButton(menuObj.transform, "PlayBtn", "START MISSION [PLAY]", new Vector2(0, -260), new Vector2(300, 50), accentBlue, Color.white, new Vector2(0.5f, 1), new Vector2(0.5f, 1));
            mainMenu.missionsButton = CreateButton(menuObj.transform, "MissionsBtn", "CAMPAIGN MISSIONS", new Vector2(0, -325), new Vector2(300, 45), new Color(0.18f, 0.22f, 0.30f), Color.white, new Vector2(0.5f, 1), new Vector2(0.5f, 1));
            mainMenu.settingsButton = CreateButton(menuObj.transform, "SettingsBtn", "SYSTEM SETTINGS", new Vector2(0, -385), new Vector2(300, 45), new Color(0.18f, 0.22f, 0.30f), Color.white, new Vector2(0.5f, 1), new Vector2(0.5f, 1));
            mainMenu.exitButton = CreateButton(menuObj.transform, "ExitBtn", "EXIT SYSTEM", new Vector2(0, -445), new Vector2(300, 45), new Color(0.18f, 0.22f, 0.30f), Color.white, new Vector2(0.5f, 1), new Vector2(0.5f, 1));

            hud.mainMenuPanel = mainMenu;

            // ==========================================
            // 3. INTRO CINEMATIC OVERLAY
            // ==========================================
            GameObject cineObj = new GameObject("IntroCinematicOverlay");
            cineObj.transform.SetParent(canvasObj.transform, false);
            RectTransform cineRect = cineObj.AddComponent<RectTransform>();
            cineRect.anchorMin = Vector2.zero;
            cineRect.anchorMax = Vector2.one;
            cineRect.offsetMin = Vector2.zero;
            cineRect.offsetMax = Vector2.zero;

            CanvasGroup cineCg = cineObj.AddComponent<CanvasGroup>();
            IntroCinematicController cineCtrl = cineObj.AddComponent<IntroCinematicController>();
            cineCtrl.cinematicUIRoot = cineObj;
            cineCtrl.fadeCanvasGroup = cineCg;

            // Hacker Box Terminal
            GameObject hackBox = new GameObject("HackerTerminalBox");
            hackBox.transform.SetParent(cineObj.transform, false);
            RectTransform hackRect = hackBox.AddComponent<RectTransform>();
            hackRect.anchorMin = new Vector2(0.5f, 0.6f);
            hackRect.anchorMax = new Vector2(0.5f, 0.6f);
            hackRect.sizeDelta = new Vector2(550, 160);
            Image hackBg = hackBox.AddComponent<Image>();
            hackBg.color = new Color(0.02f, 0.03f, 0.05f, 0.95f);
            AddAccentBar(hackBox, warningRed, true);
            cineCtrl.hackerTerminalBox = hackBox;
            cineCtrl.hackerTerminalText = CreateText(hackBox.transform, "HackText", "", new Vector2(15, -15), new Vector2(520, 130), TextAnchor.UpperLeft, color: successGreen);

            // Subtitle bottom bar
            GameObject subBar = new GameObject("SubtitleBar");
            subBar.transform.SetParent(cineObj.transform, false);
            RectTransform subRect = subBar.AddComponent<RectTransform>();
            subRect.anchorMin = new Vector2(0, 0);
            subRect.anchorMax = new Vector2(1, 0);
            subRect.pivot = new Vector2(0.5f, 0);
            subRect.sizeDelta = new Vector2(0, 90);
            Image subBg = subBar.AddComponent<Image>();
            subBg.color = new Color(0.04f, 0.05f, 0.07f, 0.92f);
            cineCtrl.subtitleText = CreateText(subBar.transform, "SubText", "", new Vector2(30, 0), new Vector2(-60, 80), TextAnchor.MiddleCenter, new Vector2(0, 0), new Vector2(1, 1), Color.white);

            cineCtrl.skipButton = CreateButton(cineObj.transform, "SkipBtn", "SKIP [ESC / SPACE]", new Vector2(-30, -30), new Vector2(180, 35), accentBlue, Color.white, new Vector2(1, 1), new Vector2(1, 1));
            hud.introCinematic = cineCtrl;
            cineObj.SetActive(false);

            // ==========================================
            // 4. MISSION BRIEFING PANEL
            // ==========================================
            GameObject briefObj = new GameObject("MissionBriefingPanel");
            briefObj.transform.SetParent(canvasObj.transform, false);
            RectTransform briefRect = briefObj.AddComponent<RectTransform>();
            briefRect.anchorMin = new Vector2(0.5f, 0.5f);
            briefRect.anchorMax = new Vector2(0.5f, 0.5f);
            briefRect.sizeDelta = new Vector2(620, 340);
            Image briefBg = briefObj.AddComponent<Image>();
            briefBg.color = lightPanelBg;
            AddAccentBar(briefObj, accentBlue, true);

            MissionBriefingPanel briefing = briefObj.AddComponent<MissionBriefingPanel>();
            briefing.panelRoot = briefObj;
            briefing.missionTitleText = CreateText(briefObj.transform, "BriefTitle", "MISSION 01: CLEAR THE EMERGENCY CORRIDOR", new Vector2(25, -25), new Vector2(570, 35), TextAnchor.UpperLeft, color: accentBlue);
            briefing.threatLevelText = CreateText(briefObj.transform, "ThreatText", "THREAT LEVEL: <color=#D94040>CRITICAL (BOTTLENECK DETECTED)</color>", new Vector2(25, -65), new Vector2(570, 25), TextAnchor.UpperLeft, color: darkNavyText);
            briefing.situationText = CreateText(briefObj.transform, "SitText", "<b>SITUATION:</b>\nDeliberate traffic disruption and signal tampering identified at Junction J2. A critical trauma ambulance (AMBULANCE_01) is en route to the hospital through the main corridor.", new Vector2(25, -100), new Vector2(570, 60), TextAnchor.UpperLeft, color: darkNavyText);
            briefing.objectiveText = CreateText(briefObj.transform, "ObjText", "<b>OBJECTIVE:</b>\nUtilize the NEXUS AI and Counterfactual Digital Twin to deploy an adaptive traffic intervention. Prevent gridlock and secure zero-delay transit for the emergency ambulance.", new Vector2(25, -170), new Vector2(570, 60), TextAnchor.UpperLeft, color: darkNavyText);
            briefing.startMissionButton = CreateButton(briefObj.transform, "StartBtn", "START MISSION [SPACE]", new Vector2(0, 20), new Vector2(260, 45), successGreen, Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            hud.missionBriefingPanel = briefing;
            briefObj.SetActive(false);

            // ==========================================
            // 5. AI ALERT PANEL
            // ==========================================
            GameObject alertObj = new GameObject("AIAlertPanel");
            alertObj.transform.SetParent(canvasObj.transform, false);
            RectTransform alertRect = alertObj.AddComponent<RectTransform>();
            alertRect.anchorMin = new Vector2(0, 0.5f);
            alertRect.anchorMax = new Vector2(0, 0.5f);
            alertRect.pivot = new Vector2(0, 0.5f);
            alertRect.sizeDelta = new Vector2(340, 200);
            alertRect.anchoredPosition = new Vector2(20, 50);
            Image alertBg = alertObj.AddComponent<Image>();
            alertBg.color = new Color(0.98f, 0.93f, 0.93f, 0.96f);
            AddAccentBar(alertObj, warningRed, true);

            AIAlertPanel alertPanel = alertObj.AddComponent<AIAlertPanel>();
            alertPanel.panelRoot = alertObj;
            alertPanel.titleText = CreateText(alertObj.transform, "AlertTitle", "AI CONGESTION ALERT", new Vector2(15, -20), new Vector2(310, 30), TextAnchor.UpperLeft, color: warningRed);
            alertPanel.junctionText = CreateText(alertObj.transform, "JunctionText", "JUNCTION: J2", new Vector2(15, -55), new Vector2(310, 25), TextAnchor.UpperLeft, color: darkNavyText);
            alertPanel.probabilityText = CreateText(alertObj.transform, "ProbText", "RISK: 87%", new Vector2(15, -85), new Vector2(310, 25), TextAnchor.UpperLeft, color: darkNavyText);
            alertPanel.forecastText = CreateText(alertObj.transform, "ForeText", "FORECAST: 5 MIN", new Vector2(15, -115), new Vector2(310, 25), TextAnchor.UpperLeft, color: darkNavyText);
            alertPanel.mockBadgeText = CreateText(alertObj.transform, "BadgeText", "[DEMO MODE]", new Vector2(15, -150), new Vector2(310, 25), TextAnchor.UpperLeft, color: accentBlue);
            hud.alertPanel = alertPanel;
            alertObj.SetActive(false);

            // ==========================================
            // 6. STRATEGY PANEL
            // ==========================================
            GameObject stratObj = new GameObject("StrategyPanel");
            stratObj.transform.SetParent(canvasObj.transform, false);
            RectTransform stratRect = stratObj.AddComponent<RectTransform>();
            stratRect.anchorMin = new Vector2(1, 0.5f);
            stratRect.anchorMax = new Vector2(1, 0.5f);
            stratRect.pivot = new Vector2(1, 0.5f);
            stratRect.sizeDelta = new Vector2(340, 260);
            stratRect.anchoredPosition = new Vector2(-20, 50);
            Image stratBg = stratObj.AddComponent<Image>();
            stratBg.color = lightPanelBg;
            AddAccentBar(stratObj, accentBlue, true);

            StrategyPanel strategyPanel = stratObj.AddComponent<StrategyPanel>();
            strategyPanel.panelRoot = stratObj;
            CreateText(stratObj.transform, "StratHeader", "DECISION CONSOLE", new Vector2(15, -20), new Vector2(310, 30), TextAnchor.UpperLeft, color: accentBlue);

            GameObject optContainer = new GameObject("OptionsContainer");
            optContainer.transform.SetParent(stratObj.transform, false);
            RectTransform optRect = optContainer.AddComponent<RectTransform>();
            optRect.anchorMin = new Vector2(0, 1);
            optRect.anchorMax = new Vector2(1, 1);
            optRect.pivot = new Vector2(0.5f, 1);
            optRect.sizeDelta = new Vector2(-30, 100);
            optRect.anchoredPosition = new Vector2(0, -55);
            strategyPanel.optionsContainer = optContainer.transform;

            strategyPanel.selectedStrategyLabel = CreateText(stratObj.transform, "SelectedStratLabel", "Selected: Divert Traffic", new Vector2(15, -165), new Vector2(310, 30), TextAnchor.UpperLeft, color: darkNavyText);

            GameObject simBtnObj = new GameObject("SimulateBtn");
            simBtnObj.transform.SetParent(stratObj.transform, false);
            RectTransform simBtnRect = simBtnObj.AddComponent<RectTransform>();
            simBtnRect.anchorMin = new Vector2(0.5f, 0);
            simBtnRect.anchorMax = new Vector2(0.5f, 0);
            simBtnRect.pivot = new Vector2(0.5f, 0);
            simBtnRect.sizeDelta = new Vector2(240, 40);
            simBtnRect.anchoredPosition = new Vector2(0, 15);
            Image simImg = simBtnObj.AddComponent<Image>();
            simImg.color = accentBlue;
            Button simBtn = simBtnObj.AddComponent<Button>();
            CreateText(simBtnObj.transform, "Label", "SIMULATE FUTURES [S]", Vector2.zero, new Vector2(240, 40), TextAnchor.MiddleCenter, new Vector2(0, 0), new Vector2(1, 1), Color.white);
            strategyPanel.simulateButton = simBtn;

            hud.strategyPanel = strategyPanel;
            stratObj.SetActive(false);

            // ==========================================
            // 7. COUNTERFACTUAL CARD PANEL
            // ==========================================
            GameObject cardObj = new GameObject("CounterfactualPanel");
            cardObj.transform.SetParent(canvasObj.transform, false);
            RectTransform cardRect = cardObj.AddComponent<RectTransform>();
            cardRect.anchorMin = new Vector2(0.5f, 0.5f);
            cardRect.anchorMax = new Vector2(0.5f, 0.5f);
            cardRect.pivot = new Vector2(0.5f, 0.5f);
            cardRect.sizeDelta = new Vector2(700, 220);
            cardRect.anchoredPosition = new Vector2(0, -60);
            Image cardBg = cardObj.AddComponent<Image>();
            cardBg.color = lightPanelBg;
            AddAccentBar(cardObj, accentBlue, true);

            CounterfactualCardPanel cardPanel = cardObj.AddComponent<CounterfactualCardPanel>();
            cardPanel.panelRoot = cardObj;
            cardPanel.summaryHeader = CreateText(cardObj.transform, "CardHeader", "COUNTERFACTUAL FUTURES", new Vector2(0, -15), new Vector2(660, 30), TextAnchor.UpperCenter, color: accentBlue);

            var c1 = CreateCard(cardObj.transform, "Card_1", "Future A: Divert", "Delay: -32.5%\nQueue: -28m", new Vector2(-240, -35), cardPanel.defaultBorderColor);
            cardPanel.card1Title = c1.title;
            cardPanel.card1Metrics = c1.metrics;
            cardPanel.card1Border = c1.border;

            var c2 = CreateCard(cardObj.transform, "Card_2", "Future B: Extend Green", "Delay: -18.0%\nQueue: -15m", new Vector2(-80, -35), cardPanel.defaultBorderColor);
            cardPanel.card2Title = c2.title;
            cardPanel.card2Metrics = c2.metrics;
            cardPanel.card2Border = c2.border;

            var c3 = CreateCard(cardObj.transform, "Card_3", "Future C: Dynamic Lane", "Delay: -6.5%\nQueue: -4m", new Vector2(80, -35), cardPanel.defaultBorderColor);
            cardPanel.card3Title = c3.title;
            cardPanel.card3Metrics = c3.metrics;
            cardPanel.card3Border = c3.border;

            var c4 = CreateCard(cardObj.transform, "Card_4", "Future D: No Action", "Delay: +45.0%\nQueue: +62m", new Vector2(240, -35), cardPanel.defaultBorderColor);
            cardPanel.card4Title = c4.title;
            cardPanel.card4Metrics = c4.metrics;
            cardPanel.card4Border = c4.border;

            hud.cardPanel = cardPanel;
            cardObj.SetActive(false);

            // ==========================================
            // 8. EXPLANATION PANEL
            // ==========================================
            GameObject expObj = new GameObject("ExplanationPanel");
            expObj.transform.SetParent(canvasObj.transform, false);
            RectTransform expRect = expObj.AddComponent<RectTransform>();
            expRect.anchorMin = new Vector2(0.5f, 0);
            expRect.anchorMax = new Vector2(0.5f, 0);
            expRect.pivot = new Vector2(0.5f, 0);
            expRect.sizeDelta = new Vector2(650, 140);
            expRect.anchoredPosition = new Vector2(0, 30);
            Image expBg = expObj.AddComponent<Image>();
            expBg.color = new Color(0.93f, 0.97f, 0.94f, 0.96f);
            AddAccentBar(expObj, successGreen, true);

            ExplanationPanel expPanel = expObj.AddComponent<ExplanationPanel>();
            expPanel.panelRoot = expObj;
            expPanel.actionText = CreateText(expObj.transform, "ExpAction", "ACTION: Divert Traffic via Cross Street East/West", new Vector2(15, -15), new Vector2(620, 25), TextAnchor.UpperLeft, color: darkNavyText);
            expPanel.reasonText = CreateText(expObj.transform, "ExpReason", "WHY: Prevents gridlock and guarantees ambulance route.", new Vector2(15, -45), new Vector2(620, 35), TextAnchor.UpperLeft, color: darkNavyText);
            expPanel.evidenceText = CreateText(expObj.transform, "ExpEvidence", "EVIDENCE: 87% bottleneck risk confirmed by XGBoost.", new Vector2(15, -80), new Vector2(620, 25), TextAnchor.UpperLeft, color: darkNavyText);
            expPanel.confidenceText = CreateText(expObj.transform, "ExpConf", "CONFIDENCE: 92%", new Vector2(15, -105), new Vector2(620, 25), TextAnchor.UpperLeft, color: successGreen);
            hud.explanationPanel = expPanel;
            expObj.SetActive(false);

            // ==========================================
            // 9. DECISION BUTTONS
            // ==========================================
            GameObject decObj = new GameObject("DecisionButtons");
            decObj.transform.SetParent(canvasObj.transform, false);
            RectTransform decRect = decObj.AddComponent<RectTransform>();
            decRect.anchorMin = new Vector2(1, 0);
            decRect.anchorMax = new Vector2(1, 0);
            decRect.pivot = new Vector2(1, 0);
            decRect.sizeDelta = new Vector2(220, 120);
            decRect.anchoredPosition = new Vector2(-20, 30);

            DecisionButtons decButtons = decObj.AddComponent<DecisionButtons>();
            decButtons.panelRoot = decObj;
            decButtons.approveButton = CreateButton(decObj.transform, "ApproveBtn", "APPROVE [A]", new Vector2(0, 60), new Vector2(200, 45), successGreen, Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            decButtons.rejectButton = CreateButton(decObj.transform, "RejectBtn", "REJECT [R]", new Vector2(0, 5), new Vector2(200, 45), warningRed, Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            hud.decisionButtons = decButtons;
            decObj.SetActive(false);

            // ==========================================
            // 10. AI DISAGREEMENT MODAL
            // ==========================================
            GameObject disagObj = new GameObject("AIDisagreementModal");
            disagObj.transform.SetParent(canvasObj.transform, false);
            RectTransform disagRect = disagObj.AddComponent<RectTransform>();
            disagRect.anchorMin = new Vector2(0.5f, 0.5f);
            disagRect.anchorMax = new Vector2(0.5f, 0.5f);
            disagRect.sizeDelta = new Vector2(520, 280);
            Image disagBg = disagObj.AddComponent<Image>();
            disagBg.color = new Color(0.99f, 0.97f, 0.92f, 0.98f);
            AddAccentBar(disagObj, new Color(0.95f, 0.65f, 0.1f), true);

            AIDisagreementModal disagModal = disagObj.AddComponent<AIDisagreementModal>();
            disagModal.modalRoot = disagObj;
            disagModal.headerText = CreateText(disagObj.transform, "DisagHeader", "⚠ AI RECOMMENDATION DISAGREEMENT", new Vector2(20, -20), new Vector2(480, 30), TextAnchor.UpperLeft, color: new Color(0.85f, 0.45f, 0.05f));
            disagModal.playerChoiceText = CreateText(disagObj.transform, "PlayerChoice", "Your Strategy: Emergency Priority", new Vector2(20, -55), new Vector2(480, 25), TextAnchor.UpperLeft, color: darkNavyText);
            disagModal.aiRecommendationText = CreateText(disagObj.transform, "AIRecom", "AI Recommended: Divert Traffic", new Vector2(20, -80), new Vector2(480, 25), TextAnchor.UpperLeft, color: darkNavyText);
            disagModal.tradeOffsText = CreateText(disagObj.transform, "TradeOffs", "Trade-off analysis details...", new Vector2(20, -110), new Vector2(480, 80), TextAnchor.UpperLeft, color: darkNavyText);

            disagModal.continueButton = CreateButton(disagObj.transform, "ContBtn", "CONTINUE [APPROVE]", new Vector2(140, 20), new Vector2(200, 40), successGreen, Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            disagModal.reconsiderButton = CreateButton(disagObj.transform, "ReconsBtn", "RECONSIDER", new Vector2(-140, 20), new Vector2(180, 40), new Color(0.4f, 0.45f, 0.55f), Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            hud.disagreementModal = disagModal;
            disagObj.SetActive(false);

            // ==========================================
            // 11. MISSION FAILURE PANEL
            // ==========================================
            GameObject failObj = new GameObject("FailurePanel");
            failObj.transform.SetParent(canvasObj.transform, false);
            RectTransform failRect = failObj.AddComponent<RectTransform>();
            failRect.anchorMin = new Vector2(0.5f, 0.5f);
            failRect.anchorMax = new Vector2(0.5f, 0.5f);
            failRect.sizeDelta = new Vector2(550, 300);
            Image failBg = failObj.AddComponent<Image>();
            failBg.color = new Color(0.98f, 0.93f, 0.93f, 0.98f);
            AddAccentBar(failObj, warningRed, true);

            FailurePanel failurePanel = failObj.AddComponent<FailurePanel>();
            failurePanel.panelRoot = failObj;
            failurePanel.failureTitleText = CreateText(failObj.transform, "FailTitle", "MISSION FAILED — NETWORK COLLAPSE", new Vector2(20, -20), new Vector2(510, 35), TextAnchor.UpperLeft, color: warningRed);
            failurePanel.reasonText = CreateText(failObj.transform, "FailReason", "Unmitigated traffic congestion resulted in total corridor gridlock.", new Vector2(20, -65), new Vector2(510, 60), TextAnchor.UpperLeft, color: darkNavyText);
            failurePanel.metricsText = CreateText(failObj.transform, "FailMetrics", "Final metrics summary...", new Vector2(20, -135), new Vector2(510, 70), TextAnchor.UpperLeft, color: darkNavyText);
            failurePanel.tryAgainButton = CreateButton(failObj.transform, "TryAgainBtn", "TRY AGAIN [SPACE]", new Vector2(0, 20), new Vector2(240, 45), warningRed, Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            hud.failurePanel = failurePanel;
            failObj.SetActive(false);

            // ==========================================
            // 12. SCORE DEBRIEF PANEL
            // ==========================================
            GameObject debriefObj = new GameObject("ScoreDebriefPanel");
            debriefObj.transform.SetParent(canvasObj.transform, false);
            RectTransform debriefRect = debriefObj.AddComponent<RectTransform>();
            debriefRect.anchorMin = new Vector2(0.5f, 0.5f);
            debriefRect.anchorMax = new Vector2(0.5f, 0.5f);
            debriefRect.sizeDelta = new Vector2(680, 380);
            Image debriefBg = debriefObj.AddComponent<Image>();
            debriefBg.color = lightPanelBg;
            AddAccentBar(debriefObj, successGreen, true);

            ScoreDebriefPanel debriefPanel = debriefObj.AddComponent<ScoreDebriefPanel>();
            debriefPanel.panelRoot = debriefObj;
            debriefPanel.titleText = CreateText(debriefObj.transform, "DebriefTitle", "MISSION 01 COMPLETE — CORRIDOR SECURED", new Vector2(25, -20), new Vector2(630, 35), TextAnchor.UpperLeft, color: accentBlue);
            debriefPanel.totalScoreText = CreateText(debriefObj.transform, "TotalScore", "1000 / 1000 PTS", new Vector2(25, -60), new Vector2(630, 35), TextAnchor.UpperLeft, color: successGreen);
            debriefPanel.breakdownText = CreateText(debriefObj.transform, "Breakdown", "Score breakdown...", new Vector2(25, -100), new Vector2(630, 90), TextAnchor.UpperLeft, color: darkNavyText);
            debriefPanel.comparisonText = CreateText(debriefObj.transform, "Comparison", "Corridor impact summary...", new Vector2(25, -195), new Vector2(630, 80), TextAnchor.UpperLeft, color: darkNavyText);

            debriefPanel.replayButton = CreateButton(debriefObj.transform, "ReplayBtn", "REPLAY MISSION", new Vector2(-150, 20), new Vector2(220, 45), new Color(0.2f, 0.25f, 0.35f), Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            debriefPanel.nextMissionButton = CreateButton(debriefObj.transform, "NextBtn", "MISSION 02 (THE HEIST)", new Vector2(150, 20), new Vector2(240, 45), successGreen, Color.white, new Vector2(0.5f, 0), new Vector2(0.5f, 0));
            hud.scoreDebriefPanel = debriefPanel;
            debriefObj.SetActive(false);
        }

        private void AddAccentBar(GameObject parentPanel, Color accentColor, bool topEdge)
        {
            GameObject bar = new GameObject("AccentBar");
            bar.transform.SetParent(parentPanel.transform, false);
            RectTransform rect = bar.AddComponent<RectTransform>();
            if (topEdge)
            {
                rect.anchorMin = new Vector2(0, 1);
                rect.anchorMax = new Vector2(1, 1);
                rect.pivot = new Vector2(0.5f, 1);
                rect.anchoredPosition = Vector2.zero;
            }
            else
            {
                rect.anchorMin = new Vector2(0, 0);
                rect.anchorMax = new Vector2(1, 0);
                rect.pivot = new Vector2(0.5f, 0);
                rect.anchoredPosition = Vector2.zero;
            }
            rect.sizeDelta = new Vector2(0, 4f);
            Image img = bar.AddComponent<Image>();
            img.color = accentColor;
        }

        private Text CreateText(Transform parent, string name, string text, Vector2 pos, Vector2 size, TextAnchor align, Vector2? minAnchor = null, Vector2? maxAnchor = null, Color? color = null)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = minAnchor ?? new Vector2(0, 1);
            rect.anchorMax = maxAnchor ?? new Vector2(0, 1);
            rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = pos;
            rect.sizeDelta = size;

            Text t = obj.AddComponent<Text>();
            t.text = text;
            t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf") ?? Resources.GetBuiltinResource<Font>("Arial.ttf");
            t.fontSize = 14;
            t.color = color ?? new Color(0.06f, 0.08f, 0.12f, 1f);
            t.alignment = align;
            return t;
        }

        private Button CreateButton(Transform parent, string name, string label, Vector2 pos, Vector2 size, Color bgColor, Color? textColor = null, Vector2? minAnchor = null, Vector2? maxAnchor = null)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.anchorMin = minAnchor ?? new Vector2(0.5f, 0);
            rect.anchorMax = maxAnchor ?? new Vector2(0.5f, 0);
            rect.pivot = new Vector2(0.5f, 0);
            rect.anchoredPosition = pos;
            rect.sizeDelta = size;

            Image img = obj.AddComponent<Image>();
            img.color = bgColor;

            Button btn = obj.AddComponent<Button>();
            CreateText(obj.transform, "Label", label, Vector2.zero, size, TextAnchor.MiddleCenter, new Vector2(0, 0), new Vector2(1, 1), textColor ?? Color.white);
            return btn;
        }

        private (Text title, Text metrics, Image border) CreateCard(Transform parent, string name, string defaultTitle, string defaultMetrics, Vector2 pos, Color defaultBorderColor)
        {
            GameObject card = new GameObject(name);
            card.transform.SetParent(parent, false);
            RectTransform rect = card.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(0.5f, 0.5f);
            rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(150, 130);
            rect.anchoredPosition = pos;

            Image bg = card.AddComponent<Image>();
            bg.color = defaultBorderColor;

            GameObject inner = new GameObject("Inner");
            inner.transform.SetParent(card.transform, false);
            RectTransform innerRect = inner.AddComponent<RectTransform>();
            innerRect.anchorMin = Vector2.zero;
            innerRect.anchorMax = Vector2.one;
            innerRect.offsetMin = new Vector2(2, 2);
            innerRect.offsetMax = new Vector2(-2, -2);
            Image innerBg = inner.AddComponent<Image>();
            innerBg.color = new Color(0.98f, 0.98f, 0.99f, 1f);

            Text titleText = CreateText(inner.transform, "Title", defaultTitle, new Vector2(0, -5), new Vector2(146, 25), TextAnchor.UpperCenter, new Vector2(0, 0), new Vector2(1, 1), new Color(0.06f, 0.08f, 0.12f, 1f));
            Text metricsText = CreateText(inner.transform, "Metrics", defaultMetrics, new Vector2(0, -35), new Vector2(146, 90), TextAnchor.UpperCenter, new Vector2(0, 0), new Vector2(1, 1), new Color(0.06f, 0.08f, 0.12f, 1f));

            return (titleText, metricsText, bg);
        }
    }
}
