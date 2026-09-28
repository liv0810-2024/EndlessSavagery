using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 游戏状态变更事件传递的数据载体
/// </summary>
public class GameStateChangeData
{
    public GameState oldState;
    public GameState newState;
}
