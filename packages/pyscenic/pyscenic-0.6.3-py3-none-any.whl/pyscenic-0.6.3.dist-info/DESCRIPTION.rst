========
pySCENIC
========

.. image:: https://travis-ci.org/aertslab/pySCENIC.svg?branch=master
  :target: https://travis-ci.org/aertslab/pySCENIC

.. image:: https://badge.fury.io/py/pyscenic.svg
  :target: https://badge.fury.io/py/pyscenic

pySCENIC is a lightning-fast python implementation of the SCENIC pipeline (Single-CEll regulatory Network Inference and
Clustering) which enables biologists to infer transcription factors, Gene Regulatory Networks and cell types from 
single-cell RNA-seq data.
pySCENIC can be run on a single desktop machine but easily scales to multi-core clusters to analyze thousands of cells
in no time.

Features
--------

All the functionality of the original R implementation is available and in addition:

1. You can leverage multi-core and multi-node clusters.
2. We implemented a version of the recovery of input genes that takes into account weights associated with these genes.
3. Regulomes with targets that are repressed are now also derived and used for cell enrichment analysis.

Installation
------------

The package itself can be installed via :code:`pip install pyscenic`.

You can also install this package directly from the source:

.. code-block:: bash

    git clone https://github.com/aertslab/pySCENIC.git
    cd pySCENIC/
    pip install .

To successfully use this pipeline you also need auxilliary datasets:

1. Databases ranking the whole genome of your species of interest based on regulatory features (i.e. transcription factors). Ranking databases are typically stored in the `feather format <https://github.com/wesm/feather>`_.
2. Motif annotation database providing the missing link between an enriched motif and the transcription factor that binds this motif. This pipeline needs a TSV text file where every line represents a particular annotation.

To acquire these datasets please contact `LCB <https://aertslab.org>`_.

Tutorial
--------

For this tutorial 3005 single cell transcriptomes taken from the mouse brain (somatosensory cortex and 
hippocampal regions) are used as an example (cf. references).

.. code-block:: python

    import os
    import pandas as pd
    import numpy as np

    from arboretum.utils import load_tf_names
    from arboretum.algo import grnboost2

    from pyscenic.rnkdb import FeatherRankingDatabase as RankingDatabase
    from pyscenic.utils import modules_from_adjacencies, save_to_yaml
    from pyscenic.prune import prune, prune2df
    from pyscenic.aucell import aucell

    import seaborn as sns

    DATA_FOLDER="~/tmp"
    RESOURCES_FOLDER="~/resources"
    DATABASE_FOLDER = "~/databases/"
    FEATHER_GLOB = os.path.join(DATABASE_FOLDER, "mm9-*.feather")
    MOTIF_ANNOTATIONS_FNAME = os.path.join(RESOURCES_FOLDER, "motifs-v9-nr.mgi-m0.001-o0.0.tbl")
    MM_TFS_FNAME = os.path.join(RESOURCES_FOLDER, 'mm_tfs.txt')
    SC_EXP_FNAME = os.path.join(RESOURCES_FOLDER, "GSE60361_C1-3005-Expression.txt")
    REGULOMES_FNAME = os.path.join(DATA_FOLDER, "regulomes.yaml")
    NOMENCLATURE = "MGI"


Preliminary work
~~~~~~~~~~~~~~~~

The scRNA-Seq data is downloaded from GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE60361 and loaded into memory

.. code-block:: python

    ex_matrix = pd.read_csv(SC_EXP_FNAME, sep='\t', header=0, index_col=0)

and duplicate genes are removed.

.. code-block:: python

    ex_matrix = ex_matrix[~ex_matrix.index.duplicated(keep='first')]
    ex_matrix.shape

.. code-block:: bash

    (19970, 3005)

Load list of Transcription Factors (TF) for *Mus musculus*. The list of known TFs for Mm was prepared from TFCat (cf. notebooks section).

.. code-block:: python

    tf_names = load_tf_names(MM_TFS_FNAME)


Load the ranking databases:

.. code-block:: python

    db_fnames = glob.glob(FEATHER_GLOB)
    def name(fname):
        return os.path.basename(fname).split(".")[0]
    dbs = [RankingDatabase(fname=fname, name=name(fname), nomenclature="MGI") for fname in db_fnames]
    dbs

.. code-block:: bash

        [FeatherRankingDatabase(name="mm9-tss-centered-10kb-10species",nomenclature=MGI),
         FeatherRankingDatabase(name="mm9-500bp-upstream-7species",nomenclature=MGI),
         FeatherRankingDatabase(name="mm9-500bp-upstream-10species",nomenclature=MGI),
         FeatherRankingDatabase(name="mm9-tss-centered-5kb-10species",nomenclature=MGI),
         FeatherRankingDatabase(name="mm9-tss-centered-10kb-7species",nomenclature=MGI),
         FeatherRankingDatabase(name="mm9-tss-centered-5kb-7species",nomenclature=MGI)]

Phase I: Inference of co-expression modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the initial phase of the pySCENIC pipeline the single cell expression profiles are used to infer 
co-expression modules from.

