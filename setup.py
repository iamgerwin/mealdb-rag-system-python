from setuptools import setup, find_packages

setup(
    name="mealdb-rag",
    version="1.0.0",
    description="RAG system for TheMealDB with local caching and ToolFront integration",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "toolfront>=0.1.0",
        "requests>=2.31.0", 
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "asyncio-throttle>=1.0.2",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "mealdb-rag=cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
