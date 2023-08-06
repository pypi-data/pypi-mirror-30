from setuptools import setup

try:
    with open('README.rst') as f:
        long_description = f.read()
except IOError:
    long_description = ''

setup(
    name="huhu",
    version="0.0.3",
    description="shortcut install & freeze pip packages",
    long_description=long_description,
    author="Mehmet Kose",
    author_email="mehmetkose122@gmail.com",
    url="https://github.com/mehmetkose/huhu",
    license="MIT",
    packages=['huhu'],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    provides=['huhu'],
    entry_points = {
        'console_scripts': [
            'huhu = huhu.__init__:main'
        ],
    },
    test_suite = "tests"
)
