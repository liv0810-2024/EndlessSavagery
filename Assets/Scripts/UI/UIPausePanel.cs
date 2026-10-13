using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class UIPausePanel : MonoBehaviour
{
    [Header("按钮配置")]
    public Button resumeBtn;
    public Button backBton;

    private void Awake()
    {
        if (resumeBtn != null)
        {
            resumeBtn.onClick.AddListener(OnResumeBtnClik);
        }
        else
        {
            Debug.LogError("[UIPausePanel] resumeBtn 未在 Inspector 里赋值！");
        }
        if (backBton != null)
        {
            backBton.onClick.AddListener(OnBackBtnClik);
        }
        else
        {
            Debug.LogError("[UIPausePanel] backBtn 未在 Inspector 里赋值！");
        }
    }
    private void OnDestroy()
    {
        if (resumeBtn != null)
        {
            resumeBtn.onClick.RemoveListener(OnResumeBtnClik);
        }
        if (backBton != null)
        {
            backBton.onClick.RemoveListener(OnBackBtnClik);
        }
    }
    public void OnResumeBtnClik()
    {
        EventCenter.instance.TriggerEvent(GameEvent.ResumeClick);
        //Debug.Log("[UIPausePanel] 点了继续按钮");
    }
    public void OnBackBtnClik()
    {
        EventCenter.instance.TriggerEvent(GameEvent.BackToLoginClick);
        //Debug.Log("[UIPausePanel] 点了继续按钮");
    }
}
