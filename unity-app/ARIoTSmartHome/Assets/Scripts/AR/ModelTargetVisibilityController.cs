using UnityEngine;
using Vuforia;

public class ModelTargetVisibilityController : MonoBehaviour
{
    [SerializeField] private GameObject trackedContent;

    private ObserverBehaviour observerBehaviour;

    private void Start()
    {
        observerBehaviour = GetComponent<ObserverBehaviour>();

        if (observerBehaviour != null)
        {
            observerBehaviour.OnTargetStatusChanged += OnTargetStatusChanged;
        }

        if (trackedContent != null)
        {
            trackedContent.SetActive(false);
        }
    }

    private void OnDestroy()
    {
        if (observerBehaviour != null)
        {
            observerBehaviour.OnTargetStatusChanged -= OnTargetStatusChanged;
        }
    }

    private void OnTargetStatusChanged(ObserverBehaviour behaviour, TargetStatus targetStatus)
    {
        bool isTracked = targetStatus.Status == Status.TRACKED;

        if (trackedContent != null)
        {
            trackedContent.SetActive(isTracked);
        }

        Debug.Log($"Model Target status: {targetStatus.Status}");
    }
}