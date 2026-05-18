using UnityEngine;
using UnityEngine.Events;

namespace StartupSim.Unity
{
    public sealed class TurnExecutorPresenter : MonoBehaviour
    {
        [SerializeField] private PreparedActionPresenter preparedActionPresenter;
        [SerializeField] private StartupSimUnityApiClient apiClient;

        public UnityEvent<string> OnTurnSubmitted = new UnityEvent<string>();

        public void ExecutePreparedTurn()
        {
            var command = preparedActionPresenter != null ? preparedActionPresenter.CurrentCommand : string.Empty;
            if (string.IsNullOrWhiteSpace(command))
            {
                return;
            }

            OnTurnSubmitted.Invoke(command);
            if (apiClient != null)
            {
                apiClient.SubmitTurn(command);
            }
        }
    }
}
