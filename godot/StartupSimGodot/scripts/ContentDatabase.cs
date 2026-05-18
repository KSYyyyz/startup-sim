using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using Godot;

namespace StartupSim.Godot;

public sealed class ContentDatabase
{
    private const string DataRoot = "res://data";

    public IReadOnlyList<ContentItem> ZoneTypes { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> Facilities { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> FacilityUpgrades { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> EmployeeRoles { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> EmployeeTraits { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> EmployeeSkills { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> EmployeeGrowthTracks { get; private set; } = new List<ContentItem>();
    public IReadOnlyList<ContentItem> EmployeeTrainingActions { get; private set; } =
        new List<ContentItem>();

    public void LoadAll()
    {
        ZoneTypes = LoadItems("zones/zone_types.json");
        Facilities = LoadItems("facilities/basic_facilities.json");
        FacilityUpgrades = LoadItems("facilities/facility_upgrades.json");
        EmployeeRoles = LoadItems("employees/employee_roles.json");
        EmployeeTraits = LoadItems("employees/employee_traits.json");
        EmployeeSkills = LoadItems("employees/employee_skills.json");
        EmployeeGrowthTracks = LoadItems("employees/employee_growth_tracks.json");
        EmployeeTrainingActions = LoadItems("employees/employee_training_actions.json");
    }

    private static IReadOnlyList<ContentItem> LoadItems(string relativePath)
    {
        var path = ProjectSettings.GlobalizePath($"{DataRoot}/{relativePath}");
        var json = File.ReadAllText(path);
        var bundle = JsonSerializer.Deserialize<ContentBundle>(
            json,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        return bundle?.Items ?? new List<ContentItem>();
    }
}

public sealed class ContentBundle
{
    [JsonPropertyName("schema_version")]
    public string SchemaVersion { get; set; } = string.Empty;

    [JsonPropertyName("items")]
    public List<ContentItem> Items { get; set; } = new();
}

public sealed class ContentItem
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("display_name")]
    public string DisplayName { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;
}
