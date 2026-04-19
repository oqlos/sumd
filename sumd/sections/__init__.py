"""sumd.sections — pluggable section architecture for SUMD rendering.

Each section is a class implementing the Section protocol (base.py).
Sections declare which profiles they belong to and whether they have
data available for a given RenderContext.

Usage (non-breaking — generate_sumd_content still works as before):
    from sumd.sections import SECTION_REGISTRY, PROFILES
    from sumd.pipeline import RenderPipeline

    pipeline = RenderPipeline(proj_dir)
    content = pipeline.run(profile='rich')
"""

from __future__ import annotations

from sumd.sections.api_stubs import ApiStubsSection
from sumd.sections.architecture import ArchitectureSection
from sumd.sections.call_graph import CallGraphSection
from sumd.sections.code_analysis import CodeAnalysisSection
from sumd.sections.configuration import ConfigurationSection
from sumd.sections.dependencies import DependenciesSection
from sumd.sections.deployment import DeploymentSection
from sumd.sections.environment import EnvironmentSection
from sumd.sections.extras import ExtrasSection
from sumd.sections.interfaces import InterfacesSection
from sumd.sections.metadata import MetadataSection
from sumd.sections.quality import QualitySection
from sumd.sections.refactor_analysis import RefactorAnalysisSection
from sumd.sections.source_snippets import SourceSnippetsSection
from sumd.sections.test_contracts import TestContractsSection
from sumd.sections.workflows import WorkflowsSection

# Registry — ordered list of all section classes.
# RenderPipeline instantiates these in order for a given profile.
SECTION_REGISTRY: list[type] = [
    MetadataSection,
    ArchitectureSection,
    InterfacesSection,
    WorkflowsSection,
    QualitySection,
    ConfigurationSection,
    DependenciesSection,
    DeploymentSection,
    EnvironmentSection,
    ExtrasSection,
    CodeAnalysisSection,
    SourceSnippetsSection,
    CallGraphSection,
    ApiStubsSection,
    TestContractsSection,
    RefactorAnalysisSection,
]

# Profile definitions — which section *names* are included per profile.
# Sections not in a profile are skipped by RenderPipeline.
PROFILES: dict[str, set[str]] = {
    "minimal": {"metadata", "architecture", "workflows", "dependencies", "deployment"},
    "light": {
        "metadata",
        "architecture",
        "interfaces",
        "workflows",
        "quality",
        "configuration",
        "dependencies",
        "deployment",
        "environment",
        "extras",
    },
    "rich": {
        "metadata",
        "architecture",
        "interfaces",
        "workflows",
        "quality",
        "configuration",
        "dependencies",
        "deployment",
        "environment",
        "extras",
        "code_analysis",
        "source_snippets",
        "call_graph",
        "api_stubs",
        "test_contracts",
    },
    # Pre-refactoring analysis profile — focused on code quality signals.
    # Includes architecture + call graph in full, skips documentation sections.
    "refactor": {
        "metadata",
        "architecture",
        "quality",
        "dependencies",
        "source_snippets",
        "refactor_analysis",
    },
}

__all__ = ["SECTION_REGISTRY", "PROFILES"]
