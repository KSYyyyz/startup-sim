using UnityEngine;
using UnityEngine.UI;

namespace StartupSim.Unity
{
    public sealed class PreparedActionPresenter : MonoBehaviour
    {
        [SerializeField] private Text titleText;
        [SerializeField] private Text commandText;

        public string CurrentCommand { get; private set; } = string.Empty;
        public PreparedActionSnapshot CurrentSnapshot { get; private set; } = new PreparedActionSnapshot();

        public void ShowPreparedAction(string roomName, string command)
        {
            ShowPreparedAction(new PreparedActionSnapshot
            {
                RoomName = roomName,
                Command = command
            });
        }

        public void ShowPreparedAction(PreparedActionSnapshot snapshot)
        {
            CurrentSnapshot = snapshot ?? new PreparedActionSnapshot();
            CurrentCommand = CurrentSnapshot.Command ?? string.Empty;
            if (titleText != null)
            {
                titleText.text = CurrentSnapshot.RoomName;
            }
            if (commandText != null)
            {
                commandText.text = CurrentCommand;
            }
        }

        public void Clear()
        {
            CurrentCommand = string.Empty;
            CurrentSnapshot = new PreparedActionSnapshot();
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
