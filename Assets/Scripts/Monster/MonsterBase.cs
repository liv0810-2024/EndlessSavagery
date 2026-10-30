using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MonsterBase : MonoBehaviour
{
    [Header("怪物配置")]
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private float stopDistance = 1.2f;

    [Header("攻击玩家")]
    [SerializeField]private float attackDamage=10f;
    [SerializeField]private float attackInterval=1.5f;
    [SerializeField]private float attackDistance=1.5f;
    private float attackTimer; //攻击用的计时器
   

    //HideInInspector:让一个变量在 Inspector 面板中隐藏，但依然会被 Unity 序列化（即数据会被保存和加载）
    [HideInInspector]public GameObject prefabSource;
    public static int AliveCount{get;private set;}
    
     private Vector3 moveDir;

    public Transform target;

    [Header("动画外观")]
    [SerializeField] private Animator visualAnimator;

    [Header("战斗信息")]
    [SerializeField]private float maxHp=30f;
    /// <summary>
    /// 当前血量
    /// </summary>
    private float hp;
     private float hpMultiplier=1f; //血量倍率

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
            HandleAttack();
        }
        else
        {
            moveDir = Vector3.zero;
        }
        UpdateAnimator();
    }

    private void OnEnable()
    {
        hp=maxHp*hpMultiplier;
        EventCenter.instance.AddEventListener(GameEvent.PlayerAttack,OnPlayerAttack);
        AliveCount++;
    }

    private void OnDisable()
    {
        EventCenter.instance.RemoveEventListener(GameEvent.PlayerAttack,OnPlayerAttack);
        AliveCount--;
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

    /// <summary>
    /// 收到玩家攻击事件：只有【自己在命中名单里】才掉血
    /// </summary>
    /// <param name="param"></param>
    private void OnPlayerAttack(object param)
    {
        PlayerAttackData data=param as PlayerAttackData;
        if(data==null)return;
        foreach(Collider hit in data.hits)
        {
            if(hit==null)continue;
            if(hit.gameObject!=gameObject)continue; //怪物判断如果打的不是我跳过
            TakeDamage(data.damage);
            return; //一次攻击只减一次血
        }
    }

    /// <summary>
    /// 扣血
    /// </summary>
    /// <param name="damage"></param>
    private void TakeDamage(float damage)
    {
        hp-=damage;
        if (hp <= 0)
        {
            Die();
        }
    }

    /// <summary>
/// 设置血量倍率（由刷怪器在生成时调用）
/// </summary>
public void SetHpMultiplier(float multiplier)
{
    hpMultiplier = Mathf.Max(1f, multiplier);   // 倍率不能小于 1
    hp = maxHp * hpMultiplier;                  // 立刻按新倍率回满血
}

    /// <summary>
    /// 死亡
    /// </summary>
    private void Die()
    {
        MonsterPool.Recycle(gameObject);
    }

    /// <summary>
    /// 怪物攻击玩家
    /// </summary>
    private void HandleAttack()
    {
        attackTimer+=Time.deltaTime;
        Vector3 toTarget=target.position-transform.position;
        toTarget.y=0f;
        if(toTarget.sqrMagnitude>attackDistance*attackDistance)return;
        if(attackTimer<attackInterval)return;
        attackTimer=0f;
        EventCenter.instance.TriggerEvent(GameEvent.MonsterAttackPlayer,attackDamage);
    }
}
