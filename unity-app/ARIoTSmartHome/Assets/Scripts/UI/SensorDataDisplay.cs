using UnityEngine;
using TMPro;

public class SensorDataDisplay : MonoBehaviour
{
    [SerializeField] private WebSocketManager webSocketManager;

    [SerializeField] private TMP_Text temperatureText;
    [SerializeField] private TMP_Text humidityText;
    [SerializeField] private TMP_Text lightText;
    [SerializeField] private TMP_Text distanceText;
    [SerializeField] private TMP_Text rawJsonText;

    private void Start()
    {
        webSocketManager.OnRawMessageReceived += HandleMessage;
        webSocketManager.Connect();
    }

    private void HandleMessage(string json)
    {
        if (rawJsonText != null)
        {
            rawJsonText.text = json;
        }

        SensorDataEnvelope envelope = JsonUtility.FromJson<SensorDataEnvelope>(json);

        if (envelope == null || envelope.type != "sensor_data" || envelope.payload == null)
        {
            return;
        }

        temperatureText.text = $"Teplota: {envelope.payload.temperature:F1} °C";
        humidityText.text = $"Vlhkosť: {envelope.payload.humidity:F1} %";
        lightText.text = $"Svetlo: {envelope.payload.light} %";
        distanceText.text = $"Vzdialenosť: {envelope.payload.distance} cm";
    }
}