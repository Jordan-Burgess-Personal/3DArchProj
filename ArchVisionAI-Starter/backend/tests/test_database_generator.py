from __future__ import annotations

from pathlib import Path

import pytest

from app.schemas import ArchitectureModel, Component, Position
from app.services.database_generator import (
    DATABASE_GENERATION_CAPABILITIES,
    SUPPORTED_DATABASES,
    _component_search_text,
    _get_init_file_details,
    _mongodb_init_content,
    _mysql_init_content,
    _normalize_text,
    _postgresql_init_content,
    _sqlite_init_content,
    detect_database_engine,
    find_supported_database,
    generate_database_files,
    get_skipped_database_components,
    is_database_component,
)


def make_component(
    component_id: str,
    name: str,
    component_type: str = "database",
    technology: str | None = None,
    description: str | None = None,
    metadata: dict | None = None,
) -> Component:
    return Component(
        id=component_id,
        type=component_type,
        name=name,
        technology=technology,
        description=description,
        position=Position(x=0, y=0, z=0),
        metadata=metadata or {},
    )


def make_model(*components: Component, name: str = "Test Project") -> ArchitectureModel:
    return ArchitectureModel(name=name, components=list(components), connections=[])


def normalize(paths):
    return [str(path).replace("\\", "/") for path in paths]


def test_supported_database_aliases():
    assert SUPPORTED_DATABASES["postgres"] == "postgresql"
    assert SUPPORTED_DATABASES["mongo"] == "mongodb"
    assert set(SUPPORTED_DATABASES.values()) == {
        "postgresql", "mysql", "mongodb", "sqlite"
    }


def test_capability_declarations_cover_database_outputs():
    relational = next(
        item for item in DATABASE_GENERATION_CAPABILITIES
        if item["catalog_id"] == "relational-database"
    )
    document = next(
        item for item in DATABASE_GENERATION_CAPABILITIES
        if item["catalog_id"] == "document-database"
    )
    access = next(
        item for item in DATABASE_GENERATION_CAPABILITIES
        if item["catalog_id"] == "database-access"
    )
    assert relational["generated_files"] == ["database/init.sql"]
    assert document["generated_files"] == ["database/init.js"]
    assert access["supported"] is False
    assert access["generated_files"] == []


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, ""), (" PostgreSQL ", "postgresql"), (123, "123"), ("", "")],
)
def test_normalize_text(value, expected):
    assert _normalize_text(value) == expected


def test_component_search_text_includes_fields_and_metadata():
    item = make_component(
        "database-1",
        "Primary Store",
        "service",
        "PostgreSQL",
        "Application records",
        {"provider": "managed", "engine": "postgres"},
    )
    text = _component_search_text(item)
    for expected in [
        "database-1", "primary store", "service", "postgresql",
        "application records", "managed", "postgres",
    ]:
        assert expected in text


@pytest.mark.parametrize(
    ("component_type", "technology"),
    [
        ("database", None),
        ("service", "PostgreSQL"),
        ("service", "Postgres"),
        ("service", "MySQL"),
        ("service", "MongoDB"),
        ("service", "Mongo"),
        ("service", "SQLite"),
    ],
)
def test_is_database_component(component_type, technology):
    item = make_component("db", "Storage", component_type, technology)
    assert is_database_component(item) is True


def test_non_database_component_is_not_database():
    item = make_component("frontend", "Web", "frontend", "React")
    assert is_database_component(item) is False


@pytest.mark.parametrize(
    ("technology", "expected"),
    [
        ("PostgreSQL", "postgresql"),
        ("postgres", "postgresql"),
        ("MySQL", "mysql"),
        ("MongoDB", "mongodb"),
        ("mongo", "mongodb"),
        ("SQLite", "sqlite"),
        ("Redis", None),
    ],
)
def test_detect_database_engine(technology, expected):
    item = make_component("db", "Storage", "database", technology)
    assert detect_database_engine(item) == expected


def test_detect_database_engine_from_metadata():
    item = make_component(
        "storage", "Store", "service", metadata={"engine": "mongodb"}
    )
    assert detect_database_engine(item) == "mongodb"


def test_find_supported_database_uses_first_supported():
    unsupported = make_component("redis", "Redis", "database", "Redis")
    mysql = make_component("mysql", "MySQL", "database", "MySQL")
    mongo = make_component("mongo", "MongoDB", "database", "MongoDB")
    selected, engine = find_supported_database(
        make_model(unsupported, mysql, mongo)
    )
    assert selected.id == "mysql"
    assert engine == "mysql"


