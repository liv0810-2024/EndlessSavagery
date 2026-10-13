using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MonsterBase : MonoBehaviour
{
    [Header("怪物配置")]
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private float stopDistance = 1.2f;
    
     private Vector3 moveDir;

    public Transform target;

    [Header("动画外观")]
    [SerializeField] private Animator visualAnimator;

    private static readonly int SpeedHash = Animator.StringToHash("Speed");

    private void Awake()
    {
        if (visualAnimator == null)
        {
            visualAnimator = GetComponentInChildren<Animator>(true);
        }
        if (visualAnimator != null)              // ← 独立判断
            visualAnimator.applyRootMotion = false;
        else
        {
             Debug.LogWarning($"[{name}] 没找到 Animator,动画不会播放。");
        }
    }
    private void Start()
    {
        GameObject people = GameObject.FindGameObjectWithTag("Player");
        if (people != null)
        {
            target = people.transform;
        }
        else
        {
            Debug.LogError("忘记给Player设置对应的标签");
        }
    }
    private void Update()
    {
        if (CanAct() && target != null)
        {
            HandleChase();
        }
        else
        {
            moveDir = Vector3.zero;
        }
        UpdateAnimator();
    }

    /// <summary>
    /// 追逐玩家
    /// </summary>
    private void HandleChase()
    {
        Vector3 toTarget = target.position - transform.position;
        toTarget.y = 0f; //只保留水平面上的分量
        if (toTarget.sqrMagnitude <= stopDistance * stopDistance)
        {
            moveDir = Vector3.zero;
            return;
        }
        moveDir = toTarget.normalized;
        Quaternion targetRot = Quaternion.LookRotation(moveDir);
        transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 10f * Time.deltaTime);
        transform.Translate(moveDir * moveSpeed * Time.deltaTime, Space.World);
    }

    /// <summary>
    /// 判断是否能行动
    /// </summary>
    /// <returns></returns>
    private bool CanAct()
    {
        return GameManager.instance.CurrentState == GameState.GamePlaying;
    }

    /// <summary>
    /// 每帧更新怪物动画
    /// </summary>
    private void UpdateAnimator()
    {
        if (visualAnimator == null) return;
        visualAnimator.SetFloat(SpeedHash, moveDir.sqrMagnitude > 0.01f ? 1f : 0f);
    }
}
