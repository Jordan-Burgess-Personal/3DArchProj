from fastapi import APIRouter
from app.schemas import ArchitectureModel
from app.services.project_generator import create_project_structure

router = APIRouter()

@router.post("/starter")
def export_starter(model: ArchitectureModel):
    path = create_project_structure(model)
    return {"message": "Starter project structure created", "path": path}
