operondemmo: an independent demo of KNOWN operon predict method
==============================================================================
|PyPI version| |Docs| |License|

.. contents:: :local:

Dependencies
--------------------------------------------------------------------------------
- `Python3.6 <https://www.python.org/>`_
- `Numpy <http://www.numpy.org>`_
- `Pandas <https://pandas.pydata.org/>`_
- Linux(Fedora)
- `Kallisto <https://pachterlab.github.io/kallisto/>`_

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

    $ wget https://github.com/GodInLove/operondemmo/archive/master.zip
    $ unzip operondemmo-master.zip
    $ cd operondemmo-master
    $ python3 setup.py install


or `download <https://github.com/GodInLove/operondemmo/releases/>`_ and install:

.. code-block:: console

    $ pip install operondemmo-*.tar.gz


Usage
--------------------------------------------------------------------------------

Quick start
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

   $ mkdir test
   $ wget http://lyd.ourblogs.me/operondemmo/test/count.tar.gz
   $ wget http://lyd.ourblogs.me/operondemmo/test/gff/eco.gff
   $ cd tar -zxf count.tar.gz
   $ rm -f count.tar.gz
   $ operondemmo -i count -g eco.gff


Outputs: ``test/OUT/operon.txt``

Basic Parameters
^^^^^^^^^^^^^^^^^^^^
-h
    **PRINT_HELP:**
    show this help message and exit
-i
    **INPUT_DIR:**
    A directory to store a group of files.
-o
    **OUTPUT_DIR:**
    A directory include output data(operon file).
-g
    **GFF_FILE:**
    The gff file of the prokaryote
-t
    **THRESHOLD**
    the threshold in (-1,1)


**INPUT_DIR:**

default: [samtools depth] result files
.. code-block::
   example_count/
      SRR6322033_count.txt
      SRR6322035_count.txt
      SRR6322037_count.txt
      ...


or when ``--kallisto``
.. code-block::
   example_input/
      eco.fna
      SRR6322033_1.fastq.gz
      SRR6322033_2.fastq.gz
      SRR6322035_1.fastq.gz
      SRR6322035_2.fastq.gz
      SRR6322037_1.fastq.gz
      SRR6322037_2.fastq.gz
      ...


Advanced Parameters
^^^^^^^^^^^^^^^^^^^^
--person
   Build co-expression matrix with person correlation
--spearman
   Build co-expression matrix with spearman correlation
--kallisto
   Build expression matrix with kallisto result


*cite:*
 1. Junier I, Unal E B, Yus E, et al. Insights into the mechanisms of basal coordination of transcription using a genome-reduced bacterium[J]. Cell systems, 2016, 2(6): 391-401.


.. |PyPI version| image:: https://img.shields.io/pypi/v/operondemmo.svg?style=flat-square
   :target: https://pypi.python.org/pypi/operondemmo
.. |Docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square
   :target: https://github.com/GodInLove/operondemmo
.. |License| image:: https://img.shields.io/aur/license/yaourt.svg?maxAge=2592000
   :target: https://github.com/GodInLove/operondemmo/blob/master/LICENSE.txt