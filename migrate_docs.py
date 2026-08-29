import os
import shutil

# Create docs directories
os.makedirs("docs/legacy", exist_ok=True)

# Move Resources to legacy
if os.path.exists("Resources"):
    for item in os.listdir("Resources"):
        src = os.path.join("Resources", item)
        dst = os.path.join("docs", "legacy", item)
        shutil.move(src, dst)
    os.rmdir("Resources")
    print("Moved Resources to docs/legacy")

# Move web to legacy
if os.path.exists("web"):
    shutil.move("web", "docs/legacy/web_ui")
    print("Moved web to docs/legacy/web_ui")

# Create missing canonical documents
docs_to_create = [
    "PRD.md",
    "TECH_STACK.md",
    "DESIGN_GUIDELINES.md",
    "GAMEPLAY.md",
    "GAME_ARCHITECTURE.md",
    "API_SPEC.md",
    "DIGITAL_TWIN_ARCHITECTURE.md",
    "AI_ARCHITECTURE.md",
    "AGENT_ARCHITECTURE.md",
    "HARDWARE_ARCHITECTURE.md",
    "DATA_SCHEMA.md",
    "EXPERIMENT_PLAN.md",
    "TEST_PLAN.md",
    "ASSET_GUIDELINES.md",
    "DEPLOYMENT.md",
    "CONTRIBUTING.md"
]

for d in docs_to_create:
    open(f"docs/{d}", "a").close()

# Write MIGRATION_MAP.md
migration_map = """# Migration Map

OLD LOCATION
→ NEW LOCATION
→ STATUS
→ ACTION

Resources/phase-1-research/
→ docs/legacy/phase-1-research/
→ LEGACY
→ Archived old planning docs.

Resources/phase-2-architecture/
→ docs/legacy/phase-2-architecture/
→ LEGACY
→ Archived old planning docs.

Resources/phase-3-digital-twin/
→ docs/legacy/phase-3-digital-twin/
→ LEGACY
→ Archived old planning docs.

Resources/phase-4-ai-intelligence/
→ docs/legacy/phase-4-ai-intelligence/
→ LEGACY
→ Archived old planning docs.

web/
→ docs/legacy/web_ui/
→ LEGACY
→ Archived simplistic web dashboard in favor of new Unity 3D client.
"""

with open("docs/MIGRATION_MAP.md", "w", encoding="utf-8") as f:
    f.write(migration_map)

print("Documentation migration completed.")
