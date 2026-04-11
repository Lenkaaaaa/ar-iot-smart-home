using UnityEngine;

public class WebSocketBootstrap : MonoBehaviour
{
    [SerializeField] private WebSocketManager webSocketManager;

    private void Start()
    {
        webSocketManager.Connect();
    }
}