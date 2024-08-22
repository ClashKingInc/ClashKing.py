from setuptools import setup, find_packages

setup(
    name="clashking.py",
    version="0.1.0",
    description="A wrapper for the ClashKing API & utils for the ClashKing Project",
    author="Your Name",
    author_email="devs@clashkingbot.com",
    url="https://github.com/yourusername/my_api_client",  # Replace with your GitHub URL
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.1",
        "cachetools>=5.2.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
