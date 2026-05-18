using Godot;

namespace StartupSim.Godot;

public partial class ArtImportPreviewController : Control
{
    [Export] public Texture2D? OfficeTileAtlas { get; set; }
    [Export] public Texture2D? ZoneStateOverlayAtlas { get; set; }
    [Export] public Texture2D? FacilityAtlas { get; set; }
    [Export] public Texture2D? EmployeeAtlas { get; set; }
    [Export] public Texture2D? EmployeeDirectionAtlas { get; set; }
    [Export] public Texture2D? EmployeeAnimationAtlas { get; set; }
    [Export] public Texture2D? StatusIconAtlas { get; set; }
    [Export] public Texture2D? UiCoreAtlas { get; set; }
    [Export] public Texture2D? FeedbackFxAtlas { get; set; }
    [Export] public Texture2D? RecruitmentPortraitAtlasV1 { get; set; }
    [Export] public Texture2D? RecruitmentPortraitAtlas { get; set; }
    [Export] public Texture2D? OfficeTileExpansionAtlas { get; set; }
    [Export] public Texture2D? FacilityPlacementAtlas { get; set; }
    [Export] public Texture2D? EmployeeStatusIconAtlas { get; set; }
    [Export] public Texture2D? ZoneStateOverlayAtlasV06 { get; set; }
    [Export] public Texture2D? FeedbackPortraitAtlasV07 { get; set; }
    [Export] public Texture2D? MainSceneBackground { get; set; }

    public bool ValidateAtlasPreview()
    {
        return ValidateAtlas(OfficeTileAtlas, 8, 4)
            && ValidateAtlas(ZoneStateOverlayAtlas, 8, 5)
            && ValidateAtlas(FacilityAtlas, 6, 3)
            && ValidateAtlas(EmployeeAtlas, 6, 5)
            && ValidateAtlas(EmployeeDirectionAtlas, 6, 4)
            && ValidateAtlas(StatusIconAtlas, 8, 4)
            && ValidateAtlas(EmployeeAnimationAtlas, 8, 6)
            && ValidateAtlas(UiCoreAtlas, 6, 4)
            && ValidateAtlas(FeedbackFxAtlas, 8, 4)
            && ValidateAtlas(RecruitmentPortraitAtlasV1, 4, 3)
            && ValidateAtlas(RecruitmentPortraitAtlas, 4, 3)
            && ValidateAtlas(OfficeTileExpansionAtlas, 8, 5)
            && ValidateAtlas(FacilityPlacementAtlas, 6, 3)
            && ValidateAtlas(EmployeeStatusIconAtlas, 8, 4)
            && ValidateAtlas(ZoneStateOverlayAtlasV06, 6, 5)
            && ValidateAtlas(FeedbackPortraitAtlasV07, 4, 3)
            && ValidateTexture(MainSceneBackground);
    }

    public string[] ValidateAtlasPreviewReport()
    {
        return new[]
        {
            BuildValidationLine("office-tile-atlas-v0.1", OfficeTileAtlas, 8, 4),
            BuildValidationLine("zone-state-overlay-atlas-v0.1", ZoneStateOverlayAtlas, 8, 5),
            BuildValidationLine("facility-upgrade-atlas-v0.1", FacilityAtlas, 6, 3),
            BuildValidationLine("employee-sprite-atlas-v0.1", EmployeeAtlas, 6, 5),
            BuildValidationLine("employee-direction-variants-v0.1", EmployeeDirectionAtlas, 6, 4),
            BuildValidationLine("status-icon-atlas-v0.1", StatusIconAtlas, 8, 4),
            BuildValidationLine("employee-animation-minimal-v0.1", EmployeeAnimationAtlas, 8, 6),
            BuildValidationLine("ui-core-atlas-v0.1", UiCoreAtlas, 6, 4),
            BuildValidationLine("feedback-fx-atlas-v0.1", FeedbackFxAtlas, 8, 4),
            BuildValidationLine("recruitment-portrait-sheet-v0.1", RecruitmentPortraitAtlasV1, 4, 3),
            BuildValidationLine("recruitment-portrait-sheet-v0.2-angle-balanced", RecruitmentPortraitAtlas, 4, 3),
            BuildValidationLine("office-tile-expansion-atlas-v0.4", OfficeTileExpansionAtlas, 8, 5),
            BuildValidationLine("facility-placement-atlas-v0.3", FacilityPlacementAtlas, 6, 3),
            BuildValidationLine("employee-status-icon-atlas-v0.5", EmployeeStatusIconAtlas, 8, 4),
            BuildValidationLine("zone-state-overlay-atlas-v0.6", ZoneStateOverlayAtlasV06, 6, 5),
            BuildValidationLine("feedback-portrait-sheet-v0.7", FeedbackPortraitAtlasV07, 4, 3),
            BuildTextureValidationLine("company-main-scene-background-v0.7.1", MainSceneBackground)
        };
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

    private bool ValidateTexture(Texture2D? texture)
    {
        return texture != null && texture.GetSize().X > 0 && texture.GetSize().Y > 0;
    }

    private string BuildValidationLine(string atlasName, Texture2D? atlas, int columns, int rows)
    {
        var firstCell = BuildFirstCellPreview(atlas, columns, rows);
        if (atlas == null || firstCell == null)
        {
            return $"{atlasName}: missing";
        }

        var textureSize = atlas.GetSize();
        var cellSize = firstCell.Region.Size;
        return $"{atlasName}: {textureSize.X:0}x{textureSize.Y:0}, {columns}x{rows}, cell {cellSize.X:0.##}x{cellSize.Y:0.##}";
    }

    private string BuildTextureValidationLine(string textureName, Texture2D? texture)
    {
        if (texture == null)
        {
            return $"{textureName}: missing";
        }

        var textureSize = texture.GetSize();
        return $"{textureName}: {textureSize.X:0}x{textureSize.Y:0}";
    }
}
