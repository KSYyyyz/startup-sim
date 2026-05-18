using UnityEngine;

namespace StartupSim.Unity
{
    public sealed class StartupSimUnityApiClient : MonoBehaviour
    {
        [SerializeField] private string apiBaseUrl = "http://127.0.0.1:8000";

        public string ApiBaseUrl => apiBaseUrl;

        public void SubmitTurn(string command)
        {
            // Unity adapter only: this does not settle TurnEngine rules.
            // The first Unity vertical slice can call the existing API here.
            Debug.Log($"StartupSim submit turn via API: {apiBaseUrl} :: {command}");
        }
    }
}
