using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public static class GameEvent 
{
    /// <summary>
    /// 游戏状态改变事件
    /// </summary>
    public const string GameStateChange="GameStateChange";
    
    /// <summary>
    /// 游戏暂停事件
    /// </summary>
    public const string GamePause="GamePause";

    /// <summary>
    /// 恢复游戏事件
    /// </summary>
    public const string ResumGame="ResumGame";
}
