"""Codebase analyzer for retrofitting existing projects with AgenticScrum.

This module performs read-only analysis of existing codebases to understand
their structure, dependencies, and patterns without modifying any files.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


class CodebaseAnalyzer:
    """Analyze existing codebases for AgenticScrum integration."""
    
    def __init__(self, project_path: Path):
        """Initialize analyzer with project path.
        
        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = Path(project_path)
        self.analysis = {
            'metadata': {
                'path': str(project_path),
                'name': project_path.name,
                'analyzed_at': None
            },
            'structure': {},
            'technology': {},
            'quality': {},
            'integration': {},
            'recommendations': []
        }
    
    def analyze(self) -> Dict:
        """Perform complete codebase analysis.
        
        Returns:
            Dictionary with analysis results
        """
        from datetime import datetime
        
        self.analysis['metadata']['analyzed_at'] = datetime.now().isoformat()
        
        # Run all analysis phases
        self._analyze_structure()
        self._analyze_technology_stack()
        self._analyze_code_quality()
        self._analyze_integration_points()
        self._generate_recommendations()
        
        return self.analysis
    
    def _analyze_structure(self):
        """Analyze project structure and organization."""
        structure = {
            'type': 'unknown',
            'directories': {},
            'file_count': 0,
            'total_size_mb': 0,
            'main_directories': [],
            'test_directories': [],
            'documentation_files': []
        }
        
        # Common directory patterns
        code_dirs = ['src', 'lib', 'app', 'pkg', 'internal', 'cmd', 'api', 'core']
        test_dirs = ['test', 'tests', 'spec', '__tests__', 'test_', '_test']
        doc_patterns = ['README', 'CONTRIBUTING', 'CHANGELOG', 'LICENSE', 'docs']
        
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', 'env', '__pycache__']]
            
            rel_path = Path(root).relative_to(self.project_path)
            
            # Track main code directories
            for d in dirs:
                if d in code_dirs:
                    structure['main_directories'].append(str(rel_path / d))
                elif any(test_pattern in d for test_pattern in test_dirs):
                    structure['test_directories'].append(str(rel_path / d))
            
            # Analyze files
            for file in files:
                file_path = Path(root) / file
                file_count += 1
                
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass
                
                # Check for documentation
                if any(doc in file.upper() for doc in doc_patterns):
                    structure['documentation_files'].append(str(file_path.relative_to(self.project_path)))
        
        structure['file_count'] = file_count
        structure['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        # Determine project type based on structure
        if any((self.project_path / indicator).exists() for indicator in ['setup.py', 'pyproject.toml']):
            structure['type'] = 'python_package'
        elif (self.project_path / 'package.json').exists():
            structure['type'] = 'node_project'
        elif (self.project_path / 'go.mod').exists():
            structure['type'] = 'go_module'
        elif any((self.project_path / f).exists() for f in ['pom.xml', 'build.gradle']):
            structure['type'] = 'java_project'
        elif (self.project_path / 'Cargo.toml').exists():
            structure['type'] = 'rust_project'
        
        self.analysis['structure'] = structure
    
    def _analyze_technology_stack(self):
        """Analyze the technology stack and dependencies."""
        tech = {
            'primary_language': 'unknown',
            'frameworks': [],
            'dependencies': {},
            'dev_dependencies': {},
            'build_tools': [],
            'test_frameworks': []
        }
        
        # Language detection based on file extensions
        language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'go': ['.go'],
            'rust': ['.rs'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'ruby': ['.rb'],
            'php': ['.php']
        }
        
        file_counts = {}
        for lang, extensions in language_extensions.items():
            count = sum(1 for _ in self.project_path.rglob('*') if _.suffix in extensions)
            if count > 0:
                file_counts[lang] = count
        
        if file_counts:
            tech['primary_language'] = max(file_counts, key=file_counts.get)
        
        # Analyze package files
        if (self.project_path / 'package.json').exists():
            self._analyze_node_project(tech)
        elif (self.project_path / 'requirements.txt').exists():
            self._analyze_python_requirements(tech)
        elif (self.project_path / 'go.mod').exists():
            self._analyze_go_mod(tech)
        elif (self.project_path / 'Cargo.toml').exists():
            self._analyze_cargo_toml(tech)
        
        # Detect CI/CD
        ci_files = {
            '.github/workflows': 'GitHub Actions',
            '.gitlab-ci.yml': 'GitLab CI',
            'Jenkinsfile': 'Jenkins',
            '.circleci/config.yml': 'CircleCI',
            '.travis.yml': 'Travis CI'
        }
        
        for ci_file, ci_name in ci_files.items():
            if (self.project_path / ci_file).exists():
                tech['build_tools'].append(ci_name)
        
        self.analysis['technology'] = tech
    
    def _analyze_node_project(self, tech: Dict):
        """Analyze Node.js project dependencies."""
        try:
            with open(self.project_path / 'package.json', 'r') as f:
                package = json.load(f)
                
            tech['dependencies'] = package.get('dependencies', {})
            tech['dev_dependencies'] = package.get('devDependencies', {})
            
            # Detect frameworks
            all_deps = {**tech['dependencies'], **tech['dev_dependencies']}
            
            framework_indicators = {
                'express': 'Express.js',
                'fastify': 'Fastify',
                'koa': 'Koa',
                'react': 'React',
                'vue': 'Vue.js',
                'angular': 'Angular',
                'svelte': 'Svelte',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js'
            }
            
            for dep, framework in framework_indicators.items():
                if dep in all_deps:
                    tech['frameworks'].append(framework)
            
            # Detect test frameworks
            test_indicators = ['jest', 'mocha', 'cypress', 'playwright', 'vitest']
            for test_fw in test_indicators:
                if test_fw in all_deps:
                    tech['test_frameworks'].append(test_fw)
                    
        except Exception as e:
            pass
    
    def _analyze_python_requirements(self, tech: Dict):
        """Analyze Python requirements."""
        try:
            with open(self.project_path / 'requirements.txt', 'r') as f:
                requirements = f.read().splitlines()
            
            for req in requirements:
                if req and not req.startswith('#'):
                    # Simple parsing (could be enhanced)
                    parts = re.split('[<>=!]', req)
                    if parts:
                        dep_name = parts[0].strip()
                        tech['dependencies'][dep_name] = req
            
            # Detect frameworks
            framework_indicators = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'pyramid': 'Pyramid',
                'tornado': 'Tornado'
            }
            
            for dep, framework in framework_indicators.items():
                if dep in tech['dependencies']:
                    tech['frameworks'].append(framework)
            
            # Detect test frameworks
            test_indicators = ['pytest', 'unittest', 'nose', 'tox']
            for test_fw in test_indicators:
                if test_fw in tech['dependencies']:
                    tech['test_frameworks'].append(test_fw)
                    
        except Exception as e:
            pass
    
    def _analyze_go_mod(self, tech: Dict):
        """Analyze go.mod file."""
        try:
            with open(self.project_path / 'go.mod', 'r') as f:
                content = f.read()
            
            # Extract dependencies
            require_block = re.search(r'require\s*\((.*?)\)', content, re.DOTALL)
            if require_block:
                deps = require_block.group(1).strip().split('\n')
                for dep in deps:
                    if dep.strip():
                        parts = dep.strip().split()
                        if len(parts) >= 2:
                            tech['dependencies'][parts[0]] = parts[1]
            
            # Detect frameworks
            framework_indicators = {
                'gin-gonic/gin': 'Gin',
                'labstack/echo': 'Echo',
                'fiber': 'Fiber',
                'beego': 'Beego',
                'revel': 'Revel'
            }
            
            for dep, framework in framework_indicators.items():
                if any(dep in d for d in tech['dependencies']):
                    tech['frameworks'].append(framework)
                    
        except Exception as e:
            pass
    
    def _analyze_cargo_toml(self, tech: Dict):
        """Analyze Cargo.toml file."""
        try:
            import toml
            with open(self.project_path / 'Cargo.toml', 'r') as f:
                cargo = toml.load(f)
            
            if 'dependencies' in cargo:
                tech['dependencies'] = cargo['dependencies']
            
            # Detect frameworks
            framework_indicators = {
                'actix-web': 'Actix-web',
                'rocket': 'Rocket',
                'warp': 'Warp',
                'axum': 'Axum'
            }
            
            for dep, framework in framework_indicators.items():
                if dep in tech['dependencies']:
                    tech['frameworks'].append(framework)
                    
        except Exception as e:
            # Fallback to simple parsing if toml not available
            pass
    
    def _analyze_code_quality(self):
        """Analyze code quality indicators."""
        quality = {
            'has_tests': False,
            'test_file_count': 0,
            'has_ci': False,
            'has_linting': False,
            'has_formatting': False,
            'documentation_score': 0,
            'estimated_coverage': 'unknown'
        }
        
        # Check for tests
        test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.spec.js', '*_test.go', 'test_*.go']
        test_count = 0
        for pattern in test_patterns:
            test_count += sum(1 for _ in self.project_path.rglob(pattern))
        
        quality['test_file_count'] = test_count
        quality['has_tests'] = test_count > 0
        
        # Check for CI
        ci_indicators = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci']
        quality['has_ci'] = any((self.project_path / ci).exists() for ci in ci_indicators)
        
        # Check for linting/formatting configs
        lint_configs = [
            '.eslintrc', '.eslintrc.json', '.eslintrc.js',  # JavaScript
            '.flake8', 'pyproject.toml', 'setup.cfg',  # Python
            '.golangci.yml',  # Go
            'rustfmt.toml',  # Rust
        ]
        quality['has_linting'] = any((self.project_path / cfg).exists() for cfg in lint_configs)
        
        format_configs = ['.prettierrc', '.black', 'rustfmt.toml', '.gofmt']
        quality['has_formatting'] = any((self.project_path / cfg).exists() for cfg in format_configs)
        
        # Documentation score (0-100)
        doc_score = 0
        if (self.project_path / 'README.md').exists():
            doc_score += 40
        if (self.project_path / 'docs').exists():
            doc_score += 30
        if any((self.project_path / f).exists() for f in ['CONTRIBUTING.md', 'ARCHITECTURE.md', 'API.md']):
            doc_score += 30
        
        quality['documentation_score'] = doc_score
        
        # Try to estimate coverage if possible
        if quality['has_ci']:
            # Look for coverage badges in README
            try:
                if (self.project_path / 'README.md').exists():
                    with open(self.project_path / 'README.md', 'r') as f:
                        readme = f.read()
                        coverage_match = re.search(r'coverage[:\s]+(\d+)%', readme, re.IGNORECASE)
                        if coverage_match:
                            quality['estimated_coverage'] = f"{coverage_match.group(1)}%"
            except:
                pass
        
        self.analysis['quality'] = quality
    
    def _analyze_integration_points(self):
        """Identify integration points for AgenticScrum."""
        integration = {
            'entry_points': [],
            'build_commands': [],
            'test_commands': [],
            'suggested_structure': {},
            'conflicts': []
        }
        
        # Detect entry points
        entry_patterns = {
            'python': ['main.py', 'app.py', 'run.py', 'manage.py', '__main__.py'],
            'javascript': ['index.js', 'app.js', 'server.js', 'main.js'],
            'go': ['main.go', 'cmd/*/main.go'],
            'rust': ['src/main.rs'],
            'java': ['**/Main.java', '**/Application.java']
        }
        
        lang = self.analysis['technology'].get('primary_language', 'unknown')
        if lang in entry_patterns:
            for pattern in entry_patterns[lang]:
                matches = list(self.project_path.glob(pattern))
                integration['entry_points'].extend([str(m.relative_to(self.project_path)) for m in matches])
        
        # Detect build/test commands from package files
        if (self.project_path / 'package.json').exists():
            try:
                with open(self.project_path / 'package.json', 'r') as f:
                    package = json.load(f)
                    scripts = package.get('scripts', {})
                    
                    if 'build' in scripts:
                        integration['build_commands'].append(f"npm run build")
                    if 'test' in scripts:
                        integration['test_commands'].append(f"npm test")
            except:
                pass
        
        # Suggest AgenticScrum structure
        integration['suggested_structure'] = {
            '.agentic/': 'AgenticScrum metadata and analysis',
            'agents/': 'AI agent configurations',
            'spec/': 'User stories and specifications',
            'docs/EPICS/': 'Epic documentation',
            'docs/PRD.md': 'Product requirements document',
            'docs/PROJECT_SUMMARY.md': 'High-level project tracking'
        }
        
        # Check for potential conflicts
        for suggested_dir in ['agents', 'spec']:
            if (self.project_path / suggested_dir).exists():
                integration['conflicts'].append(f"{suggested_dir}/ already exists")
        
        self.analysis['integration'] = integration
    
    def _generate_recommendations(self):
        """Generate specific recommendations for the project."""
        recs = []
        
        # Testing recommendations
        if not self.analysis['quality']['has_tests']:
            recs.append({
                'category': 'testing',
                'priority': 'high',
                'recommendation': 'Add test suite',
                'rationale': 'No tests detected. AgenticScrum QAA agent can help create comprehensive tests.'
            })
        elif self.analysis['quality']['test_file_count'] < 5:
            recs.append({
                'category': 'testing',
                'priority': 'medium',
                'recommendation': 'Expand test coverage',
                'rationale': f'Only {self.analysis["quality"]["test_file_count"]} test files found. Consider adding more tests.'
            })
        
        # Documentation recommendations
        if self.analysis['quality']['documentation_score'] < 50:
            recs.append({
                'category': 'documentation',
                'priority': 'high',
                'recommendation': 'Improve documentation',
                'rationale': 'Limited documentation found. POA agent can help create comprehensive docs.'
            })
        
        # CI/CD recommendations
        if not self.analysis['quality']['has_ci']:
            recs.append({
                'category': 'automation',
                'priority': 'medium',
                'recommendation': 'Add CI/CD pipeline',
                'rationale': 'No CI/CD detected. AgenticScrum can help set up automated workflows.'
            })
        
        # Code quality recommendations
        if not self.analysis['quality']['has_linting']:
            recs.append({
                'category': 'code_quality',
                'priority': 'medium',
                'recommendation': 'Add linting configuration',
                'rationale': 'No linting config found. This helps maintain code quality.'
            })
        
        # Architecture recommendations
        if not self.analysis['structure']['main_directories']:
            recs.append({
                'category': 'architecture',
                'priority': 'low',
                'recommendation': 'Consider organizing code into modules',
                'rationale': 'Flat structure detected. Modular organization improves maintainability.'
            })
        
        self.analysis['recommendations'] = recs
    
    def generate_retrofit_plan(self) -> Dict:
        """Generate a specific plan for retrofitting this project.
        
        Returns:
            Dictionary with retrofit plan
        """
        plan = {
            'approach': 'gradual',
            'preserve': [],
            'add': [],
            'phases': [],
            'risks': []
        }
        
        # What to preserve
        plan['preserve'] = [
            'All existing code and functionality',
            'Current directory structure',
            'Build and deployment processes',
            'Git history and workflows'
        ]
        
        # What to add
        plan['add'] = [
            'AgenticScrum agent configurations',
            'Structured requirements documentation',
            'AI-assisted development workflows',
            'Enhanced project tracking'
        ]
        
        # Implementation phases
        plan['phases'] = [
            {
                'phase': 1,
                'name': 'Setup',
                'duration': '1 day',
                'tasks': [
                    'Add .agentic/ directory for metadata',
                    'Create CLAUDE.md for AI assistance',
                    'Initialize agent configurations'
                ]
            },
            {
                'phase': 2,
                'name': 'Documentation',
                'duration': '2-3 days',
                'tasks': [
                    'Generate PRD.md from existing code',
                    'Create initial epics and stories',
                    'Document current architecture'
                ]
            },
            {
                'phase': 3,
                'name': 'Integration',
                'duration': '1 week',
                'tasks': [
                    'Configure development agents',
                    'Set up sprint workflows',
                    'Integrate QA automation'
                ]
            }
        ]
        
        # Identify risks
        if self.analysis['integration']['conflicts']:
            plan['risks'].append({
                'risk': 'Directory conflicts',
                'impact': 'low',
                'mitigation': 'Use alternative directory names or merge contents'
            })
        
        if self.analysis['structure']['total_size_mb'] > 100:
            plan['risks'].append({
                'risk': 'Large codebase',
                'impact': 'medium',
                'mitigation': 'Focus on incremental integration, starting with new features'
            })
        
        return plan
    
    def generate_analysis_report(self) -> str:
        """Generate a markdown report of the analysis.
        
        Returns:
            Markdown formatted analysis report
        """
        report = f"""# Codebase Analysis Report

## Project: {self.analysis['metadata']['name']}

**Analyzed**: {self.analysis['metadata']['analyzed_at']}  
**Path**: {self.analysis['metadata']['path']}

## Summary

- **Type**: {self.analysis['structure']['type']}
- **Primary Language**: {self.analysis['technology']['primary_language']}
- **Size**: {self.analysis['structure']['file_count']} files, {self.analysis['structure']['total_size_mb']} MB
- **Quality Score**: {self._calculate_quality_score()}/100

## Technology Stack

### Language & Frameworks
- **Primary Language**: {self.analysis['technology']['primary_language']}
- **Frameworks**: {', '.join(self.analysis['technology']['frameworks']) or 'None detected'}
- **Test Frameworks**: {', '.join(self.analysis['technology']['test_frameworks']) or 'None detected'}

### Build Tools
{self._format_list(self.analysis['technology']['build_tools'])}

## Code Quality

- **Has Tests**: {'✅' if self.analysis['quality']['has_tests'] else '❌'}
- **Test Files**: {self.analysis['quality']['test_file_count']}
- **CI/CD**: {'✅' if self.analysis['quality']['has_ci'] else '❌'}
- **Linting**: {'✅' if self.analysis['quality']['has_linting'] else '❌'}
- **Documentation Score**: {self.analysis['quality']['documentation_score']}/100

## Structure

### Main Directories
{self._format_list(self.analysis['structure']['main_directories'])}

### Test Directories
{self._format_list(self.analysis['structure']['test_directories'])}

## Recommendations

"""
        
        for rec in self.analysis['recommendations']:
            report += f"### {rec['recommendation']} ({rec['priority'].title()} Priority)\n"
            report += f"{rec['rationale']}\n\n"
        
        report += """## Integration Plan

The following structure will be added without modifying existing code:

"""
        
        for path, desc in self.analysis['integration']['suggested_structure'].items():
            report += f"- `{path}` - {desc}\n"
        
        if self.analysis['integration']['conflicts']:
            report += "\n### Potential Conflicts\n"
            for conflict in self.analysis['integration']['conflicts']:
                report += f"- {conflict}\n"
        
        return report
    
    def _calculate_quality_score(self) -> int:
        """Calculate overall quality score."""
        score = 0
        
        # Testing (30 points)
        if self.analysis['quality']['has_tests']:
            score += 20
            if self.analysis['quality']['test_file_count'] > 10:
                score += 10
        
        # CI/CD (20 points)
        if self.analysis['quality']['has_ci']:
            score += 20
        
        # Code quality (20 points)
        if self.analysis['quality']['has_linting']:
            score += 10
        if self.analysis['quality']['has_formatting']:
            score += 10
        
        # Documentation (30 points)
        score += int(self.analysis['quality']['documentation_score'] * 0.3)
        
        return score
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list for markdown."""
        if not items:
            return "- None\n"
        return '\n'.join(f"- {item}" for item in items) + '\n'