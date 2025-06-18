"""Setup script for AgenticScrum CLI utility."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version from __init__.py
version = "0.1.0"
with open("agentic_scrum_setup/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="agentic-scrum-setup",
    version=version,
    author="AgenticScrum Contributors",
    author_email="",
    description="CLI utility for initializing AgenticScrum projects with AI agent configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AgenticScrum",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jinja2>=3.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agentic-scrum-setup=agentic_scrum_setup.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agentic_scrum_setup": [
            "templates/**/*.j2",
            "templates/**/.*.j2",  # Include hidden files like .gitignore.j2
            "templates/**/*.sample", 
            "templates/**/*.sh",
            "templates/**/*.py",
            "templates/**/*.md",
            "templates/**/*.txt",
            "templates/**/*.json",
        ],
    },
)