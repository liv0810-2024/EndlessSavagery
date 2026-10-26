using System;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

// Offline asset authoring only. Never runs in a player build or edits a scene.
[InitializeOnLoad]
public static class CombatAssetDelivery
{
    const string Request = "ArtSource/Delivery/build.request";
    static Scene workScene;
    static CombatAssetDelivery() { EditorApplication.update += Poll; }
    static void Poll()
    {
        if (!File.Exists(Request) || EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return;
        File.Delete(Request);
        try { Build(); }
        catch(Exception e) { File.WriteAllText("ArtSource/Delivery/build-error.txt", e.ToString()); Debug.LogException(e); }
    }
    static readonly string[] Names = { "WildernessSlime", "ShadowWolf", "StoneGuardian" };
    static string Model(string n) => "Assets/Characters/Monsters/" + n + "/" + n + "_Animated.fbx";
    static void Require(bool ok, string message) { if(!ok) throw new InvalidOperationException(message); }
    static AnimationClip ImportClip(string path, string name, bool loop)
    {
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
        var importer = (ModelImporter)AssetImporter.GetAtPath(path);
        importer.importAnimation = true;
        importer.animationType = ModelImporterAnimationType.Generic;
        importer.animationCompression = ModelImporterAnimationCompression.Off;
        importer.importCameras = false; importer.importLights = false;
        importer.optimizeGameObjects = false;
        var clips = importer.defaultClipAnimations;
        Require(clips.Length == 1, path + " expected exactly one clip, got " + clips.Length);
        clips[0].name = name; clips[0].loopTime = loop;
        clips[0].loopPose = false;
        importer.clipAnimations = clips;
        importer.SaveAndReimport();
        var source = AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().First(c => !c.name.StartsWith("__preview"));
        string output = Path.GetDirectoryName(path).Replace('\\','/') + "/" + name + ".anim";
        var clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(output);
        if(clip == null) { clip = Object.Instantiate(source); AssetDatabase.CreateAsset(clip, output); }
        else EditorUtility.CopySerialized(source, clip);
        clip.name=name;
        var settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = loop;
        AnimationUtility.SetAnimationClipSettings(clip,settings);
        EditorUtility.SetDirty(clip);
        return clip;
    }
    static GameObject Visual(string path, string name)
    {
        var source=AssetDatabase.LoadAssetAtPath<GameObject>(path);
        Require(source != null, "Model missing: " + path);
        var go=(GameObject)PrefabUtility.InstantiatePrefab(source, workScene);
        PrefabUtility.UnpackPrefabInstance(go,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
        go.name=name;
        var animator=go.GetComponent<Animator>();
        if(animator == null) animator=go.AddComponent<Animator>();
        animator.runtimeAnimatorController=null;animator.applyRootMotion=false;
        return go;
    }
    static void Check(GameObject go, AnimationClip clip, StringBuilder report)
    {
        Require(go.GetComponentsInChildren<Renderer>(true).Length>0,go.name+" has no mesh");
        foreach(var t in go.GetComponentsInChildren<Transform>(true))
            Require(GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)==0,"Missing script: "+t.name);
        foreach(var r in go.GetComponentsInChildren<Renderer>(true))
            Require(r.sharedMaterials.All(m=>m!=null && m.shader!=null),"Missing material: "+r.name);
        var bindings=AnimationUtility.GetCurveBindings(clip);
        Require(bindings.Length>0,"No curves: "+clip.name);
        foreach(var b in bindings)
            Require(b.path=="" || go.transform.Find(b.path)!=null,"Unbound animation: "+clip.name+" -> "+b.path);
        var ts=go.GetComponentsInChildren<Transform>(true);
        clip.SampleAnimation(go,0);
        var positions=ts.Select(t=>t.localPosition).ToArray();
        var rotations=ts.Select(t=>t.localRotation).ToArray();
        var scales=ts.Select(t=>t.localScale).ToArray();
        clip.SampleAnimation(go,clip.length*.27f);
        int moving=Enumerable.Range(0,ts.Length).Count(i=>Vector3.Distance(positions[i],ts[i].localPosition)>.0001f || Quaternion.Angle(rotations[i],ts[i].localRotation)>.1f || Vector3.Distance(scales[i],ts[i].localScale)>.0001f);
        Require(moving>0,"Clip does not move model: "+clip.name);
        clip.SampleAnimation(go,clip.length);
        float seam=Enumerable.Range(0,ts.Length).Max(i=>Vector3.Distance(positions[i],ts[i].localPosition)+Quaternion.Angle(rotations[i],ts[i].localRotation)+Vector3.Distance(scales[i],ts[i].localScale));
        Require(seam<.2f,"End pose discontinuity: "+clip.name+" "+seam);
        clip.SampleAnimation(go,0);
        report.AppendLine(go.name+": PASS, renderers="+go.GetComponentsInChildren<Renderer>(true).Length+", curves="+bindings.Length+", animatedNodes="+moving+", duration="+clip.length+", endPoseError="+seam);
    }
    static void Persist(GameObject go, string path, AnimationClip clip, StringBuilder report)
    {
        Check(go,clip,report);
        PrefabUtility.SaveAsPrefabAsset(go,path);
        Object.DestroyImmediate(go);
        var loaded=PrefabUtility.LoadPrefabContents(path);
        try { Check(loaded,clip,report); Require(loaded.GetComponent<Animator>().runtimeAnimatorController==null,"Controller should be unassigned"); }
        finally { PrefabUtility.UnloadPrefabContents(loaded); }
    }
    static void ExtractMaterials(GameObject go, string directory)
    {
        Directory.CreateDirectory(directory);
        foreach(var renderer in go.GetComponentsInChildren<Renderer>())
        {
            var materials=renderer.sharedMaterials;
            for(int i=0;i<materials.Length;i++)
            {
                var source=materials[i];
                Require(source != null,"Missing source material: "+renderer.name);
                string path=directory+"/"+source.name+".mat";
                var material=AssetDatabase.LoadAssetAtPath<Material>(path);
                if(material==null){material=new Material(source);AssetDatabase.CreateAsset(material,path);}
                // FBX imports Blender emission strength directly. Keep small accents
                // readable without clipping to solid neon in the built-in renderer.
                if(material.HasProperty("_EmissionColor"))
                {
                    var emission=material.GetColor("_EmissionColor");
                    var peak=Mathf.Max(emission.r,Mathf.Max(emission.g,emission.b));
                    if(peak>.6f) material.SetColor("_EmissionColor",emission*(.6f/peak));
                }
                EditorUtility.SetDirty(material);
                materials[i]=material;
            }
            renderer.sharedMaterials=materials;
        }
    }
    [MenuItem("Endless Savagery/Assets/Build Combat Delivery")]
    public static void Build()
    {
        workScene=EditorSceneManager.NewPreviewScene();
        try { BuildAssets(); }
        finally { EditorSceneManager.ClosePreviewScene(workScene); }
    }
    static void BuildAssets()
    {
        Directory.CreateDirectory("ArtSource/Delivery");
        Directory.CreateDirectory("Assets/Prefabs/Monsters");
        var report=new StringBuilder("Combat assets: editor import, binding, sampling and prefab reload validation\n");
        foreach(var name in Names)
        {
            var clip=ImportClip(Model(name),name+"_Walk",true);
            var go=Visual(Model(name),name);
            ExtractMaterials(go,"Assets/Characters/Monsters/"+name+"/Materials");
            int layer=LayerMask.NameToLayer("Monster");
            if(layer>=0) foreach(var t in go.GetComponentsInChildren<Transform>(true)) t.gameObject.layer=layer;
            var renderers=go.GetComponentsInChildren<Renderer>();
            var bounds=renderers[0].bounds;
            foreach(var r in renderers) bounds.Encapsulate(r.bounds);
            var collider=go.AddComponent<CapsuleCollider>();
            collider.center=go.transform.InverseTransformPoint(bounds.center);
            collider.radius=Mathf.Min(bounds.extents.x,bounds.extents.z)*.85f;
            collider.height=Mathf.Max(bounds.size.y,collider.radius*2);
            // These are art prefabs. The owner attaches gameplay behaviour separately.
            Persist(go,"Assets/Prefabs/Monsters/"+name+".prefab",clip,report);
        }
        string dashPath="Assets/Characters/AshenWatcher/AshenWatcher_Dash.fbx";
        var dash=ImportClip(dashPath,"AshenWatcher_Dash",false);
        var dashModel=Visual(dashPath,"AshenWatcher_Dash_Review");
        Check(dashModel,dash,report);Object.DestroyImmediate(dashModel);
        var player=Visual("Assets/Characters/AshenWatcher/AshenWatcher_Animated.fbx","ExistingPlayer_DashCompatibility");
        // Both exports use the same skeleton. Verify actual paths on the existing player.
        Check(player,dash,report);Object.DestroyImmediate(player);
        string vfxPath="Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades.fbx";
        var orbit=ImportClip(vfxPath,"PlayerOrbitBlades_Orbit",true);
        var vfx=Visual(vfxPath,"PlayerOrbitBlades");
        Directory.CreateDirectory("Assets/VFX/PlayerOrbitBlades/Materials");
        foreach(var r in vfx.GetComponentsInChildren<Renderer>())
        {
            var mats=r.sharedMaterials;
            for(int i=0;i<mats.Length;i++)
            {
                var source=mats[i];var matName=source.name;
                string p="Assets/VFX/PlayerOrbitBlades/Materials/"+matName+".mat";
                var mat=AssetDatabase.LoadAssetAtPath<Material>(p);
                if(mat==null){mat=new Material(source);AssetDatabase.CreateAsset(mat,p);}
                if(!matName.Contains("Bronze"))
                {
                    var shader=Shader.Find("EndlessSavagery/OrbitGlow");Require(shader!=null,"Orbit glow shader missing");
                    mat.shader=shader;
                    mat.SetColor("_Tint",matName.Contains("Trail")?new Color(.38f,.07f,.9f,.6f):matName.Contains("Edge")?new Color(.85f,.6f,1f,1):new Color(.55f,.15f,1f,1));
                }
                EditorUtility.SetDirty(mat);mats[i]=mat;
            }
            r.sharedMaterials=mats;
        }
        Persist(vfx,"Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades.prefab",orbit,report);
        AssetDatabase.SaveAssets();
        File.WriteAllText("ArtSource/Delivery/validation.txt",report+"ALL_CHECKS_PASSED\n");
        if(File.Exists("ArtSource/Delivery/build-error.txt")) File.Delete("ArtSource/Delivery/build-error.txt");
        Debug.Log("COMBAT_DELIVERY_COMPLETE");
    }
    // Review images use the actual saved prefabs and their Unity materials.
    public static void BuildAndRender()
    {
        Build();
        workScene=EditorSceneManager.NewPreviewScene();
        var originalAmbient=RenderSettings.ambientLight;
        var originalAmbientMode=RenderSettings.ambientMode;
        try
        {
            Directory.CreateDirectory("ArtSource/Delivery/UnityPreviews");
            foreach(var name in Names.Concat(new[]{"AshenWatcher_Dash","PlayerOrbitBlades"}))
            {
                string prefabPath=name=="PlayerOrbitBlades"?"Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades.prefab":"Assets/Prefabs/Monsters/"+name+".prefab";
                var source=AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
                var go=name=="AshenWatcher_Dash"?Visual("Assets/Characters/AshenWatcher/AshenWatcher_Animated.fbx",name):(GameObject)PrefabUtility.InstantiatePrefab(source,workScene);
                string clipPath=name=="AshenWatcher_Dash"?"Assets/Characters/AshenWatcher/AshenWatcher_Dash.anim":name=="PlayerOrbitBlades"?"Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades_Orbit.anim":"Assets/Characters/Monsters/"+name+"/"+name+"_Walk.anim";
                var clip=AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);
                clip.SampleAnimation(go,clip.length*.27f);
                var renderers=go.GetComponentsInChildren<Renderer>();
                var bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);
                var cameraGo=new GameObject("AssetReviewCamera");SceneManager.MoveGameObjectToScene(cameraGo,workScene);
                var camera=cameraGo.AddComponent<Camera>();
                camera.cameraType=CameraType.Preview;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.055f,.065f,.09f);
                camera.orthographic=true;camera.orthographicSize=Mathf.Max(bounds.size.y,Mathf.Max(bounds.size.x,bounds.size.z))*.72f;
                camera.nearClipPlane=.01f;camera.farClipPlane=100;
                camera.transform.position=bounds.center+new Vector3(4,4,6);camera.transform.LookAt(bounds.center);
                camera.scene=workScene;
                RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Flat;
                RenderSettings.ambientLight=new Color(.45f,.45f,.5f);
                var lightGo=new GameObject("AssetReviewLight");SceneManager.MoveGameObjectToScene(lightGo,workScene);
                var light=lightGo.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.35f;light.transform.rotation=Quaternion.Euler(35,-35,0);
                var fillGo=new GameObject("AssetReviewFill");SceneManager.MoveGameObjectToScene(fillGo,workScene);
                var fill=fillGo.AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.7f;fill.color=new Color(.7f,.78f,1f);fill.transform.rotation=Quaternion.Euler(25,150,0);
                var target=new RenderTexture(768,768,24,RenderTextureFormat.ARGB32);
                target.Create();camera.targetTexture=target;camera.Render();
                var previous=RenderTexture.active;RenderTexture.active=target;
                var texture=new Texture2D(768,768,TextureFormat.RGB24,false);texture.ReadPixels(new Rect(0,0,768,768),0,0);texture.Apply();
                File.WriteAllBytes("ArtSource/Delivery/UnityPreviews/"+name+".png",texture.EncodeToPNG());
                RenderTexture.active=previous;camera.targetTexture=null;target.Release();
                Object.DestroyImmediate(target);Object.DestroyImmediate(texture);Object.DestroyImmediate(cameraGo);Object.DestroyImmediate(lightGo);Object.DestroyImmediate(fillGo);Object.DestroyImmediate(go);
            }
            Debug.Log("COMBAT_UNITY_PREVIEWS_COMPLETE");
        }
        finally { RenderSettings.ambientLight=originalAmbient;RenderSettings.ambientMode=originalAmbientMode;EditorSceneManager.ClosePreviewScene(workScene); }
    }
    public static void Inspect()
    {
        var report = new StringBuilder();
        foreach(var p in Names.Select(Model).Concat(new[]{
            "Assets/Characters/AshenWatcher/AshenWatcher_Animated.fbx",
            "Assets/Characters/AshenWatcher/AshenWatcher_Dash.fbx",
            "Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades.fbx"}))
        {
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(p);
            report.AppendLine(p + " loaded=" + (model != null));
            if(model == null) continue;
            foreach(var t in model.GetComponentsInChildren<Transform>(true))
                report.AppendLine("  " + AnimationUtility.CalculateTransformPath(t, model.transform) + " pos=" + t.localPosition + " rot=" + t.localEulerAngles + " scale=" + t.localScale);
            foreach(var clip in AssetDatabase.LoadAllAssetsAtPath(p).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview")))
            {
                report.AppendLine("CLIP " + clip.name + " length=" + clip.length);
                foreach(var b in AnimationUtility.GetCurveBindings(clip).Take(8)) report.AppendLine("  " + b.path + " " + b.propertyName);
            }
        }
        Directory.CreateDirectory("ArtSource/Delivery");
        File.WriteAllText("ArtSource/Delivery/import-inspection.txt", report.ToString());
        Debug.Log("COMBAT_INSPECTION_COMPLETE");
    }
}
