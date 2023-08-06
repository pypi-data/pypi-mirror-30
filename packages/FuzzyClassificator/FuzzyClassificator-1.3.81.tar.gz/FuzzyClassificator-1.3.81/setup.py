#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup
import os

__version__ = '1.3'  # identify main version of FuzzyClassificator

if 'TRAVIS_BUILD_NUMBER' in os.environ and 'TRAVIS_BRANCH' in os.environ:
    print("This is TRAVIS-CI build")
    print("TRAVIS_BUILD_NUMBER = {}".format(os.environ['TRAVIS_BUILD_NUMBER']))
    print("TRAVIS_BRANCH = {}".format(os.environ['TRAVIS_BRANCH']))

    __version__ += '.{}{}'.format(
        '' if 'release' in os.environ['TRAVIS_BRANCH'] or os.environ['TRAVIS_BRANCH'] == 'master' else 'dev',
        os.environ['TRAVIS_BUILD_NUMBER'],
    )

else:
    print("This is local build")
    __version__ += '.localbuild'  # set version as major.minor.localbuild if local build: python setup.py install

print("FuzzyClassificator build version = {}".format(__version__))


setup(
    name='FuzzyClassificator',

    version=__version__,

    description='This program uses neural networks to solve classification problems, and uses fuzzy sets and fuzzy logic to interpreting results.',

    long_description='You can see detailed user manual here: https://devopshq.github.io/FuzzyClassificator/',

    license='MIT',

    author='Timur Gilmullin',

    author_email='tim55667757@gmail.com',

    url='https://devopshq.github.io/FuzzyClassificator/',

    download_url='https://github.com/devopshq/FuzzyClassificator.git',

    entry_points={'console_scripts': ['FuzzyClassificator = FuzzyClassificator:Main']},

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],

    keywords=[
        'classificating',
        'clustering',
        'classificator',
        'fuzzy',
        'logic',
        'math',
        'science',
        'research',
    ],

    packages=[
        '.',
    ],

    setup_requires=[
    ],

    tests_require=[
        'pytest',
    ],

    install_requires=[
    ],

    package_data={
        '': [
            './pybrain/*.py',
            './pybrain/auxiliary/*.py',
            './pybrain/datasets/*.py',
            './pybrain/optimization/*.py',
            './pybrain/optimization/distributionbased/*.py',
            './pybrain/optimization/finitedifference/*.py',
            './pybrain/optimization/memetic/*.py',
            './pybrain/optimization/populationbased/*.py',
            './pybrain/optimization/populationbased/coevolution/*.py',
            './pybrain/optimization/populationbased/multiobjective/*.py',
            './pybrain/rl/agents/*.py',
            './pybrain/rl/environments/*.py',
            './pybrain/rl/environments/cartpole/*.py',
            './pybrain/rl/environments/cartpole/fast_version/*.py',
            './pybrain/rl/environments/classic/*.py',
            './pybrain/rl/environments/flexcube/*.py',
            './pybrain/rl/environments/functions/*.py',
            './pybrain/rl/environments/mazes/*.py',
            './pybrain/rl/environments/mazes/tasks/*.py',
            './pybrain/rl/environments/ode/*.py',
            './pybrain/rl/environments/ode/instances/*.py',
            './pybrain/rl/environments/ode/models/*.py',
            './pybrain/rl/environments/ode/tasks/*.py',
            './pybrain/rl/environments/ode/tools/*.py',
            './pybrain/rl/environments/shipsteer/*.py',
            './pybrain/rl/environments/simple/*.py',
            './pybrain/rl/environments/simplerace/*.py',
            './pybrain/rl/environments/twoplayergames/*.py',
            './pybrain/rl/environments/twoplayergames/capturegameplayers/*.py',
            './pybrain/rl/environments/twoplayergames/gomokuplayers/*.py',
            './pybrain/rl/environments/twoplayergames/tasks/*.py',
            './pybrain/rl/experiments/*.py',
            './pybrain/rl/explorers/*.py',
            './pybrain/rl/explorers/continuous/*.py',
            './pybrain/rl/explorers/discrete/*.py',
            './pybrain/rl/learners/*.py',
            './pybrain/rl/learners/directsearch/*.py',
            './pybrain/rl/learners/meta/*.py',
            './pybrain/rl/learners/modelbased/*.py',
            './pybrain/rl/learners/valuebased/*.py',
            './pybrain/structure/*.py',
            './pybrain/structure/connections/*.py',
            './pybrain/structure/evolvables/*.py',
            './pybrain/structure/modules/*.py',
            './pybrain/structure/networks/*.py',
            './pybrain/structure/networks/custom/*.py',
            './pybrain/supervised/*.py',
            './pybrain/supervised/evolino/*.py',
            './pybrain/supervised/knn/*.py',
            './pybrain/supervised/knn/lsh/*.py',
            './pybrain/supervised/trainers/*.py',
            './pybrain/tools/*.py',
            './pybrain/tools/customxml/*.py',
            './pybrain/tools/datasets/*.py',
            './pybrain/tools/mixtures/*.py',
            './pybrain/tools/networking/*.py',
            './pybrain/tools/plotting/*.py',
            './pybrain/unsupervised/*.py',
            './pybrain/unsupervised/trainers/*.py',

            './tests/*.py',
            'FuzzyClassificator.py',
            'PyBrainLearning.py',
            'FuzzyRoutines.py',
            'FCLogger.py',
            'candidates.dat',
            'ethalons.dat',
            'network.xml',
            'report.txt',
            'LICENSE',
            'README.md',
            'classification_process.*',
        ],
    },

    zip_safe=True,
)
