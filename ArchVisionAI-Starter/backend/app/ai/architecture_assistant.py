import os
from openai import OpenAI
from app.schemas import ArchitectureModel

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

DEMO_MODEL = {
    "name": "AI Generated Architecture",
    "description": "Starter architecture generated from plain English input.",
    "components": [
        {"id": "frontend", "type": "frontend", "name": "React Frontend", "technology": "React + Tailwind", "position": {"x": -3, "y": 0, "z": 0}},
        {"id": "api", "type": "backend", "name": "FastAPI Backend", "technology": "Python FastAPI", "position": {"x": 0, "y": 0, "z": 0}},
        {"id": "db", "type": "database", "name": "Project Database", "technology": "PostgreSQL", "position": {"x": 3, "y": 0, "z": 0}},
        {"id": "ai", "type": "external_api", "name": "OpenAI API", "technology": "OpenAI", "position": {"x": 0, "y": 0, "z": -2}},
    ],
    "connections": [
        {"id": "c1", "source": "frontend", "target": "api", "label": "HTTP requests"},
        {"id": "c2", "source": "api", "target": "db", "label": "Reads/writes projects"},
        {"id": "c3", "source": "api", "target": "ai", "label": "AI generation/feedback"},
    ]
}

def generate_architecture(prompt: str) -> dict:
    if not client:
        return DEMO_MODEL

    system = """
    You convert software architecture descriptions into strict JSON matching this schema:
    {name, description, components:[{id,type,name,technology,description,position:{x,y,z}}],
    connections:[{id,source,target,label}]}. Do not include markdown.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content

def review_architecture(model: ArchitectureModel) -> list[str]:
    suggestions = []
    component_types = {c.type for c in model.components}
    if "frontend" in component_types and "backend" not in component_types:
        suggestions.append("Add a backend/API layer so the frontend does not communicate directly with storage or sensitive services.")
    if "database" in component_types and "auth" not in component_types:
        suggestions.append("Consider adding authentication/authorization before allowing project data to be saved or shared.")
    if "backend" in component_types and "database" not in component_types:
        suggestions.append("Add a database if users need saved architecture models, history, or exported project records.")
    if not suggestions:
        suggestions.append("Architecture looks reasonable for an MVP. Next improvement: add logging, validation, and deployment configuration.")
    return suggestions
