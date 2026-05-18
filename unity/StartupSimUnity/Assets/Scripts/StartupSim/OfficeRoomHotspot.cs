using UnityEngine;
using UnityEngine.Events;

namespace StartupSim.Unity
{
    public sealed class OfficeRoomHotspot : MonoBehaviour
    {
        [SerializeField] private string roomId = "product";
        [SerializeField] private string roomName = "产品室";
        [SerializeField] private string preparedCommand = "花10万研发产品";

        public UnityEvent<string, string, string> OnRoomSelected = new UnityEvent<string, string, string>();

        public string RoomId => roomId;
        public string RoomName => roomName;
        public string PreparedCommand => preparedCommand;

        public void Select()
        {
            OnRoomSelected.Invoke(roomId, roomName, preparedCommand);
        }
    }
}
