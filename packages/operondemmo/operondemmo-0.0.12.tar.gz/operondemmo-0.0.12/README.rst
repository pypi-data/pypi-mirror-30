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

   $ operondemmo -i input_dir -f fna_file_path -g gff_file_path



Outputs: ``test/OUT/operon.txt``

Or:

.. code-block:: console

   $ operondemmo -i input_dir -f fna_file_path -g gff_file_path -o out_dir -t threshold


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
    The gff file of the prokaryote.
-t
    **THRESHOLD:**
    the threshold in (-1,1).
-f
    **FNA_FILE:**
    The fna file of the prokaryote genome.
-p
    **PROCESS_NUM**
    Specify the number of processing threads.


**INPUT_DIR:**


.. code-block:: console

   example_input/
      c1/
         SRR6322033_1.fastq.gz
         SRR6322033_2.fastq.gz
      c2/
         SRR6322035_1.fastq.gz
         SRR6322035_2.fastq.gz
      c3/
         SRR6322037_1.fastq.gz
         SRR6322037_2.fastq.gz
      ...


Advanced Parameters
^^^^^^^^^^^^^^^^^^^^
--person
   Build co-expression matrix with person correlation
--spearman
   Build co-expression matrix with spearman correlation


*cite:*
 1. Junier I, Unal E B, Yus E, et al. Insights into the mechanisms of basal coordination of transcription using a genome-reduced bacterium[J]. Cell systems, 2016, 2(6): 391-401.
 2. Bray N L, Pimentel H, Melsted P, et al. Near-optimal probabilistic RNA-seq quantification[J]. Nature biotechnology, 2016, 34(5): 525.

.. |PyPI version| image:: https://img.shields.io/pypi/v/operondemmo.svg?style=flat-square
   :target: https://pypi.python.org/pypi/operondemmo
.. |Docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square
   :target: http://lyd.ourblogs.me/operondemmo/
.. |License| image:: https://img.shields.io/aur/license/yaourt.svg?maxAge=2592000
   :target: https://github.com/GodInLove/operondemmo/blob/master/LICENSE.txt