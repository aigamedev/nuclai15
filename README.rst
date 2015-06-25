nucl.ai Workshops 2015
======================

Installation & Dependencies
---------------------------

1. Download and Install Anaconda Python distribution (preferable is Python 3.4)
    http://continuum.io/downloads
2. Install MingGW and libpython
    conda install mingw libpython
3. Install scikit-neuralnetwork
    pip install scikit-neuralnetwork
4. Make sure **sknn** package is on your PYTHONPATH
    set PYTHONPATH=%PYTHONPATH%;<Anacoda installation folder>\\Lib\\site-packages\\sknn (for Windows)
    export PYTHONPATH=$PYTHONPATH:<Anacoda installation folder>\\Lib\\site-packages\\sknn (for Linux and OSX)



This repository contains the source code and data to participate in the workshops at the nucl.ai Conference 2015.  Programs should work on Windows, Linux and Mac OSX with either Python 2.7 or Python 3.4.

You'll find multiple folders here:

  1. **vision —** Object detection and recognition using neural networks.
  2. **dota2 —** Preference learning from large quantities of replay data.
  
See each sub-folder for further details and instructions.
