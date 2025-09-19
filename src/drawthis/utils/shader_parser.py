from pathlib import Path

def parse_shader(file) -> str:
    path = Path.cwd().parent / "render" / "shaders" / file
    if not path.exists():
        raise FileNotFoundError(f"Shader file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return f.read()