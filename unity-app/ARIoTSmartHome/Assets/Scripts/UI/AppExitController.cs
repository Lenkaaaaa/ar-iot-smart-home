using System.Collections;
using UnityEngine;

public class AppExitController : MonoBehaviour
{
    [SerializeField] private WebSocketManager webSocketManager;
    [SerializeField] private float quitDelay = 0.2f;

    public void ExitApplication()
    {
        StartCoroutine(ExitRoutine());
    }

    private IEnumerator ExitRoutine()
    {
        if (webSocketManager != null)
        {
            webSocketManager.Disconnect();
        }

        yield return new WaitForSeconds(quitDelay);

#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }
}