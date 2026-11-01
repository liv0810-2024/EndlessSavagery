using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;

public class FloatingTextSpawner : MonoBehaviour
{
    /// <summary>
    /// 伤害预制体
    /// </summary>
    public FloatingText floatingTextPrefab;
   public void Show(string content,Vector3 worldPos,Color color)
    {
        if (floatingTextPrefab == null)
        {
            return;
        }
       FloatingText ft=Instantiate(floatingTextPrefab,worldPos,Quaternion.identity); 
       ft.Init(content,color);
    }
}
