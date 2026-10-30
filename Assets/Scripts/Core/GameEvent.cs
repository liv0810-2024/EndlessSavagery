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

    /// <summary>
    /// 玩家攻击怪物事件
    /// </summary>
    public const string PlayerAttack="PlayerAttack";

    /// <summary>
    /// 怪物攻击玩家的事件
    /// </summary>
    public const string MonsterAttackPlayer="MonsterAttackPlayer";

    /// <summary>
    /// 波次变换事件
    /// </summary>
    public const string WaveChange="WaveChange"; 

    #region UI
    /// <summary>
    /// 点击开始游戏
    /// </summary>
    public const string StartGameClick="StartGameClick";

    /// <summary>
    /// 继续游戏
    /// </summary>
    public const string ResumeClick="ResumeClick";

    /// <summary>
    /// 重新开始
    /// </summary>
    public const string RestartClick="RestartClick";

    /// <summary>
    /// 返回主界面
    /// </summary>
    public const string BackToLoginClick="BackToLoginClick";

    /// <summary>
    /// 玩家血量改变UI事件
    /// </summary>
    public const string PalyerHpChange="PalyerHpChange";
    
    #endregion
}
