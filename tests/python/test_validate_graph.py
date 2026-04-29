import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_graph_schema_is_valid_json():
    with open(REPO / "graph.schema.json") as f:
        schema = json.load(f)
    assert schema["$schema"].startswith("http")
    assert "properties" in schema
    for required in ("version", "nodes", "edges", "dynamic_templates", "branch_labels"):
        assert required in schema["required"], f"{required} missing from required list"


def test_graph_schema_node_shape():
    with open(REPO / "graph.schema.json") as f:
        schema = json.load(f)
    node = schema["properties"]["nodes"]["items"]
    for required in ("id", "module_file", "phase", "exec_type", "tier", "required_output_sections"):
        assert required in node["required"]
    assert set(node["properties"]["exec_type"]["enum"]) == {"inline", "spawn"}
    assert set(node["properties"]["tier"]["enum"]) == {"large", "medium", "small", "no-llm"}


def test_graph_schema_edge_kinds():
    with open(REPO / "graph.schema.json") as f:
        schema = json.load(f)
    edge = schema["properties"]["edges"]["items"]
    assert set(edge["properties"]["kind"]["enum"]) == {"forward", "back", "conditional", "dynamic"}
