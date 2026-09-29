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
    
    #endregion
}
