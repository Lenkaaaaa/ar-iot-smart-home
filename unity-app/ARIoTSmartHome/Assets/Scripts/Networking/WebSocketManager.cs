using System;
using System.Text;
using UnityEngine;
using NativeWebSocket;

public class WebSocketManager : MonoBehaviour
{
    [SerializeField] private string serverUrl = "ws://192.168.1.7:8080";

    private WebSocket websocket;

    public Action<string> OnRawMessageReceived;

    public bool IsConnected =>
        websocket != null && websocket.State == WebSocketState.Open;

    public async void Connect()
    {
        Debug.Log("Trying to connect to: " + serverUrl);

        websocket = new WebSocket(serverUrl);

        websocket.OnOpen += () =>
        {
            Debug.Log("WebSocket connected.");
        };

        websocket.OnError += (error) =>
        {
            Debug.LogError("WebSocket error: " + error);
        };

        websocket.OnClose += (code) =>
        {
            Debug.Log("WebSocket closed with code: " + code);
        };

        websocket.OnMessage += (bytes) =>
        {
            string message = Encoding.UTF8.GetString(bytes);
            Debug.Log("Received: " + message);
            OnRawMessageReceived?.Invoke(message);
        };

        await websocket.Connect();
    }

    public async void SendJson(string json)
    {
        if (websocket == null || websocket.State != WebSocketState.Open)
        {
            Debug.LogWarning("WebSocket is not connected.");
            return;
        }

        await websocket.SendText(json);
    }

    public async void Disconnect()
    {
        if (websocket == null)
        {
            return;
        }

        if (websocket.State == WebSocketState.Open || websocket.State == WebSocketState.Connecting)
        {
            await websocket.Close();
        }
    }

    private void Update()
    {
#if !UNITY_WEBGL || UNITY_EDITOR
        websocket?.DispatchMessageQueue();
#endif
    }

    private async void OnApplicationQuit()
    {
        if (websocket != null)
        {
            await websocket.Close();
        }
    }
}