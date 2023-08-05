# -*- coding: utf-8 -*-

import pandas as pd
from .recovery import enrichment4cells
from tqdm import tqdm
from typing import Sequence, Type
from .genesig import GeneSignature
from multiprocessing import cpu_count, Process, Array
from boltons.iterutils import chunked
from multiprocessing.sharedctypes import RawArray
from operator import mul
import numpy as np
import logging
from math import ceil
from ctypes import c_uint32
from operator import attrgetter


LOGGER = logging.getLogger(__name__)
# To reduce the memory footprint of a ranking matrix we use unsigned 32bit integers which provides a range from 0
# through 4,294,967,295. This should be sufficient even for region-based approaches.
DTYPE = 'uint32'
DTYPE_C = c_uint32


def create_rankings(ex_mtx: pd.DataFrame) -> pd.DataFrame:
    """
    Create a whole genome rankings dataframe from a single cell expression profile dataframe.

    :param ex_mtx: The expression profile matrix. The rows should correspond to different cells, the columns to different
        genes (n_cells x n_genes).
    :return: A genome rankings dataframe (n_cells x n_genes).
    """
    return ex_mtx.rank(axis=1, ascending=False, method='first').astype(DTYPE)


enrichment = enrichment4cells


def _enrichment(shared_ro_memory_array, modules, genes, cells, rank_threshold, auc_threshold, auc_mtx, offset):
    # The rankings dataframe is properly reconstructed (checked this).
    df_rnk = pd.DataFrame(data=np.frombuffer(shared_ro_memory_array, dtype=DTYPE).reshape(len(cells), len(genes)),
                          columns=genes, index=cells)
    # To avoid additional memory burden de resulting AUCs are immediately stored in the output sync. array.
    result_mtx = np.frombuffer(auc_mtx.get_obj(), dtype='d')
    inc = len(cells)
    for idx, module in enumerate(modules):
        result_mtx[offset+(idx*inc):offset+((idx+1)*inc)] = enrichment4cells(df_rnk, module, rank_threshold,
                                                                             auc_threshold).values.flatten(order="C")


def aucell(exp_mtx: pd.DataFrame, modules: Sequence[Type[GeneSignature]],
           rank_threshold: int = 5000, auc_threshold: float = 0.05,
           noweights: bool = False, num_cores: int = cpu_count()) -> pd.DataFrame:
    """
    Calculate enrichment of regulomes for single cells.

    :param exp_mtx: The expression matrix (n_cells x n_genes).
    :param modules: The regulomes.
    :param rank_threshold: The total number of ranked genes to take into account when creating a recovery curve.
    :param auc_threshold: The fraction of the ranked genome to take into account for the calculation of the
        Area Under the recovery Curve.
    :param noweights: Should the weights of the genes part of regulome be used in calculation of enrichment?
    :param num_cores: The number of cores to use.
    :return: A dataframe with the AUCs (n_cells x n_modules).
    """
    df_rnk = create_rankings(exp_mtx)

    if num_cores == 1:
        # Show progress bar ...
        aucs = pd.concat([enrichment(df_rnk, module.noweights() if noweights else module,
                                 rank_threshold=rank_threshold,
                                 auc_threshold=auc_threshold) for module in tqdm(modules)]).unstack("Regulome")
        aucs.columns = aucs.columns.droplevel(0)
        return aucs
    else:
        # Decompose the rankings dataframe: the index and columns are shared with the child processes via pickling.
        genes = df_rnk.columns.values
        cells = df_rnk.index.values
        # The actual rankings are shared directly. This is possible because during a fork from a parent process the child
        # process inherits the memory of the parent process. A RawArray is used instead of a synchronize Array because
        # these rankings are read-only.
        shared_ro_memory_array = RawArray(DTYPE_C, mul(*df_rnk.shape))
        array = np.frombuffer(shared_ro_memory_array, dtype=DTYPE)
        # Copy the contents of df_rank into this shared memory block using row-major ordering.
        array[:] = df_rnk.as_matrix().flatten(order='C')

        # The resulting AUCs are returned via a synchronize array.
        auc_mtx = Array('d', len(cells) * len(modules))  # Double precision floats.

        # Convert the modules to modules with uniform weights if necessary.
        if noweights:
            modules = list(map(lambda m: m.noweights(), modules))

        # Do the analysis in separate child processes.
        chunk_size = ceil(float(len(modules))/num_cores)
        processes = [Process(target=_enrichment, args=(shared_ro_memory_array, chunk,
                                                       genes, cells,
                                                       rank_threshold, auc_threshold,
                                                       auc_mtx, (chunk_size*len(cells))*idx))
                     for idx, chunk in enumerate(chunked(modules, chunk_size))]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        # Reconstitute the results array. Using C or row-major ordering.
        return pd.DataFrame(data=np.ctypeslib.as_array(auc_mtx.get_obj()).reshape(len(modules), len(cells)),
                           columns=pd.Index(data=cells, name='Cell'),
                            index=pd.Index(data=list(map(attrgetter("name"), modules)), name='Regulome')).T

