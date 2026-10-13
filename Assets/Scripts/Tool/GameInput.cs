using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameInput : MonoBehaviour
{
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            if (GameManager.instance.CurrentState != GameState.GamePause)
            {
                GameManager.instance.PauseGame();
            }
            else
            {
                GameManager.instance.ResumeGame();
            }
        }
        else
        {
            return;
        }
    }
}
