using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FloatingText : MonoBehaviour
{
    public TextMesh textMesh;
    private float timer;
    [Header("漂浮字体设置")]
    public float floatSpeed=1f; //向上漂浮的速度
    public float fadeDuration=2f; //漂浮持续时间

    private void Update()
    {
        //向上移动
        transform.position+=Vector3.up*(floatSpeed*Time.deltaTime);
        //始终面向主相机
        if (Camera.main != null)
        {
            transform.rotation=Camera.main.transform.rotation;
        }
        //倒计时淡出
        timer+=Time.deltaTime;
        float t=Mathf.Clamp01(timer/fadeDuration);
        Color c=textMesh.color;
        c.a=1f-t;
        textMesh.color=c;
        if (timer > fadeDuration)
        {
            Destroy(gameObject);
        }
    }

    public void Init(string content,Color color)
    {
        if (textMesh != null)
        {
            textMesh=GetComponent<TextMesh>();
        }
        textMesh.text=content;
        textMesh.color=color;
        timer=0f;
    }
}
