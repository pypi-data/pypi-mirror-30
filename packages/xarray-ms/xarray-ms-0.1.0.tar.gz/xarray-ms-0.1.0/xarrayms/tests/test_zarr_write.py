from __future__ import print_function

import argparse
import logging
import os
import os.path

import dask.array as da
from xarrayms import xds_from_ms
import zarr

logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.WARN)

def create_parser():
    p = argparse.ArgumentParser()
    p.add_argument("ms")

    return p

args = create_parser().parse_args()

store = zarr.DirectoryStore("zarr_data")
group = zarr.hierarchy.group(store=store, overwrite=True,
                            synchronizer=zarr.ThreadSynchronizer())


from dask.diagnostics import ProgressBar, Profiler

with ProgressBar(), Profiler() as prof:
    for i, ds in enumerate(xds_from_ms(args.ms)):

        _, ms = os.path.split(args.ms.rstrip(os.sep))

        field_id = ds.attrs['FIELD_ID']
        data_desc_id = ds.attrs['DATA_DESC_ID']

        ds_group = group.create_group('%s/FIELD_ID_%s/DATA_DESC_ID_%s'
                            % (ms, field_id, data_desc_id))

        compressor = zarr.Blosc(cname='zstd', clevel=3, shuffle=2)

        for name, array in ds.data_vars.items():
            array_size = array.nbytes / (1024.**2)
            print("Writing out %s of size %.3fMB" % (name, array_size))
            chunks = tuple(max(c) for c in array.chunks)
            zarr_out = ds_group.zeros(name, shape=array.shape,
                                            dtype=array.dtype,
                                            chunks=chunks,
                                            compressor=compressor)

            da.store(array.data, zarr_out)

    prof.visualize(file_path="prof.html")
