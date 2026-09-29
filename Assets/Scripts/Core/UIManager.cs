using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class UIManager : Singleton<UIManager>
{
    [Header("登陆面板")]
    public GameObject loginPanel;

    [Header("游戏面板")]
    public GameObject gameHudPanel;

    [Header("暂停面板")]
    public GameObject pausePanel;

    [Header("游戏结束面板")]
    public GameObject gameOverPanel;
    private Dictionary<UIPanelType,GameObject> panelDic=new Dictionary<UIPanelType, GameObject>();

    //初始化
    protected override void Awake()
    {
        base.Awake();
        if(instance!=this)return;
        EventCenter.instance.AddEventListener(GameEvent.GameStateChange,OnGameStateChange);
        InitPanel();
    }

    /// <summary>
    /// 初始化面板
    /// </summary>
    public void InitPanel()
    {
        panelDic.Clear();
        panelDic.Add(UIPanelType.LoginPanel,loginPanel);
        panelDic.Add(UIPanelType.GameHudPanel,gameHudPanel);
        panelDic.Add(UIPanelType.PausePanle,pausePanel);
        panelDic.Add(UIPanelType.GameOverPanel,gameOverPanel);
        HideAllPanel();
    }

    /// <summary>
    /// 隐藏所有面板
    /// </summary>
    public void HideAllPanel()
    {
        foreach(var panel in panelDic.Values)
        {
            if(panel!=null) panel.SetActive(false);
        }

        // 旧方法
        // loginPanel.SetActive(false);
        // gameHudPanel.SetActive(false);
        // pausePanel.SetActive(false);
        // gameOverPanel.SetActive(false);
    }

    /// <summary>
    /// 打开面板
    /// </summary>
    /// <param name="panelType">面板类型</param>
    public void OpenPanel(UIPanelType panelType)
    {
        if (panelDic.ContainsKey(panelType))
        {
            panelDic[panelType].SetActive(true);
        }
        else
        {
            Debug.LogWarning($"没有找到面板：{panelType}");
        }
    }

    /// <summary>
    /// 关闭面板
    /// </summary>
    /// <param name="panelType">面板类型</param>
    public void ClosePanel(UIPanelType panelType)
    {
        if (panelDic.TryGetValue(panelType ,out GameObject gameObjectPanel))
        {
            gameObjectPanel.SetActive(false);
        }
        else
        {
            Debug.LogWarning($"没有找到面板：{panelType}");
        }
    }

    /// <summary>
    /// 注册监听ui事件
    /// </summary>
    private void OnEnable()
    {
        EventCenter.instance.AddEventListener(GameEvent.GameStateChange,OnGameStateChange);
    }

    /// <summary>
    /// 取消ui监听
    /// </summary>
    private void OnDisable()
    {
        EventCenter.instance.RemoveEventListener(GameEvent.GameStateChange,OnGameStateChange);
    }

    /// <summary>
    /// 收到游戏状态变化，自动切换ui
    /// </summary>
    /// <param name="param"></param>
    private void OnGameStateChange(object param)
    {
        GameStateChangeData data=param as GameStateChangeData;
        if (data == null)
        {
            Debug.LogError("GameStateChange 传参类型错误");
            return;
        }
        HideAllPanel();
        switch (data.newState)
        {
            case GameState.Login:
            OpenPanel(UIPanelType.LoginPanel);
            break;
            case GameState.GamePause:
            OpenPanel(UIPanelType.GameHudPanel);
            OpenPanel(UIPanelType.PausePanle);
            break;
            case GameState.GamePlaying:
            OpenPanel(UIPanelType.GameHudPanel);
            break;
            case GameState.GameOver:
            OpenPanel(UIPanelType.GameOverPanel);
            break;
        }
    }
}
