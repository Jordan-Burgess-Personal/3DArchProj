from pathlib import Path
from app.schemas import ArchitectureModel
import re

BASE_OUTPUT = Path("generated_projects")

def slugify(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip()).strip("-").lower() or "archvision-project"

def create_project_structure(model: ArchitectureModel) -> str:
    project_dir = BASE_OUTPUT / slugify(model.name)
    project_dir.mkdir(parents=True, exist_ok=True)

    folders = ["frontend/src", "backend/app/routes", "backend/app/services", "database", "docs"]
    for folder in folders:
        (project_dir / folder).mkdir(parents=True, exist_ok=True)

    (project_dir / "README.md").write_text(
        f"""# {model.name}

Generated from ArchVision AI.
""",
        encoding="utf-8",
    )

    (project_dir / "architecture.json").write_text(
        model.model_dump_json(indent=2),
        encoding="utf-8",
    )

    (project_dir / "docker-compose.yml").write_text(
        """# TODO: add services based on architecture model
""",
        encoding="utf-8",
    )

    return str(project_dir)