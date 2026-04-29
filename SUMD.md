# todocs

Static-analysis documentation generator for project portfolios — WordPress-ready markdown articles without LLM

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `todocs`
- **version**: `0.1.11`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, pyqual.yaml, goal.yaml, src(2 mod), project/(2 analysis files)

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

## Interfaces

### CLI Entry Points

- `todocs`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m todocs
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m todocs --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m todocs --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m todocs --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 38 assertions from pytest
ASSERT[38]{field, operator, expected}:
  eps.sample, ==, "sample.cli:main"
  len(endpoints), ==, 3
  result.cli_commands, ==, []
  result.public_classes, ==, []
  result.entry_points, ==, {}
  profile.name, ==, "sample-project"
  profile.metadata.version, ==, "1.2.3"
  profile.tech_stack.primary_language, ==, "python"
  profile.name, ==, "js-app"
  profile.metadata.version, ==, "2.0.0"
  profile.tech_stack.primary_language, ==, "javascript"
  profile.name, ==, "empty-proj"
  profile.code_stats.source_files, ==, 0
  len(profiles), ==, CONSTANT_3
  name, ==, "sample-project"
  metadata.version, ==, "1.2.3"
  len(filtered), ==, len(all_profiles) - 1
  all(p.name, !=, "web-gamma" for p in filtered)
  generated_by, ==, "todocs v0.1.0"
  eps.sample, ==, "sample.cli:main"
  len(endpoints), ==, 3
  result.cli_commands, ==, []
  result.public_classes, ==, []
  result.entry_points, ==, {}
  profile.name, ==, "sample-project"
  profile.metadata.version, ==, "1.2.3"
  profile.tech_stack.primary_language, ==, "python"
  profile.name, ==, "js-app"
  profile.metadata.version, ==, "2.0.0"
  profile.tech_stack.primary_language, ==, "javascript"
  profile.name, ==, "empty-proj"
  profile.code_stats.source_files, ==, 0
  len(profiles), ==, CONSTANT_3
  name, ==, "sample-project"
  metadata.version, ==, "1.2.3"
  len(filtered), ==, len(all_profiles) - 1
  all(p.name, !=, "web-gamma" for p in filtered)
  generated_by, ==, "todocs v0.1.0"
```

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

## Configuration

```yaml
project:
  name: todocs
  version: 0.1.11
  env: local
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

## Deployment

```bash markpact:run
pip install todocs

# development install
pip install -e .[dev]
```

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`todocs`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `todocs/__init__.py:__version__`

## Makefile Targets

- `help`
- `install`
- `dev`
- `test`
- `test-cov`
- `lint`
- `format`
- `clean`
- `build`
- `publish`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# todocs | 59f 9596L | python:57,less:1,shell:1 | 2026-04-29
# stats: 83 func | 61 cls | 59 mod | CC̄=4.5 | critical:6 | cycles:0
# alerts[5]: CC main=25; CC _generate_summary=12; CC render_architecture=12; CC render_docker=12; CC render_usage=11
# hotspots[5]: main fan=20; main fan=14; readme fan=13; export_cmd fan=13; generate_articles fan=13
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[59]:
  app.doql.less,81
  docs/examples/advanced_usage.py,10
  docs/examples/quickstart.py,17
  examples/api_surface_deep.py,177
  examples/article_sections_demo.py,120
  examples/custom_analysis.py,188
  examples/organization_health_report.py,202
  examples/scan_org.py,62
  examples/scan_single.py,98
  project.sh,50
  tests/conftest.py,452
  tests/test_analyzers.py,219
  tests/test_cli_e2e.py,355
  tests/test_extractors.py,258
  tests/test_formatters_outputs.py,267
  tests/test_integration.py,334
  tests/test_new_cli.py,134
  tests/test_new_generators.py,206
  tests/test_todocs.py,302
  todocs/__init__.py,11
  todocs/analyzers/__init__.py,6
  todocs/analyzers/api_surface.py,290
  todocs/analyzers/code_metrics.py,265
  todocs/analyzers/dependencies.py,134
  todocs/analyzers/import_graph.py,237
  todocs/analyzers/maturity.py,104
  todocs/analyzers/structure.py,234
  todocs/analyzers/utils.py,22
  todocs/cli/__init__.py,54
  todocs/cli/__main__.py,7
  todocs/cli/commands.py,290
  todocs/cli/progress.py,173
  todocs/cli/utils.py,71
  todocs/cli.py,72
  todocs/core.py,445
  todocs/examples/advanced_usage.py,10
  todocs/examples/quickstart.py,17
  todocs/extractors/__init__.py,2
  todocs/extractors/changelog_parser.py,104
  todocs/extractors/docker_parser.py,199
  todocs/extractors/makefile_parser.py,154
  todocs/extractors/metadata.py,220
  todocs/extractors/readme_parser.py,362
  todocs/extractors/toon_parser.py,344
  todocs/formatters/__init__.py,2
  todocs/formatters/table_formatter.py,146
  todocs/generators/__init__.py,6
  todocs/generators/article.py,141
  todocs/generators/article_sections.py,461
  todocs/generators/base.py,15
  todocs/generators/comparison.py,490
  todocs/generators/org_index_gen.py,115
  todocs/generators/project_card_gen.py,132
  todocs/generators/status_report_gen.py,201
  todocs/outputs/__init__.py,2
  todocs/outputs/html.py,161
  todocs/outputs/json.py,101
  todocs/outputs/markdown.py,113
  todocs/utils/__init__.py,151
