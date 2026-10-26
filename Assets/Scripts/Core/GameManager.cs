using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.SocialPlatforms;

public class GameManager : Singleton<GameManager>
{
    /// <summary>
    /// 当前游戏状态
    /// </summary>
    public GameState CurrentState { get; private set; }

    protected override void Awake()
    {
        base.Awake();
        if (instance != this) return;
        //监听UI按钮
        EventCenter.instance.AddEventListener(GameEvent.StartGameClick, OnStartGameClick);
        EventCenter.instance.AddEventListener(GameEvent.BackToLoginClick, OnBackToLoginClick);
        EventCenter.instance.AddEventListener(GameEvent.ResumeClick, OnResumeClick);
        EventCenter.instance.AddEventListener(GameEvent.RestartClick, OnRestartClick);
    }

    private void OnDestroy()
    {
        EventCenter.instance.RemoveEventListener(GameEvent.StartGameClick, OnStartGameClick);
        EventCenter.instance.RemoveEventListener(GameEvent.BackToLoginClick, OnBackToLoginClick);
        EventCenter.instance.RemoveEventListener(GameEvent.ResumeClick, OnResumeClick);
        EventCenter.instance.RemoveEventListener(GameEvent.RestartClick, OnRestartClick);
    }
    //游戏状态初始化
    private void Start()
    {
        // 直接 Play 战斗场景时，自动进入对局状态，方便单独调试战斗场景
        // 从登录场景开始时，才保持 Login 状态
        if (SceneManager.GetActiveScene().name == "GameScene")
            SwitchState(GameState.GamePlaying);
        else
            SwitchState(GameState.Login);
    }

    //事件回调
    private void OnStartGameClick(object param) => StartGame();
    private void OnBackToLoginClick(object param) => BackToLogin();
    private void OnResumeClick(object param) => ResumeGame();
    private void OnRestartClick(object param) => RestartGame();

    /// <summary>
    /// 切换游戏状态
    /// </summary>
    /// <param name="gameState"></param>
    public void SwitchState(GameState newStates)
    {
        GameStateChangeData data = new GameStateChangeData()
        {
            oldState = CurrentState,
            newState = newStates
        };
        CurrentState = newStates;
        //打日志：随时能在 Console 看到状态变成了什么，方便排查"为什么角色不动"这类问题
        Debug.Log($"[GameManager] 状态切换：{data.oldState} → {data.newState}");
        //广播切换状态
        EventCenter.instance.TriggerEvent(GameEvent.GameStateChange, data);
    }

    #region 各个游戏状态的转换
    /// <summary>
    /// 开始游戏，加载战斗场景
    /// </summary>
    public void StartGame()
    {
        Time.timeScale = 1;
        //加载场景
        SceneManager.LoadScene("GameScene");
        SwitchState(GameState.GamePlaying);
    }

    /// <summary>
    /// 返回登陆界面
    /// </summary>
    public void BackToLogin()
    {
        Time.timeScale = 1;
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
            Time.timeScale = 0; //暂停时间
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
            Time.timeScale = 1;
            EventCenter.instance.TriggerEvent(GameEvent.ResumGame);
        }
    }

    public void GameOver()
    {
        if (CurrentState != GameState.GamePlaying) return;
        SwitchState(GameState.GameOver);
        Time.timeScale = 0;
    }

    public void RestartGame()
    {
        Time.timeScale=1f;
        SceneManager.LoadScene("GameScene");
        SwitchState(GameState.GamePlaying);
    }
    #endregion

}
