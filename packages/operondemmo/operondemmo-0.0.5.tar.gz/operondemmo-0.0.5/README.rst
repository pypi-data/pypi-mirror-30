operondemmo: an independent demo of KNOWN operon predict method
==============================================================================
|PyPI version| |Docs| |License|

.. contents:: :local:

Library
--------------------------------------------------------------------------------
- Python3.6
- Numpy
- Pandas
- Linux(Fedora)

Install
--------------------------------------------------------------------------------

PyPI
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pip3 install operondemmo --user


or `download operondemmo <https://pypi.python.org/pypi/operondemmo/>`_ and install:

.. code-block:: console

    $ pip3 install operondemmo-*.tar.gz --user


To upgrade to latest version:

.. code-block:: console

    $ pip3 install --upgrade operondemmo --user


GitHub
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ git clone https://github.com/GodInLove/operondemmo.git
    $ cd operondemmo
    $ python3 setup.py install


or `download <https://github.com/GodInLove/operondemmo/releases/>`_ and install:

.. code-block:: console

    $ pip install operondemmo-*.tar.gz


Usage
--------------------------------------------------------------------------------

Quick start
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ git clone https://github.com/GodInLove/operondemmo.git
    $ cd operondemmo/test/count && tar -zxf count.tar.gz
    $ rm -f count.tar.gz
    $ cd ..
    $ operondemmo -i count -g gff/eco.gff


Outputs: ``test/OUT/operon.txt``

Basic Parameters
^^^^^^^^^^^^^^^^^^^^
-h
    **PRINT_HELP**
    (show this help message and exit)
-i
    **INPUT_FILES**
    (A directory to store a group of result files through [samtools depth XXX > xxx.txt] command)
-o
    **OUTPUT_PATH**
    (A directory include output data(operon file).)
-g
    **GFF_FILE**
    (The gff file of the prokaryote)
-t
    **THRESHOLD**
    (the threshold in (-1,1))

Advanced Parameters
^^^^^^^^^^^^^^^^^^^^
--person
   Build co-expression matrix with person correlation
--spearman
   Build co-expression matrix with spearman correlation



*cite:*
 1. Junier I, Unal E B, Yus E, et al. Insights into the mechanisms of basal coordination of transcription using a genome-reduced bacterium[J]. Cell systems, 2016, 2(6): 391-401.


.. |PyPI version| image:: https://img.shields.io/pypi/v/operondemmo.svg?style=flat-square
   :target: https://pypi.python.org/pypi/operondemmo
.. |Docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square
   :target: https://github.com/GodInLove/operondemmo
.. |License| image:: https://img.shields.io/aur/license/yaourt.svg?maxAge=2592000
   :target: https://github.com/GodInLove/operondemmo/blob/master/LICENSE.txt