D:
  docs/examples/advanced_usage.py:
  docs/examples/quickstart.py:
  examples/api_surface_deep.py:
    e: print_section,analyze_entry_points,analyze_cli_commands,analyze_public_symbols,analyze_rest_endpoints,analyze_symbol_sources,main
    print_section(title)
    analyze_entry_points(analyzer)
    analyze_cli_commands(analyzer)
    analyze_public_symbols(analyzer)
    analyze_rest_endpoints(analyzer)
    analyze_symbol_sources(analyzer)
    main()
  examples/article_sections_demo.py:
    e: main
    main()
  examples/custom_analysis.py:
    e: _print_section_header,_analyze_import_graph,_analyze_api_surface,_analyze_toon_files,_analyze_makefile,_analyze_docker,_analyze_code_metrics,main
    _print_section_header(title)
    _analyze_import_graph(project_path)
    _analyze_api_surface(project_path)
    _analyze_toon_files(project_path)
    _analyze_makefile(project_path)
    _analyze_docker(project_path)
    _analyze_code_metrics(project_path)
    main()
  examples/organization_health_report.py:
    e: analyze_maturity_distribution,analyze_code_metrics,analyze_tech_stacks,find_critical_projects,print_health_summary,main
    analyze_maturity_distribution(profiles)
    analyze_code_metrics(profiles)
    analyze_tech_stacks(profiles)
    find_critical_projects(profiles;threshold)
    print_health_summary(profiles;org_name)
    main()
  examples/scan_org.py:
    e: main
    main()
  examples/scan_single.py:
    e: main
    main()
  tests/conftest.py:
    e: sample_project,js_project,empty_project,multi_org
    sample_project(tmp_path)
    js_project(tmp_path)
    empty_project(tmp_path)
    multi_org(tmp_path)
  tests/test_analyzers.py:
    e: TestImportGraphAnalyzer,TestAPISurfaceAnalyzer
    TestImportGraphAnalyzer: test_build_graph(1),test_graph_separates_tests(1),test_hub_modules(1),test_empty_project(1),test_cycle_detection(1),test_internal_package_detection(1)
    TestAPISurfaceAnalyzer: test_analyze(1),test_detect_cli_commands(1),test_detect_entry_points(1),test_detect_public_classes(1),test_detect_public_functions(1),test_detect_rest_endpoints(1),test_empty_project(1),test_extract_all(1)
  tests/test_cli_e2e.py:
    e: sample_project,sample_organization,TestCLIInspect,TestCLIGenerate,TestCLICompare,TestCLIHealth,TestCLIReadme,TestCLIHelp
    TestCLIInspect: test_inspect_markdown_output(2),test_inspect_json_output(2),test_inspect_stdout(1)  # E2E tests for 'todocs inspect' command.
    TestCLIGenerate: test_generate_articles(2),test_generate_with_json_report(2)  # E2E tests for 'todocs generate' command.
    TestCLICompare: test_compare_multiple_projects(2),test_compare_insufficient_projects(2)  # E2E tests for 'todocs compare' command.
    TestCLIHealth: test_health_report(2)  # E2E tests for 'todocs health' command.
    TestCLIReadme: test_readme_generation(2),test_readme_no_projects(1)  # E2E tests for 'todocs readme' command.
    TestCLIHelp: test_main_help(0),test_subcommand_help(0)  # E2E tests for CLI help commands.
    sample_project(tmp_path)
    sample_organization(tmp_path;sample_project)
  tests/test_extractors.py:
    e: TestToonParser,TestMakefileParser,TestDockerParser
    TestToonParser: test_find_toon_files_empty(1),test_find_toon_files(1),test_parse_map_basic(1),test_parse_analysis(1),test_parse_flow(1),test_parse_all(1)
    TestMakefileParser: test_parse_makefile(1),test_parse_empty(1),test_parse_taskfile(1),test_get_target_names(1)
    TestDockerParser: test_parse_full(1),test_parse_no_docker(1),test_parse_dockerfile_only(1),test_parse_multistage_dockerfile(1)
  tests/test_formatters_outputs.py:
    e: TestTableFormatter,TestHTMLOutput,TestJSONOutput,TestMarkdownOutput
    TestTableFormatter: test_format_comparison_default(1),test_format_comparison_sort_by_sloc(1),test_format_comparison_limit(1),test_format_comparison_custom_columns(1),test_format_matrix(1),test_format_ranking(1)
    TestHTMLOutput: test_write_html(2),test_html_contains_all_projects(2),test_html_has_cards(2),test_html_has_stats(2),test_html_single_project(2)
    TestJSONOutput: test_write_json(2),test_json_meta(2),test_json_summary(2),test_json_project_entries(2),test_json_project_metrics(2),test_json_empty(1)
    TestMarkdownOutput: test_write_all_default(2),test_write_all_with_cards(2),test_write_all_with_status(2),test_write_all_includes_comparison(2),test_write_all_includes_health(2)
  tests/test_integration.py:
    e: TestComparisonGenerator,TestCLI,TestIntegration
    TestComparisonGenerator: test_generate_comparison(2),test_generate_category_articles(2),test_generate_health_report(2),test_shared_dependencies(2)
    TestCLI: test_help(0),test_version(0),test_inspect_json(1),test_inspect_markdown(1),test_inspect_to_file(2),test_generate(2),test_generate_with_json_report(2),test_compare(2),test_health(2)
    TestIntegration: test_full_pipeline_python(2),test_full_pipeline_js(2),test_full_pipeline_empty(2),test_organization_scan(2),test_profile_serialization_roundtrip(1),test_exclude_directories(1),test_article_frontmatter_valid(2)
  tests/test_new_cli.py:
    e: TestCLIStatus,TestCLICards,TestCLIIndex,TestCLIExport
    TestCLIStatus: test_status_command(2),test_status_help(0),test_status_with_org_name(2)
    TestCLICards: test_cards_command(2),test_cards_help(0)
    TestCLIIndex: test_index_command(2),test_index_help(0),test_index_no_projects(1)
    TestCLIExport: test_export_html(2),test_export_json(2),test_export_help(0),test_export_no_projects(1),test_export_json_contains_all_projects(2)
  tests/test_new_generators.py:
    e: TestProjectCardGenerator,TestStatusReportGenerator,TestOrgIndexGenerator
    TestProjectCardGenerator: test_generate_single_card(2),test_generate_all_cards(2),test_card_frontmatter(2),test_card_badges(1),test_card_features(1),test_card_empty_project(2)
    TestStatusReportGenerator: test_generate_report(2),test_report_frontmatter(2),test_kpi_values(1),test_recommendations(1),test_empty_profiles(1),test_recent_activity(1)
    TestOrgIndexGenerator: test_generate_index(2),test_index_frontmatter(2),test_index_lists_all_projects(2),test_index_category_tables(1),test_index_quick_stats(1),test_index_empty(1)
  tests/test_todocs.py:
    e: sample_project,TestMetadataExtractor,TestReadmeParser,TestChangelogParser,TestStructureAnalyzer,TestCodeMetrics,TestDependencyAnalyzer,TestScanProject,TestGenerateArticles
    TestMetadataExtractor: test_extract_pyproject(1),test_missing_project(1)
    TestReadmeParser: test_parse_sections(1),test_no_readme(1)
    TestChangelogParser: test_parse_entries(1)
    TestStructureAnalyzer: test_analyze(1),test_detect_tech_stack(1)
    TestCodeMetrics: test_analyze(1),test_key_modules(1)
    TestDependencyAnalyzer: test_runtime_deps(1),test_dev_deps(1)
    TestScanProject: test_full_scan(1),test_profile_serialization(1)
    TestGenerateArticles: test_generate(2),test_index_content(2)
    sample_project(tmp_path)
  todocs/__init__.py:
  todocs/analyzers/__init__.py:
  todocs/analyzers/api_surface.py:
    e: APISurfaceAnalyzer
    APISurfaceAnalyzer: __init__(2),analyze(0),_should_skip(1),_detect_entry_points(0),_detect_cli_commands(0),_decorator_name(1),_scan_public_symbols(0),_collect_target_files(0),_extract_from_file(3),_extract_class(4),_extract_function(4),_extract_all(1),_detect_rest_endpoints(0)  # Detect public API surface of a project.
  todocs/analyzers/code_metrics.py:
    e: CodeMetricsAnalyzer
    CodeMetricsAnalyzer: __init__(2),_should_skip(1),_is_test(1),_scan(0),_count_lines(1),analyze(0),_collect_complexity_data(0),_collect_radon_metrics(5),_collect_ast_fallback(2),_ast_complexity(1),_extract_module_docstring(1),_extract_imports(1),_parse_module_ast(1),_extract_module_info(1),get_key_modules(1)  # Analyze code metrics: lines, complexity, maintainability.
  todocs/analyzers/dependencies.py:
    e: DependencyAnalyzer
    DependencyAnalyzer: __init__(1),_load_pyproject(0),_parse_dep_name(1),_deduplicate(1),_deps_from_requirements(1),_deps_from_package_json(1),_pyproject_runtime_deps(1),_pyproject_dev_deps(1),get_runtime_deps(0),get_dev_deps(0)  # Extract project dependencies without executing anything.
  todocs/analyzers/import_graph.py:
    e: ImportGraphAnalyzer
    ImportGraphAnalyzer: __init__(2),_should_skip(1),_iter_py_files(0),_module_name(1),_collect_modules(0),_build_import_edges(2),build_graph(0),_parse_file_imports(2),_resolve_relative_import(2),_build_fan_metrics(1),_detect_internal_packages(0),_detect_cycles(1),get_hub_modules(1)  # Analyze import relationships between project modules.
  todocs/analyzers/maturity.py:
    e: MaturityScorer
    MaturityScorer: __init__(2),score(0)  # Compute a maturity score (0-100) for a project.
  todocs/analyzers/structure.py:
    e: StructureAnalyzer
    StructureAnalyzer: __init__(2),_should_skip(1),_iter_files(0),analyze(0),detect_tech_stack(0),_detect_languages(0),_detect_build_tools(0),_detect_test_frameworks(0),_detect_ci_cd(0),_detect_containers(0),_detect_frameworks(0),_read_deps_text(0)  # Analyze project directory structure.
  todocs/analyzers/utils.py:
    e: should_skip
    should_skip(path;skip_dirs)
  todocs/cli/__init__.py:
    e: main
    main()
  todocs/cli/__main__.py:
  todocs/cli/commands.py:
    e: generate,inspect,compare,health,readme,status,cards,index,_write_html_export,_write_json_export,export_cmd
    generate(root_dir;output_dir;org_name;org_url;exclude;json_report;verbose)
    inspect(project_dir;output;fmt)
    compare(root_dir;output_path;org_name;exclude)
    health(root_dir;output_path;org_name;exclude)
    readme(root_dir;output_path;org_name;exclude;title;verbose)
    status(root_dir;output_path;org_name;exclude)
    cards(root_dir;output_dir;org_name;exclude)
    index(root_dir;output_path;org_name;exclude)
    _write_html_export(profiles;output_path;org_name)
    _write_json_export(profiles;output_path;org_name)
    export_cmd(root_dir;output_path;fmt;org_name;exclude)
  todocs/cli/progress.py:
    e: discover_and_show_progress,scan_with_progress,print_project_summary,generate_articles_with_progress,generate_with_rich,generate_without_rich
    discover_and_show_progress(root;exclude;console)
    scan_with_progress(root;exclude;console;project_dirs)
    print_project_summary(console;profiles)
    generate_articles_with_progress(profiles;out;org_name;org_url;console)
    generate_with_rich(root;out;exclude;org_name;org_url)
    generate_without_rich(root;out;exclude;org_name;org_url)
  todocs/cli/utils.py:
    e: detect_org_from_git,write_json_report
    detect_org_from_git(root_dir)
    write_json_report(profiles;json_report;console;has_rich)
  todocs/cli.py:
  todocs/core.py:
    e: _run_extraction_phase,_run_analysis_phase,_run_scoring_phase,scan_project,_get_default_excludes,_is_valid_project_dir,_discover_projects,_scan_project_with_progress,scan_organization,generate_articles,_categorize,_generate_summary,TechStack,CodeStats,ProjectMetadata,MaturityProfile,ProjectProfile
    TechStack:  # Detected technology stack.
    CodeStats:  # Aggregated code statistics.
    ProjectMetadata:  # Extracted project metadata.
    MaturityProfile:  # Project maturity assessment.
    ProjectProfile: to_dict(0),to_json(1)  # Complete project profile for article generation.
    _run_extraction_phase(project_path;profile)
    _run_analysis_phase(project_path;profile;scan_filter)
    _run_scoring_phase(project_path;profile)
    scan_project(project_path;max_depth)
    _get_default_excludes()
    _is_valid_project_dir(child;exclude)
    _discover_projects(root_path;exclude)
    _scan_project_with_progress(project_dir;idx;total;max_depth;progress_callback)
    scan_organization(root_path;exclude;max_depth;progress_callback)
    generate_articles(profiles;output_dir;org_name;org_url;include_comparison;include_categories;include_health)
    _categorize(profile)
    _generate_summary(profile)
  todocs/examples/advanced_usage.py:
  todocs/examples/quickstart.py:
  todocs/extractors/__init__.py:
  todocs/extractors/changelog_parser.py:
    e: ChangelogParser
    ChangelogParser: __init__(1),parse(1),_find_changelog(0),_parse_entries(2),_summarize_entry(2)  # Extract structured entries from CHANGELOG.md.
  todocs/extractors/docker_parser.py:
    e: DockerParser
    DockerParser: __init__(1),parse(0),_find_dockerfiles(0),_find_compose_files(0),_parse_dockerfile(1),_read_dockerfile(1),_extract_from_images(1),_clean_image_name(1),_extract_exposed_ports(1),_extract_entrypoint(1),_extract_cmd(1),_iter_instructions(1),_parse_compose(1)  # Extract Docker infrastructure from Dockerfile and docker-com
  todocs/extractors/makefile_parser.py:
    e: MakefileParser
    MakefileParser: __init__(1),parse(0),_parse_makefile(1),_collect_phony_targets(1),_parse_target_line(4),_extract_help_text(3),_collect_commands(2),_parse_taskfile(1),get_target_names(0)  # Extract targets and structure from Makefile or Taskfile.yml.
  todocs/extractors/metadata.py:
    e: MetadataExtractor
    MetadataExtractor: __init__(1),extract(0),_merge(2),_from_pyproject(0),_from_setup_cfg(0),_from_setup_py(0),_extract_setup_kwargs(1),_from_package_json(0),_extract_license(1)  # Extract structured metadata from project config files.
  todocs/extractors/readme_parser.py:
    e: ReadmeParser
    ReadmeParser: __init__(1),_check_nltk(0),parse(0),_find_readme(0),_parse_sections(1),_extract_description(1),_extract_preamble(1),_extract_post_h1(1),_extract_after_h2(1),_extract_heading_sections(1),get_first_paragraph(0),_summarize_with_nlp(2),extract_key_features(1)  # Extract structured sections from a README.md file.
  todocs/extractors/toon_parser.py:
    e: ToonParser
    ToonParser: __init__(1),find_toon_files(0),parse_all(0),parse_map(1),_parse_map_header(1),_parse_modules_section(1),_parse_details_section(1),_parse_class_line(2),_parse_function_line(2),parse_analysis(1),_parse_analysis_header(1),_parse_health_section(1),_parse_refactor_section(1),_parse_layers_section(1),parse_flow(1),parse_functions(1),_read(1)  # Parse .toon files into structured data.
  todocs/formatters/__init__.py:
  todocs/formatters/table_formatter.py:
    e: TableFormatter
    TableFormatter: format_comparison(5),format_matrix(2),format_ranking(5),_default_columns(0),_default_features(0),_sort_profiles(3),_render_table(2)  # Generate markdown comparison tables from project profiles.
  todocs/generators/__init__.py:
  todocs/generators/article.py:
    e: ArticleGenerator
    ArticleGenerator: generate(2),generate_index(2),_render_article(1),_render_index(1)  # Generate markdown articles for WordPress from analyzed proje
  todocs/generators/article_sections.py:
    e: render_frontmatter,render_header,render_overview,render_tech_stack,render_architecture,render_metrics,render_maturity,render_dependencies,_render_entry_points,_render_cli_commands,_render_rest_endpoints,_render_public_classes,render_api_surface,render_build_targets,render_docker,render_changelog,render_usage,render_footer
    render_frontmatter(p;org_name;generated_at)
    render_header(p;org_url)
    render_overview(p;org_name)
    render_tech_stack(p)
    render_architecture(p)
    render_metrics(p)
    render_maturity(p)
    render_dependencies(p)
    _render_entry_points(entry_pts)
    _render_cli_commands(cli_cmds)
    _render_rest_endpoints(endpoints)
    _render_public_classes(pub_classes)
    render_api_surface(p)
    render_build_targets(p)
    render_docker(p)
    render_changelog(p)
    render_usage(p)
    render_footer(generated_at)
  todocs/generators/base.py:
    e: BaseGenerator
    BaseGenerator: __init__(2)  # Base class for all generators with common initialization.
  todocs/generators/comparison.py:
    e: ComparisonGenerator
    ComparisonGenerator: generate_comparison(3),generate_category_articles(2),generate_health_report(2),_render_comparison(2),_size_comparison(1),_maturity_leaderboard(1),_complexity_comparison(1),_tech_stack_overview(1),_dependency_overlap(1),_render_category(2),_render_health_report(1),_health_executive_summary(1),_health_grade_distribution(1),_missing_features(1),_health_projects_needing_attention(1),_health_top_performers(1),generate_readme_list(3),_render_readme_list(2),_readme_summary_table(1),_project_features(1),_readme_project_section(1),_footer(0)  # Generate comparative analysis articles across projects.
  todocs/generators/org_index_gen.py:
    e: OrgIndexGenerator
    OrgIndexGenerator: generate(2),render(1),_frontmatter(1),_header(1),_quick_stats(1),_category_sections(1),_alphabetical_index(1),_footer(0)  # Generate an index.md catalog page for all projects in an org
  todocs/generators/project_card_gen.py:
    e: ProjectCardGenerator
    ProjectCardGenerator: generate(2),generate_all(2),render_card(1),_frontmatter(1),_badge_line(1),_description(1),_stats_table(1),_features_line(1),_deps_line(1),_footer(0)  # Generate a compact project card suitable for WordPress embed
  todocs/generators/status_report_gen.py:
    e: StatusReportGenerator
    StatusReportGenerator: generate(2),render(1),_frontmatter(1),_header(1),_kpi_dashboard(1),_grade_breakdown(1),_language_distribution(1),_truncated_names(2),_quality_gaps(1),_largest_projects(1),_recent_activity(1),_recommendations(1),_footer(0)  # Generate a comprehensive organization status report.
  todocs/outputs/__init__.py:
  todocs/outputs/html.py:
    e: HTMLOutput
    HTMLOutput: write(2),render(1),_render_row(1),_render_card(1)  # Write project profiles as a standalone HTML report.
  todocs/outputs/json.py:
    e: JSONOutput
    JSONOutput: write(2),render(1),_meta(1),_summary(1),_project_entry(1)  # Write project profiles as structured JSON for APIs and dashb
  todocs/outputs/markdown.py:
    e: MarkdownOutput
    MarkdownOutput: __init__(2),write_all(7),_write_articles(2),_write_index(3),_write_cards(3),_write_comparison_reports(4),_write_status_report(3)  # Write project profiles as markdown files (WordPress-ready).
  todocs/utils/__init__.py:
    e: create_scan_filter,GitignoreParser
    GitignoreParser: __init__(2),_load_gitignore(0),_parse_patterns(1),_match_pattern(3),is_ignored(2)  # Parse and match .gitignore patterns.
    create_scan_filter(project_path;max_depth;extra_excludes)
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

## Intent

Static-analysis documentation generator for project portfolios — WordPress-ready markdown articles without LLM
