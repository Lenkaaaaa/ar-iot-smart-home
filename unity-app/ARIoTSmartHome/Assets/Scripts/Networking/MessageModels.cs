using System;

[Serializable]
public class SensorDataEnvelope
{
    public string type;
    public SensorPayload payload;
}

[Serializable]
public class SensorPayload
{
    public float temperature;
    public float humidity;
    public int light;
    public int distance;
}