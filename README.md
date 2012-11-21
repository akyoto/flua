Flua
====================

General info
---------------------

Flua is a general purpose programming language (or environment, if you like).
Its main features are:

 * Data flow programming
 * Mutable and immutable data structures depending on what you currently need
 * Multiple syntax support
 * Language can be extended via patterns
 * Automatic Parallelization based on Whitelists
 * Code is saved in XML files which hold all the data about them (documentation, etc.)

It is currently in the Alpha phase.

 * Website: http://flua-lang.org/
 * More info: https://github.com/blitzprog/flua/wiki/Flua-design-document

Installation on Debian
---------------------
If you use Debian or Ubuntu just execute this:

    sudo apt-get install python3 python3-pyqt4 git g++ build-essential xorg-dev libx11-dev libxt-dev libxext-dev libgl1-mesa-dev libglu1-mesa-dev libxrandr-dev libfreeimage3 libfreeimage-dev freeglut3 freeglut3-dev
    git clone git://github.com/blitzprog/flua.git
    python3 ./flua/flua-studio.py

This works on Ubuntu 12.04 and higher. On Ubuntu 11.xx or non-debian based systems you need to compile these dependencies manually or install the equivalent packages.

Installation on Windows
---------------------
Just download and extract this archive:
https://github.com/downloads/blitzprog/flua/Flua-x86.7z

Compiling dependencies manually
---------------------

If you are using Ubuntu 11.xx or a non-debian based system, this section is for you.
Install git, g++, Python 3 and these development packages via your package manager (Ubuntu 11.xx is used as an example):

    sudo apt-get install python3 git g++ build-essential python3-dev libqt4-dev

Afterwards:

 * Download SIP source: http://www.riverbankcomputing.co.uk/software/sip/download
 * Compile SIP for Python 3.x
 * Download PyQt 4 source: http://www.riverbankcomputing.co.uk/software/pyqt/download
 * Compile PyQt 4 for Python 3.x
 
Compiling these libraries can be done via:

    python3 configure.py
    make
    sudo make install

Download Flua via git (unless you already downloaded it):

    git clone git://github.com/blitzprog/flua.git
    
Start flua-studio.py which is in the top-level flua directory:
    
    python3 ./flua/flua-studio.py
    
On 64-Bit systems you might need to install libc-i386-dev as well.
If you want to compile the graphics examples you'll need X11 and OpenGL
development packages (libx11-dev libxt-dev libxext-dev libgl1-mesa-dev libglu1-mesa-dev).
