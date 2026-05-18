using System;

namespace StartupSim.Core.Office
{
    public readonly struct OfficeCell : IEquatable<OfficeCell>
    {
        public OfficeCell(int x, int y)
        {
            X = x;
            Y = y;
        }

        public int X { get; }
        public int Y { get; }

        public bool Equals(OfficeCell other)
        {
            return X == other.X && Y == other.Y;
        }

        public override bool Equals(object? obj)
        {
            return obj is OfficeCell other && Equals(other);
        }

        public override int GetHashCode()
        {
            unchecked
            {
                return (X * 397) ^ Y;
            }
        }

        public override string ToString()
        {
            return $"{X},{Y}";
        }
    }
}
