"""
Module for simple directory based functions
"""
import itertools
import os
import shutil


def recursive_dirs(in_func):
    """
    Decorator for allowing recursion for generic directory based
    functions
    """
    def recursive_func(directory, *args, **kwargs):

        if isinstance(directory, list):
            return list(itertools.chain.from_iterable([list_files(d, *args, **kwargs)
                                                       for d in directory]))
        else:
            return in_func(directory, **kwargs)

    return recursive_func


@recursive_dirs
def list_files(directory='', extensions=None, return_full_path=True):
    """
    List all files contained in a directory

    Parameters
    ----------
    directory : str, list, optional
        Absolute or relative directory path to list files in
    extensions : list, or str, optional
        String or list of strings specifying file extensions to include
    return_full_path : bool, optional
        Whether to return the full paths or just the base name

    """


    directory = os.path.abspath(directory)

    files = [f for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]

    # Restrict by file extension
    if extensions:
        if isinstance(extensions, str):
            extensions = [extensions]
        files = [f for f in files
                 if os.path.splitext(f)[1][1:] in extensions]

    if return_full_path:
        files = [os.path.join(directory, f) for f in files]

    files.sort()

    return files


@recursive_dirs
def list_dirs(directory='', return_full_path=True):
    """
    List all directories contained in a directory

    Parameters
    ----------
    directory : str, optional
        Absolute or relative directory path to list directories in
    return_full_path : bool, optional
        Whether to return the full paths or just the base names

    """
    directory = os.path.abspath(directory)

    dir_list = [d for d in os.listdir(directory)
               if os.path.isdir(os.path.join(directory, d))]

    if return_full_path:
        dir_list = [os.path.join(directory, d) for d in dir_list]

    dir_list.sort()

    return dir_list


@recursive_dirs
def list_items(directory='', return_full_path=True):
    """
    List all files and directories contained in a directory

    Parameters
    ----------
    directory : str, optional
        Absolute or relative directory path to list directories in
    return_full_path : bool, optional
        Whether to return the full paths or just the base names

    """
    items = (list_files(directory=directory, return_full_path=return_full_path)
             + list_dirs(directory=directory,
                         return_full_path=return_full_path))

    return items


@recursive_dirs
def list_records(directory='', return_full_path=True):
    """
    List all wfdb records in a directory (by finding header files).
    Wraps around list_files with .hea extension.

    Usage:
    list_records(directory=os.getcwd(), return_full_path=True)
    """

    files = list_files(directory=directory, extensions='hea',
                       return_full_path=return_full_path)
    records = [f.split('.hea')[0] for f in files]

    records.sort()

    return records


def clear_dir(directory):
    """
    rm -rf
    """
    items = list_items(directory)

    for item in items:
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item)


def cat(file):
    """
    Print the contents of a file. Just like unix cat.
    """
    with open(file) as f:
        print(f.read())


def read_lines(file, start_line=0, stop_line=None, strip=True, rm_empty=True):
    """
    Read lines of a file into a list

    Parameters
    ----------
    start_line : int, optional
        Starting line number to read from
    stop_line : int, optional
        Final line number to read
    strip : bool, optional
        Whether to remove leading/trailing whitespaces and newlines

    """
    lines = []

    with open(file, 'r') as f:
        for line in itertools.islice(f, start_line, stop_line):
            lines.append(line)

    if strip:
        lines = [l.strip() for l in lines]

    if rm_empty:
        lines = [l for l in lines if l]

    return lines


def write_lines(file, lines):
    """
    Write the lines in a list to a file.

    Each list element will be written to a new line.
    """
    f = open(file, 'w')
    for line in lines:
        f.write('%s\n' % line)



def dir_size(directory='', readable=False, walk=True):
    """
    Recursive size of a directory in bytes
    Like du -s with default options.
    Or just get size of local files with walk=False

    Parameters
    ----------
    directory : str
        The base directory
    readable : bool, optionsl
        If False, return number of bytes. If True, return (size, units)
    walk : bool, optional
        Whether to crawl subdirectories like du -sh. Otherwise only
        lists size of contents in immediate directory

    """
    total_size = 0

    if walk:
        for dirpath, dirnames, filenames in os.walk(directory):
            for fname in filenames:
                file = os.path.join(dirpath, fname)
                total_size += os.path.getsize(file)
    else:
        total_size = sum([os.path.getsize(file) for file in list_files(directory)])

    if readable:
        return readable_size(total_size)
    else:
        return total_size


# File/folder size functions
allowed_units = ['K','M','G','T']
unit_factor = dict(zip(allowed_units, [1024**i for i in range(1, len(allowed_units)+1)]))


def convert_size(n_bytes, unit):
    """
    Convert number of bytes to another unit. kb, mb, gb ,tb.
    """
    if unit not in allowed_units:
        raise ValueError('units must be one of the following:', allowed_units)

    return n_bytes / unit_factor[unit]


def readable_size(n_bytes, return_fmt='pairs'):
    """
    Get readable size. Returns number of _bytes, and the units.
    ie. readable_size(1024) == (1, 'K')

    Parameters
    ----------
    n_bytes : int
        Number of bytes to convert
    return_fmt : str, optional
        One of:
          - 'pairs': returns tuple pairs of (size, unit)
          - 'size': returns size
          - 'string': returns string str(size) + units

    """
    if return_fmt == 'size':
        return readable_size(n_bytes)[0]
    elif return_fmt == 'string':
        s, u = readable_size(n_bytes)
        return ' '.join(('%.2f' % s, u))

    if n_bytes < 1024:
        return n_bytes, ''

    for unit in allowed_units:
        n_units = convert_size(n_bytes, unit)
        if n_units < 1024:
            return n_units, unit

    raise ValueError('Size is beyond terrabytes?')


def replace_spaces(directory='', replacement='-', walk=True):
    """
    Replace all spaces in file names contained in a directory

    """
    if walk:
        files = []
        for dirpath, _, filenames in os.walk(directory):
            # Not an empty directory
            if filenames:
                files = files + [os.path.join(dirpath, fn) for fn in filenames]
    else:
        files = list_files(directory=directory)

    for file in files:
        dirname = os.path.dirname(file)
        basename = os.path.basename(file)
        if ' ' in basename:
            os.rename(file, os.path.join(dirname, basename.replace(' ',
                replacement)))
