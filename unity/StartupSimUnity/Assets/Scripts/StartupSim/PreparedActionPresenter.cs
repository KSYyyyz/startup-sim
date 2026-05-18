using UnityEngine;
using UnityEngine.UI;

namespace StartupSim.Unity
{
    public sealed class PreparedActionPresenter : MonoBehaviour
    {
        [SerializeField] private Text titleText;
        [SerializeField] private Text commandText;

        public string CurrentCommand { get; private set; } = string.Empty;

        public void ShowPreparedAction(string roomName, string command)
        {
            CurrentCommand = command ?? string.Empty;
            if (titleText != null)
            {
                titleText.text = roomName;
            }
            if (commandText != null)
            {
                commandText.text = CurrentCommand;
            }
        }

        public void Clear()
        {
            CurrentCommand = string.Empty;
            if (titleText != null)
            {
                titleText.text = string.Empty;
            }
            if (commandText != null)
            {
                commandText.text = string.Empty;
            }
        }
    }
}
