using System.Text.Json;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class GoldenCaseTests
{
    [Fact]
    public void ProductInvestmentGoldenCaseDocumentsPythonReference()
    {
        var root = FindRepositoryRoot();
        var goldenPath = Path.Combine(root, "csharp", "golden-cases", "month01_product_investment.json");
        var json = File.ReadAllText(goldenPath);
        using var document = JsonDocument.Parse(json);
        var rootElement = document.RootElement;

        Assert.Equal("python-turn-engine-reference", rootElement.GetProperty("authority").GetString());
        Assert.Equal("花10万研发产品", rootElement.GetProperty("input").GetProperty("command").GetString());
        Assert.Equal(2, rootElement.GetProperty("expected").GetProperty("month").GetInt32());
        Assert.Equal(-220000, rootElement.GetProperty("expected").GetProperty("cash_change").GetInt32());
        Assert.Equal(8, rootElement.GetProperty("expected").GetProperty("product_change").GetInt32());
    }

    private static string FindRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory != null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "pyproject.toml")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new DirectoryNotFoundException("Could not find repository root.");
    }
}
