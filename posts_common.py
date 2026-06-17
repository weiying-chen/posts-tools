from __future__ import annotations

from pathlib import Path


def is_current_directory_docx(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".docx" and not path.name.startswith("~$")


def default_targets() -> list[Path]:
    return sorted(
        (path for path in Path.cwd().iterdir() if is_current_directory_docx(path)),
        key=lambda path: path.name.lower(),
    )


def resolve_targets(paths: list[Path]) -> list[Path]:
    if not paths:
        return default_targets()

    targets: list[Path] = []
    for path in paths:
        if path.is_dir():
            targets.extend(
                sorted(
                    (child for child in path.iterdir() if is_current_directory_docx(child)),
                    key=lambda child: child.name.lower(),
                )
            )
        else:
            targets.append(path)
    return targets


def output_path_for(source: Path, output_dir: Path | None, suffix: str) -> Path:
    if output_dir is not None:
        return output_dir / source.name
    if not suffix:
        return source
    return source.with_name(f"{source.stem}{suffix}{source.suffix}")
