from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "godot" / "StartupSimGodot" / "data"

CONTENT_FILES: dict[str, tuple[Path, set[str]]] = {
    "zone_types": (
        DATA / "zones" / "zone_types.json",
        {"id", "display_name", "description", "color", "allowed_facility_tags", "output_tags"},
    ),
    "basic_facilities": (
        DATA / "facilities" / "basic_facilities.json",
        {
            "id",
            "display_name",
            "description",
            "zone_ids",
            "tags",
            "footprint",
            "base_cost",
            "monthly_cost",
            "capacity",
            "effects",
        },
    ),
    "facility_upgrades": (
        DATA / "facilities" / "facility_upgrades.json",
        {
            "id",
            "facility_id",
            "level",
            "display_name",
            "upgrade_cost",
            "monthly_cost_delta",
            "effects",
        },
    ),
    "employee_skills": (
        DATA / "employees" / "employee_skills.json",
        {"id", "display_name", "category", "description"},
    ),
    "employee_roles": (
        DATA / "employees" / "employee_roles.json",
        {"id", "display_name", "description", "primary_skill", "target_zone_ids", "salary"},
    ),
    "employee_traits": (
        DATA / "employees" / "employee_traits.json",
        {"id", "display_name", "polarity", "description", "effects"},
    ),
    "employee_growth_tracks": (
        DATA / "employees" / "employee_growth_tracks.json",
        {"id", "role_ids", "skill_id", "max_level", "levels"},
    ),
    "employee_training_actions": (
        DATA / "employees" / "employee_training_actions.json",
        {
            "id",
            "display_name",
            "description",
            "target_skill_ids",
            "duration_days",
            "cost",
            "fatigue_delta",
            "output_penalty",
            "effects",
        },
    ),
}


def main() -> int:
    try:
        bundles = {
            name: load_bundle(path, required) for name, (path, required) in CONTENT_FILES.items()
        }
        validate_references(bundles)
    except ValueError as exc:
        print(f"Godot 内容数据检查失败: {exc}", file=sys.stderr)
        return 1

    item_count = sum(len(bundle["items"]) for bundle in bundles.values())
    print(f"Godot 内容数据检查通过: {len(bundles)} 个文件, {item_count} 条定义")
    return 0


def load_bundle(path: Path, required_fields: set[str]) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"缺少内容文件: {path.relative_to(ROOT)}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 格式错误: {path.relative_to(ROOT)}: {exc}") from exc

    if data.get("schema_version") != "godot-content.g1":
        raise ValueError(f"{path.relative_to(ROOT)} 缺少 schema_version=godot-content.g1")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError(f"{path.relative_to(ROOT)} 必须包含非空 items")

    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{path.relative_to(ROOT)} 第 {index + 1} 项不是对象")

        missing = required_fields - set(item)
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(
                f"{path.relative_to(ROOT)}:{item.get('id', index)} 缺字段 {missing_text}"
            )

        item_id = item["id"]
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"{path.relative_to(ROOT)} 第 {index + 1} 项 id 无效")
        if item_id in seen_ids:
            raise ValueError(f"{path.relative_to(ROOT)} 存在重复 id: {item_id}")
        seen_ids.add(item_id)

    return data


def validate_references(bundles: dict[str, dict[str, Any]]) -> None:
    zone_ids = collect_ids(bundles["zone_types"])
    facility_ids = collect_ids(bundles["basic_facilities"])
    skill_ids = collect_ids(bundles["employee_skills"])
    role_ids = collect_ids(bundles["employee_roles"])

    for facility in bundles["basic_facilities"]["items"]:
        require_known_values(facility, "zone_ids", zone_ids)
        footprint = facility["footprint"]
        if footprint.get("width", 0) <= 0 or footprint.get("height", 0) <= 0:
            raise ValueError(f"{facility['id']} 的 footprint 必须大于 0")

    for upgrade in bundles["facility_upgrades"]["items"]:
        require_known_value(upgrade, "facility_id", facility_ids)
        if upgrade["level"] < 2:
            raise ValueError(f"{upgrade['id']} 的升级等级必须从 2 开始")

    for role in bundles["employee_roles"]["items"]:
        require_known_value(role, "primary_skill", skill_ids)
        require_known_values(role, "target_zone_ids", zone_ids)

    for growth_track in bundles["employee_growth_tracks"]["items"]:
        require_known_value(growth_track, "skill_id", skill_ids)
        require_known_values(growth_track, "role_ids", role_ids)
        levels = growth_track["levels"]
        if not isinstance(levels, list) or not levels:
            raise ValueError(f"{growth_track['id']} 必须包含成长等级")
        if growth_track["max_level"] != max(level["level"] for level in levels):
            raise ValueError(f"{growth_track['id']} max_level 必须等于最高等级")

    for training_action in bundles["employee_training_actions"]["items"]:
        require_known_values(training_action, "target_skill_ids", skill_ids)
        if training_action["duration_days"] <= 0 or training_action["cost"] <= 0:
            raise ValueError(f"{training_action['id']} 培训时间和成本必须大于 0")


def collect_ids(bundle: dict[str, Any]) -> set[str]:
    return {item["id"] for item in bundle["items"]}


def require_known_value(item: dict[str, Any], field: str, allowed: set[str]) -> None:
    value = item[field]
    if value not in allowed:
        raise ValueError(f"{item['id']} 引用了不存在的 {field}: {value}")


def require_known_values(item: dict[str, Any], field: str, allowed: set[str]) -> None:
    values = item[field]
    if not isinstance(values, list) or not values:
        raise ValueError(f"{item['id']} 的 {field} 必须是非空列表")
    for value in values:
        if value not in allowed:
            raise ValueError(f"{item['id']} 引用了不存在的 {field}: {value}")


if __name__ == "__main__":
    raise SystemExit(main())
