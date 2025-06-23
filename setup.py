from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="customer-care-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Customer Care AI - An intelligent customer support chatbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/customer-care-ai",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    python_requires=">=3.8",
    install_requires=[
        "rasa>=3.6.0",
        "python-dotenv>=0.19.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "customer-care-ai=main:main",
        ],
    },
)
