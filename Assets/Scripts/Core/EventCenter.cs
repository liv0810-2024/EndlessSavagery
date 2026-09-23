using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EventCenter : Singleton<EventCenter>
{
    private Dictionary<string, Action<object>> eventDic = new Dictionary<string, Action<object>>();
    /// <summary>
    /// 监听注册
    /// </summary>
    /// <param name="eventName"></param>
    /// <param name="callback"></param>
    public void AddEventListener(string eventName, Action<object> callback)
    {
        if (eventDic.ContainsKey(eventName))
        {
            eventDic[eventName] += callback;
        }
        else
        {
            eventDic[eventName] = callback;
        }
    }

    /// <summary>
    /// 出发事件
    /// </summary>
    /// <param name="eventName"></param>
    /// <param name="param"></param>
    public void TriggerEvent(string eventName,object param = null)
    {
        if(eventDic.TryGetValue(eventName,out var action))
        {
            action?.Invoke(param);
        }
    }

    /// <summary>
    /// 移除事件
    /// </summary>
    /// <param name="eventName"></param>
    /// <param name="callback"></param>
    public void RemoveEventListener(string eventName,Action<object> callback)
    {
        if(eventDic.TryGetValue(eventName,out var action))
        {
            eventDic[eventName]-=action;
        }
    }

    /// <summary>
    /// 清除事件 切换状态之后统一调用
    /// </summary>
    public void Clear()
    {
        eventDic.Clear();
    }
}
