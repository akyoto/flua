bp
====================

General info
---------------------

blitzprog (short: bp) is a general purpose programming language (or environment, if you like).
Its main features are:

 * Data flow programming
 * Mutable AND immutable data structures depending on what you currently need
 * Automatic Parallelization
 * Syntax independent
 * Language can be extended via patterns
 * Code is saved in XML files which hold all the data about them (documentation, etc.)

It is currently in the development phase and not stable.

Website: http://blitzprog.org/

Installation
---------------------
bp is based on Python 3 so you only need to install the Python 3 interpreter and the dependencies.

Installation on Linux distributions:

On debian based systems (Ubuntu, Linux Mint, etc.) install the dependencies using the packet manager (Python 3, PyQt 4, Git, g++):

    sudo apt-get install python3 python3-pyqt4 git g++

This works on Ubuntu 12.04 and higher. On Ubuntu 11.xx or non-debian based systems you need to compile these dependencies manually or install the equivalent packages. If you're using a non-debian based system I'm sure you know what you are doing.

Afterwards download bp via git:

    git clone git://github.com/blitzprog/bp.git

And start it:

    ./bp-editor.py
    
The Linux version of bp (both the IDE and the standalone compiler) is slightly faster than the Windows one.

Compiling dependencies manually:

If you are using Ubuntu 12.04 you don't need to do this. If you are using Ubuntu 11.xx or a non-debian based system, this section is for you.
Install git, g++, Python 3 and these development packages via your package manager (Ubuntu 11.xx is used as an example):

    sudo apt-get install python3 git g++ build-essential python3-dev libqt4-dev
    

Afterwards:

 * Download SIP source: http://www.riverbankcomputing.co.uk/software/sip/download
 * Compile SIP for Python 3.x
 * Download PyQt 4 source: href="http://www.riverbankcomputing.co.uk/software/pyqt/download
 * Compile PyQt 4 for Python 3.x
 
Compiling these libraries can be done via:

    python3 configure.py
    make
    sudo checkinstall

If checkinstall doesn't work try

    sudo make install

Download bp via git (unless you already downloaded it):

    git clone git://github.com/blitzprog/bp.git
    
Start bp-editor.py which is in the top-level bp directory:
    
    ./bp-editor.py
    
On 64-Bit systems you might need to install libc-i386-dev as well.
