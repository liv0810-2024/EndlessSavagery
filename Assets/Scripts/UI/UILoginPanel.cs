using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 登陆面板
/// </summary>
public class UILoginPanel : MonoBehaviour
{
    [Header("游戏开始按钮")]
   [SerializeField] private Button startButton;
    private void Awake()
    {
        if (startButton != null)
        {
            startButton.onClick.AddListener(OnStartGmaeBtnClick);
        }
        else
        {
            Debug.LogError("[UILoginPanel] startGameBtn 未在 Inspector 里赋值！");
            return;
        }
    }
    private void OnDestroy()
    {
        if (startButton != null)
        {
           startButton.onClick.RemoveListener(OnStartGmaeBtnClick);
    }
    private void OnStartGmaeBtnClick()
    {
        EventCenter.instance.TriggerEvent(GameEvent.StartGameClick);
    }
}
