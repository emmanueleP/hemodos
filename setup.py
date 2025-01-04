from setuptools import setup, find_packages

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hemodos",
    version="1.0.3",
    author="Emmanuele Pani",
    author_email="150518833+emmanueleP@users.noreply.github.com", #GitHub email
    description="Software per la Gestione delle Donazioni di Sangue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emmanueleP/Hemodos",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    package_data={
        'hemodos': ['assets/*', 'config.json'],
    },
    entry_points={
        'console_scripts': [
            'hemodos=src.main:main',
        ],
    },
) 