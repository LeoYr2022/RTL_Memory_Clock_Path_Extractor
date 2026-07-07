#!/usr/bin/env python3
"""Convert clock-path JSON into a Draw.io diagram."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


REQUIRED_TOP_KEYS = ("testcase", "top", "clock_paths")
REQUIRED_PATH_KEYS = (
    "memory_instance",
    "memory_module",
    "clock_pin",
    "clock_net",
    "source_clocks",
    "normal_path",
    "bypass_path",
)

COLUMN_WIDTHS = {
    "source": 160,
    "mux": 150,
    "mux_net": 130,
    "divider": 150,
    "div_net": 130,
    "bypass": 150,
    "clock_net": 130,
    "memory": 150,
}

COLUMN_ORDER = (
    "source",
    "mux",
    "mux_net",
    "divider",
    "div_net",
    "bypass",
    "clock_net",
    "memory",
)

COLUMN_TITLES = {
    "source": "Source Clocks",
    "mux": "Clock Mux",
    "mux_net": "Mux Net",
    "divider": "Divider",
    "div_net": "Div Net",
    "bypass": "Bypass",
    "clock_net": "Memory Clock",
    "memory": "Memory",
}

BASE_X = 40
BASE_Y = 90
COL_GAP = 35
ROW_GAP = 95
NODE_HEIGHT = 48

ROW_FILLS = ("#fff2cc", "#d5e8d4", "#dae8fc", "#f8cecc")

STYLE_HEADER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#eeeeee;"
    "strokeColor=#666666;fontStyle=1;"
)
STYLE_TITLE = "text;html=1;strokeColor=none;fillColor=none;fontSize=18;fontStyle=1;"
STYLE_ROW_BG = "rounded=0;whiteSpace=wrap;html=1;strokeColor=none;opacity=25;"
STYLE_SOURCE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;"
    "strokeColor=#d6b656;"
)
STYLE_BLOCK = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;"
    "strokeColor=#6c8ebf;"
)
STYLE_DIVIDER = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;"
    "strokeColor=#82b366;"
)
STYLE_BYPASS = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
    "strokeColor=#b85450;"
)
STYLE_NET = (
    "ellipse;whiteSpace=wrap;html=1;fillColor=#e1d5e7;"
    "strokeColor=#9673a6;"
)
STYLE_MEMORY = (
    "shape=cylinder3d;whiteSpace=wrap;html=1;boundedLbl=1;"
    "backgroundOutline=1;size=15;fillColor=#f5f5f5;strokeColor=#666666;"
)
STYLE_EDGE = (
    "endArrow=block;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;"
    "strokeColor=#333333;"
)
STYLE_BYPASS_EDGE = STYLE_EDGE + "dashed=1;strokeColor=#b85450;"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert clock-path JSON into a Draw.io .drawio file."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input JSON path.")
    parser.add_argument("--output", required=True, type=Path, help="Output drawio path.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def require_keys(data: dict[str, Any], keys: tuple[str, ...], context: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{context} is missing required keys: {', '.join(missing)}")


def validate_clock_paths(data: dict[str, Any]) -> list[dict[str, Any]]:
    require_keys(data, REQUIRED_TOP_KEYS, "input JSON")
    clock_paths = data["clock_paths"]
    if not isinstance(clock_paths, list) or not clock_paths:
        raise ValueError("clock_paths must be a non-empty list")

    for index, path in enumerate(clock_paths):
        context = f"clock_paths[{index}]"
        if not isinstance(path, dict):
            raise ValueError(f"{context} must be an object")
        require_keys(path, REQUIRED_PATH_KEYS, context)
        for list_key in ("source_clocks", "normal_path", "bypass_path"):
            if not isinstance(path[list_key], list) or not path[list_key]:
                raise ValueError(f"{context}.{list_key} must be a non-empty list")
            if not all(isinstance(item, str) for item in path[list_key]):
                raise ValueError(f"{context}.{list_key} must contain only strings")
        for scalar_key in ("memory_instance", "memory_module", "clock_pin", "clock_net"):
            if not isinstance(path[scalar_key], str) or not path[scalar_key]:
                raise ValueError(f"{context}.{scalar_key} must be a non-empty string")

    return clock_paths


def stable_id(*parts: str) -> str:
    raw = "_".join(parts)
    return re.sub(r"[^A-Za-z0-9_:-]+", "_", raw).strip("_")


def find_first(items: list[str], pattern: str, fallback: str) -> str:
    for item in items:
        if pattern in item:
            return item
    return fallback


def column_x_positions() -> dict[str, int]:
    positions: dict[str, int] = {}
    x_pos = BASE_X
    for column in COLUMN_ORDER:
        positions[column] = x_pos
        x_pos += COLUMN_WIDTHS[column] + COL_GAP
    return positions


def add_cell(
    root: ET.Element,
    cell_id: str,
    value: str,
    style: str,
    x_pos: int,
    y_pos: int,
    width: int,
    height: int,
    parent: str = "1",
) -> ET.Element:
    cell = ET.SubElement(
        root,
        "mxCell",
        {
            "id": cell_id,
            "value": value,
            "style": style,
            "vertex": "1",
            "parent": parent,
        },
    )
    ET.SubElement(
        cell,
        "mxGeometry",
        {
            "x": str(x_pos),
            "y": str(y_pos),
            "width": str(width),
            "height": str(height),
            "as": "geometry",
        },
    )
    return cell


def add_edge(
    root: ET.Element,
    edge_id: str,
    source_id: str,
    target_id: str,
    style: str,
    value: str = "",
    parent: str = "1",
) -> ET.Element:
    edge = ET.SubElement(
        root,
        "mxCell",
        {
            "id": edge_id,
            "value": value,
            "style": style,
            "edge": "1",
            "parent": parent,
            "source": source_id,
            "target": target_id,
        },
    )
    ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
    return edge


def add_header(root: ET.Element, x_positions: dict[str, int]) -> None:
    for column in COLUMN_ORDER:
        add_cell(
            root,
            stable_id("header", column),
            COLUMN_TITLES[column],
            STYLE_HEADER,
            x_positions[column],
            BASE_Y - 55,
            COLUMN_WIDTHS[column],
            34,
        )


def add_clock_path_row(
    root: ET.Element,
    path: dict[str, Any],
    row_index: int,
    x_positions: dict[str, int],
) -> None:
    row_y = BASE_Y + row_index * ROW_GAP
    memory = path["memory_instance"]
    normal_path = path["normal_path"]

    mux = find_first(normal_path, "_clk_mux", f"{memory}_clk_mux")
    mux_net = find_first(normal_path, "_mux_clk", f"{memory}_mux_clk")
    divider = find_first(normal_path, "_clk_divider", f"{memory}_clk_divider")
    div_net = find_first(normal_path, "_div_clk", f"{memory}_div_clk")
    bypass = find_first(normal_path, "_clk_bypass", f"{memory}_clk_bypass")
    clock_net = path["clock_net"]
    memory_pin = f"{memory}.{path['clock_pin']}"

    total_width = (
        sum(COLUMN_WIDTHS[column] for column in COLUMN_ORDER)
        + COL_GAP * (len(COLUMN_ORDER) - 1)
    )
    add_cell(
        root,
        stable_id(memory, "row_bg"),
        "",
        STYLE_ROW_BG + f"fillColor={ROW_FILLS[row_index % len(ROW_FILLS)]};",
        BASE_X - 15,
        row_y - 12,
        total_width + 30,
        NODE_HEIGHT + 24,
    )

    node_specs = {
        "source": ("\n".join(path["source_clocks"]), STYLE_SOURCE),
        "mux": (mux, STYLE_BLOCK),
        "mux_net": (mux_net, STYLE_NET),
        "divider": (divider, STYLE_DIVIDER),
        "div_net": (div_net, STYLE_NET),
        "bypass": (bypass, STYLE_BYPASS),
        "clock_net": (clock_net, STYLE_NET),
        "memory": (memory_pin, STYLE_MEMORY),
    }

    node_ids: dict[str, str] = {}
    for column in COLUMN_ORDER:
        node_id = stable_id(memory, column)
        node_ids[column] = node_id
        value, style = node_specs[column]
        add_cell(
            root,
            node_id,
            value,
            style,
            x_positions[column],
            row_y,
            COLUMN_WIDTHS[column],
            NODE_HEIGHT,
        )

    normal_edges = (
        ("source", "mux"),
        ("mux", "mux_net"),
        ("mux_net", "divider"),
        ("divider", "div_net"),
        ("div_net", "bypass"),
        ("bypass", "clock_net"),
        ("clock_net", "memory"),
    )
    for source_column, target_column in normal_edges:
        add_edge(
            root,
            stable_id(memory, source_column, target_column),
            node_ids[source_column],
            node_ids[target_column],
            STYLE_EDGE,
        )

    add_edge(
        root,
        stable_id(memory, "mux_net", "bypass_path"),
        node_ids["mux_net"],
        node_ids["bypass"],
        STYLE_BYPASS_EDGE,
        "bypass",
    )


def build_drawio(data: dict[str, Any], clock_paths: list[dict[str, Any]]) -> ET.ElementTree:
    x_positions = column_x_positions()
    width = (
        BASE_X * 2
        + sum(COLUMN_WIDTHS[column] for column in COLUMN_ORDER)
        + COL_GAP * (len(COLUMN_ORDER) - 1)
    )
    height = BASE_Y + ROW_GAP * len(clock_paths) + 70

    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": "2026-07-07T00:00:00.000Z",
            "agent": "json_clock_paths_to_drawio.py",
            "version": "24.7.17",
            "type": "device",
        },
    )
    diagram = ET.SubElement(
        mxfile,
        "diagram",
        {
            "id": stable_id(data["testcase"], "diagram"),
            "name": data["testcase"],
        },
    )
    graph = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": str(width),
            "dy": str(height),
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(width),
            "pageHeight": str(height),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(graph, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    title = f"{data['testcase']} clock paths ({data['top']})"
    add_cell(root, "title", title, STYLE_TITLE, BASE_X, 20, width - BASE_X * 2, 30)
    add_header(root, x_positions)
    for row_index, path in enumerate(clock_paths):
        add_clock_path_row(root, path, row_index, x_positions)

    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    return tree


def main() -> int:
    args = parse_args()
    try:
        data = load_json(args.input)
        clock_paths = validate_clock_paths(data)
        tree = build_drawio(data, clock_paths)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tree.write(args.output, encoding="utf-8", xml_declaration=True)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
