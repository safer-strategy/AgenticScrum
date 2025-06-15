#!/usr/bin/env python3
"""
AgenticScrum Project Retrofitter
Analyzes existing projects and generates configurations for AgenticScrum integration
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


@dataclass
class ProjectAnalysis:
    """Results of project analysis"""
    languages: Dict[str, int]
    frameworks: List[str]
    structure_type: str
    test_frameworks: List[str]
    ci_platforms: List[str]
    code_patterns: Dict[str, List[str]]
    complexity_score: float
    team_size_estimate: int
    project_age_estimate: int


@dataclass
class RetrofitPlan:
    """Retrofit implementation plan"""
    phases: List[Dict]
    recommended_agents: List[str]
    integration_points: Dict[str, str]
    risk_assessment: Dict[str, str]
    timeline_weeks: int


class ProjectRetrofitter:
    """Main class for retrofitting existing projects with AgenticScrum"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analysis = None
        self.plan = None
        
    def assess(self) -> ProjectAnalysis:
        """Perform comprehensive project assessment"""
        print(f"Analyzing project at {self.project_path}...")
        
        self.analysis = ProjectAnalysis(
            languages=self._detect_languages(),
            frameworks=self._detect_frameworks(),
            structure_type=self._analyze_structure(),
            test_frameworks=self._detect_test_frameworks(),
            ci_platforms=self._detect_ci_platforms(),
            code_patterns=self._analyze_code_patterns(),
            complexity_score=self._calculate_complexity(),
            team_size_estimate=self._estimate_team_size(),
            project_age_estimate=self._estimate_project_age()
        )
        
        return self.analysis
    
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages and their file counts"""
        language_extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        language_counts = defaultdict(int)
        
        for ext, lang in language_extensions.items():
            files = list(self.project_path.rglob(f'*{ext}'))
            # Exclude common non-source directories
            files = [f for f in files if not any(
                part in f.parts for part in 
                ['node_modules', 'venv', '.git', 'build', 'dist', '__pycache__']
            )]
            if files:
                language_counts[lang] = len(files)
                
        return dict(language_counts)
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks based on configuration files and imports"""
        frameworks = []
        
        # Check package.json for JS frameworks
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                framework_indicators = {
                    'react': ['react', 'react-dom'],
                    'vue': ['vue'],
                    'angular': ['@angular/core'],
                    'express': ['express'],
                    'nextjs': ['next'],
                    'electron': ['electron'],
                    'svelte': ['svelte']
                }
                
                for framework, indicators in framework_indicators.items():
                    if any(ind in deps for ind in indicators):
                        frameworks.append(framework)
        
        # Check Python requirements
        for req_file in ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']:
            req_path = self.project_path / req_file
            if req_path.exists():
                content = req_path.read_text()
                
                python_frameworks = {
                    'django': ['django'],
                    'flask': ['flask'],
                    'fastapi': ['fastapi'],
                    'pyramid': ['pyramid'],
                    'tornado': ['tornado']
                }
                
                for framework, indicators in python_frameworks.items():
                    if any(ind in content.lower() for ind in indicators):
                        frameworks.append(framework)
                        break
        
        # Check for Java frameworks
        pom_xml = self.project_path / 'pom.xml'
        build_gradle = self.project_path / 'build.gradle'
        
        if pom_xml.exists() or build_gradle.exists():
            frameworks.append('java-maven' if pom_xml.exists() else 'java-gradle')
            
            # Check for Spring
            if pom_xml.exists():
                content = pom_xml.read_text()
                if 'spring' in content.lower():
                    frameworks.append('spring')
        
        return frameworks
    
    def _analyze_structure(self) -> str:
        """Determine project structure type"""
        # Check for monorepo indicators
        if (self.project_path / 'lerna.json').exists():
            return 'monorepo-lerna'
        if (self.project_path / 'nx.json').exists():
            return 'monorepo-nx'
        if (self.project_path / 'rush.json').exists():
            return 'monorepo-rush'
            
        # Check for microservices
        service_indicators = ['docker-compose.yml', 'kubernetes', 'helm']
        if any((self.project_path / ind).exists() for ind in service_indicators):
            # Look for multiple service directories
            potential_services = []
            for item in self.project_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    if any((item / ind).exists() for ind in ['Dockerfile', 'package.json', 'pom.xml']):
                        potential_services.append(item)
            
            if len(potential_services) > 2:
                return 'microservices'
        
        # Check for standard patterns
        if (self.project_path / 'src').exists():
            if (self.project_path / 'src' / 'main').exists():
                return 'maven-structure'
            return 'standard-src'
            
        return 'custom-structure'
    
    def _detect_test_frameworks(self) -> List[str]:
        """Detect testing frameworks"""
        test_frameworks = []
        
        # JavaScript/TypeScript
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                js_test_frameworks = ['jest', 'mocha', 'cypress', 'playwright', 'vitest']
                test_frameworks.extend([fw for fw in js_test_frameworks if fw in deps])
        
        # Python
        for req_file in ['requirements.txt', 'requirements-dev.txt', 'setup.py']:
            req_path = self.project_path / req_file
            if req_path.exists():
                content = req_path.read_text().lower()
                python_test_frameworks = ['pytest', 'unittest', 'nose', 'behave']
                test_frameworks.extend([fw for fw in python_test_frameworks if fw in content])
                break
        
        return list(set(test_frameworks))
    
    def _detect_ci_platforms(self) -> List[str]:
        """Detect CI/CD platforms"""
        ci_platforms = []
        
        ci_indicators = {
            'github-actions': '.github/workflows',
            'gitlab-ci': '.gitlab-ci.yml',
            'jenkins': 'Jenkinsfile',
            'travis': '.travis.yml',
            'circle-ci': '.circleci/config.yml',
            'azure-pipelines': 'azure-pipelines.yml',
            'bitbucket-pipelines': 'bitbucket-pipelines.yml'
        }
        
        for platform, indicator in ci_indicators.items():
            if (self.project_path / indicator).exists():
                ci_platforms.append(platform)
                
        return ci_platforms
    
    def _analyze_code_patterns(self) -> Dict[str, List[str]]:
        """Analyze common code patterns"""
        patterns = defaultdict(list)
        
        # Analyze Python patterns
        python_files = list(self.project_path.rglob('*.py'))[:10]  # Sample first 10
        for py_file in python_files:
            try:
                with open(py_file) as f:
                    tree = ast.parse(f.read())
                    
                # Check for common patterns
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check for inheritance patterns
                        if node.bases:
                            patterns['inheritance'].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        # Check for decorators
                        if node.decorator_list:
                            patterns['decorators'].extend(
                                [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                            )
            except:
                pass
        
        # Analyze JavaScript patterns
        js_files = list(self.project_path.rglob('*.js'))[:10]
        for js_file in js_files:
            try:
                content = js_file.read_text()
                # Simple pattern matching
                if 'class ' in content:
                    patterns['es6-classes'].append(js_file.name)
                if 'async ' in content:
                    patterns['async-await'].append(js_file.name)
                if 'import ' in content or 'export ' in content:
                    patterns['es6-modules'].append(js_file.name)
            except:
                pass
                
        return dict(patterns)
    
    def _calculate_complexity(self) -> float:
        """Calculate project complexity score (0-100)"""
        score = 0.0
        
        # Factor 1: Number of languages (max 20 points)
        num_languages = len(self._detect_languages())
        score += min(num_languages * 5, 20)
        
        # Factor 2: Number of files (max 20 points)
        total_files = sum(1 for _ in self.project_path.rglob('*') if _.is_file())
        if total_files > 1000:
            score += 20
        elif total_files > 500:
            score += 15
        elif total_files > 100:
            score += 10
        else:
            score += 5
            
        # Factor 3: Directory depth (max 20 points)
        max_depth = max(len(p.parts) for p in self.project_path.rglob('*')) - len(self.project_path.parts)
        score += min(max_depth * 2, 20)
        
        # Factor 4: External dependencies (max 20 points)
        dep_count = 0
        if (self.project_path / 'package.json').exists():
            with open(self.project_path / 'package.json') as f:
                data = json.load(f)
                dep_count += len(data.get('dependencies', {}))
        if (self.project_path / 'requirements.txt').exists():
            dep_count += len((self.project_path / 'requirements.txt').read_text().splitlines())
        
        score += min(dep_count / 5, 20)
        
        # Factor 5: Test coverage indicator (max 20 points)
        test_dirs = ['test', 'tests', 'spec', '__tests__']
        has_tests = any((self.project_path / td).exists() for td in test_dirs)
        score += 20 if has_tests else 0
        
        return min(score, 100)
    
    def _estimate_team_size(self) -> int:
        """Estimate team size based on git history"""
        try:
            # Get unique contributors in last 6 months
            result = subprocess.run(
                ['git', 'log', '--since="6 months ago"', '--format=%ae'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                emails = set(result.stdout.strip().split('\n'))
                return len(emails)
        except:
            pass
            
        # Fallback: estimate based on project size
        total_files = sum(1 for _ in self.project_path.rglob('*') if _.is_file())
        if total_files > 1000:
            return 10
        elif total_files > 500:
            return 5
        else:
            return 2
    
    def _estimate_project_age(self) -> int:
        """Estimate project age in years"""
        try:
            # Get first commit date
            result = subprocess.run(
                ['git', 'log', '--reverse', '--format=%at', '-1'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                import time
                first_commit_timestamp = int(result.stdout.strip())
                age_seconds = time.time() - first_commit_timestamp
                return int(age_seconds / (365 * 24 * 60 * 60))
        except:
            pass
            
        return 1  # Default to 1 year
    
    def generate_plan(self) -> RetrofitPlan:
        """Generate retrofit plan based on analysis"""
        if not self.analysis:
            self.assess()
            
        # Determine recommended agents based on languages
        agents = ['poa', 'sma', 'qaa', 'saa']
        for lang in self.analysis.languages:
            agents.append(f'deva_{lang}')
            
        # Calculate timeline based on complexity
        if self.analysis.complexity_score > 70:
            timeline_weeks = 12
        elif self.analysis.complexity_score > 40:
            timeline_weeks = 8
        else:
            timeline_weeks = 4
            
        # Create phased plan
        phases = [
            {
                'phase': 1,
                'name': 'Foundation',
                'duration_weeks': 2,
                'tasks': [
                    'Install AgenticScrum tools',
                    'Create initial configuration',
                    'Document existing patterns',
                    'Set up POA agent'
                ]
            },
            {
                'phase': 2,
                'name': 'Pilot Integration',
                'duration_weeks': 2,
                'tasks': [
                    'Configure developer agents',
                    'Pilot with new feature development',
                    'Integrate QA agent for code reviews',
                    'Establish feedback loops'
                ]
            },
            {
                'phase': 3,
                'name': 'Expansion',
                'duration_weeks': timeline_weeks - 6,
                'tasks': [
                    'Roll out to full team',
                    'Integrate with CI/CD',
                    'Implement security audits',
                    'Optimize agent configurations'
                ]
            },
            {
                'phase': 4,
                'name': 'Optimization',
                'duration_weeks': 2,
                'tasks': [
                    'Performance tuning',
                    'Process refinement',
                    'Knowledge transfer',
                    'Success metrics evaluation'
                ]
            }
        ]
        
        # Identify integration points
        integration_points = {}
        if self.analysis.ci_platforms:
            integration_points['ci_cd'] = self.analysis.ci_platforms[0]
        if 'github-actions' in self.analysis.ci_platforms:
            integration_points['issue_tracker'] = 'github-issues'
        elif 'gitlab-ci' in self.analysis.ci_platforms:
            integration_points['issue_tracker'] = 'gitlab-issues'
            
        # Risk assessment
        risks = {}
        if self.analysis.complexity_score > 70:
            risks['complexity'] = 'high'
        if self.analysis.team_size_estimate > 10:
            risks['coordination'] = 'high'
        if not self.analysis.test_frameworks:
            risks['quality'] = 'high'
            
        self.plan = RetrofitPlan(
            phases=phases,
            recommended_agents=agents,
            integration_points=integration_points,
            risk_assessment=risks,
            timeline_weeks=timeline_weeks
        )
        
        return self.plan
    
    def init_agents(self, languages: List[str], frameworks: List[str]) -> None:
        """Initialize agent configurations for retrofit"""
        agents_dir = self.project_path / 'agents'
        agents_dir.mkdir(exist_ok=True)
        
        # Create base agents
        base_agents = ['poa', 'sma', 'qaa', 'saa']
        for agent in base_agents:
            agent_dir = agents_dir / agent
            agent_dir.mkdir(exist_ok=True)
            
            # Create retrofit-specific persona rules
            persona_config = {
                'agent_role': agent.upper(),
                'agent_goal': f'Support {agent} activities in retrofit context',
                'project_age': self._estimate_project_age(),
                'team_size': self._estimate_team_size(),
                'primary_language': list(self.analysis.languages.keys())[0] if self.analysis else 'python',
                'framework': frameworks[0] if frameworks else 'none',
                'llm_provider': 'openai',
                'default_model': 'gpt-4-turbo-preview',
                'additional_capabilities': [],
                'custom_rules': [],
                'line_length': 100,
                'naming_convention': 'snake_case',
                'approved_deps_file': 'requirements.txt',
                'discovered_patterns': [],
                'existing_docs': [],
                'project_root': str(self.project_path),
                'vcs_type': 'git',
                'git_workflow': 'github-flow',
                'branch_prefix': 'feature/',
                'ci_platform': self.analysis.ci_platforms[0] if self.analysis and self.analysis.ci_platforms else 'github-actions',
                'ci_config_path': '.github/workflows/ci.yml',
                'integration_stage': 'test',
                'issue_tracker': 'github',
                'project_key': 'PROJ',
                'story_format': 'markdown',
                'language': 'python'
            }
            
            # Write persona rules
            persona_path = agent_dir / 'persona_rules.yaml'
            with open(persona_path, 'w') as f:
                yaml.dump(persona_config, f, default_flow_style=False)
                
            # Create priming script
            priming_path = agent_dir / 'priming_script.md'
            priming_content = f"""# {agent.upper()} Retrofit Priming Script

You are working on an existing project that is being retrofitted with AgenticScrum.

## Project Context
- **Age**: {self._estimate_project_age()} years
- **Team Size**: {self._estimate_team_size()} developers  
- **Primary Language**: {list(self.analysis.languages.keys())[0] if self.analysis else 'Unknown'}
- **Structure**: {self.analysis.structure_type if self.analysis else 'Unknown'}

## Retrofit Guidelines
1. Respect existing patterns and conventions
2. Introduce changes gradually
3. Maintain backward compatibility
4. Document all decisions

## Your Role
As the {agent.upper()}, you must balance AgenticScrum best practices with the reality of working on an existing codebase.

## Current Task
[Task details will be inserted here]
"""
            with open(priming_path, 'w') as f:
                f.write(priming_content)
        
        # Create developer agents for each language
        for lang in languages:
            deva_dir = agents_dir / f'deva_{lang}'
            deva_dir.mkdir(exist_ok=True)
            
            # Language-specific configuration
            # ... (similar to above but with language-specific details)
            
        print(f"Created agent configurations in {agents_dir}")
    
    def create_config(self) -> Path:
        """Create initial agentic_config.yaml for retrofit"""
        if not self.analysis:
            self.assess()
            
        config = {
            'project_name': self.project_path.name,
            'project_type': 'retrofit',
            'retrofit_mode': True,
            'integration_strategy': 'gradual',
            
            'existing_structure': {
                'type': self.analysis.structure_type,
                'preserve': True,
                'source_dirs': self._find_source_dirs(),
                'test_dirs': self._find_test_dirs()
            },
            
            'detected_stack': {
                'languages': list(self.analysis.languages.keys()),
                'frameworks': self.analysis.frameworks,
                'test_frameworks': self.analysis.test_frameworks
            },
            
            'llm_config': {
                'provider': 'openai',
                'default_model': 'gpt-4-turbo-preview',
                'temperature': 0.3
            },
            
            'agents': {
                'enabled': ['poa', 'sma', 'qaa'],
                'gradual_rollout': True,
                'pilot_features': []
            },
            
            'integration': {
                'ci_cd': self.analysis.ci_platforms[0] if self.analysis.ci_platforms else 'none',
                'preserve_workflows': True,
                'add_agentic_checks': True
            }
        }
        
        config_path = self.project_path / 'agentic_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
        print(f"Created configuration at {config_path}")
        return config_path
    
    def _find_source_dirs(self) -> List[str]:
        """Find source code directories"""
        common_source_dirs = ['src', 'lib', 'app', 'source', 'code']
        found_dirs = []
        
        for dir_name in common_source_dirs:
            if (self.project_path / dir_name).exists():
                found_dirs.append(dir_name)
                
        # Also check for language-specific patterns
        if any(self.project_path.rglob('*.py')):
            for item in self.project_path.iterdir():
                if item.is_dir() and (item / '__init__.py').exists():
                    found_dirs.append(str(item.relative_to(self.project_path)))
                    
        return found_dirs if found_dirs else ['.']
    
    def _find_test_dirs(self) -> List[str]:
        """Find test directories"""
        common_test_dirs = ['test', 'tests', 'spec', 'specs', '__tests__', 'testing']
        found_dirs = []
        
        for dir_name in common_test_dirs:
            if (self.project_path / dir_name).exists():
                found_dirs.append(dir_name)
                
        return found_dirs
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate comprehensive retrofit report"""
        if not self.analysis:
            self.assess()
        if not self.plan:
            self.generate_plan()
            
        report = f"""# AgenticScrum Retrofit Assessment Report

## Project: {self.project_path.name}

### Executive Summary
- **Complexity Score**: {self.analysis.complexity_score:.1f}/100
- **Estimated Timeline**: {self.plan.timeline_weeks} weeks
- **Team Size**: {self.analysis.team_size_estimate} developers
- **Project Age**: {self.analysis.project_age_estimate} years

### Technology Stack
**Languages**: {', '.join(f"{lang} ({count} files)" for lang, count in self.analysis.languages.items())}
**Frameworks**: {', '.join(self.analysis.frameworks) if self.analysis.frameworks else 'None detected'}
**Test Frameworks**: {', '.join(self.analysis.test_frameworks) if self.analysis.test_frameworks else 'None detected'}
**CI/CD**: {', '.join(self.analysis.ci_platforms) if self.analysis.ci_platforms else 'None detected'}

### Structure Analysis
- **Type**: {self.analysis.structure_type}
- **Code Patterns**: {json.dumps(self.analysis.code_patterns, indent=2)}

### Recommended Agents
{', '.join(self.plan.recommended_agents)}

### Integration Points
{json.dumps(self.plan.integration_points, indent=2)}

### Risk Assessment
{json.dumps(self.plan.risk_assessment, indent=2)}

### Implementation Plan
"""
        
        for phase in self.plan.phases:
            report += f"\n#### Phase {phase['phase']}: {phase['name']} ({phase['duration_weeks']} weeks)\n"
            for task in phase['tasks']:
                report += f"- {task}\n"
                
        report += """
### Next Steps
1. Review this assessment with your team
2. Run `retrofit_project.py init-agents` to create agent configurations  
3. Start with Phase 1 tasks
4. Monitor progress and adjust as needed

### Success Metrics
- Code quality improvements
- Development velocity increase  
- Bug reduction rate
- Team satisfaction scores

Generated by AgenticScrum Retrofit Tool
"""
        
        if output_path:
            output_file = Path(output_path)
            output_file.write_text(report)
            print(f"Report saved to {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Retrofit existing projects with AgenticScrum',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assess a project
  python retrofit_project.py assess --path /path/to/project
  
  # Generate a retrofit plan
  python retrofit_project.py plan --path /path/to/project
  
  # Initialize agents
  python retrofit_project.py init-agents --path /path/to/project --languages python,javascript
  
  # Create initial configuration
  python retrofit_project.py create-config --path /path/to/project
  
  # Generate full report
  python retrofit_project.py report --path /path/to/project --output retrofit_report.md
        """
    )
    
    parser.add_argument('command', 
                       choices=['assess', 'plan', 'init-agents', 'create-config', 'report'],
                       help='Command to execute')
    parser.add_argument('--path', required=True, help='Path to existing project')
    parser.add_argument('--output', help='Output file path (for report command)')
    parser.add_argument('--languages', help='Comma-separated list of languages (for init-agents)')
    parser.add_argument('--frameworks', help='Comma-separated list of frameworks (for init-agents)')
    
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.path)
    if not project_path.exists():
        print(f"Error: Project path {project_path} does not exist")
        sys.exit(1)
        
    retrofitter = ProjectRetrofitter(args.path)
    
    try:
        if args.command == 'assess':
            analysis = retrofitter.assess()
            print("\nProject Assessment Results:")
            print(json.dumps(asdict(analysis), indent=2))
            
        elif args.command == 'plan':
            plan = retrofitter.generate_plan()
            print("\nRetrofit Implementation Plan:")
            print(json.dumps(asdict(plan), indent=2))
            
        elif args.command == 'init-agents':
            languages = args.languages.split(',') if args.languages else ['python']
            frameworks = args.frameworks.split(',') if args.frameworks else []
            retrofitter.init_agents(languages, frameworks)
            
        elif args.command == 'create-config':
            config_path = retrofitter.create_config()
            print(f"\nConfiguration created at: {config_path}")
            
        elif args.command == 'report':
            report = retrofitter.generate_report(args.output)
            if not args.output:
                print(report)
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()