# todocs

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `todocs`
- **version**: `0.1.11`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, pyqual.yaml, goal.yaml, src(2 mod), project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: todocs;
  version: 0.1.11;
}

dependencies {
  runtime: "tomli>=2.0; python_version<'3.11', pyyaml>=6.0, jinja2>=3.1, radon>=6.0, rich>=13.0, click>=8.1";
  dev: "pytest>=7.0, pytest-cov, black, ruff";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="todocs"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=pip install -e .;
}

workflow[name="dev"] {
  trigger: manual;
  step-1: run cmd=pip install -e ".[dev]";
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=python -m pytest tests/ -v;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=python -m pytest tests/ -v --cov=todocs --cov-report=term-missing;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=ruff check todocs/ tests/;
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=black todocs/ tests/;
  step-2: run cmd=ruff check --fix todocs/ tests/;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf dist/ build/ *.egg-info todocs/*.egg-info;
  step-2: run cmd=find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true;
  step-3: run cmd=find . -type f -name "*.pyc" -delete;
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd=python -m build;
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd=python -m twine upload dist/*;
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: docker-compose;
  python_version: >=3.10;
}
```

### Source Modules

- `todocs.cli`
- `todocs.core`

## Workflows

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: todocs-quality

  metrics:
    cc_max: 15
    critical_max: 0

  custom_tools:
    - name: code2llm_todocs
      binary: code2llm
      command: >-
        code2llm {workdir} -f toon -o ./project --no-chunk
        --exclude .git .venv .venv_test build dist __pycache__ .pytest_cache .code2llm_cache .benchmarks .mypy_cache .ruff_cache node_modules
      output: ""
      allow_failure: false

    - name: vallm_todocs
      binary: vallm
      command: >-
        vallm batch {workdir} --recursive --format toon --output ./project
        --exclude .git,.venv,.venv_test,build,dist,__pycache__,.pytest_cache,.code2llm_cache,.benchmarks,.mypy_cache,.ruff_cache,node_modules
      output: ""
      allow_failure: false

  stages:
    - name: analyze
      tool: code2llm_todocs
      optional: true
      timeout: 0

    - name: validate
      tool: vallm_todocs
      optional: true
      timeout: 0

    - name: lint
      tool: ruff
      optional: true

    - name: fix
      tool: prefact
      optional: true
      when: metrics_fail
      timeout: 900

    - name: test
      run: python3 -m pytest -q
      when: always

  loop:
    max_iterations: 3
    on_fail: report

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Dependencies

### Runtime

```text markpact:deps python
tomli>=2.0; python_version<'3.11'
pyyaml>=6.0
jinja2>=3.1
radon>=6.0
rich>=13.0
click>=8.1
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-cov
black
ruff
```

## Source Map

*Top 1 modules by symbol density — signatures for LLM orientation.*

### `todocs.core` (`todocs/core.py`)

```python
def _run_extraction_phase(project_path, profile)  # CC=2, fan=11
def _run_analysis_phase(project_path, profile, scan_filter)  # CC=2, fan=11
def _run_scoring_phase(project_path, profile)  # CC=1, fan=4
def scan_project(project_path, max_depth)  # CC=1, fan=5
def _get_default_excludes()  # CC=1, fan=0
def _is_valid_project_dir(child, exclude)  # CC=6, fan=4
def _discover_projects(root_path, exclude)  # CC=4, fan=8
def _scan_project_with_progress(project_dir, idx, total, max_depth, progress_callback)  # CC=3, fan=3
def scan_organization(root_path, exclude, max_depth, progress_callback)  # CC=3, fan=5
def generate_articles(profiles, output_dir, org_name, org_url, include_comparison, include_categories, include_health)  # CC=6, fan=13
def _categorize(profile)  # CC=9, fan=4
def _generate_summary(profile)  # CC=12, fan=6 ⚠
class TechStack:  # Detected technology stack.
class CodeStats:  # Aggregated code statistics.
class ProjectMetadata:  # Extracted project metadata.
class MaturityProfile:  # Project maturity assessment.
class ProjectProfile:  # Complete project profile for article generation.
    def to_dict()  # CC=1
    def to_json(indent)  # CC=1
```

## Call Graph

*63 nodes · 65 edges · 17 modules · CC̄=3.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `main` *(in examples.article_sections_demo)* | 4 | 0 | 64 | **64** |
| `main` *(in examples.scan_single)* | 25 ⚠ | 0 | 57 | **57** |
| `print_health_summary` *(in examples.organization_health_report)* | 9 | 1 | 48 | **49** |
| `render_architecture` *(in todocs.generators.article_sections)* | 12 ⚠ | 2 | 33 | **35** |
| `main` *(in examples.scan_org)* | 9 | 0 | 26 | **26** |
| `main` *(in examples.api_surface_deep)* | 3 | 0 | 26 | **26** |
| `analyze_public_symbols` *(in examples.api_surface_deep)* | 7 | 1 | 24 | **25** |
| `main` *(in examples.organization_health_report)* | 4 | 0 | 23 | **23** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/todocs
# nodes: 63 | edges: 65 | modules: 17
# CC̄=3.6

HUBS[20]:
  examples.article_sections_demo.main
    CC=4  in:0  out:64  total:64
  examples.scan_single.main
    CC=25  in:0  out:57  total:57
  examples.organization_health_report.print_health_summary
    CC=9  in:1  out:48  total:49
  todocs.generators.article_sections.render_architecture
    CC=12  in:2  out:33  total:35
  examples.scan_org.main
    CC=9  in:0  out:26  total:26
  examples.api_surface_deep.main
    CC=3  in:0  out:26  total:26
  examples.api_surface_deep.analyze_public_symbols
    CC=7  in:1  out:24  total:25
  examples.organization_health_report.main
    CC=4  in:0  out:23  total:23
  examples.custom_analysis._analyze_api_surface
    CC=10  in:1  out:22  total:23
  todocs.generators.article_sections.render_metrics
    CC=4  in:3  out:19  total:22
  todocs.cli.progress.generate_without_rich
    CC=6  in:1  out:20  total:21
  todocs.cli.commands.readme
    CC=4  in:0  out:21  total:21
  examples.custom_analysis._analyze_import_graph
    CC=7  in:1  out:19  total:20
  todocs.generators.article_sections.render_tech_stack
    CC=8  in:3  out:16  total:19
  todocs.cli.commands.export_cmd
    CC=3  in:0  out:19  total:19
  todocs.cli.commands.compare
    CC=2  in:0  out:18  total:18
  todocs.core.generate_articles
    CC=6  in:3  out:15  total:18
  examples.custom_analysis._analyze_toon_files
    CC=6  in:1  out:17  total:18
  todocs.cli.commands.index
    CC=2  in:0  out:17  total:17
  todocs.cli.commands.inspect
    CC=3  in:0  out:17  total:17

MODULES:
  examples.api_surface_deep  [7 funcs]
    analyze_cli_commands  CC=7  out:13
    analyze_entry_points  CC=3  out:5
    analyze_public_symbols  CC=7  out:24
    analyze_rest_endpoints  CC=6  out:15
    analyze_symbol_sources  CC=5  out:13
    main  CC=3  out:26
    print_section  CC=1  out:4
  examples.article_sections_demo  [1 funcs]
    main  CC=4  out:64
  examples.custom_analysis  [8 funcs]
    _analyze_api_surface  CC=10  out:22
    _analyze_code_metrics  CC=3  out:11
    _analyze_docker  CC=7  out:13
    _analyze_import_graph  CC=7  out:19
    _analyze_makefile  CC=4  out:6
    _analyze_toon_files  CC=6  out:17
    _print_section_header  CC=1  out:3
    main  CC=2  out:12
  examples.organization_health_report  [3 funcs]
    analyze_maturity_distribution  CC=5  out:6
    main  CC=4  out:23
    print_health_summary  CC=9  out:48
  examples.scan_org  [1 funcs]
    main  CC=9  out:26
  examples.scan_single  [1 funcs]
    main  CC=25  out:57
  todocs.analyzers.api_surface  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.code_metrics  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.import_graph  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.structure  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.utils  [1 funcs]
    should_skip  CC=4  out:1
  todocs.cli.commands  [8 funcs]
    cards  CC=1  out:15
    compare  CC=2  out:18
    export_cmd  CC=3  out:19
    health  CC=1  out:15
    index  CC=2  out:17
    inspect  CC=3  out:17
    readme  CC=4  out:21
    status  CC=1  out:15
  todocs.cli.progress  [6 funcs]
    discover_and_show_progress  CC=1  out:8
    generate_articles_with_progress  CC=1  out:7
    generate_with_rich  CC=3  out:11
    generate_without_rich  CC=6  out:20
    print_project_summary  CC=7  out:10
    scan_with_progress  CC=1  out:10
  todocs.core  [12 funcs]
    _categorize  CC=9  out:7
    _discover_projects  CC=4  out:8
    _generate_summary  CC=12  out:11
    _get_default_excludes  CC=1  out:0
    _is_valid_project_dir  CC=6  out:4
    _run_analysis_phase  CC=2  out:13
    _run_extraction_phase  CC=2  out:14
    _run_scoring_phase  CC=1  out:4
    _scan_project_with_progress  CC=3  out:3
    generate_articles  CC=6  out:15
  todocs.generators.article  [1 funcs]
    _render_article  CC=3  out:15
  todocs.generators.article_sections  [9 funcs]
    render_api_surface  CC=8  out:14
    render_architecture  CC=12  out:33
    render_dependencies  CC=8  out:12
    render_frontmatter  CC=6  out:5
    render_header  CC=7  out:8
    render_maturity  CC=3  out:6
    render_metrics  CC=4  out:19
    render_overview  CC=6  out:6
    render_tech_stack  CC=8  out:16
  todocs.utils  [1 funcs]
    create_scan_filter  CC=2  out:10

EDGES:
  examples.custom_analysis._analyze_import_graph → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_api_surface → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_toon_files → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_makefile → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_docker → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_code_metrics → examples.custom_analysis._print_section_header
  examples.custom_analysis.main → examples.custom_analysis._analyze_import_graph
  examples.custom_analysis.main → examples.custom_analysis._analyze_api_surface
  examples.custom_analysis.main → examples.custom_analysis._analyze_toon_files
  examples.custom_analysis.main → examples.custom_analysis._analyze_makefile
  examples.custom_analysis.main → examples.custom_analysis._analyze_docker
  examples.custom_analysis.main → examples.custom_analysis._analyze_code_metrics
  examples.organization_health_report.print_health_summary → examples.organization_health_report.analyze_maturity_distribution
  examples.organization_health_report.main → todocs.core.scan_organization
  examples.article_sections_demo.main → todocs.core.scan_project
  examples.scan_single.main → todocs.core.scan_project
  examples.scan_org.main → todocs.core.scan_organization
  examples.scan_org.main → todocs.core.generate_articles
  examples.api_surface_deep.analyze_entry_points → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_cli_commands → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_public_symbols → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_rest_endpoints → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_symbol_sources → examples.api_surface_deep.print_section
  examples.api_surface_deep.main → examples.api_surface_deep.analyze_entry_points
  todocs.core._run_scoring_phase → todocs.core._categorize
  todocs.core._run_scoring_phase → todocs.core._generate_summary
  todocs.core.scan_project → todocs.utils.create_scan_filter
  todocs.core.scan_project → todocs.core._run_extraction_phase
  todocs.core.scan_project → todocs.core._run_analysis_phase
  todocs.core.scan_project → todocs.core._run_scoring_phase
  todocs.core._discover_projects → todocs.core._get_default_excludes
  todocs.core._discover_projects → todocs.core._is_valid_project_dir
  todocs.core._scan_project_with_progress → todocs.core.scan_project
  todocs.core.scan_organization → todocs.core._discover_projects
  todocs.core.scan_organization → todocs.core._scan_project_with_progress
  todocs.cli.progress.discover_and_show_progress → todocs.core._discover_projects
  todocs.cli.progress.scan_with_progress → todocs.core.scan_organization
  todocs.cli.progress.generate_articles_with_progress → todocs.core.generate_articles
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.discover_and_show_progress
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.print_project_summary
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.scan_with_progress
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.generate_articles_with_progress
  todocs.cli.progress.generate_without_rich → todocs.core._discover_projects
  todocs.cli.progress.generate_without_rich → todocs.core.generate_articles
  todocs.cli.commands.inspect → todocs.core.scan_project
  todocs.cli.commands.compare → todocs.core.scan_organization
  todocs.cli.commands.health → todocs.core.scan_organization
  todocs.cli.commands.readme → todocs.core.scan_organization
  todocs.cli.commands.status → todocs.core.scan_organization
  todocs.cli.commands.cards → todocs.core.scan_organization
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**
- assert `name == "sample-project"`
- assert `generated_by == "todocs v0.1.0"`
- assert `name == "sample-project"`

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/todocs
# nodes: 63 | edges: 65 | modules: 17
# CC̄=3.6

HUBS[20]:
  examples.article_sections_demo.main
    CC=4  in:0  out:64  total:64
  examples.scan_single.main
    CC=25  in:0  out:57  total:57
  examples.organization_health_report.print_health_summary
    CC=9  in:1  out:48  total:49
  todocs.generators.article_sections.render_architecture
    CC=12  in:2  out:33  total:35
  examples.scan_org.main
    CC=9  in:0  out:26  total:26
  examples.api_surface_deep.main
    CC=3  in:0  out:26  total:26
  examples.api_surface_deep.analyze_public_symbols
    CC=7  in:1  out:24  total:25
  examples.organization_health_report.main
    CC=4  in:0  out:23  total:23
  examples.custom_analysis._analyze_api_surface
    CC=10  in:1  out:22  total:23
  todocs.generators.article_sections.render_metrics
    CC=4  in:3  out:19  total:22
  todocs.cli.progress.generate_without_rich
    CC=6  in:1  out:20  total:21
  todocs.cli.commands.readme
    CC=4  in:0  out:21  total:21
  examples.custom_analysis._analyze_import_graph
    CC=7  in:1  out:19  total:20
  todocs.generators.article_sections.render_tech_stack
    CC=8  in:3  out:16  total:19
  todocs.cli.commands.export_cmd
    CC=3  in:0  out:19  total:19
  todocs.cli.commands.compare
    CC=2  in:0  out:18  total:18
  todocs.core.generate_articles
    CC=6  in:3  out:15  total:18
  examples.custom_analysis._analyze_toon_files
    CC=6  in:1  out:17  total:18
  todocs.cli.commands.index
    CC=2  in:0  out:17  total:17
  todocs.cli.commands.inspect
    CC=3  in:0  out:17  total:17

MODULES:
  examples.api_surface_deep  [7 funcs]
    analyze_cli_commands  CC=7  out:13
    analyze_entry_points  CC=3  out:5
    analyze_public_symbols  CC=7  out:24
    analyze_rest_endpoints  CC=6  out:15
    analyze_symbol_sources  CC=5  out:13
    main  CC=3  out:26
    print_section  CC=1  out:4
  examples.article_sections_demo  [1 funcs]
    main  CC=4  out:64
  examples.custom_analysis  [8 funcs]
    _analyze_api_surface  CC=10  out:22
    _analyze_code_metrics  CC=3  out:11
    _analyze_docker  CC=7  out:13
    _analyze_import_graph  CC=7  out:19
    _analyze_makefile  CC=4  out:6
    _analyze_toon_files  CC=6  out:17
    _print_section_header  CC=1  out:3
    main  CC=2  out:12
  examples.organization_health_report  [3 funcs]
    analyze_maturity_distribution  CC=5  out:6
    main  CC=4  out:23
    print_health_summary  CC=9  out:48
  examples.scan_org  [1 funcs]
    main  CC=9  out:26
  examples.scan_single  [1 funcs]
    main  CC=25  out:57
  todocs.analyzers.api_surface  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.code_metrics  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.import_graph  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.structure  [1 funcs]
    _should_skip  CC=1  out:1
  todocs.analyzers.utils  [1 funcs]
    should_skip  CC=4  out:1
  todocs.cli.commands  [8 funcs]
    cards  CC=1  out:15
    compare  CC=2  out:18
    export_cmd  CC=3  out:19
    health  CC=1  out:15
    index  CC=2  out:17
    inspect  CC=3  out:17
    readme  CC=4  out:21
    status  CC=1  out:15
  todocs.cli.progress  [6 funcs]
    discover_and_show_progress  CC=1  out:8
    generate_articles_with_progress  CC=1  out:7
    generate_with_rich  CC=3  out:11
    generate_without_rich  CC=6  out:20
    print_project_summary  CC=7  out:10
    scan_with_progress  CC=1  out:10
  todocs.core  [12 funcs]
    _categorize  CC=9  out:7
    _discover_projects  CC=4  out:8
    _generate_summary  CC=12  out:11
    _get_default_excludes  CC=1  out:0
    _is_valid_project_dir  CC=6  out:4
    _run_analysis_phase  CC=2  out:13
    _run_extraction_phase  CC=2  out:14
    _run_scoring_phase  CC=1  out:4
    _scan_project_with_progress  CC=3  out:3
    generate_articles  CC=6  out:15
  todocs.generators.article  [1 funcs]
    _render_article  CC=3  out:15
  todocs.generators.article_sections  [9 funcs]
    render_api_surface  CC=8  out:14
    render_architecture  CC=12  out:33
    render_dependencies  CC=8  out:12
    render_frontmatter  CC=6  out:5
    render_header  CC=7  out:8
    render_maturity  CC=3  out:6
    render_metrics  CC=4  out:19
    render_overview  CC=6  out:6
    render_tech_stack  CC=8  out:16
  todocs.utils  [1 funcs]
    create_scan_filter  CC=2  out:10

EDGES:
  examples.custom_analysis._analyze_import_graph → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_api_surface → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_toon_files → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_makefile → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_docker → examples.custom_analysis._print_section_header
  examples.custom_analysis._analyze_code_metrics → examples.custom_analysis._print_section_header
  examples.custom_analysis.main → examples.custom_analysis._analyze_import_graph
  examples.custom_analysis.main → examples.custom_analysis._analyze_api_surface
  examples.custom_analysis.main → examples.custom_analysis._analyze_toon_files
  examples.custom_analysis.main → examples.custom_analysis._analyze_makefile
  examples.custom_analysis.main → examples.custom_analysis._analyze_docker
  examples.custom_analysis.main → examples.custom_analysis._analyze_code_metrics
  examples.organization_health_report.print_health_summary → examples.organization_health_report.analyze_maturity_distribution
  examples.organization_health_report.main → todocs.core.scan_organization
  examples.article_sections_demo.main → todocs.core.scan_project
  examples.scan_single.main → todocs.core.scan_project
  examples.scan_org.main → todocs.core.scan_organization
  examples.scan_org.main → todocs.core.generate_articles
  examples.api_surface_deep.analyze_entry_points → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_cli_commands → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_public_symbols → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_rest_endpoints → examples.api_surface_deep.print_section
  examples.api_surface_deep.analyze_symbol_sources → examples.api_surface_deep.print_section
  examples.api_surface_deep.main → examples.api_surface_deep.analyze_entry_points
  todocs.core._run_scoring_phase → todocs.core._categorize
  todocs.core._run_scoring_phase → todocs.core._generate_summary
  todocs.core.scan_project → todocs.utils.create_scan_filter
  todocs.core.scan_project → todocs.core._run_extraction_phase
  todocs.core.scan_project → todocs.core._run_analysis_phase
  todocs.core.scan_project → todocs.core._run_scoring_phase
  todocs.core._discover_projects → todocs.core._get_default_excludes
  todocs.core._discover_projects → todocs.core._is_valid_project_dir
  todocs.core._scan_project_with_progress → todocs.core.scan_project
  todocs.core.scan_organization → todocs.core._discover_projects
  todocs.core.scan_organization → todocs.core._scan_project_with_progress
  todocs.cli.progress.discover_and_show_progress → todocs.core._discover_projects
  todocs.cli.progress.scan_with_progress → todocs.core.scan_organization
  todocs.cli.progress.generate_articles_with_progress → todocs.core.generate_articles
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.discover_and_show_progress
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.print_project_summary
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.scan_with_progress
  todocs.cli.progress.generate_with_rich → todocs.cli.progress.generate_articles_with_progress
  todocs.cli.progress.generate_without_rich → todocs.core._discover_projects
  todocs.cli.progress.generate_without_rich → todocs.core.generate_articles
  todocs.cli.commands.inspect → todocs.core.scan_project
  todocs.cli.commands.compare → todocs.core.scan_organization
  todocs.cli.commands.health → todocs.core.scan_organization
  todocs.cli.commands.readme → todocs.core.scan_organization
  todocs.cli.commands.status → todocs.core.scan_organization
  todocs.cli.commands.cards → todocs.core.scan_organization
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 64f 43927L | python:45,yaml:14,txt:2,toml:1,shell:1 | 2026-04-29
# CC̄=3.6 | critical:3/371 | dups:0 | cycles:0

HEALTH[3]:
  🟡 CC    main CC=25 (limit:15)
  🟡 CC    _summarize_with_nlp CC=16 (limit:15)
  🟡 CC    extract_key_features CC=16 (limit:15)

REFACTOR[1]:
  1. split 3 high-CC methods  (CC>15)

PIPELINES[231]:
  [1] Src [main]: main → _analyze_import_graph → _print_section_header
      PURITY: 100% pure
  [2] Src [main]: main → scan_organization → _discover_projects → _get_default_excludes
      PURITY: 100% pure
  [3] Src [main]: main → scan_project → create_scan_filter
      PURITY: 100% pure
  [4] Src [main]: main → scan_project → create_scan_filter
      PURITY: 100% pure
  [5] Src [main]: main → scan_organization → _discover_projects → _get_default_excludes
      PURITY: 100% pure

LAYERS:
  examples/                       CC̄=6.0    ←in:0  →out:27  !! split
  │ organization_health_report   201L  0C    6m  CC=9      ←0
  │ custom_analysis            187L  0C    8m  CC=10     ←0
  │ api_surface_deep           176L  0C    7m  CC=7      ←0
  │ article_sections_demo      119L  0C    1m  CC=4      ←0
  │ !! scan_single                 97L  0C    1m  CC=25     ←0
  │ scan_org                    61L  0C    1m  CC=9      ←0
  │
  todocs/                         CC̄=4.4    ←in:19  →out:0
  │ !! analysis.yaml            33924L  0C    0m  CC=0.0    ←0
  │ !! project.yaml               598L  0C    0m  CC=0.0    ←0
  │ comparison                 489L  1C   22m  CC=14     ←0
  │ article_sections           460L  0C   18m  CC=12     ←2
  │ core                       444L  5C   14m  CC=12     ←6
  │ !! readme_parser              361L  1C   13m  CC=16     ←0
  │ toon_parser                343L  1C   17m  CC=11     ←0
  │ commands                   289L  0C   11m  CC=4      ←0
  │ api_surface                289L  1C   13m  CC=13     ←0
  │ code_metrics               264L  1C   15m  CC=10     ←0
  │ import_graph               236L  1C   13m  CC=9      ←0
  │ structure                  233L  1C   12m  CC=7      ←0
  │ metadata                   219L  1C    9m  CC=13     ←0
  │ status_report_gen          200L  1C   13m  CC=11     ←0
  │ docker_parser              198L  1C   13m  CC=13     ←0
  │ progress                   172L  0C    6m  CC=7      ←1
  │ html                       160L  1C    4m  CC=12     ←0
  │ makefile_parser            153L  1C    9m  CC=10     ←0
  │ __init__                   150L  1C    6m  CC=8      ←1
  │ table_formatter            145L  1C    7m  CC=8      ←0
  │ article                    140L  1C    4m  CC=13     ←0
  │ dependencies               133L  1C   10m  CC=8      ←0
  │ project_card_gen           131L  1C   10m  CC=5      ←0
  │ org_index_gen              114L  1C    8m  CC=6      ←0
  │ markdown                   112L  1C    7m  CC=4      ←0
  │ changelog_parser           103L  1C    5m  CC=9      ←0
  │ maturity                   103L  1C    2m  CC=14     ←0
  │ json                       100L  1C    5m  CC=14     ←0
  │ utils                       70L  0C    2m  CC=5      ←1
  │ __init__                    53L  0C    1m  CC=1      ←0
  │ prompt.txt                  37L  0C    0m  CC=0.0    ←0
  │ utils                       21L  0C    1m  CC=4      ←4
  │ base                        14L  1C    1m  CC=1      ←0
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │ __main__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    48L  0C    1m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                1033L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              313L  0C   75m  CC=0.0    ←0
  │ calls.toon.yaml            178L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         114L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       82L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           53L  0C    0m  CC=0.0    ←0
  │ validation.toon.yaml        51L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         47L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ goal.yaml                  429L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 55L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              54L  0C    0m  CC=0.0    ←0
  │ project.sh                  50L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:0  →out:0
  │ quickstart                  16L  0C    0m  CC=0.0    ←0
  │ advanced_usage               9L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     Makefile                                  0L

COUPLING:
                              examples  todocs.generators             todocs         todocs.cli
           examples                 ──                 22                  5                     !! fan-out
  todocs.generators                ←22                 ──                                        hub
             todocs                 ←5                                    ──                ←14  hub
         todocs.cli                                                       14                 ──  !! fan-out
  CYCLES: none
  HUB: todocs/ (fan-in=19)
  HUB: todocs.generators/ (fan-in=22)
  SMELL: examples/ fan-out=27 → split needed
  SMELL: todocs.cli/ fan-out=14 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 6 groups | 48f 6890L | 2026-04-29

SUMMARY:
  files_scanned: 48
  total_lines:   6890
  dup_groups:    6
  dup_fragments: 14
  saved_lines:   53
  scan_ms:       4896

HOTSPOTS[7] (files with most duplication):
  todocs/cli/commands.py  dup=38L  groups=2  frags=4  (0.6%)
  todocs/generators/org_index_gen.py  dup=22L  groups=3  frags=3  (0.3%)
  todocs/generators/status_report_gen.py  dup=22L  groups=3  frags=3  (0.3%)
  todocs/generators/comparison.py  dup=6L  groups=1  frags=1  (0.1%)
  todocs/analyzers/api_surface.py  dup=3L  groups=1  frags=1  (0.0%)
  todocs/analyzers/import_graph.py  dup=3L  groups=1  frags=1  (0.0%)
  todocs/analyzers/structure.py  dup=3L  groups=1  frags=1  (0.0%)

DUPLICATES[6] (ranked by impact):
  [b4541c910e42c23b]   STRU  health  L=14 N=2 saved=14 sim=1.00
      todocs/cli/commands.py:120-133  (health)
      todocs/cli/commands.py:181-194  (status)
  [0268d57159098ba6]   STRU  _footer  L=6 N=3 saved=12 sim=1.00
      todocs/generators/comparison.py:484-489  (_footer)
      todocs/generators/org_index_gen.py:109-114  (_footer)
      todocs/generators/status_report_gen.py:195-200  (_footer)
  [94efd6d0e3c09b5b]   STRU  _frontmatter  L=11 N=2 saved=11 sim=1.00
      todocs/generators/org_index_gen.py:37-47  (_frontmatter)
      todocs/generators/status_report_gen.py:57-67  (_frontmatter)
  [2e47812ae45bc5f6]   EXAC  __init__  L=3 N=3 saved=6 sim=1.00
      todocs/analyzers/api_surface.py:21-23  (__init__)
      todocs/analyzers/import_graph.py:22-24  (__init__)
      todocs/analyzers/structure.py:95-97  (__init__)
  [71f2e414249618ab]   EXAC  generate  L=5 N=2 saved=5 sim=1.00
      todocs/generators/org_index_gen.py:17-21  (generate)
      todocs/generators/status_report_gen.py:33-37  (generate)
  [52a45e98d8363c52]   STRU  _write_html_export  L=5 N=2 saved=5 sim=1.00
      todocs/cli/commands.py:245-249  (_write_html_export)
      todocs/cli/commands.py:252-256  (_write_json_export)

REFACTOR[6] (ranked by priority):
  [1] ○ extract_function   → todocs/cli/utils/health.py
      WHY: 2 occurrences of 14-line block across 1 files — saves 14 lines
      FILES: todocs/cli/commands.py
  [2] ○ extract_function   → todocs/generators/utils/_footer.py
      WHY: 3 occurrences of 6-line block across 3 files — saves 12 lines
      FILES: todocs/generators/comparison.py, todocs/generators/org_index_gen.py, todocs/generators/status_report_gen.py
  [3] ○ extract_function   → todocs/generators/utils/_frontmatter.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: todocs/generators/org_index_gen.py, todocs/generators/status_report_gen.py
  [4] ○ extract_function   → todocs/analyzers/utils/__init__.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: todocs/analyzers/api_surface.py, todocs/analyzers/import_graph.py, todocs/analyzers/structure.py
  [5] ○ extract_function   → todocs/generators/utils/generate.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: todocs/generators/org_index_gen.py, todocs/generators/status_report_gen.py
  [6] ○ extract_function   → todocs/cli/utils/_write_html_export.py
      WHY: 2 occurrences of 5-line block across 1 files — saves 5 lines
      FILES: todocs/cli/commands.py

QUICK_WINS[4] (low risk, high savings — do first):
  [1] extract_function   saved=14L  → todocs/cli/utils/health.py
      FILES: commands.py
  [2] extract_function   saved=12L  → todocs/generators/utils/_footer.py
      FILES: comparison.py, org_index_gen.py, status_report_gen.py
  [3] extract_function   saved=11L  → todocs/generators/utils/_frontmatter.py
      FILES: org_index_gen.py, status_report_gen.py
  [4] extract_function   saved=6L  → todocs/analyzers/utils/__init__.py
      FILES: api_surface.py, import_graph.py, structure.py

EFFORT_ESTIMATE (total ≈ 1.8h):
  easy   health                              saved=14L  ~28min
  easy   _footer                             saved=12L  ~24min
  easy   _frontmatter                        saved=11L  ~22min
  easy   __init__                            saved=6L  ~12min
  easy   generate                            saved=5L  ~10min
  easy   _write_html_export                  saved=5L  ~10min

METRICS-TARGET:
  dup_groups:  6 → 0
  saved_lines: 53 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 347 func | 32f | 2026-04-29

NEXT[2] (ranked by impact):
  [1] !  SPLIT-FUNC      ReadmeParser.extract_key_features  CC=16  fan=14
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 224

  [2] !  SPLIT-FUNC      ReadmeParser._summarize_with_nlp  CC=16  fan=13
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 208


RISKS[0]: none

METRICS-TARGET:
  CC̄:          3.5 → ≤2.4
  max-CC:      16 → ≤8
  god-modules: 0 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=3.7 → now CC̄=3.5
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 96f | 55✓ 3⚠ 9✗ | 2026-04-13

SUMMARY:
  scanned: 96  passed: 55 (57.3%)  warnings: 3  errors: 9  unsupported: 32

WARNINGS[3]{path,score}:
  tests/test_integration.py,0.96
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,test_full_pipeline_python has cyclomatic complexity 38 (max: 15),164
      complexity.cyclomatic,warning,test_organization_scan has cyclomatic complexity 16 (max: 15),245
  examples/scan_single.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,main has cyclomatic complexity 25 (max: 15),19
      complexity.lizard_cc,warning,main: CC=16 exceeds limit 15,19
  todocs/generators/article_sections.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 14.4 (threshold: 20),

ERRORS[9]{path,score}:
  todocs/project/analysis.yaml,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 1 parse error(s) in yaml,
  tests/conftest.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,3
  tests/test_analyzers.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,3
  tests/test_extractors.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,3
  tests/test_new_cli.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,4
  tests/test_new_generators.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,3
  tests/test_cli_e2e.py,0.94
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,11
  tests/test_formatters_outputs.py,0.95
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,4
  tests/test_todocs.py,0.95
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,5

UNSUPPORTED[3]{bucket,count}:
  *.md,18
  *.txt,2
  other,12
```

## Intent

Static-analysis documentation generator for project portfolios — WordPress-ready markdown articles without LLM
