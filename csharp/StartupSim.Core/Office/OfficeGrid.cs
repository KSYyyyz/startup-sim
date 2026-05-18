using System;
using System.Collections.Generic;
using System.Linq;

namespace StartupSim.Core.Office
{
    public sealed class OfficeGrid
    {
        private readonly Dictionary<OfficeCell, string> occupants =
            new Dictionary<OfficeCell, string>();

        public OfficeGrid(int width, int height, int cellSize)
        {
            if (width <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(width),
                    "Office grid width must be positive.");
            }

            if (height <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(height),
                    "Office grid height must be positive.");
            }

            if (cellSize <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(cellSize),
                    "Office grid cell size must be positive.");
            }

            Width = width;
            Height = height;
            CellSize = cellSize;
        }

        public int Width { get; }
        public int Height { get; }
        public int CellSize { get; }

        public OfficeCell WorldToCell(float worldX, float worldY)
        {
            return new OfficeCell(
                (int)Math.Floor(worldX / CellSize),
                (int)Math.Floor(worldY / CellSize));
        }

        public bool Contains(OfficeCell cell)
        {
            return cell.X >= 0 && cell.X < Width && cell.Y >= 0 && cell.Y < Height;
        }

        public bool TryOccupy(OfficeRect rect, string occupantId)
        {
            if (string.IsNullOrWhiteSpace(occupantId))
            {
                return false;
            }

            var cells = rect.Cells().ToArray();
            if (cells.Length == 0 || cells.Any(cell => !Contains(cell) || occupants.ContainsKey(cell)))
            {
                return false;
            }

            foreach (var cell in cells)
            {
                occupants[cell] = occupantId;
            }

            return true;
        }

        public void Release(OfficeRect rect)
        {
            foreach (var cell in rect.Cells())
            {
                occupants.Remove(cell);
            }
        }

        public bool IsOccupied(OfficeCell cell)
        {
            return occupants.ContainsKey(cell);
        }

        public string? GetOccupant(OfficeCell cell)
        {
            return occupants.TryGetValue(cell, out var occupantId) ? occupantId : null;
        }

        public OfficeGridSnapshot ToSnapshot()
        {
            return new OfficeGridSnapshot
            {
                Width = Width,
                Height = Height,
                CellSize = CellSize,
                OccupiedCells = occupants
                    .OrderBy(entry => entry.Key.Y)
                    .ThenBy(entry => entry.Key.X)
                    .Select(entry => new OccupiedOfficeCell
                    {
                        X = entry.Key.X,
                        Y = entry.Key.Y,
                        OccupantId = entry.Value
                    })
                    .ToList()
            };
        }
    }
}
