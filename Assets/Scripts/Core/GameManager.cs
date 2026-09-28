using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : Singleton<GameManager>
{
    /// <summary>
    /// 当前游戏状态
    /// </summary>
     public GameState CurrentState{get;private set;}
     //游戏状态初始化
    private void Start()
    {
        SwitchState(GameState.Login);
    }
    /// <summary>
    /// 切换游戏状态
    /// </summary>
    /// <param name="gameState"></param>
    public void SwitchState(GameState newStates)
    {
        GameStateChangeData data=new GameStateChangeData()
        {
            oldState=CurrentState,
            newState=newStates
        };
        CurrentState=newStates;
        //广播切换状态
        EventCenter.instance.TriggerEvent(GameEvent.GameStateChange,data);
    } 

    #region 各个游戏状态的转换
    /// <summary>
    /// 开始游戏，加载战斗场景
    /// </summary>
    public void StartGame()
    {
        Time.timeScale=1;
        //加载场景
        SceneManager.LoadScene("GameScene");
        SwitchState(GameState.GamePlaying);
    }

    /// <summary>
    /// 返回登陆界面
    /// </summary>
    public void BackToLogin()
    {
        Time.timeScale=1;
        SceneManager.LoadScene("GameLogin");
        SwitchState(GameState.Login);
    }

    /// <summary>
    /// 暂停游戏
    /// </summary>
    public void PauseGame()
    {
        if (CurrentState == GameState.GamePlaying)
        {
            SwitchState(GameState.GamePause);
            Time.timeScale=0; //暂停时间
            EventCenter.instance.TriggerEvent(GameEvent.GamePause);
        }  
    }

    /// <summary>
    /// 恢复游戏
    /// </summary>
    public void ResumeGame()
    {
        if (CurrentState == GameState.GamePause)
        {
            SwitchState(GameState.GamePlaying);
            Time.timeScale=1;
            EventCenter.instance.TriggerEvent(GameEvent.ResumGame);
        }
    }
    #endregion
    
}
