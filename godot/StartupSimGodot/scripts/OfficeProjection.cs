using Godot;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public readonly struct OfficeProjection
{
    public OfficeProjection(float tileWidth, float tileHeight, Vector2 origin)
    {
        TileWidth = tileWidth;
        TileHeight = tileHeight;
        Origin = origin;
    }

    public float TileWidth { get; }
    public float TileHeight { get; }
    public Vector2 Origin { get; }

    public Vector2 CellToScreen(int x, int y)
    {
        return Origin + new Vector2((x - y) * TileWidth * 0.5f, (x + y) * TileHeight * 0.5f);
    }

    public OfficeCell ScreenToCell(Vector2 local)
    {
        var dx = (local.X - Origin.X) / (TileWidth * 0.5f);
        var dy = (local.Y - Origin.Y) / (TileHeight * 0.5f);
        return new OfficeCell((int)Mathf.Floor((dy + dx) * 0.5f), (int)Mathf.Floor((dy - dx) * 0.5f));
    }

    public Vector2[] CellDiamond(int x, int y)
    {
        var top = CellToScreen(x, y);
        return new[]
        {
            top,
            top + new Vector2(TileWidth * 0.5f, TileHeight * 0.5f),
            top + new Vector2(0f, TileHeight),
            top + new Vector2(-TileWidth * 0.5f, TileHeight * 0.5f)
        };
    }

    public Rect2 CellBounds(int x, int y)
    {
        var top = CellToScreen(x, y);
        return new Rect2(top.X - TileWidth * 0.5f, top.Y, TileWidth, TileHeight);
    }

    public Vector2 CellCenter(int x, int y)
    {
        return CellToScreen(x, y) + new Vector2(0f, TileHeight * 0.5f);
    }

    public Vector2 FootAnchor(int x, int y)
    {
        return CellToScreen(x, y) + new Vector2(0f, TileHeight * 0.82f);
    }
}
