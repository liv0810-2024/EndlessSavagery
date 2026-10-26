using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 怪物对象池：回收的怪物不销毁，休眠起来，下次刷怪直接唤醒复用。
/// 纯静态类 —— 不需要挂到任何物体上，也不需要 Singleton。
/// </summary>
public static class MonsterPool
{
    public static readonly Dictionary<GameObject, Queue<GameObject>> pools = new Dictionary<GameObject, Queue<GameObject>>(); 
    public static Transform root; //隐藏时物体挂载的地方

    /// <summary>
    /// 从池子里取一个（没有就新建），摆到指定位置并激活。
    /// </summary>
    /// <param name="prefab">预制体</param>
    /// <param name="position">位置</param>
    /// <param name="rotation">方向</param>
    public static GameObject Spawn(GameObject prefab, Vector3 position, Quaternion rotation)
    {
        EnsureRoot();
        if(!pools.TryGetValue(prefab,out Queue<GameObject> queue))
        {
            queue=new Queue<GameObject>();
            pools[prefab]=queue;
        }
        //从队列里取一个还活着的实例
        GameObject go=null;
        while(queue.Count > 0)
        {
            go=pools[prefab].Dequeue();
            if(go!=null)break;
            go=null;
        }
        //如果里面没有存货
        if (go == null)
        {
            go=Object.Instantiate(prefab);
            // 记住它来自哪个 prefab，回收时靠这个找队列
            MonsterBase monsterBase=go.GetComponent<MonsterBase>();
            if(monsterBase!=null)monsterBase.prefabSource=prefab;
        }
        go.transform.SetPositionAndRotation(position,rotation);
        go.SetActive(true);
        return go;

    }

    /// <summary>
    /// 把怪物放回池子（不销毁）。
    /// </summary>
    /// <param name="go"></param>
    public static void Recycle(GameObject go)
    {
        if (go == null)
        {
            return;
        }   
        MonsterBase monsterBase=go.GetComponent<MonsterBase>();
        // 不是池子管理的物体（没有 MonsterBase，或不知道来源）→ 正常销毁
        if (monsterBase == null || monsterBase.prefabSource == null)
        {
            Object.Destroy(go);
            return;
        }
        EnsureRoot();
        go.SetActive(false);
        go.transform.SetParent(root,false);
        // 塞回对应 prefab 的队列（用 TryGetValue 防御队列不存在的情况）
        if(!pools.TryGetValue(monsterBase.prefabSource,out Queue<GameObject> queue))
        {
            queue=new Queue<GameObject>();
            pools[monsterBase.prefabSource]=queue;
        }
        queue.Enqueue(go);
    }
    public static void EnsureRoot()
    {
        if(root!=null)return;
        pools.Clear();// 旧数据全部丢掉
        root=new GameObject("[MonsterPool]").transform;
    }
}
