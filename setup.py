"""
Setup configuration for DocScalpel.

Enables pip installation with CLI entry point.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="docscalpel",
    version="1.1.0",
    description="Surgical precision for PDF element extraction - Extract figures, tables, and equations using deep learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Minsu Jang",
    author_email="minsu@etri.re.kr",
    url="https://github.com/zebehn/docscalpel",
    project_urls={
        "Documentation": "https://github.com/zebehn/docscalpel/blob/main/README.md",
        "Source": "https://github.com/zebehn/docscalpel",
        "Issue Tracker": "https://github.com/zebehn/docscalpel/issues",
    },
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests", "tests.*", "fixtures", "docs"]),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'docscalpel=docscalpel.cli.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="pdf extraction figures tables equations deep-learning yolo document-analysis",
)
