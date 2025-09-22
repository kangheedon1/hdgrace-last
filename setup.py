"""
Setup configuration for HDGRACE package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from package
version = "2.0.0"

setup(
    name="hdgrace",
    version=version,
    author="HDGRACE Development Team",
    author_email="dev@hdgrace.com",
    description="High-Definition Generator and Runtime Application Code Engine - Production Ready",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kangheedon1/hdgrace-last",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies - keeping minimal for production deployment
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "pre-commit>=2.0.0",
        ],
        "yaml": [
            "PyYAML>=5.4.0",
        ],
        "full": [
            "PyYAML>=5.4.0",
            "lxml>=4.6.0",
            "requests>=2.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hdgrace=hdgrace.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hdgrace": [
            "templates/*.txt",
            "config/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/kangheedon1/hdgrace-last/issues",
        "Source": "https://github.com/kangheedon1/hdgrace-last",
        "Documentation": "https://github.com/kangheedon1/hdgrace-last/wiki",
    },
)