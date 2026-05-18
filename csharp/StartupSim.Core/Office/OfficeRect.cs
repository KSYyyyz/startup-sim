using System.Collections.Generic;

namespace StartupSim.Core.Office
{
    public readonly struct OfficeRect
    {
        public OfficeRect(int x, int y, int width, int height)
        {
            X = x;
            Y = y;
            Width = width;
            Height = height;
        }

        public int X { get; }
        public int Y { get; }
        public int Width { get; }
        public int Height { get; }

        public IEnumerable<OfficeCell> Cells()
        {
            for (var y = Y; y < Y + Height; y++)
            {
                for (var x = X; x < X + Width; x++)
                {
                    yield return new OfficeCell(x, y);
                }
            }
        }
    }
}
