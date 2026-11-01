using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MonsterSpawner : MonoBehaviour
{
    [Header("怪物预制体")]
    [SerializeField] GameObject[] monsterPrefabs;

    [Header("怪物配置（第一波）")]
    [SerializeField] private float spawnInterval = 2f;
    [SerializeField] private int maxAlive = 20; //同屏最多多少怪

    [SerializeField] private float minDistance = 8f;
    [SerializeField] private float maxDistance = 13f;

    [Header("难度曲线")]
    [SerializeField] private float waveDuration=30f;
    [SerializeField] private float spawnIntervalStep=0.15f; //每波怪间隔减多少
    [SerializeField] private float minSpawnInterval=0.4f; //间隔最小能多少
    [SerializeField] private int maxAliveStep=3; //每波上限加多少只
    [SerializeField] private int maxAliveLimit = 60;            // 同屏上限阈值
    [SerializeField] private float hpGrowthPerWave = 0.2f;      // 每波血量增长比例
    //运行时状态
    private float timer;
    private Transform player;

    public int currentWave = 1;             // 当前波次
    private float waveTimer;                 // 当前这一波已过的时间
    private float currentSpawnInterval;      // 当前刷怪间隔
    private int currentMaxAlive;             // 当前同屏上限
    private float currentHpMultiplier = 1f;  // 当前血量倍率

    private void Start()
    {
        timer = 0f;
        GameObject people = GameObject.FindGameObjectWithTag("Player");
        if (people != null)
        {
            player = people.transform;
        }
        else
        {
            Debug.LogError("MonsterSpawner脚本找不到玩家");
        }
        ApplyWave();
    }
    private void Update()
    {
        if (GameManager.instance.CurrentState != GameState.GamePlaying) return;
        if (monsterPrefabs == null || monsterPrefabs.Length == 0) return;
        UpdateWave();
        //如果场上满怪物了也不继续生成
        if (MonsterBase.AliveCount >= currentMaxAlive) return;
        timer += Time.deltaTime;
        if (timer < currentSpawnInterval) return;
        timer = 0;
        SpawnOne();
    }

    /// <summary>
    /// 根据当前波次，算出并应用这一波的难度参数
    /// </summary>
    private void ApplyWave()
    {
        //算刷怪间隔
        currentSpawnInterval = Mathf.Max(minSpawnInterval, spawnInterval - (currentWave - 1) * spawnIntervalStep);
        //算同屏上限
        currentMaxAlive = Mathf.Min(maxAliveLimit, maxAlive + (currentWave - 1) * maxAliveStep);
        //血量倍率
        currentHpMultiplier = 1f + (currentWave - 1) * hpGrowthPerWave;
        //日志
        Debug.Log($"[MonsterSpawner] 第 {currentWave} 波：间隔 {currentSpawnInterval:F2}s，" +
                  $"同屏上限 {currentMaxAlive}，血量 x{currentHpMultiplier:F2}");
        //广播
        WaveData data = new WaveData
        {
            wave = currentWave,
            currentInterval = currentSpawnInterval,
            maxAlive = currentMaxAlive
        };
        EventCenter.instance.TriggerEvent(GameEvent.WaveChange, data);
    }

    /// <summary>
    /// 更新波次
    /// </summary>
    private void UpdateWave()
    {
        waveTimer += Time.deltaTime;
        if (waveTimer < waveDuration) return;
        waveTimer = 0;
        currentWave++;
        ApplyWave();
    }

    /// <summary>
    /// 生成怪物
    /// </summary>
    private void SpawnOne()
    {
        Vector3 spawnPosition = GetSpawnPosition();

        GameObject prefab = monsterPrefabs[Random.Range(0, monsterPrefabs.Length)];

        // 从对象池取一个
        GameObject monster = MonsterPool.Spawn(prefab, spawnPosition, Quaternion.identity);

        // 按当前波次设置血量倍率
        MonsterBase monsterBase = monster.GetComponent<MonsterBase>();
        if (monsterBase != null)
            monsterBase.SetHpMultiplier(currentHpMultiplier);
    }

    /// <summary>
    /// 获取怪物的位置
    /// </summary>
    /// <returns></returns>
    private Vector3 GetSpawnPosition()
    {
        if (player == null)
        {
            return Vector3.zero;
        }
        // 随机角度（0 ~ 2π = 一整圈）和随机半径
        float angle = Random.Range(0, Mathf.PI * 2f);
        float distance = Random.Range(minDistance, maxDistance);
        Vector3 offest = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * distance;
        Vector3 pos = player.position + offest;
        pos.y = player.position.y;
        return pos;
    }
}
