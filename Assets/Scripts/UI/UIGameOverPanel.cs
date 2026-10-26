using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class UIGameOverPanel : MonoBehaviour
{
    [Header("按钮配置")]
    public Button RestarButton;
    public Button QuitButton; //退出游戏的按钮

    #region 生命周期
    private void Awake()
    {
        if (RestarButton != null)
        {
            RestarButton.onClick.AddListener(RestarGame);
        }
        if (QuitButton != null)
        {
            QuitButton.onClick.AddListener(QuitGame);
        }
    }

    private void OnDestroy()
    {
        if (RestarButton != null)
        {
            RestarButton.onClick.RemoveListener(RestarGame);
        }
        if (QuitButton != null)
        {
            QuitButton.onClick.RemoveListener(QuitGame);
        }
    }
    #endregion

    #region 按钮逻辑

    private void RestarGame()
    {
        EventCenter.instance.TriggerEvent(GameEvent.RestartClick);
    }

    private void QuitGame()
    {
        EventCenter.instance.TriggerEvent(GameEvent.BackToLoginClick);
//         #if UNITY_EDITOR
//     UnityEditor.EditorApplication.isPlaying = false;   // 编辑器：停下 Play
// #else
//     Application.Quit();                                 // 打包后：退出程序
// #endif
    }
    #endregion
}
