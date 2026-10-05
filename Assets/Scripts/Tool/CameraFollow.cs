using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 俯视角相机跟随：保持固定角度，只跟着玩家平移
/// </summary>
public class CameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;   // 跟随目标（把 Player 拖进来）
    [SerializeField] private Vector3 offset = new Vector3(0f, 12f, -8f);   // 相对偏移
    [SerializeField] private float pitch = 55f;  // 俯视角度
    private void Start()
    {
        transform.rotation=Quaternion.Euler(pitch,0f,0f);
    }
    private void LateUpdate()
    {
        if (target != null)
        {
            transform.position=target.position+offset;
        }
    }
}
