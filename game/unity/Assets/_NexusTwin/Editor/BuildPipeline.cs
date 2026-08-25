using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace NexusTwin.Build
{
    public static class BuildPipeline
    {
        [MenuItem("NEXUS-TWIN/Build Standalone Windows")]
        public static void BuildWindows()
        {
            string[] scenes = new string[]
            {
                "Assets/_NexusTwin/Scenes/Gameplay_J1J2J3.unity"
            };

            string buildDir = "c:/Users/Home/Downloads/PROJECTS/NEXUS-TWIN/build/NEXUS-TWIN_Mission01_Windows";
            if (!Directory.Exists(buildDir))
            {
                Directory.CreateDirectory(buildDir);
            }

            string locationPathName = Path.Combine(buildDir, "NEXUS-TWIN.exe");

            BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = locationPathName,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            };

            Debug.Log($"[BuildPipeline] Starting StandaloneWindows64 build to: {locationPathName}");
            BuildReport report = UnityEditor.BuildPipeline.BuildPlayer(buildPlayerOptions);
            BuildSummary summary = report.summary;

            if (summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"[BuildPipeline] Build SUCCEEDED: {summary.totalSize} bytes, output at {locationPathName}");
            }
            else if (summary.result == BuildResult.Failed)
            {
                Debug.LogError($"[BuildPipeline] Build FAILED with {summary.totalErrors} errors");
            }
        }
    }
}
