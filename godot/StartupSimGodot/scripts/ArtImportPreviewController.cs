using Godot;

namespace StartupSim.Godot;

public partial class ArtImportPreviewController : Control
{
    [Export] public Texture2D? OfficeTileAtlas { get; set; }
    [Export] public Texture2D? FacilityAtlas { get; set; }
    [Export] public Texture2D? EmployeeAtlas { get; set; }
    [Export] public Texture2D? StatusIconAtlas { get; set; }
    [Export] public Texture2D? RecruitmentPortraitAtlas { get; set; }

    public bool ValidateAtlasPreview()
    {
        return ValidateAtlas(OfficeTileAtlas, 8, 4)
            && ValidateAtlas(FacilityAtlas, 6, 3)
            && ValidateAtlas(EmployeeAtlas, 6, 5)
            && ValidateAtlas(StatusIconAtlas, 8, 4)
            && ValidateAtlas(RecruitmentPortraitAtlas, 4, 3);
    }

    public AtlasTexture? BuildFirstCellPreview(Texture2D? atlas, int columns, int rows)
    {
        if (atlas == null || columns <= 0 || rows <= 0)
        {
            return null;
        }

        var textureSize = atlas.GetSize();
        var preview = new AtlasTexture
        {
            Atlas = atlas,
            Region = new Rect2(0, 0, textureSize.X / columns, textureSize.Y / rows)
        };
        return preview;
    }

    private bool ValidateAtlas(Texture2D? atlas, int columns, int rows)
    {
        var firstCell = BuildFirstCellPreview(atlas, columns, rows);
        return firstCell != null && firstCell.Region.Size.X > 0 && firstCell.Region.Size.Y > 0;
    }
}
