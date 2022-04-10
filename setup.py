import os
import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


def load_requirements(path_dir=here, comment_char="#"):
    with open(os.path.join(path_dir, "requirements.txt"), "r") as file:
        lines = [line.strip() for line in file.readlines()]
    requirements = []
    for line in lines:
        # filer all comments
        if comment_char in line:
            line = line[: line.index(comment_char)]
        if line:  # if requirement is not empty
            requirements.append(line)
    return requirements


setup(
    name='airfoil_generator',
    version='0.1',
    description='流场数据集生成器',
    author='Yao Weijie',
    author_email='996267113@qq.com',
    python_requires='>=3.6',
    packages=find_packages(),
    install_requires=load_requirements(),
    entry_points={
        'console_scripts': [
            'airfoil_generator = airfoil_generator.cli:main',
        ]
    }
)
