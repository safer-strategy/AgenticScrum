"""Conversational onboarding module for AgenticScrum.

This module provides a natural conversation-based approach to project setup,
allowing users to describe their project in their own words while the POA
agent extracts requirements and creates the necessary structure.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import json
import re
from datetime import datetime


class ConversationalOnboarding:
    """Handle conversational project onboarding with POA guidance."""
    
    def __init__(self, output_dir: str = '.'):
        """Initialize the conversational onboarding handler.
        
        Args:
            output_dir: Directory where project will be created
        """
        self.output_dir = Path(output_dir)
        self.project_info = {
            'requirements': {},
            'gaps': [],
            'conversation_log': []
        }
        self.is_retrofit = False
        self.existing_analysis = {}
        
    def detect_existing_project(self, path: Optional[Path] = None) -> bool:
        """Detect if this is an existing project that needs retrofitting.
        
        Args:
            path: Path to check (defaults to current directory)
            
        Returns:
            True if existing project detected, False otherwise
        """
        check_path = path or Path.cwd()
        
        # Indicators of existing project
        indicators = [
            'package.json',
            'requirements.txt',
            'go.mod',
            'Cargo.toml',
            'pom.xml',
            'build.gradle',
            'composer.json',
            'Gemfile',
            '.git',
            'src/',
            'lib/',
            'app/',
        ]
        
        for indicator in indicators:
            if (check_path / indicator).exists():
                self.is_retrofit = True
                return True
                
        return False
    
    def analyze_existing_codebase(self, path: Path) -> Dict:
        """Perform read-only analysis of existing codebase.
        
        Args:
            path: Path to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'project_type': 'unknown',
            'language': 'unknown',
            'framework': None,
            'size': {'files': 0, 'loc': 0},
            'structure': {},
            'dependencies': [],
            'test_coverage': None,
            'strengths': [],
            'gaps': [],
            'integration_points': []
        }
        
        # Detect language and framework
        if (path / 'package.json').exists():
            analysis['language'] = self._detect_js_project(path)
            analysis['project_type'] = 'node'
        elif (path / 'requirements.txt').exists() or (path / 'setup.py').exists():
            analysis['language'] = 'python'
            analysis['project_type'] = 'python'
            analysis['framework'] = self._detect_python_framework(path)
        elif (path / 'go.mod').exists():
            analysis['language'] = 'go'
            analysis['project_type'] = 'go'
        elif (path / 'Cargo.toml').exists():
            analysis['language'] = 'rust'
            analysis['project_type'] = 'rust'
        
        # Count files and estimate size
        file_count = 0
        code_extensions = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.cs', '.rb', '.php'}
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                if file_path.suffix in code_extensions:
                    file_count += 1
                    
        analysis['size']['files'] = file_count
        
        # Check for tests
        test_dirs = ['test', 'tests', 'spec', '__tests__']
        for test_dir in test_dirs:
            if (path / test_dir).exists():
                analysis['strengths'].append(f"Has {test_dir} directory")
                
        # Check for documentation
        if (path / 'README.md').exists() or (path / 'README.rst').exists():
            analysis['strengths'].append("Has README")
        else:
            analysis['gaps'].append("No README found")
            
        # Check for CI/CD
        ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci']
        for ci_file in ci_files:
            if (path / ci_file).exists():
                analysis['strengths'].append(f"Has CI/CD ({ci_file})")
                
        self.existing_analysis = analysis
        return analysis
    
    def _detect_js_project(self, path: Path) -> str:
        """Detect JavaScript or TypeScript project."""
        if (path / 'tsconfig.json').exists():
            return 'typescript'
        return 'javascript'
    
    def _detect_python_framework(self, path: Path) -> Optional[str]:
        """Detect Python framework being used."""
        # Check imports in Python files
        framework_indicators = {
            'fastapi': ['from fastapi', 'import fastapi'],
            'flask': ['from flask', 'import flask'],
            'django': ['from django', 'import django', 'django.core'],
            'pytest': ['import pytest', 'from pytest'],
        }
        
        for py_file in path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for framework, indicators in framework_indicators.items():
                        if any(ind in content.lower() for ind in indicators):
                            return framework
            except:
                continue
                
        return None
    
    def start_conversation(self) -> str:
        """Start the conversational onboarding process.
        
        Returns:
            Initial POA greeting and prompt
        """
        # Check if this is an existing project
        if self.detect_existing_project():
            return self._start_retrofit_conversation()
        else:
            return self._start_greenfield_conversation()
    
    def _start_greenfield_conversation(self) -> str:
        """Start conversation for a new project."""
        return """Hello! I'm your Product Owner Agent (POA), and I'm here to help you create your project.

I'll guide you through a natural conversation to understand what you want to build. You can:
- Describe your idea in your own words
- Paste an existing PRD or requirements document
- Share a simple description or detailed specifications

There's no wrong way to start. What would you like to build?"""

    def _start_retrofit_conversation(self) -> str:
        """Start conversation for an existing project."""
        # Analyze the existing codebase
        analysis = self.analyze_existing_codebase(Path.cwd())
        
        return f"""I notice you have an existing {analysis['language']} project. I'll help you enhance it with AgenticScrum!

I've performed a read-only analysis of your codebase:
- **Language**: {analysis['language']}
- **Framework**: {analysis['framework'] or 'Not detected'}
- **Project Size**: {analysis['size']['files']} code files
- **Strengths**: {', '.join(analysis['strengths'][:3]) if analysis['strengths'] else 'To be assessed'}

I can help you:
1. Add AgenticScrum agents for better development workflow
2. Create structured documentation from your existing code
3. Set up enhanced project management with AI assistance

Your existing code will remain untouched - I'll only add new supportive files.

What aspects of your project would you like to enhance?"""

    def process_user_input(self, user_input: str) -> Tuple[str, Dict]:
        """Process user input and extract requirements.
        
        Args:
            user_input: Raw user input (conversation or PRD)
            
        Returns:
            Tuple of (POA response, extracted requirements)
        """
        # Log conversation
        self.project_info['conversation_log'].append({
            'timestamp': datetime.now().isoformat(),
            'speaker': 'user',
            'message': user_input
        })
        
        # Detect input type
        input_type = self._classify_input(user_input)
        
        if input_type == 'formal_prd':
            return self._process_formal_prd(user_input)
        elif input_type == 'technical_spec':
            return self._process_technical_spec(user_input)
        else:
            return self._process_informal_description(user_input)
    
    def _classify_input(self, user_input: str) -> str:
        """Classify the type of user input.
        
        Returns:
            'formal_prd', 'technical_spec', or 'informal'
        """
        lower_input = user_input.lower()
        
        # Check for PRD indicators
        prd_indicators = [
            'product requirements',
            'executive summary',
            'functional requirements',
            'non-functional requirements',
            'acceptance criteria',
            'user stories',
            '## requirements',
            '# prd'
        ]
        
        if any(indicator in lower_input for indicator in prd_indicators):
            return 'formal_prd'
        
        # Check for technical spec indicators
        tech_indicators = [
            'api endpoints',
            'database schema',
            'architecture',
            'class diagram',
            'system design',
            'technical requirements'
        ]
        
        if any(indicator in lower_input for indicator in tech_indicators):
            return 'technical_spec'
        
        return 'informal'
    
    def _process_formal_prd(self, prd_content: str) -> Tuple[str, Dict]:
        """Process a formal PRD document."""
        extracted = self._extract_from_prd(prd_content)
        
        # Identify gaps
        gaps = self._identify_requirement_gaps(extracted)
        
        if gaps:
            response = f"""I've reviewed your comprehensive PRD. Excellent structure! I found most of what I need, but let me clarify a few points:

"""
            for i, gap in enumerate(gaps[:3], 1):  # Limit to 3 questions at a time
                response += f"{i}. {gap['question']}\n"
                
            self.project_info['gaps'] = gaps
        else:
            response = """Perfect! Your PRD is very comprehensive. I have everything I need to create a structured development plan.

Based on your requirements, I'll create:
1. Epic breakdown with prioritized features
2. Initial user stories for the first sprint
3. Technical architecture recommendations
4. Development timeline estimation

Would you like me to proceed with creating the project structure?"""
        
        self.project_info['requirements'].update(extracted)
        return response, extracted
    
    def _process_informal_description(self, description: str) -> Tuple[str, Dict]:
        """Process an informal project description."""
        # Extract what we can
        extracted = {
            'raw_description': description,
            'detected_features': self._extract_features(description),
            'detected_users': self._extract_user_types(description),
            'detected_goals': self._extract_goals(description)
        }
        
        # Build conversational response
        response = "That sounds interesting! "
        
        # Ask clarifying questions based on what's missing
        questions = []
        
        if not extracted['detected_users']:
            questions.append("Who will be the primary users of this system?")
        
        if not extracted['detected_goals']:
            questions.append("What's the main problem you're trying to solve?")
            
        if len(extracted['detected_features']) < 2:
            questions.append("What are the key features you envision?")
        
        if questions:
            response += "Let me understand better:\n\n"
            for q in questions[:2]:  # Ask max 2 questions at a time
                response += f"- {q}\n"
        else:
            response += """I think I understand the basics. Let me dig a bit deeper:

- How many users do you expect to have?
- What's your timeline for launching this?
- Are there any specific technical requirements or constraints I should know about?"""
        
        self.project_info['requirements'].update(extracted)
        return response, extracted
    
    def _extract_from_prd(self, prd_content: str) -> Dict:
        """Extract structured information from PRD."""
        extracted = {}
        
        # Extract sections using regex
        sections = {
            'vision': r'(?:vision|executive summary|overview)[:\s]*\n(.*?)(?=\n#|\n##|\Z)',
            'users': r'(?:target users|user personas|users)[:\s]*\n(.*?)(?=\n#|\n##|\Z)',
            'features': r'(?:features|functional requirements|functionality)[:\s]*\n(.*?)(?=\n#|\n##|\Z)',
            'technical': r'(?:technical requirements|architecture|technical)[:\s]*\n(.*?)(?=\n#|\n##|\Z)',
            'security': r'(?:security|compliance|privacy)[:\s]*\n(.*?)(?=\n#|\n##|\Z)',
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, prd_content, re.IGNORECASE | re.DOTALL)
            if match:
                extracted[key] = match.group(1).strip()
        
        return extracted
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract potential features from text."""
        features = []
        
        # Look for feature indicators
        feature_patterns = [
            r'(?:feature|functionality|capability)[:\s]+([^.!?\n]+)',
            r'(?:ability to|able to|can)\s+([^.!?\n]+)',
            r'(?:system should|app should|it should)\s+([^.!?\n]+)',
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            features.extend(matches)
        
        return list(set(features))[:10]  # Limit to 10 features
    
    def _extract_user_types(self, text: str) -> List[str]:
        """Extract potential user types from text."""
        users = []
        
        # Common user type patterns
        user_patterns = [
            r'(?:for|used by|users?)\s+(\w+\s*\w*)\s*(?:who|that|to)',
            r'(\w+\s*\w*)\s+(?:will use|uses|needs)',
        ]
        
        for pattern in user_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            users.extend(matches)
        
        return list(set(users))[:5]
    
    def _extract_goals(self, text: str) -> List[str]:
        """Extract project goals from text."""
        goals = []
        
        goal_patterns = [
            r'(?:goal is to|aims to|designed to)\s+([^.!?\n]+)',
            r'(?:solve|address|improve|help)\s+([^.!?\n]+)',
        ]
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            goals.extend(matches)
        
        return list(set(goals))[:5]
    
    def _identify_requirement_gaps(self, extracted: Dict) -> List[Dict]:
        """Identify missing critical requirements."""
        gaps = []
        
        required_elements = {
            'security': "I notice you haven't mentioned security requirements. How should user data be protected?",
            'scale': "What scale are you planning for? (number of users, data volume, geographic distribution)",
            'timeline': "What's your target timeline for the MVP and full launch?",
            'integrations': "Will this need to integrate with any existing systems or third-party services?",
            'compliance': "Are there any regulatory compliance requirements (GDPR, HIPAA, etc.)?",
            'budget': "Do you have any budget constraints I should be aware of?",
        }
        
        for key, question in required_elements.items():
            if key not in extracted or not extracted.get(key):
                gaps.append({
                    'element': key,
                    'question': question,
                    'priority': 'high' if key in ['security', 'scale'] else 'medium'
                })
        
        return gaps
    
    def _process_technical_spec(self, spec_content: str) -> Tuple[str, Dict]:
        """Process a technical specification."""
        extracted = {
            'technical_details': spec_content,
            'is_technical': True
        }
        
        response = """I see you've provided technical specifications. This is great for understanding the implementation details!

