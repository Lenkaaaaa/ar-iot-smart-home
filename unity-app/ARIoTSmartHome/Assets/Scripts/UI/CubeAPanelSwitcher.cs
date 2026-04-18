using UnityEngine;

public class CubeAPanelSwitcher : MonoBehaviour
{
    [SerializeField] private GameObject monitoringPanel;
    [SerializeField] private GameObject controlPanel;

    private void Start()
    {
        ShowMonitoringPanel();
    }

    public void ShowMonitoringPanel()
    {
        Debug.Log("ShowMonitoringPanel called");
        if (monitoringPanel != null) monitoringPanel.SetActive(true);
        if (controlPanel != null) controlPanel.SetActive(false);
    }

    public void ShowControlPanel()
    {
        Debug.Log("ShowControlPanel called");
        if (monitoringPanel != null) monitoringPanel.SetActive(false);
        if (controlPanel != null) controlPanel.SetActive(true);
    }
}