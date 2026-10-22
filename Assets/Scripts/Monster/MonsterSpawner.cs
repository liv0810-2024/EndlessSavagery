using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;

public class MonsterSpawner : MonoBehaviour
{
    [Header("怪物预制体")]
    [SerializeField] GameObject[] monsterPrefabs;

    [Header("怪物配置")]
    [SerializeField] private float spawnInterval = 2f;
    [SerializeField] private int maxAlive = 20; //同屏最多多少怪

    [SerializeField] private float minDistance = 8f;
    [SerializeField] private float maxDistance = 13f;

    //运行时状态
    private float timer;
    private Transform player;

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
            Debug.Log("MonsterSpawner脚本找不到玩家");
        }
    }
    private void Update()
    {
        if (GameManager.instance.CurrentState != GameState.GamePlaying) return;
        if (monsterPrefabs == null || monsterPrefabs.Length == 0) return;
        //如果场上满怪物了也不继续生成
        if (MonsterBase.AliveCount >= maxAlive) return;
        timer += Time.deltaTime;
        if (timer < spawnInterval) return;
        timer = 0;
        SpwanOne();
    }

    /// <summary>
    /// 生成怪物
    /// </summary>
    private void SpwanOne()
    {
        Vector3 spawnPositon = GetSpawnPosition();
        GameObject prefab = monsterPrefabs[Random.Range(0, monsterPrefabs.Length)];
        //Quaternion.identity —— "没有旋转"
        Instantiate(prefab, spawnPositon, Quaternion.identity);
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
        Vector3 offest = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(distance))*distance;
        Vector3 pos = player.position + offest;
        pos.y = player.position.y;
        return pos;
    }
}