def test_find_supported_database_returns_none():
    selected, engine = find_supported_database(
        make_model(make_component("web", "Web", "frontend", "React"))
    )
    assert selected is None
    assert engine is None


def test_skipped_database_components():
    postgres = make_component("postgres", "PostgreSQL", technology="PostgreSQL")
    mysql = make_component("mysql", "MySQL", technology="MySQL")
    redis = make_component("redis", "Redis", technology="Redis")
    assert get_skipped_database_components(
        make_model(postgres, mysql, redis), "postgres"
    ) == ["MySQL", "Redis"]


@pytest.mark.parametrize(
    ("function", "marker"),
    [
        (_postgresql_init_content, "-- Database: PostgreSQL"),
        (_mysql_init_content, "-- Database: MySQL"),
        (_mongodb_init_content, "// Database: MongoDB"),
        (_sqlite_init_content, "-- Database: SQLite"),
    ],
)
def test_init_content_contains_project_and_database(function, marker):
    content = function("Sample Project")
    assert "Generated by ArchVision AI" in content
    assert "Sample Project" in content
    assert marker in content
    assert "app_health" in content
    assert "healthy" in content


@pytest.mark.parametrize(
    ("engine", "filename", "marker"),
    [
        ("postgresql", "init.sql", "SERIAL PRIMARY KEY"),
        ("mysql", "init.sql", "AUTO_INCREMENT PRIMARY KEY"),
        ("mongodb", "init.js", "insertOne"),
        ("sqlite", "init.sql", "AUTOINCREMENT"),
    ],
)
def test_get_init_file_details(engine, filename, marker):
    actual_filename, content = _get_init_file_details(engine, "Project")
    assert actual_filename == filename
    assert marker in content


def test_get_init_file_details_rejects_unknown_engine():
    with pytest.raises(ValueError, match="Unsupported database engine"):
        _get_init_file_details("redis", "Project")


@pytest.mark.parametrize(
    ("technology", "engine", "filename", "marker"),
    [
        ("PostgreSQL", "postgresql", "init.sql", "-- Database: PostgreSQL"),
        ("MySQL", "mysql", "init.sql", "-- Database: MySQL"),
        ("MongoDB", "mongodb", "init.js", "// Database: MongoDB"),
        ("SQLite", "sqlite", "init.sql", "-- Database: SQLite"),
    ],
)
def test_generate_database_files(
    tmp_path: Path, technology, engine, filename, marker
):
    database = make_component("db-1", f"{technology} Database", technology=technology)
    result = generate_database_files(
        tmp_path, make_model(database, name="Generated Project")
    )
    output = tmp_path / "database" / filename
    assert result["database_engine"] == engine
    assert result["generated_database_component_id"] == "db-1"
    assert normalize(result["generated_database_files"]) == [
        f"database/{filename}"
    ]
    assert result["skipped_database_components"] == []
    assert output.is_file()
    assert marker in output.read_text(encoding="utf-8")
    assert "Generated Project" in output.read_text(encoding="utf-8")


def test_generate_database_files_without_supported_database(tmp_path):
    redis = make_component("redis", "Redis", technology="Redis")
    result = generate_database_files(tmp_path, make_model(redis))
    assert result == {
        "database_engine": None,
        "generated_database_component_id": None,
        "generated_database_files": [],
        "skipped_database_components": ["Redis"],
    }
    assert not (tmp_path / "database").exists()


def test_generation_reports_additional_databases_as_skipped(tmp_path):
    postgres = make_component("postgres", "PostgreSQL", technology="PostgreSQL")
    mongo = make_component("mongo", "MongoDB", technology="MongoDB")
    result = generate_database_files(tmp_path, make_model(postgres, mongo))
    assert result["database_engine"] == "postgresql"
    assert result["skipped_database_components"] == ["MongoDB"]


def test_generation_overwrites_owned_file_and_preserves_unowned_file(tmp_path):
    database_dir = tmp_path / "database"
    database_dir.mkdir()
    init_file = database_dir / "init.sql"
    custom_file = database_dir / "custom.sql"
    init_file.write_text("stale", encoding="utf-8")
    custom_file.write_text("custom", encoding="utf-8")
    database = make_component("db", "SQLite", technology="SQLite")
    generate_database_files(tmp_path, make_model(database))
    assert init_file.read_text(encoding="utf-8") != "stale"
    assert custom_file.read_text(encoding="utf-8") == "custom"