Run GENIE3 or GRNBoost from `arboretum <https://github.com/tmoerman/arboretum>`_ to infer co-expression modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The arboretum package is used for this phase of the pipeline. For this notebook only a sample of 1,000 cells is used
for the co-expression module inference is used.

.. code-block:: python

    N_SAMPLES = ex_matrix.shape[1] # Full dataset
    adjancencies = grnboost2(expression_data=ex_matrix.T.sample(n=N_SAMPLES, replace=False),
                        tf_names=tf_names, verbose=True)

Derive potential regulomes from these co-expression modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Regulomes are derived from adjacencies based on three methods:

The first method to create the TF-modules is to select the best targets for each transcription factor:

1. Targets with weight > 0.001
2. Targets with weight > 0.005

The second method is to select the top targets for a given TF:

1. Top 50 targets (targets with highest weight)

The alternative way to create the TF-modules is to select the best regulators for each gene (this is actually how GENIE3 internally works). Then, these targets can be assigned back to each TF to form the TF-modules. In this way we will create three more gene-sets:

1. Targets for which the TF is within its top 5 regulators
2. Targets for which the TF is within its top 10 regulators
3. Targets for which the TF is within its top 50 regulators

A distinction is made between modules which contain targets that are being activated and genes that are being repressed. Relationship between TF and its target, i.e. activator or repressor, is derived using the original expression profiles. The Pearson product-moment correlation coefficient is used to derive this information.

In addition, the transcription factor is added to the module and modules that have less than 20 genes are removed.

.. code-block:: python

    modules = list(modules_from_adjacencies(adjacencies, ex_matrix, nomenclature=NOMENCLATURE))


Phase II: Prune modules for targets with cis regulatory footprints (aka RcisTarget)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    df = prune2df(dbs, modules, MOTIF_ANNOTATIONS_FNAME)
    regulomes = df2regulomes(df, NOMENCLATURE)

Directly calculating regulomes without the intermediate dataframe of enriched features is also possible:

.. code-block:: python

    regulomes = prune(dbs, modules, MOTIF_ANNOTATIONS_FNAME)
    save_to_yaml(regulomes, REGULOMES_FNAME)

Multi-core systems and clusters can leveraged in the following way:

.. code-block:: python

    # The fastest multi-core implementation:
    df = prune2df(dbs, modules, MOTIF_ANNOTATIONS_FNAME,
                        client_or_address="custom_multiprocessing", num_workers=8)
    # or alternatively:
    regulomes = prune(dbs, modules, MOTIF_ANNOTATIONS_FNAME,
                        client_or_address="custom_multiprocessing", num_workers=8)

    # The clusters can be leveraged via the dask framework:
    df = prune2df(dbs, modules, MOTIF_ANNOTATIONS_FNAME, client_or_address="local")
    # or alternatively:
    regulomes = prune(dbs, modules, MOTIF_ANNOTATIONS_FNAME, client_or_address="local")

Phase III: Cellular regulome enrichment matrix (aka AUCell)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Characterize the different cells in a single-cell transcriptomics experiment by the enrichment of the previously discovered
regulomes. Enrichment of a regulome is measures as AUC of the recovery curve of the genes that define this regulome.

.. code-block:: python

    auc_mtx = aucell(ex_matrix.T, regulomes, num_workers=4)
    sns.clustermap(auc_mtx, figsize=(8,8))

Command Line Interface
----------------------

A command line version of the tool is included. This tool is available after proper installation of the package via ::code`pip`.

.. code-block::

    { ~ }  » pyscenic                                            ~
    usage: SCENIC - Single-CEll regulatory Network Inference and Clustering
               [-h] [-o OUTPUT] {grn,motifs,prune,aucell} ...

    positional arguments:
      {grn,motifs,prune,aucell}
                            sub-command help
        grn                 Derive co-expression modules from expression matrix.
        motifs              Find enriched motifs for gene signatures.
        prune               Prune targets from a co-expression module based on
                            cis-regulatory cues.
        aucell              b help

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Output file/stream.


Website
-------

For more information, please visit http://scenic.aertslab.org .

License
-------

GNU General Public License v3

References
----------

- The original method was published in Nature Methods: ``S. Aibar, C. B. González-Blas, T. Moerman, V. A. Huynh-Thu, H. Imrichová, G. Hulselmans, F. Rambow, J.-C. Marine, P. Geurts, J. Aerts, J. van den Oord, Z. K. Atak, J. Wouters, and S. Aerts, “SCENIC: single-cell regulatory network inference and clustering.,” Nat Meth, vol. 14, no. 11, pp. 1083–1086, Nov. 2017.``
- The tutorial is based on the paper: ``A. Zeisel, A. B. M͡oz-Manchado, S. Codeluppi, P. Lönnerberg, G. L. Manno, A. Juréus, S. Marques, H. Munguba, L. He, C. Betsholtz, C. Rolny, G. Castelo-Branco, J. Hjerling-Leffler, and S. Linnarsson, “Cell types in the mouse cortex and hippocampus revealed by single-cell RNA-seq,” Science, vol. 347, no. 6226, pp. 1138–1142, Mar. 2015.``
- The R implementation is available on `github <https://github.com/aertslab/SCENIC>`_
- The first phase of the pipeline, i.e. inference of co-expression modules, can be done via the python package `arboretum`_


