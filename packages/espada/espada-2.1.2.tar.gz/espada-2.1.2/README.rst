Espada
======
Command line tool to generate a Cmake based C++ project.

Installation
------------

First off you need to have a C++ Compiler such as CLang installed.  As well as having CMake and Python installed on
your machine. There are several ways you can install espada.

Get Started
^^^^^^^^^^^

..code::
    pip install espada

This will install espada plus all the dependencies.

Usage
-----

..code::
    erebus project NumberGuess
    cd NumberGuess
    erebus class -c guess --test
    mkdir build
    cd build
    cmake ..
    make


Development setup
-----------------
1. Install python
2. Install pip
3. Install VirtualEnv
4. Go to the Directory you cloned the repo and run ::
    virtualenv .env

..code::
    .env\Scripts\activate
    pip install -r requirements.txt
    pip install --editable .

