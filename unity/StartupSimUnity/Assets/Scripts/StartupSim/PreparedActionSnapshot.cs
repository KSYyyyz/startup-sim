namespace StartupSim.Unity
{
    [System.Serializable]
    public sealed class PreparedActionSnapshot
    {
        public string RoomName;
        public string Command;
        public string ActionType;
        public int Budget;
        public int FundraiseAmount;
        public float EquityOffered;
    }
}
