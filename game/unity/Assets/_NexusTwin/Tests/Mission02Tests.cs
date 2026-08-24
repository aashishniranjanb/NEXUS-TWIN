#if UNITY_INCLUDE_TESTS || UNITY_EDITOR
using NUnit.Framework;
using UnityEngine;
using NexusTwin.Core;
using NexusTwin.Data;
using NexusTwin.Gameplay;
using NexusTwin.Scoring;
using NexusTwin.Networking;

namespace NexusTwin.Tests
{
    public class Mission02Tests
    {
        [SetUp]
        public void Setup()
        {
            var gmObj = new GameObject("GameManager");
            var gm = gmObj.AddComponent<GameManager>();
            gm.currentMission = 2;
            gm.useMockData = true;
        }

        [TearDown]
        public void Teardown()
        {
            var gm = Object.FindFirstObjectByType<GameManager>();
            if (gm != null) Object.DestroyImmediate(gm.gameObject);
        }

        [Test]
        public void TestMission02DataMocking()
        {
            var provider = new MockGameDataProvider();
            Assert.AreEqual("STANDALONE DEMO ENGINE", provider.ProviderName);

            provider.FetchAIPrediction("J2", (alert) =>
            {
                Assert.AreEqual(0.78f, alert.probability);
                Assert.AreEqual("J2", alert.junctionId);
            });

            provider.FetchStrategies("J2", (options) =>
            {
                Assert.AreEqual(5, options.Length);
                Assert.AreEqual(StrategyType.DynamicLane, options[0].type);
                Assert.AreEqual(StrategyType.EmergencyPriority, options[1].type);
            });
        }

        [Test]
        public void TestMission02Scoring()
        {
            var scoreObj = new GameObject("ScoreController");
            var scoreCtrl = scoreObj.AddComponent<ScoreController>();

            var score = scoreCtrl.ComputeScore(38.0f, 35.0f, 12.4f, true);
            Assert.AreEqual(300, score.trafficFlow);
            Assert.IsTrue(score.Total > 600);

            Object.DestroyImmediate(scoreObj);
        }
    }
}
#endif
