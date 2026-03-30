using UnityEngine;
using UnityEngine.UI;

public class ControlPanelUI : MonoBehaviour
{
    [SerializeField] private WebSocketManager webSocketManager;

    [Header("RGB Sliders")]
    [SerializeField] private Slider redSlider;
    [SerializeField] private Slider greenSlider;
    [SerializeField] private Slider blueSlider;

    [Header("Servo")]
    [SerializeField] private int servoStep = 15;

    private int currentServoAngle = 0;

    public void SendRgbColor()
    {
        int r = Mathf.RoundToInt(redSlider.value);
        int g = Mathf.RoundToInt(greenSlider.value);
        int b = Mathf.RoundToInt(blueSlider.value);

        string json = $"{{\"type\":\"control_command\",\"command\":\"rgb\",\"r\":{r},\"g\":{g},\"b\":{b}}}";
        webSocketManager.SendJson(json);
    }

    public void TurnLightOff()
    {
        string json = "{\"type\":\"control_command\",\"command\":\"rgb\",\"r\":0,\"g\":0,\"b\":0}";
        webSocketManager.SendJson(json);

        redSlider.value = 0;
        greenSlider.value = 0;
        blueSlider.value = 0;
    }

    public void SetWarmWhite()
    {
        redSlider.value = 255;
        greenSlider.value = 180;
        blueSlider.value = 100;
        SendRgbColor();
    }

    public void SetColdWhite()
    {
        redSlider.value = 180;
        greenSlider.value = 220;
        blueSlider.value = 255;
        SendRgbColor();
    }

    public void OpenBlinds()
    {
        currentServoAngle -= servoStep;
        currentServoAngle = Mathf.Clamp(currentServoAngle, 0, 180);
        SendServoCommand();
    }

    public void CloseBlinds()
    {
        currentServoAngle += servoStep;
        currentServoAngle = Mathf.Clamp(currentServoAngle, 0, 180);
        SendServoCommand();
    }

    private void SendServoCommand()
    {
        string json = $"{{\"type\":\"control_command\",\"command\":\"servo\",\"value\":{currentServoAngle}}}";
        webSocketManager.SendJson(json);
    }
}