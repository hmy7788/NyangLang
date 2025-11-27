from setuptools import setup, find_packages

setup(
    name="nyanglang",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["main"],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["nyang=main:main"]},
)