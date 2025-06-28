"""
Setup configuration for Agent Studio

Package configuration for distributing Agent Studio as a Python package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Set version directly to avoid exec issues
version = {"__version__": "1.0.0"}

setup(
    name="agent-studio",
    version=version.get("__version__", "1.0.0"),
    author="Agent Studio Team",
    author_email="team@agent-studio.dev",
    description="A comprehensive framework for building agent-based workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agent-studio/agent-studio",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "langgraph": [
            "langgraph>=0.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-studio=agent_studio.cli.main:main_cli",
            "agentstudio=agent_studio.cli.main:main_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "agent_studio": [
            "templates/*",
            "templates/**/*",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/agent-studio/agent-studio/issues",
        "Source": "https://github.com/agent-studio/agent-studio",
        "Documentation": "https://agent-studio.readthedocs.io/",
    },
)
