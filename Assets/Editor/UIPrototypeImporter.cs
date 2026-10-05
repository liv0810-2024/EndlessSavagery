#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

/// <summary>
/// Copies the generated UI prototype pack into Assets so Unity imports it as project content.
/// </summary>
[InitializeOnLoad]
public static class UIPrototypeImporter
{
    private const string SourceFolderName = "UI_Prototype";
    private const string DestinationFolderName = "UI_Prototype";

    static UIPrototypeImporter()
    {
        EditorApplication.delayCall += ImportIfNeeded;
    }

    [MenuItem("Tools/Endless Savagery/Import UI Prototype")]
    public static void ImportFromMenu()
    {
        ImportIfNeeded(true);
    }

    private static void ImportIfNeeded()
    {
        ImportIfNeeded(false);
    }

    private static void ImportIfNeeded(bool showDialog)
    {
        try
        {
            string projectRoot = Directory.GetParent(Application.dataPath).FullName;
            string source = Path.Combine(projectRoot, SourceFolderName);
            string destination = Path.Combine(Application.dataPath, DestinationFolderName);

            if (!Directory.Exists(source))
            {
                if (showDialog)
                {
                    EditorUtility.DisplayDialog("UI Prototype", "找不到项目根目录下的 UI_Prototype 文件夹。", "确定");
                }
                return;
            }

            Directory.CreateDirectory(destination);
            int copied = 0;

            foreach (string sourceFile in Directory.GetFiles(source, "*", SearchOption.AllDirectories))
            {
                if (sourceFile.EndsWith(".meta", StringComparison.OrdinalIgnoreCase))
                    continue;

                string relative = sourceFile.Substring(source.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                string destinationFile = Path.Combine(destination, relative);
                string destinationDirectory = Path.GetDirectoryName(destinationFile);
                if (!string.IsNullOrEmpty(destinationDirectory))
                    Directory.CreateDirectory(destinationDirectory);

                bool shouldCopy = !File.Exists(destinationFile) || File.GetLastWriteTimeUtc(sourceFile) > File.GetLastWriteTimeUtc(destinationFile);
                if (shouldCopy)
                {
                    File.Copy(sourceFile, destinationFile, true);
                    copied++;
                }
            }

            AssetDatabase.Refresh();

            if (showDialog)
            {
                EditorUtility.DisplayDialog("UI Prototype", $"已同步 {copied} 个文件到 Assets/UI_Prototype/。", "确定");
            }
        }
        catch (Exception exception)
        {
            Debug.LogError($"UI Prototype 导入失败: {exception}");
            if (showDialog)
            {
                EditorUtility.DisplayDialog("UI Prototype", "导入失败，请查看 Console 日志。", "确定");
            }
        }
    }
}
#endif