To create a complete project plan, I also need to understand:
1. Who are the end users and what problems are we solving for them?
2. What are the business goals and success metrics?
3. What's the timeline and any constraints?

Could you share more about the business and user aspects of this project?"""
        
        self.project_info['requirements'].update(extracted)
        return response, extracted
    
    def complete_requirements_gathering(self) -> bool:
        """Check if we have enough information to proceed.
        
        Returns:
            True if requirements are complete enough
        """
        required = ['users', 'features', 'goals']
        have_required = all(
            key in self.project_info['requirements'] 
            for key in required
        )
        
        # For retrofits, we need less information
        if self.is_retrofit:
            return bool(self.project_info['requirements'])
        
        return have_required
    
    def generate_project_structure(self) -> Dict:
        """Generate the project structure from gathered requirements.
        
        Returns:
            Dictionary with project configuration
        """
        reqs = self.project_info['requirements']
        
        # Determine project configuration
        config = {
            'project_name': self._extract_project_name(),
            'project_type': 'single',  # Can be enhanced to detect fullstack
            'language': self._determine_language(),
            'framework': self._determine_framework(),
            'agents': self._determine_agents(),
            'enable_qa': True,
            'enable_mcp': True,
            'conversation_derived': True,
            'original_requirements': self.project_info
        }
        
        if self.is_retrofit:
            config['is_retrofit'] = True
            config['existing_analysis'] = self.existing_analysis
            
        return config
    
    def _extract_project_name(self) -> str:
        """Extract or generate project name."""
        # Try to extract from requirements
        if 'name' in self.project_info['requirements']:
            return self.project_info['requirements']['name']
        
        # Try to extract from description
        desc = self.project_info['requirements'].get('raw_description', '')
        
        # Look for "X app", "X system", "X platform"
        patterns = [
            r'(?:build|create|develop)\s+(?:a|an|the)?\s*(\w+)',
            r'(\w+)\s+(?:app|system|platform|tool)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                name = match.group(1)
                return name.replace(' ', '')
        
        return 'MyProject'
    
    def _determine_language(self) -> str:
        """Determine the best language based on requirements."""
        if self.is_retrofit:
            return self.existing_analysis.get('language', 'python')
        
        # Check for language mentions in requirements
        reqs_text = str(self.project_info['requirements']).lower()
        
        languages = {
            'python': ['python', 'django', 'flask', 'fastapi', 'ml', 'data', 'api'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'frontend'],
            'typescript': ['typescript', 'ts', 'angular', 'type-safe'],
            'go': ['go', 'golang', 'microservice', 'performance'],
            'rust': ['rust', 'system', 'performance', 'safety'],
            'java': ['java', 'spring', 'enterprise'],
        }
        
        scores = {}
        for lang, keywords in languages.items():
            scores[lang] = sum(1 for kw in keywords if kw in reqs_text)
        
        # Return language with highest score, default to python
        if scores:
            return max(scores, key=scores.get)
        return 'python'
    
    def _determine_framework(self) -> Optional[str]:
        """Determine the best framework based on requirements."""
        if self.is_retrofit:
            return self.existing_analysis.get('framework')
        
        lang = self._determine_language()
        reqs_text = str(self.project_info['requirements']).lower()
        
        framework_keywords = {
            'python': {
                'fastapi': ['api', 'rest', 'fast', 'modern'],
                'django': ['admin', 'cms', 'full'],
                'flask': ['simple', 'micro', 'lightweight']
            },
            'javascript': {
                'express': ['api', 'server', 'backend'],
                'react': ['ui', 'frontend', 'interactive'],
                'nodejs': ['server', 'real-time']
            }
        }
        
        if lang in framework_keywords:
            frameworks = framework_keywords[lang]
            scores = {}
            
            for fw, keywords in frameworks.items():
                scores[fw] = sum(1 for kw in keywords if kw in reqs_text)
            
            if scores:
                best_fw = max(scores, key=scores.get)
                if scores[best_fw] > 0:
                    return best_fw
        
        return None
    
    def _determine_agents(self) -> str:
        """Determine which agents to include."""
        agents = ['poa', 'sma']  # Always include these
        
        lang = self._determine_language()
        
        # Add language-specific developer agent
        lang_agent_map = {
            'python': 'deva_python',
            'javascript': 'deva_javascript',
            'typescript': 'deva_typescript',
            'go': 'deva_go',
            'rust': 'deva_rust',
            'java': 'deva_java',
        }
        
        if lang in lang_agent_map:
            agents.append(lang_agent_map[lang])
        
        # Always add QA agent
        agents.append('qaa')
        
        # Add security agent if security mentioned
        if 'security' in str(self.project_info['requirements']).lower():
            agents.append('saa')
        
        return ','.join(agents)
    
    def save_original_requirements(self, project_path: Path):
        """Save the original requirements for reference.
        
        Args:
            project_path: Path to the project directory
        """
        docs_path = project_path / 'docs'
        docs_path.mkdir(exist_ok=True)
        
        # Save original requirements/conversation
        original_path = docs_path / 'PRD_ORIGINAL.md'
        
        with open(original_path, 'w') as f:
            f.write("# Original Project Requirements\n\n")
            f.write("*This document preserves the original requirements as provided by the user.*\n\n")
            
            f.write("## Conversation Log\n\n")
            for entry in self.project_info['conversation_log']:
                f.write(f"**{entry['speaker'].title()}** ({entry['timestamp']}):\n")
                f.write(f"{entry['message']}\n\n")
                f.write("---\n\n")
            
            if self.project_info['requirements']:
                f.write("## Extracted Requirements\n\n")
                f.write("```json\n")
                f.write(json.dumps(self.project_info['requirements'], indent=2))
                f.write("\n```\n")