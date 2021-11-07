from setuptools import setup

setup(
    name="QticTacToe",
    version="1.0",
    author="somebody",
    author_email="a@b.io",
    description="...",
    long_description=open("README.rst", "r").read(),
    keywords="game multiplayer example pyqt5",
    project_urls={
        "Author Website": "https://www.alandmoore.com",
        "Publisher Website": "https://packtpub.com",
        "Source Code": "https://git.example.com/qtictactoe",
    },
    # packages and dependencies
    packages=["qtictactoe", "qtictactoe.images"],
    install_requires=["PyQt6"],
    python_requires=">=3.6",
    extras_require={"NetworkPlay": ["requests"]},
    # include_package_data=True,
    package_data={"qtictactoe.images": ["*.png"]},
    entry_points={"console_scripts": ["qtictactoe = qtictactoe.__main__:main"]},
)
