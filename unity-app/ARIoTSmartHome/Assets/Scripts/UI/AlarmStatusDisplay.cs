using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;

public class AlarmStatusDisplay : MonoBehaviour
{
    [Header("API")]
    [SerializeField] private string dashboardApiBaseUrl = "http://192.168.1.10:5000";

    [Header("Texts")]
    [SerializeField] private TMP_Text temperatureText;
    [SerializeField] private TMP_Text humidityText;
    [SerializeField] private TMP_Text lightText;
    [SerializeField] private TMP_Text distanceText;

    [Header("Normal Style")]
    [SerializeField] private Color normalColor = Color.white;
    [SerializeField] private float normalFontSize = 28f;

    [Header("Alarm Style")]
    [SerializeField] private Color alarmColor = Color.red;
    [SerializeField] private float alarmFontSize = 32f;

    [Header("Refresh")]
    [SerializeField] private float refreshIntervalSeconds = 5f;

    private void Start()
    {
        StartCoroutine(PollAlarmsRoutine());
    }

    private IEnumerator PollAlarmsRoutine()
    {
        while (true)
        {
            yield return FetchAndApplyAlarms();
            yield return new WaitForSeconds(refreshIntervalSeconds);
        }
    }

    private IEnumerator FetchAndApplyAlarms()
    {
        string url = dashboardApiBaseUrl + "/api/alarms";

        using UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogWarning("Alarm API request failed: " + request.error);
            yield break;
        }

        string json = request.downloadHandler.text;
        AlarmApiResponse response = JsonUtility.FromJson<AlarmApiResponse>(json);

        if (response == null)
        {
            Debug.LogWarning("Alarm API response could not be parsed.");
            yield break;
        }

        ApplyAlarmToText(temperatureText, response.temperature, "Temperature", "°C");
        ApplyAlarmToText(humidityText, response.humidity, "Humidity", "%");
        ApplyAlarmToText(lightText, response.light, "Light", "%");
        ApplyAlarmToText(distanceText, response.distance, "Distance", "cm");
    }

    private void ApplyAlarmToText(TMP_Text targetText, AlarmValueData data, string label, string unit)
    {
        if (targetText == null || data == null)
        {
            return;
        }

        targetText.text = $"{label}: {data.value:F1} {unit} (limit: {data.threshold:F1} {unit})";

        if (data.active)
        {
            targetText.color = alarmColor;
            targetText.fontSize = alarmFontSize;
        }
        else
        {
            targetText.color = normalColor;
            targetText.fontSize = normalFontSize;
        }
    }
}

[System.Serializable]
public class AlarmApiResponse
{
    public AlarmValueData temperature;
    public AlarmValueData humidity;
    public AlarmValueData light;
    public AlarmValueData distance;
    public AlarmThresholds thresholds;
}

[System.Serializable]
public class AlarmValueData
{
    public bool active;
    public float value;
    public float threshold;
    public string message;
}

[System.Serializable]
public class AlarmThresholds
{
    public float temperature;
    public float humidity;
    public float light;
    public float distance;
}