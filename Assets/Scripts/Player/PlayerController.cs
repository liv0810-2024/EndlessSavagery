using UnityEngine;

/// <summary>
/// 玩家控制器：负责移动 + 自动攻击 + 驱动动画
/// 分工：本脚本控制 Player【根节点】的位置和朝向；动画只驱动【外观子物体】
/// </summary>
public class PlayerController : MonoBehaviour
{
    [Header("移动速度")]
    [SerializeField] private float moveSpeed = 5f;

    [Header("攻击")]
    [SerializeField] private float atk = 12f;
    [SerializeField] private float attackRange = 2.5f;
    [SerializeField] private float attackCD = 0.8f;

    [Header("引用")]
    //普通 int 是数字，LayerMask 是"层的集合"。你在 Inspector 里看到的是一个下拉框（可以勾多个层），声明成 LayerMask 就是为了拿到这个下拉框
    [SerializeField] private LayerMask monsterLayer;  // 怪物所在的 Layer

    [Header("动画外观")]
    [SerializeField] private Animator visualAnimator; // 外观子物体上的 Animator

    // 把 "Speed" 字符串预先转成哈希值，避免每帧做字符串查找
    private static readonly int SpeedHash = Animator.StringToHash("Speed");

    private Vector3 moveDir;    // 移动方向
    private float attackTimer;  // 攻击计时器

    private void Awake()
    {
        // Inspector 没拖的话，从子物体里找（true = 连未激活的也找）
        if (visualAnimator == null)
            visualAnimator = GetComponentInChildren<Animator>(true);

        if (visualAnimator == null)
        {
            Debug.LogWarning("[PlayerController] 没找到 Animator，动画不会播放。" +
                             "请把外观子物体拖到 Visual Animator 槽位，并确认它上面有 Animator 组件。");
        }
        else
        {
            // 关闭根运动：位置由本脚本说了算，动画只负责姿势，避免双倍位移
            visualAnimator.applyRootMotion = false;
        }
    }

    private void Update()
    {
        if (CanAct())
        {
            HandleMove();
            HandleAttack();
        }
        else
        {
            // 暂停 / 结算：方向清零，角色停住
            moveDir = Vector3.zero;
        }
        UpdateAnimator();
    }

    /// <summary>
    /// 移动
    /// </summary>
    private void HandleMove()
    {
        float x = Input.GetAxisRaw("Horizontal");
        float z = Input.GetAxisRaw("Vertical");   // 地面是 XZ 平面，"前后"对应 z 轴
        moveDir = new Vector3(x, 0f, z);
        // 这里判断的是"有没有输入"，不需要精确长度，所以用平方值
        //moveDir.sqrMagnitude = 长度的平方
        if (moveDir.sqrMagnitude > 0.01f)
        {
            moveDir = moveDir.normalized; // 归一化：斜向走才不会变快
            transform.Translate(moveDir * moveSpeed * Time.deltaTime, Space.World);
            // 平滑转向移动方向
            //Quaternion.LookRotation(方向向量) = "让物体的正前方看向这个方向"
            Quaternion targetRot = Quaternion.LookRotation(moveDir);
            //  Slerp 算出的是"新旋转"，必须赋回 transform.rotation，否则角色永远不转向
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 15f * Time.deltaTime);
        }
    }

    /// <summary>
    /// 判断是否能行动（暂停 / 结算时冻结）
    /// </summary>
    private bool CanAct()
    {
        return GameManager.instance.CurrentState == GameState.GamePlaying;
    }

    /// <summary>
    /// 更新动画
    /// </summary>
    private void UpdateAnimator()
    {
        if (visualAnimator == null) return;

        // 0 = 待机，1 = 移动（Animator 里靠 Speed 的值在 Idle / Move 之间切换）
        visualAnimator.SetFloat(SpeedHash, moveDir.sqrMagnitude > 0.01f ? 1f : 0f);
    }

    /// <summary>
    /// 攻击计时
    /// </summary>
    private void HandleAttack()
    {
        attackTimer += Time.deltaTime;
        if (attackTimer >= attackCD)
        {
            attackTimer = 0;
            DoAttack();
        }
    }

    /// <summary>
    /// 检测范围的敌人并派发伤害
    /// </summary>
    private void DoAttack()
    {
        // 以自身为球心，attackRange 为半径，只检测 Monster 层
        Collider[] hits = Physics.OverlapSphere(transform.position, attackRange, monsterLayer);
        if (hits.Length == 0) return;
        EventCenter.instance.TriggerEvent(GameEvent.PlayerAttack, atk);
        //Debug.Log($"[Player] 发动攻击，命中 {hits.Length} 个目标，伤害 {atk}");
    }

    /// <summary>
    /// 在 Scene 视图画出攻击范围（只在选中时显示）
    /// </summary>
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = new Color(1f, 0.3f, 0.3f, 0.6f);   // 红色（带透明度）
        Gizmos.DrawWireSphere(transform.position, attackRange);
    }
}
