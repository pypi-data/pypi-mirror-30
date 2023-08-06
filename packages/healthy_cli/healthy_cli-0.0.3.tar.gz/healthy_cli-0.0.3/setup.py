from setuptools import setup

setup(
    name='healthy_cli',
    version='0.0.3',
    url='https://github.com/OwnHealthIL/Backend',
    python_requires='>=2.7, <3',
    install_requires=['docopt==0.6.2'],
    entry_points="""
    [console_scripts]
    healthy_cli = run_service:main
    """
)