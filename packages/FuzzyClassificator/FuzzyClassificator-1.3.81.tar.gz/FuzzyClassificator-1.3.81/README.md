FuzzyClassificator
==================

[![FuzzyClassificator build status](https://travis-ci.org/devopshq/FuzzyClassificator.svg?branch=develop)](https://travis-ci.org/devopshq/FuzzyClassificator) [![FuzzyClassificator code quality](https://api.codacy.com/project/badge/Grade/f1511115ad144614915fc5767029e2d9)](https://www.codacy.com/app/tim55667757/FuzzyClassificator/dashboard) [![FuzzyClassificator on PyPI](https://img.shields.io/pypi/v/FuzzyClassificator.svg)](https://pypi.python.org/pypi/FuzzyClassificator) [![FuzzyClassificator license](https://img.shields.io/pypi/l/FuzzyClassificator.svg)](https://github.com/devopshq/FuzzyClassificator/blob/master/LICENSE)

*Index:*
- [Introduction](#Chapter_1)
- [How to work with FuzzyClassificator](#Chapter_2)
    - [Presets](#Chapter_2_1)
    - [Install](#Chapter_2_2)
    - [Usage](#Chapter_2_3)
        - [Optional arguments](#Chapter_2_3_1)
        - [Work modes](#Chapter_2_3_2)
        - [Usage examples](#Chapter_2_3_3)
- [Preparing data](#Chapter_3)
    - [ethalons.dat](#Chapter_3_1)
        - [Example of ethalons.dat](#Chapter_3_1_1)
    - [candidates.dat](#Chapter_3_2)
        - [Example of candidates.dat](#Chapter_3_2_1)
- [Report of classificating](#Chapter_4)
- [Work with API](#Chapter_5)
    - [FuzzyClassificator.py](#Chapter_5_1)
        - [API example to run Learning mode](#Chapter_5_1_1)
        - [API example to run Classifying mode](#Chapter_5_1_2)
        - [Another API parameters](#Chapter_5_1_3)
    - [PyBrainLearning.py](#Chapter_5_2)
    - [FuzzyRoutines.py](#Chapter_5_3)
        - [Work with membership functions](#Chapter_5_3_1)
        - [Work with fuzzy set](#Chapter_5_3_2)
        - [Work with fuzzy scales](#Chapter_5_3_3)
        - [Work with Universal Fuzzy Scale](#Chapter_5_3_4)
        - [Work with fuzzy logic operators](#Chapter_5_3_5)
        - [Output examples](#Chapter_5_3_6)


<a name="Chapter_1"></a>Introduction
------------------------------------

This program uses neural networks to solve classification problems, and uses fuzzy sets and fuzzy logic to interpreting results. FuzzyClassificator provided under the MIT License.

How does it work? Let see the process scheme below.

![Two Stage of Classification Process](classification_process.png "Two Stage of Classification Process")


<a name="Chapter_2"></a>How to work with FuzzyClassificator
-----------------------------------------------------------

FuzzyClassificator uses ethalons.dat (default) as learning data and candidates.dat (default) for classifying data (See "Preparing data" chapter).
Work contains two steps:

1. Learning. At this step program parses ethalon data, learning neural network on this data and then saves neural network configuration into file.

2. Classifying. At this step program uses trained network for classification candidates from data file.


<a name="Chapter_2_1"></a>**Presets**

The simplest way to use FuzziClassificator without some troubles is to install Pyzo + Anaconda interpreter, which contains all needable scientific libraries.

[Pyzo](http://www.pyzo.org/start.html) is a cross-platform Python IDE focused on interactivity and introspection, which makes it very suitable for scientific computing.

[Anaconda](https://www.continuum.io/downloads) is the open data science platform powered by Python. The open source version of Anaconda is a high performance distribution of Python and includes most of the popular Python packages for scientific calculation.

In all examples below, we used an Anaconda Python interpreter when you saw keyword "python" or "pip".


<a name="Chapter_2_2"></a>**Install**

You can install FuzzyClassificator using standart pip from Anaconda Python interpreter:

    pip install FuzzyClassificator [--upgrade] [--pre]
    
or using standart setuptools from Anaconda Python interpreter to build local version:

    git clone https://github.com/devopshq/FuzzyClassificator.git FuzzyClassificator
    cd FuzzyClassificator
    python setup.py install

After installing you can check the version of the FuzzyClassificator:

    FuzzyClassificator --version


<a name="Chapter_2_3"></a>**Usage**

Run program through Anaconda Python interpreter: 
    
    python FuzzyClassificator.py [options] [--learn]|[--classify] [Network_Options]

or like command-line script if installed via pip:

    FuzzyClassificator [options] [--learn]|[--classify] [Network_Options]

In all the examples below, we will assume that the FuzzyClassificator installed via pip.


<a name="Chapter_2_3_1"></a>***Optional arguments***

    -h, --help
        Show help message and exit.

    -v, --version
        Show current version of FuzzyClassificator: 
            [major].[minor].[build] if builded from master or release*,
            [major].[minor].dev[build] if builded from other branches,
            [major].[minor].localbuild if local builded with setup.py install,
            unknown if not installed from PyPI or simply run as python script.

    -l [verbosity], --debug-level=[verbosity]
        Use 1, 2, 3, 4, 5 or DEBUG, INFO, WARNING, ERROR, CRITICAL debug info verbosity,
        INFO (2) by default.

    -e [ethalon_filename], --ethalons=[ethalon_filename]
        File with ethalon data samples, ethalons.dat by default.

    -c [candidates_filename], --candidates=[candidates_filename]
        File with candidates data samples, candidates.dat by default.

    -n [network_filename], --network=[network_filename]
        File with Neuro Network configuration, network.xml by default.

    -r [report_filename], --report=[report_filename]
        File with Neuro Network configuration, report.txt by default.

    -bn [best_network_filename], --best-network=[best_network_filename]
        Copy best network to this file, best_nn.xml by default.

    -bni [best_network_info_filename], --best-network-info=[best_network_info_filename]
        File with information about best network, best_nn.txt by default.

    -ic [indexes], --ignore-col=[indexes]
        Columns in input files that should be ignored.
        Use only dash and comma as separator numbers, other symbols are ignored.
        Example (no space after comma): 1,2,5-11

    -ir [indexes], --ignore-row=[indexes]
        Rows in input files that should be ignored.
        Use only dash and comma as separator numbers, other symbols are ignored.
        1st header row always set as ignored.
        Example (no space after comma): 2,4-7

    -sep [TAB|SPACE|separator_char], --separator=[TAB|SPACE|separator_char]
        Column's separator in raw data files.
        It can be TAB or SPACE abbreviation, comma, dot, semicolon or other char.
        TAB symbol by default.

    --no-fuzzy
        Add key if You doesn't want show fuzzy results, only real. Not set by default.

    --show-expected
        Show expected results in Classify mode. 
        WARNING! Use only if your dat-file contains columns with expected results!

    --reload
        Add key if You want reload network from file before usage. Not set by default.

    -u [epochs], --update=[epochs]
        Update error status after this epochs time, 5 by default.
        This parameter affected training speed.


<a name="Chapter_2_3_2"></a>***Work modes***

Learning Mode:
    
    --learn [Network_Options]
        Start program in learning mode, where Network_Options is a dictionary:
        
        {
        config=inputs,layer1,layer2,...,outputs
            where inputs is number of neurons in input layer,
            layer1..N are number of neurons in hidden layers,
            and outputs is number of neurons in output layer

        epochs=[int_num]
            this is a positive integer number, greater than 0, means the number of training cycles

        rate=[float_num]
            this is parameter of rate of learning, float number in (0, 1]

        momentum=[float_num]
            this is parameter of momentum of learning, float number in (0, 1]

        epsilon=[float_num]
            this parameter used to compare the distance between the two vectors, float number in (0, 1]

        stop=[float_num]
            this is stop parameter of learning (percent of errors), float number in [0, 100]
        }

Classifying Mode:

    --classify [Network_Options]
        Start program in classificator mode, where Network_Options is a dictionary:

        {
        config=inputs,layer1,layer2,...,outputs
            where inputs is number of neurons in input layer,
            layer1..N are number of neurons in hidden layers,
            and outputs is number of neurons in output layer
        }


<a name="Chapter_2_3_3"></a>***Usage examples***

Start learning with user's ethalon data file and neuronet options Config=(3,[3,2],2), 10 epochs, 0.05 learning rate and 0.05 momentum, epsilon is 0.1 and stop learning if errors less than 10%, update information in log every epochs and reload previous network for re-train:

    FuzzyClassificator --ethalons ethalons.dat --separator=TAB --debug-level=DEBUG --update 1 --reload --learn config=3,3,2,2 epochs=10 rate=0.05 momentum=0.05 epsilon=0.1 stop=10

Classify all candidates from file candidates.dat and show result in report.txt:

    FuzzyClassificator --candidates candidates.dat --network network.xml --report report.txt --separator=TAB --debug-level=DEBUG --classify config=3,3,2,2


<a name="Chapter_3"></a>Preparing data
--------------------------------------


<a name="Chapter_3_1"></a>**ethalons.dat**

This is default file with ethalon dataset. This file contains tab-delimited data (by default) that looks like this:

    <first header line with column names> 
    and then some strings contains real or fuzzy values:
    - M input columns: <1st value><tab>...<tab><M-th value>
    - N output columns: <1st value><tab>...<tab><N-th value>
For each input vector level of membership in the class characterized by the output vector.


<a name="Chapter_3_1_1"></a>***Example of ethalons.dat***

    input1  input2  input3  1st_class_output  2nd_class_output
    0.1     0.2     Min     Min               Max
    0.2     0.3     Low     Min               Max
    0.3     0.4     Med     Min               Max
    0.4     0.5     Med     Max               Min
    0.5     0.6     High    Max               Min
    0.6     0.7     Max     Max               Min

For training on this dataset use learn key with parameters:

    --learn config=3,3,2,2 

where first config parameter mean that dimension of input vector is 3, last config parameter mean that 
dimension of output vector is 2, and the middle "3,2" parameters means that neural network must be created with two hidden layers, three neurons in 1st hidden layer and two neurons in 2nd.


<a name="Chapter_3_2"></a>**candidates.dat**

This is default file with dataset for classifying. This file contains tab-delimited data (by default) that looks like this:

    <first header line with column names>
    and then some strings contains real or fuzzy values:
    -  M input columns: <1st value><tab>...<tab><M-th value>


<a name="Chapter_3_2_1"></a>***Example of candidates.dat***

    input1  input2  input3  1st_class_output  2nd_class_output
    0.12    0.32    Min
    0.32    0.35    Low
    0.54    0.57    Med
    0.65    0.68    High
    0.76    0.79    Max


<a name="Chapter_4"></a>Report of classificating
------------------------------------------------

If you trained Neuronet with command:

    FuzzyClassificator --ethalons ethalons.dat --learn config=3,3,2,2 epochs=1000 rate=0.1 momentum=0.05

and then you classificated candidates vectors with command:

    FuzzyClassificator --candidates candidates.dat --network network.xml --report report.txt --classify config=3,3,2,2

then you will get the *report.text* file with information that looks like this:

    Neuronet: x:\work\projects\FuzzyClassificator_dohq\network.xml

    FuzzyScale = {Min, Low, Med, High, Max}
        Min = <Hyperbolic(x, {'a': 8, 'c': 0, 'b': 20}), [0.0, 0.23]>
        Low = <Bell(x, {'a': 0.17, 'c': 0.34, 'b': 0.23}), [0.17, 0.4]>
        Med = <Bell(x, {'a': 0.34, 'c': 0.6, 'b': 0.4}), [0.34, 0.66]>
        High = <Bell(x, {'a': 0.6, 'c': 0.77, 'b': 0.66}), [0.6, 0.83]>
        Max = <Parabolic(x, {'a': 0.77, 'b': 0.95}), [0.77, 1.0]>

    Classification results for candidates vectors:

        Header: [input1 input2 input3]	[1st_class_output 2nd_class_output]
        ----------------------------------------------------------------------
        Input: ['0.12', '0.32', 'Min']	Output: ['Min', 'Max']
        Input: ['0.32', '0.35', 'Low']	Output: ['Low', 'High']
        Input: ['0.54', '0.57', 'Med']	Output: ['Max', 'Min']
        Input: ['0.65', '0.68', 'High']	Output: ['Max', 'Min']
        Input: ['0.76', '0.79', 'Max']	Output: ['Max', 'Min']


<a name="Chapter_5"></a>Work with API
-------------------------------------


<a name="Chapter_5_1"></a>**FuzzyClassificator.py**

This is main module which realizes user command-line interaction. Main methods are *LearningMode()* and *ClassifyingMode()* which provide similar program modes. The module provide user interface that implemented in PyBrainLearning.py.

API use Main() function to work with both mode. The learnParameters in Main() used first and classifyParameters used second. If some of them defined they used with high priority than CLI parameters.

Also you can use API Main() function to run Classify mode right after Learning mode.

Learning mode contain steps realized by *LearningMode()*:

1. Creating PyBrain network instance with pre-defined config parameters.
2. Parsing raw data file with ethalons.
3. Preparing PyBrain dataset.
4. Initialize empty PyBrain network for learning or reading network configuration from file.
5. Creating PyBrain trainer.
6. Starts learning and saving network configuration to file.

The *LearningMode()* method takes a dictionary with the values of the initialization parameters for the neural network training.

Classifying mode contains steps realized by *ClassifyingMode()*:

1. Creating PyBrain network instance.
2. Parsing raw data file with candidates.
3. Loading trained network from network configuration file.
4. Activating network for all candidate input vectors.
5. Interpreting results.

The *ClassifyingMode()* method only runs calculations using the trained neural network.

Some examples are below.


<a name="Chapter_5_1_1"></a>***API example to run Learning mode***

When you run Learning mode in CLI, for example:

    FuzzyClassificator --debug-level=info -u 1 --learn config=3,3,2,2 epochs=100 rate=0.5 momentum=0.5 epsilon=0.05 stop=1

also you can run the same Learning mode command using API:

    import FuzzyClassificator as FC
    import FCLogger

    FCLogger.SetLevel("info")
    FC.epochsToUpdate = 1

    parameters = {
        "config": "3,3,2,2",
        "epochs": 100,
        "rate": 0.5,
        "momentum": 0.5,
        "epsilon": 0.05,
        "stop": 1
    }

    FC.Main(learnParameters=parameters)  # Learning mode


<a name="Chapter_5_1_2"></a>***API example to run Classifying mode***

When you run Classifying mode in CLI, for example:

    FuzzyClassificator --candidates candidates.dat --network network.xml --report report.txt --separator=TAB --debug-level=DEBUG --classify config=3,3,2,2

also you can run the same Classifying mode command using API:

    import FuzzyClassificator as FC
    from FCLogger import SetLevel

    FC.candidatesDataFile = "candidates.dat"
    FC.neuroNetworkFile = "network.xml"
    FC.reportDataFile = "report.txt"
    FC.sepSymbol = "TAB"
    SetLevel("DEBUG")

    parameters = {
        "config": "3,3,2,2",
    }

    FC.Main(classifyParameters=parameters)  # Classifying mode


<a name="Chapter_5_1_3"></a>***Another API parameters***

    import FuzzyClassificator as FC  # Import main classificator's module.

    # Start learning or classificating mode with parameters. 
    # If parameters are not defined then CLI-parameters are used.
    FC.Main(learnParameters=None, classifyParameters=None)

    FC.__version__  # Version of current FuzzyClassificator build.

    FC.ethalonsDataFile  # File with ethalon data samples, 'ethalons.dat' by default.

    FC.candidatesDataFile  # File with candidates data samples, 'candidates.dat' by default.

    FC.neuroNetworkFile  # File with Neuro Network configuration, 'network.xml' by default.

    FC.reportDataFile  # Report file with classification analysis, 'report.txt' by default.

    FC.bestNetworkFile  # Where best network saved, 'best_nn.xml' by default.

    FC.bestNetworkInfoFile  # Where information about best network saved, 'best_nn.txt' by default.

    FC.epochsToUpdate  # Epochs between error status updated, 5 by default.

    FC.ignoreColumns  # List of ignored columns. Empty list [] by default, e.g. FC.ignoreColumns = [1, 3].

    FC.ignoreRows  # List of ignored rows. [1] by default, e.g. FC.ignoreRows = [1, 3].

    FC.sepSymbol  # Separator symbol. TAB symbol '\t' used by default.

    FC.reloadNetworkFromFile  # Reload or not Neuro Network from file before usage. False by default.

    FC.noFuzzyOutput  # Show results with fuzzy values too if False (default). Show only real values in report if True.

    FC.showExpected  # Show expected results in Classify mode. WARNING! Use only if your dat-file contains columns with expected results to avoid errors!


<a name="Chapter_5_2"></a>**PyBrainLearning.py**

This is library for work with fuzzy neural networks. You can import and re-use module in your programm if you'd like to realize own work with networks.

All routines to work with fuzzy neural networks realized in *FuzzyNeuroNetwork()* class. It contains next main methods:

    import PyBrainLearning as FL  # Import supporting module.

    FL.ParseRawDataFile()  # Used for parsing file with text raw data.

    FL.PrepareDataSet()  # Used for converting parsed raw-data into PyBrain dataset format.

    FL.CreateNetwork()  # Used for creating PyBrain network.

    FL.CreateTrainer()  # Used for creating PyBrain trainer.

    FL.SaveNetwork()  # Used for saving network in PyBrain xml-format.

    FL.LoadNetwork()  # Used for loading network from PyBrain xml-format file.

    FL.Train()  # Realize network training mechanism.

    FL.CreateReport()  # Create text report after classification vector-candidates.


<a name="Chapter_5_3"></a>**FuzzyRoutines.py**

Library contains some routines for work with fuzzy logic operators, fuzzy datasets and fuzzy scales.

There are some examples of working with fuzzy library after importing it. Just copying at the end of FuzzyRoutines and run it.


<a name="Chapter_5_3_1"></a>***Work with membership functions***

Usage of some membership functions (uncomment one of them):

    #mjuPars = {'a': 7, 'b': 4, 'c': 0}  # hyperbolic params example
    #funct = MFunction(userFunc='hyperbolic', **mjuPars)  # creating instance of hyperbolic function

    #mjuPars = {'a': 0, 'b': 0.3, 'c': 0.4}  # bell params example
    #funct = MFunction(userFunc='bell', **mjuPars)  # creating instance of bell function

    #mjuPars = {'a': 0, 'b': 1}  # parabolic params example
    #funct = MFunction(userFunc='parabolic', **mjuPars)  # creating instance of parabolic function

    #mjuPars = {'a': 0.2, 'b': 0.8, 'c': 0.7}  # triangle params example
    #funct = MFunction(userFunc='triangle', **mjuPars)  # creating instance of triangle function

    mjuPars = {'a': 0.1, 'b': 1, 'c': 0.5, 'd': 0.8}  # trapezium params example
    funct = MFunction(userFunc='trapezium', **mjuPars)  # creating instance of trapezium function

    #mjuPars = {'a': 0.5, 'b': 0.15}  # exponential params example
    #funct = MFunction(userFunc='exponential', **mjuPars)  # creating instance of exponential function

    #mjuPars = {'a': 15, 'b': 0.5}  # sigmoidal params example
    #funct = MFunction(userFunc='sigmoidal', **mjuPars)  # creating instance of sigmoidal function

    #funct = MFunction(userFunc='desirability')  # creating instance of desirability function without parameters

    print('Printing Membership function parameters: ', funct)

Calculating some function's values in [0, 1]:

    xPar = 0
    for i in range(0, 11, 1):
        xPar = (xPar + i) / 10
        res = funct.mju(xPar)  # calculate one value of MF with given parameters
        print('{}({:1.1f}, {}) = {:1.4f}'.format(funct.name, xPar, funct.parameters, res))


<a name="Chapter_5_3_2"></a>***Work with fuzzy set***

    fuzzySet = FuzzySet(funct, (0., 1.))  # creating fuzzy set A = <mju_funct, support_set>
    print('Printing fuzzy set after init before changes:', fuzzySet)
    print('Defuz({}) = {:1.2f}'.format(fuzzySet.name, fuzzySet.Defuz()))

    changedMjuPars = copy.deepcopy(mjuPars)  # change parameters of membership function with deepcopy example:
    changedMjuPars['a'] = 0
    changedMjuPars['b'] = 1
    changedSupportSet = (0.5, 1)  # change support set
    fuzzySet.name = 'Changed fuzzy set'

    fuzzySet.mFunction.parameters = changedMjuPars
    fuzzySet.supportSet = changedSupportSet

    print('New membership function parameters: ', fuzzySet.mFunction.parameters)
    print('New support set: ', fuzzySet.supportSet)
    print('New value of Defuz({}) = {:1.2f}'.format(fuzzySet.name, fuzzySet.Defuz()))
    print('Printing fuzzy set after changes:', fuzzySet)


<a name="Chapter_5_3_3"></a>***Work with fuzzy scales***

Fuzzy scale is an ordered set of linguistic variables that looks like this:

S = [{'name': 'name_1', 'fSet': fuzzySet_1}, {'name': 'name_2', 'fSet': fuzzySet_2}, ...]

where name is a linguistic name of fuzzy set, fSet is a user define fuzzy set of FuzzySet type.

    scale = FuzzyScale()  # intialize new fuzzy scale with default levels
    print('Printing default fuzzy scale in human-readable:', scale)

    print('Defuz() of all default levels:')
    for item in scale.levels:
        print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

Add new fuzzy levels:

    print('Define some new levels:')

    minFunct = MFunction('hyperbolic', **{'a': 2, 'b': 20, 'c': 0})
    levelMin = FuzzySet(membershipFunction=minFunct, supportSet=(0., 0.5), linguisticName='min')
    print('Printing Level 1 in human-readable:', levelMin)

    medFunct = MFunction('bell', **{'a': 0.4, 'b': 0.55, 'c': 0.7})
    levelMed = FuzzySet(membershipFunction=medFunct, supportSet=(0.25, 0.75), linguisticName='med')
    print('Printing Level 2 in human-readable:', levelMed)

    maxFunct = MFunction('triangle', **{'a': 0.65, 'b': 1, 'c': 1})
    levelMax = FuzzySet(membershipFunction=maxFunct, supportSet=(0.7, 1.), linguisticName='max')
    print('Printing Level 3 in human-readable:', levelMax)

Change scale levels:

    scale.name = 'New Scale'
    scale.levels = [{'name': levelMin.name, 'fSet': levelMin},
                    {'name': levelMed.name, 'fSet': levelMed},
                    {'name': levelMax.name, 'fSet': levelMax}]  # add new ordered set of linguistic variables into scale

    print('Changed List of levels as objects:', scale.levels)
    print('Printing changed fuzzy scale in human-readable:', scale)

    print('Defuz() of all New Scale levels:')
    for item in scale.levels:
        print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))


<a name="Chapter_5_3_4"></a>***Work with Universal Fuzzy Scale***

Universal fuzzy scales S_f = {Min, Low, Med, High, Max} pre-defined in UniversalFuzzyScale() class.

    uniFScale = UniversalFuzzyScale()
    print('Levels of Universal Fuzzy Scale:', uniFScale.levels)
    print('Printing scale:', uniFScale)

    print('Defuz() of all Universal Fuzzy Scale levels:')
    for item in uniFScale.levels:
        print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

Use Fuzzy() function to looking for level on Fuzzy Scale:

    xPar = 0
    for i in range(0, 10, 1):
        xPar = (xPar + i) / 10
        res = uniFScale.Fuzzy(xPar)  # calculate fuzzy level for some real values
        print('Fuzzy({:1.1f}, {}) = {}, {}'.format(xPar, uniFScale.name, res['name'], res['fSet']))

Finding fuzzy level using GetLevelByName() function with exact matching:

    print('Finding level by name with exact matching:')

    res = uniFScale.GetLevelByName('Min')
    print('GetLevelByName(Min, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('High')
    print('GetLevelByName(High, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('max')
    print('GetLevelByName(max, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

Finding fuzzy level using GetLevelByName() function without exact matching:

    print('Finding level by name without exact matching:')

    res = uniFScale.GetLevelByName('mIn', exactMatching=False)
    print("GetLevelByName('mIn', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('max', exactMatching=False)
    print("GetLevelByName('max', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('Hig', exactMatching=False)
    print("GetLevelByName('Hig', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('LOw', exactMatching=False)
    print("GetLevelByName('LOw', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('eD', exactMatching=False)
    print("GetLevelByName('eD', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('Highest', exactMatching=False)
    print("GetLevelByName('Highest', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))


<a name="Chapter_5_3_5"></a>***Work with fuzzy logic operators***

Checks that number is in [0, 1]:

    print('IsCorrectFuzzyNumberValue(0.5) =', IsCorrectFuzzyNumberValue(0.5))
    print('IsCorrectFuzzyNumberValue(1.1) =', IsCorrectFuzzyNumberValue(1.1))

Calculates result of fuzzy NOT, fuzzy NOT with alpha parameter and parabolic fuzzy NOT operations:

    print('FNOT(0.25) =', FuzzyNOT(0.25))
    print('FNOT(0.25, alpha=0.25) =', FuzzyNOT(0.25, alpha=0.25))
    print('FNOT(0.25, alpha=0.75) =', FuzzyNOT(0.25, alpha=0.75))
    print('FNOT(0.25, alpha=1) =', FuzzyNOT(0.25, alpha=1))

    print('FNOTParabolic(0.25, alpha=0.25) =', FuzzyNOTParabolic(0.25, alpha=0.25))
    print('FNOTParabolic(0.25, alpha=0.75) =', FuzzyNOTParabolic(0.25, alpha=0.75))

Calculates result of fuzzy AND/OR operations:

    print('FuzzyAND(0.25, 0.5) =', FuzzyAND(0.25, 0.5))
    print('FuzzyOR(0.25, 0.5) =', FuzzyOR(0.25, 0.5))

Calculates result of T-Norm operations, where T-Norm is one of conjunctive operators - logic, algebraic, boundary, drastic:

    print("TNorm(0.25, 0.5, 'logic') =", TNorm(0.25, 0.5, normType='logic'))
    print("TNorm(0.25, 0.5, 'algebraic') =", TNorm(0.25, 0.5, normType='algebraic'))
    print("TNorm(0.25, 0.5, 'boundary') =", TNorm(0.25, 0.5, normType='boundary'))
    print("TNorm(0.25, 0.5, 'drastic') =", TNorm(0.25, 0.5, normType='drastic'))

Calculates result of S-coNorm operations, where S-coNorm is one of disjunctive operators - logic, algebraic, boundary, drastic:

    print("SCoNorm(0.25, 0.5, 'logic') =", SCoNorm(0.25, 0.5, normType='logic'))
    print("SCoNorm(0.25, 0.5, 'algebraic') =", SCoNorm(0.25, 0.5, normType='algebraic'))
    print("SCoNorm(0.25, 0.5, 'boundary') =", SCoNorm(0.25, 0.5, normType='boundary'))
    print("SCoNorm(0.25, 0.5, 'drastic') =", SCoNorm(0.25, 0.5, normType='drastic'))

Calculates result of T-Norm operations for N numbers, N > 2:

    print("TNormCompose(0.25, 0.5, 0.75, 'logic') =", TNormCompose(0.25, 0.5, 0.75, normType='logic'))
    print("TNormCompose(0.25, 0.5, 0.75, 'algebraic') =", TNormCompose(0.25, 0.5, 0.75, normType='algebraic'))
    print("TNormCompose(0.25, 0.5, 0.75, 'boundary') =", TNormCompose(0.25, 0.5, 0.75, normType='boundary'))
    print("TNormCompose(0.25, 0.5, 0.75, 'drastic') =", TNormCompose(0.25, 0.5, 0.75, normType='drastic'))

Calculates result of S-coNorm operations for N numbers, N > 2:

    print("SCoNormCompose(0.25, 0.5, 0.75, 'logic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='logic'))
    print("SCoNormCompose(0.25, 0.5, 0.75, 'algebraic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='algebraic'))
    print("SCoNormCompose(0.25, 0.5, 0.75, 'boundary') =", SCoNormCompose(0.25, 0.5, 0.75, normType='boundary'))
    print("SCoNormCompose(0.25, 0.5, 0.75, 'drastic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='drastic'))


<a name="Chapter_5_3_6"></a>***Output examples***

If you run code above - you'll see next console output:

    Printing Membership function with parameters:  Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8})
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0000
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0000
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.2750
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.5525
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.8302
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 1.0000
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 1.0000
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 1.0000
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.6173
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0617
    Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0000

    Printing fuzzy set after init and before changes: FuzzySet = <Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}), [0.0, 1.0]>
    Defuz(FuzzySet) = 0.59

    New membership function with parameters:  Trapezium(x, {"a": 0, "b": 1, "c": 0.5, "d": 0.8})
    New support set:  (0.5, 1)
    New value of Defuz(Changed fuzzy set) = 0.70

    Printing fuzzy set after changes: Changed fuzzy set = <Trapezium(x, {"a": 0, "b": 1, "c": 0.5, "d": 0.8}), [0.5, 1]>
    Printing default fuzzy scale in human-readable: DefaultScale = {Min, Med, High}
        Minimum = <Hyperbolic(x, {"a": 7, "b": 4, "c": 0}), [0.0, 1.0]>
        Medium = <Bell(x, {"a": 0.35, "b": 0.5, "c": 0.6}), [0.0, 1.0]>
        High = <Triangle(x, {"a": 0.7, "b": 1, "c": 1}), [0.0, 1.0]>

    Defuz() of all default levels:
    Defuz(Min) = 0.10
    Defuz(Med) = 0.55
    Defuz(High) = 0.90

    Define some new levels:
    Printing Level 1 in human-readable: min = <Hyperbolic(x, {"a": 2, "b": 20, "c": 0}), [0.0, 0.5]>
    Printing Level 2 in human-readable: med = <Bell(x, {"a": 0.4, "b": 0.55, "c": 0.7}), [0.25, 0.75]>
    Printing Level 3 in human-readable: max = <Triangle(x, {"a": 0.65, "b": 1, "c": 1}), [0.7, 1.0]>

    Changed List of levels as objects: [{'name': 'min', 'fSet': <__main__.FuzzySet object at 0x00000000027B1208>}, {'name': 'med', 'fSet': <__main__.FuzzySet object at 0x00000000027B1278>}, {'name': 'max', 'fSet': <__main__.FuzzySet object at 0x00000000027B1320>}]

    Printing changed fuzzy scale in human-readable: New Scale = {min, med, max}
        min = <Hyperbolic(x, {"a": 2, "b": 20, "c": 0}), [0.0, 0.5]>
        med = <Bell(x, {"a": 0.4, "b": 0.55, "c": 0.7}), [0.25, 0.75]>
        max = <Triangle(x, {"a": 0.65, "b": 1, "c": 1}), [0.7, 1.0]>

    Defuz() of all New Scale levels:
    Defuz(min) = 0.24
    Defuz(med) = 0.61
    Defuz(max) = 0.89

    Levels of Universal Fuzzy Scale: [{'name': 'Min', 'fSet': <__main__.FuzzySet object at 0x00000000027B14A8>}, {'name': 'Low', 'fSet': <__main__.FuzzySet object at 0x00000000027B1518>}, {'name': 'Med', 'fSet': <__main__.FuzzySet object at 0x00000000027B1588>}, {'name': 'High', 'fSet': <__main__.FuzzySet object at 0x00000000027B15F8>}, {'name': 'Max', 'fSet': <__main__.FuzzySet object at 0x00000000027B1668>}]
    Printing scale: FuzzyScale = {Min, Low, Med, High, Max}
        Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
        Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
        Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
        High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
        Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>

    Defuz() of all Universal Fuzzy Scale levels:
    Defuz(Min) = 0.06
    Defuz(Low) = 0.29
    Defuz(Med) = 0.50
    Defuz(High) = 0.71
    Defuz(Max) = 0.93

    Fuzzy(0.0, FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    Fuzzy(0.1, FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    Fuzzy(0.2, FuzzyScale) = Low, Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
    Fuzzy(0.3, FuzzyScale) = Low, Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
    Fuzzy(0.4, FuzzyScale) = Med, Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
    Fuzzy(0.5, FuzzyScale) = Med, Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
    Fuzzy(0.7, FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    Fuzzy(0.8, FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    Fuzzy(0.9, FuzzyScale) = Max, Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>
    Fuzzy(1.0, FuzzyScale) = Max, Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>

    Finding level by name with exact matching:
    GetLevelByName(Min, FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    GetLevelByName(High, FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    GetLevelByName(max, FuzzyScale) = None, None

    Finding level by name without exact matching:
    GetLevelByName('mIn', FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    GetLevelByName('max', FuzzyScale) = Max, Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>
    GetLevelByName('Hig', FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    GetLevelByName('LOw', FuzzyScale) = Low, Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
    GetLevelByName('eD', FuzzyScale) = Med, Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
    GetLevelByName('Highest', FuzzyScale) = None, None

    IsCorrectFuzzyNumberValue(0.5) = True
    IsCorrectFuzzyNumberValue(1.1) = False

    FNOT(0.25) = 0.75
    FNOT(0.25, alpha=0.25) = 0.25

    FNOT(0.25, alpha=0.75) = 0.9166666666666666
    FNOT(0.25, alpha=1) = 1.0

    FNOTParabolic(0.25, alpha=0.25) = 0.25000000000000017
    FNOTParabolic(0.25, alpha=0.75) = 0.9820000000000008

    FuzzyAND(0.25, 0.5) = 0.25
    FuzzyOR(0.25, 0.5) = 0.5

    TNorm(0.25, 0.5, 'logic') = 0.25
    TNorm(0.25, 0.5, 'algebraic') = 0.125
    TNorm(0.25, 0.5, 'boundary') = 1
    TNorm(0.25, 0.5, 'drastic') = 0

    SCoNorm(0.25, 0.5, 'logic') = 0.5
    SCoNorm(0.25, 0.5, 'algebraic') = 0.625
    SCoNorm(0.25, 0.5, 'boundary') = 0.75
    SCoNorm(0.25, 0.5, 'drastic') = 1

    TNormCompose(0.25, 0.5, 0.75, 'logic') = 0.25
    TNormCompose(0.25, 0.5, 0.75, 'algebraic') = 0.09375
    TNormCompose(0.25, 0.5, 0.75, 'boundary') = 0.75
    TNormCompose(0.25, 0.5, 0.75, 'drastic') = 0

    SCoNormCompose(0.25, 0.5, 0.75, 'logic') = 0.75
    SCoNormCompose(0.25, 0.5, 0.75, 'algebraic') = 0.90625
    SCoNormCompose(0.25, 0.5, 0.75, 'boundary') = 0
    SCoNormCompose(0.25, 0.5, 0.75, 'drastic') = 1
