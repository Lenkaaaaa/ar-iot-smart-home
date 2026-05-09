using UnityEngine;
using TMPro;

public class SensorDataDisplay : MonoBehaviour
{
    [SerializeField] private WebSocketManager webSocketManager;

    [SerializeField] private TMP_Text temperatureText;
    [SerializeField] private TMP_Text humidityText;
    [SerializeField] private TMP_Text lightText;
    [SerializeField] private TMP_Text distanceText;

    private void Start()
    {
        webSocketManager.OnRawMessageReceived += HandleMessage;
    }

    private void HandleMessage(string json)
    {
        SensorDataEnvelope envelope = JsonUtility.FromJson<SensorDataEnvelope>(json);

        if (envelope == null || envelope.type != "sensor_data" || envelope.payload == null)
        {
            return;
        }

        temperatureText.text = $"Temperature: {envelope.payload.temperature:F1}°C";
        humidityText.text = $"Humidity: {envelope.payload.humidity:F1}%";
        lightText.text = $"Light: {envelope.payload.light}%";
        distanceText.text = $"Distance: {envelope.payload.distance}cm";
    }
}