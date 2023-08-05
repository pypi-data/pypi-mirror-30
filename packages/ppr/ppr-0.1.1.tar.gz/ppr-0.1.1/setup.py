from setuptools import setup, find_packages

setup(
    name = 'ppr',
    version = '0.1.1',
    packages = find_packages(),
    description = 'Planar Python Robotics',
    long_description=('Software tool to experiment with 2D motion planning problems' +
    'for robot manipulators.'),
    author = 'Jeroen De Maeyer',
    author_email = 'jeroen.demaeyer@kuleuven.be',
    url = 'https://u0100037.pages.mech.kuleuven.be/planar_python_robotics/',
    download_url = 'https://gitlab.mech.kuleuven.be/u0100037/planar_python_robotics/raw/master/dist/ppr-0.1.1.tar.gz',
    keywords = ['robotics', 'motion planning'],
    classifiers = [],
    install_requires=['scipy', 'matplotlib'],
    python_requires='>=3',
)
