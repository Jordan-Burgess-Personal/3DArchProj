from fastapi import APIRouter
from app.schemas import ProjectCreate

router = APIRouter()
_saved_projects = []

@router.get("")
def list_projects():
    return _saved_projects

@router.post("")
def create_project(project: ProjectCreate):
    record = project.model.model_dump()
    record["name"] = project.name
    _saved_projects.append(record)
    return {"message": "Project saved", "project": record}
