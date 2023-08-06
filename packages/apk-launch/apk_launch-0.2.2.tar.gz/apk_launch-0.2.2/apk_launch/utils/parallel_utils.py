"""
parallel_utils is a helper file for handling parallel operations.

    Copyright (C) 2018 Zach Yannes
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
import sys
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)


def parallelize(function, array, n_jobs=16, use_kwargs=False, front_num=3):
    """
    Run function in parallel.

    Args:
        function: function to run
        array: input args for function
        n_jobs: number of jobs to use (defaults to 16)
        use_kwargs: use kwargs for function args (defaults to False)
        front_num: number of functions to run serially (defaults to 3)

    Returns:
        outputs from function

    """
    if front_num > 0:
        front = [function(**a) if use_kwargs else function(a) for a in array[:front_num]]
    if n_jobs == 1:
        return front + [function(a) for a in tqdm(array[front_num:])]
    # with ProcessPoolExecutor(max_workers = n_jobs) as pool:
    with ThreadPoolExecutor(max_workers=n_jobs) as pool:
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(function, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        # pylint: disable=unused-variable
        for func in tqdm(as_completed(futures), **kwargs):
            pass

    out = []
    for future in tqdm(futures):
        # pylint: disable=broad-except
        try:
            out.append(future.result())
        except Exception as err:
            out.append(err)
    return front + out


def parallelize_multiple(functions, array, n_jobs=16, use_kwargs=False):
    """
    Run multiple function in parallel.

    Args:
        function: function to run
        array: input args for function
        n_jobs: number of jobs to use (defaults to 16)
        use_kwargs: use kwargs for function args (defaults to False)

    Returns:
        outputs from functions

    """
    if len(functions) != len(array):
        LOG.error('Error: length of array (%s) does not match length of functions (%s)',
                  len(array), len(functions))
        sys.exit(1)

    if n_jobs == 1:
        return [f(a) for f, a in tqdm(zip(functions, array))]
    # with ProcessPoolExecutor(max_workers = n_jobs) as pool:
    with ThreadPoolExecutor(max_workers=n_jobs) as pool:
        if use_kwargs:
            futures = [pool.submit(f, **a) for f, a in zip(functions, array)]
        else:
            futures = [pool.submit(f, a) for f, a in zip(functions, array)]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        # pylint: disable=unused-variable
        for func in tqdm(as_completed(futures), **kwargs):
            pass

    out = []
    for future in tqdm(futures):
        # pylint: disable=broad-except
        try:
            out.append(future.result())
        except Exception as err:
            out.append(err)
    return out
