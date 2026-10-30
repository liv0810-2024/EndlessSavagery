using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 战斗 HUD：血条 / 血量数字 / 波次 / 存活时间
/// </summary>
public class UIGameHudPanel : MonoBehaviour
{
    [Header("血量")]
    [SerializeField] private Slider hpSlider;
    [SerializeField] private Text hpText;

    [Header("波次")]
    [SerializeField] private Text waveText;

    [Header("存活时间")]
    [SerializeField] private Text timeText;

    /// <summary>
    /// 存活时间
    /// </summary>
    private float survivalTime;

    private void Awake()
    {
        EventCenter.instance.AddEventListener(GameEvent.PalyerHpChange, OnPlayerHpChange);
        EventCenter.instance.AddEventListener(GameEvent.WaveChange, OnWaveChange);
    }

    private void Update()
    {
        survivalTime += Time.deltaTime;
        UpdateTimeText();
    }

    private void OnDestroy()
    {
        EventCenter.instance.RemoveEventListener(GameEvent.PalyerHpChange, OnPlayerHpChange);
        EventCenter.instance.RemoveEventListener(GameEvent.WaveChange, OnWaveChange);
    }

    /// <summary>
    /// 收到血量变化，更新血条和数字
    /// </summary>
    private void OnPlayerHpChange(object param)
    {
        PlayerHpData data = (PlayerHpData)param;
        if (data == null) return;
        if (hpSlider != null)
        {
            float ratio = data.maxHp > 0f ? data.currentHp / data.maxHp : 0f;
            hpSlider.value = ratio;
        }
        if (hpText != null)
        {
            hpText.text = $"{Mathf.CeilToInt(data.currentHp)} / {Mathf.CeilToInt(data.maxHp)}";
        }
    }

    /// <summary>
    /// 收到波次变化跟新文本
    /// </summary>
    private void OnWaveChange(object param)
    {
        WaveData data = param as WaveData;
        if (data == null)
        {
            return;
        }
        if (waveText != null) waveText.text = $"第 {data.wave} 波";
    }

    /// <summary>
    /// 把秒修改成分
    /// </summary>
    private void UpdateTimeText()
    {
        if (timeText == null) return;

        int minutes = Mathf.FloorToInt(survivalTime / 60f);
        int seconds = Mathf.FloorToInt(survivalTime % 60f);
        timeText.text = $"{minutes:00}:{seconds:00}";
    }
}
