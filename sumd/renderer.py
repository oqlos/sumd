"""renderer — backwards-compatibility shim.

All rendering logic has moved to sumd.sections/* and sumd.pipeline.
Only generate_sumd_content() is retained for external callers.
"""

from __future__ import annotations

from pathlib import Path


def generate_sumd_content(
    proj_dir: Path,
    return_sources: bool = False,
    raw_sources: bool = True,
    profile: str = "rich",
) -> str | tuple[str, list[str]]:
    """Generate SUMD.md content from a project directory.

    Delegates to RenderPipeline — kept for backwards compatibility.
    """
    from sumd.pipeline import RenderPipeline  # local import to avoid circular

    return RenderPipeline(proj_dir, raw_sources=raw_sources).run(
        profile=profile, return_sources=return_sources
    )


__all__ = ["generate_sumd_content"]
