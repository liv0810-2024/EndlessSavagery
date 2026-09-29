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

    protected override void Awake()
    {
        base.Awake();
        if(instance!=this)return;
        //监听UI按钮
        EventCenter.instance.AddEventListener(GameEvent.StartGameClick,OnStartGameClick);
        EventCenter.instance.AddEventListener(GameEvent.BackToLoginClick,OnStartGameClick);
    }

    private void OnDestroy()
    {
        EventCenter.instance.RemoveEventListener(GameEvent.StartGameClick, OnStartGameClick);
        EventCenter.instance.RemoveEventListener(GameEvent.BackToLoginClick, OnBackToLoginClick);
    }
    //游戏状态初始化
    private void Start()
    {
        SwitchState(GameState.Login);
    }

    //事件回调
    private void OnStartGameClick(object param)=>StartGame();
    private void OnBackToLoginClick(object param)=>BackToLogin();
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
