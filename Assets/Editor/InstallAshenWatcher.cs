using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>Attaches the Blender player visual without replacing gameplay components.</summary>
public static class InstallAshenWatcher
{
    private const string ScenePath = "Assets/Scenes/GameScene.scene";
    private const string ModelPath = "Assets/Characters/AshenWatcher/AshenWatcher.fbx";

    [MenuItem("Endless Savagery/Install Ashen Watcher")]
    public static void Install()
    {
        var scene = EditorSceneManager.OpenScene(ScenePath);
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
        if (model == null)
            throw new System.InvalidOperationException("Ashen Watcher FBX has not imported: " + ModelPath);

        var player = GameObject.Find("Player");
        if (player == null)
            throw new System.InvalidOperationException("Player object missing from GameScene.");

        var oldVisual = player.transform.Find("AshenWatcher_Visual");
        if (oldVisual != null)
            Object.DestroyImmediate(oldVisual.gameObject);

        var visual = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
        visual.name = "AshenWatcher_Visual";
        visual.transform.SetParent(player.transform, false);
        // The current Player root is 0.5 m above the ground. The FBX origin is at the feet.
        visual.transform.localPosition = new Vector3(0f, -0.5f, 0f);
        // This FBX arrives Z-up in Tuanjie; rotate it to Unity's Y-up world.
        visual.transform.localRotation = Quaternion.Euler(-90f, 0f, 0f);
        visual.transform.localScale = Vector3.one;

        var cubeRenderer = player.GetComponent<MeshRenderer>();
        if (cubeRenderer != null)
            cubeRenderer.enabled = false;

        var collider = player.GetComponent<BoxCollider>();
        if (collider != null)
        {
            collider.size = new Vector3(0.7f, 2f, 0.7f);
            collider.center = new Vector3(0f, 0.5f, 0f);
        }

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Debug.Log("Ashen Watcher installed under Player in " + ScenePath);
    }

    public static void Validate()
    {
        EditorSceneManager.OpenScene(ScenePath);
        var player = GameObject.Find("Player");
        var visual = player != null ? player.transform.Find("AshenWatcher_Visual") : null;
        if (player == null || visual == null)
            throw new System.InvalidOperationException("Player visual is missing from GameScene.");
        if (player.GetComponent<PlayerController>() == null)
            throw new System.InvalidOperationException("PlayerController is missing after install.");

        var renderers = visual.GetComponentsInChildren<Renderer>();
        if (renderers.Length == 0)
            throw new System.InvalidOperationException("Imported FBX has no renderers.");
        var bounds = renderers[0].bounds;
        var missingMaterials = 0;
        var texturedMaterials = 0;
        foreach (var renderer in renderers)
        {
            bounds.Encapsulate(renderer.bounds);
            foreach (var material in renderer.sharedMaterials)
            {
                if (material == null) missingMaterials++;
                else if (material.mainTexture != null) texturedMaterials++;
            }
        }
        Debug.Log("Ashen Watcher diagnostics. Renderers=" + renderers.Length +
                  ", Bounds=" + bounds + ", VisualScale=" + visual.localScale +
                  ", VisualRotation=" + visual.localRotation.eulerAngles +
                  ", FirstMeshScale=" + renderers[0].transform.lossyScale);
        if (missingMaterials > 0)
            throw new System.InvalidOperationException("Imported FBX has " + missingMaterials + " missing materials.");
        if (bounds.size.y < 1.7f || bounds.size.y > 2.3f)
            throw new System.InvalidOperationException("Unexpected character height: " + bounds.size.y);
        Debug.Log("Ashen Watcher validation passed. Renderers=" + renderers.Length +
                  ", Bounds=" + bounds + ", MaterialsMissing=" + missingMaterials +
                  ", TexturedMaterialSlots=" + texturedMaterials);
    }
}
