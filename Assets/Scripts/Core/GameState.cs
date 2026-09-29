using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum GameState
{
    None=0,
    /// <summary>
    /// 登陆页面
    /// </summary>
    Login,
    /// <summary>
    /// 游戏对局中
    /// </summary>
    GamePlaying,
    /// <summary>
    /// 游戏暂停
    /// </summary>
    GamePause,
    /// <summary>
    /// 游戏结束
    /// </summary>
    GameOver
}
