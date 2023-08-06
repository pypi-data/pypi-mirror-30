from setuptools import setup

setup(
    # The name of our pip package
    name='SPOJ-CMD',
    # The Python packages in this project
    packages=[
        # This is the `spoj` folder that contains __init__.py and cli.py
        'SPOJ',
    ],
    version="0.0.1",
    entry_points={
        'console_scripts': [
            #This line to maps main()` method in cli.py
            # to a shell command `spoj`
            'spoj = SPOJ.cli:main',
        ],
    },
	
    description='Python command line client to access SPOJ problems',
    url='https://github.com/amoghj8/spoj-cmd',
    author='Amogh A Joshi',
    author_email='amoghj8@gmail.com',
    scripts=['SPOJ/cli.py'],
    license='MIT',
    keywords='spoj cli competitiveprogramming developer'
)
