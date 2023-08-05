# Copyright (c) 2010-2018 Andrew Dalke Scientific, AB (Sweden)
# See the contents of "chemfp/__init__.py" for full license details.

import argparse

import sys

import itertools
import heapq
import struct
import os
import re

from .. import __version__ as chemfp_version
from .. import arena as arena_module
from .. import bitops
from .. import io
from .. import open as _open_fingerprints, ChemFPError, Metadata, open_fingerprint_writer

from . import cmdsupport
from .._compat import myrepr

imap = getattr(itertools, "imap", map) # itertools.imap() for Python 2.7, map() for Python 3.x

def die(errmsg):
    sys.stderr.write("ERROR: %s\n" % (errmsg,))
    return SystemExit(1)

def open_fingerprints(source, format):
    try:
        return _open_fingerprints(source, format=format)
    except (IOError, io.ParseError) as err:
        # IOErrors and ParseErrors include the filename
        raise die(err)
    except (ChemFPError, ValueError) as err:
        assert source is not None, source  # Not supposed to raise this case
        raise die("%s: %r" % (err, source))

###### Progress classes

class _Progress(object):
    def __init__(self, outfile):
        self.outfile = outfile
        self._reset_msg = ""

    def start(self):
        pass
        
    def _update(self, msg):
        if msg is None:
            return
        self.outfile.write(self._reset_msg)
        self.outfile.write(msg)
        self.outfile.flush()
        self._reset_msg = "\r" + (" " *len(msg)) + "\r"
        
    def start_close(self):
        self._update(self.close_msg)
        
    def end(self):
        self.outfile.write(self._reset_msg)
        self.outfile.flush()
        self._reset_msg = ""

class SequentialProgress(_Progress):
    def __init__(self, num_filenames, close_msg=None, outfile=sys.stderr):
        _Progress.__init__(self, outfile)
        self.num_filenames = num_filenames
        self.close_msg = close_msg
        self.outfile = outfile
        self.count = 0
        if not num_filenames:
            self._where = " records from stdin."
        else:
            self._where = None  # You must first call 'start_filename'!

    def start_filename(self, filename):
        self.count += 1
        if self.num_filenames == 1:
            where = " records from %s" % (repr(filename)[1:-1])
        else:
            where = " records. File %d/%d: %s" % (self.count, self.num_filenames, repr(filename)[1:-1])
        self._where = where

    def update_status(self, num_records):
        msg = str(num_records) + self._where
        self._update(msg)


class MergeProgress(_Progress):
    def __init__(self, num_filenames, outfile=sys.stderr):
        assert num_filenames >= 2, "use a SequentialProgress"
        _Progress.__init__(self, outfile)
        self._where = " records from %d files." % (num_filenames,)

    def update_status(self, num_records):
        msg = str(num_records) + self._where
        self._update(msg)


###### Use when the output is in FPS format but where the fingerprints must be sorted
        
class MemoryWriter(object):
    def __init__(self, arena_builder, output, format):
        self.arena_builder = arena_builder
        self.output = output
        self.format = format

    def write_fingerprints(self, id_fp_pairs):
        self.arena_builder.add_fingerprints(id_fp_pairs)

    def close(self):
        arena = self.arena_builder.make_arena()
        self.arena_builder = None
        arena.save(self.output, format=self.format)
            

def make_memory_writer(output, metadata, format):
    # Want to reorder, and want fps output. Do this in memory
    arena_builder = arena_module.ArenaBuilder(metadata=metadata, reorder=True, alignment=1)
    return MemoryWriter(arena_builder, output, format)
                              

###### 
            

def make_sequential_chunk_reader(filenames, format, progress):
    progress.start_filename(filenames[0])
    compat_values, compat_filenames = start_compatibility()

    reader = open_fingerprints(filenames[0], format=format)
    try:
        check_compatibility(compat_values, compat_filenames, reader, filenames[0])
    except TypeError as err:
        raise die(str(err))

    def read_sequential_records(first_reader, filenames, format):
        yield first_reader
        first_reader.close()
        first_reader = None
        for i, filename in enumerate(filenames):
            progress.start_filename(filename)
            reader = open_fingerprints(filename, format=format)
            try:
                check_compatibility(compat_values, compat_filenames, reader, filename)
            except TypeError as err:
                reader.close()
                raise die(str(err))
            yield reader
            reader.close()

    # Use information from the first reader to make a new metadata.
    md = reader.metadata
    metadata = Metadata(
        num_bits = md.num_bits,
        num_bytes = md.num_bytes,
        type = md.type,
        aromaticity = md.aromaticity,
        software = md.software,
        #date = chemfp.io.utcnow(),
        )
        
         
    return metadata, read_sequential_records(reader, filenames[1:], format)

# Keep track of a dictionary of expected values for each compatability factor.
def start_compatibility():
    compat_values = {}
    compat_filenames = {}
    for name in ("type", "num_bits", "num_bytes", "storage_size", "software", "aromaticity"):
        compat_values[name] = None      # The expected value; None if unknown, _incompatible if problem.
        compat_filenames[name] = None   # Where the information came from
    compat_values["all_fpb"] = True
    return compat_values, compat_filenames


_incompatible = object()

# Check a given attribute for compatibility issues.
def _compatibility(attribute, values, filenames,
                   new_value, new_filename, error):
    # Compare to an old value, if it exists.
    old_value = values[attribute]
    if old_value is None:
        if new_value is None:
            # Nothing assigned
            return
        # Use the new value
        values[attribute] = new_value
        filenames[attribute] = new_filename
        return

    if new_value is None:
        # Have an old value, don't have a new value. Stay with the old value.
        return

    # Have an old and a new value. Make sure they are the same.
    if old_value != new_value:
        if old_value is _incompatible:  # already seen this. Supress additional warnings.
            return
        old_filename = filenames[attribute]
        values[attribute] = _incompatible
        error(values, attribute, old_value, old_filename, new_value, new_filename)
    
def _compat_error(values, attribute, old_value, old_filename, new_value, new_filename):
    raise TypeError("%r has a %s of %s, which is not compatible with the %r which has a %s of %s"
                    % (new_filename, attribute, myrepr(new_value), old_filename, attribute, myrepr(old_value)))

def _compat_ignore(values, attribute, old_value, old_filename, new_value, new_filename):
    pass

## def _compat_first(values, attribute, old_value, old_filename, new_value, new_filename):
##     # Restore the old value
##     values[attribute] = old_value

def _compat_warning(values, attribute, old_value, old_filename, new_value, new_filename):
    sys.stderr.write("WARNING: %r has a %s of %s, which is not compatible with %r which has a %s of %s"
                     % (new_filename, attribute, myrepr(new_value), old_filename, attribute, myrepr(old_value)))
    


def check_compatibility(compat_values, compat_filenames, reader, new_filename):
    metadata = reader.metadata
    _compatibility("type", compat_values, compat_filenames,
                   metadata.type, new_filename, _compat_error)
    #print >>open("/dev/stderr", "w"), "Check", metadata, repr(metadata), repr(metadata.num_bytes)
    if metadata.num_bytes is not None:
        # By construction, this means the file is empty, and without metadata
        _compatibility("num_bits", compat_values, compat_filenames,
                       metadata.num_bits, new_filename, _compat_error)
        _compatibility("num_bytes", compat_values, compat_filenames,
                       metadata.num_bytes, new_filename, _compat_error)
    _compatibility("software", compat_values, compat_filenames,
                   metadata.software, new_filename, _compat_ignore)
    _compatibility("aromaticity", compat_values, compat_filenames,
                   metadata.aromaticity, new_filename, _compat_warning)  # use logs?

    if isinstance(reader, arena_module.FingerprintArena):
        _compatibility("storage_size", compat_values, compat_filenames,
                       reader.storage_size, new_filename, _compat_ignore)
    else:
        compat_values["all_fpb"] = False

################ Merge multiple inputs in parallel

# Assume the inputs are in popcount order, and keep the output
# fingerprints in popcount order. (Break ties based on input filename
# index.)

# Standard decorate-sort-undecorate approach, using heapq.merge to
# sort the already-sorted inputs.
         
def decorate_with_popcount(reader, position):
    byte_popcount = bitops.byte_popcount
    for id, fp in reader:
        yield byte_popcount(fp), position, id, fp

def decorate_arena_with_popcount(arena, position):
    popcount_indices = arena.popcount_indices
    indices = struct.unpack("<" + "I"*(len(popcount_indices)//4), popcount_indices)
    for popcount in range(len(indices)-1):
        start_index = indices[popcount]
        end_index = indices[popcount+1]
        subarena = arena[start_index:end_index]
        for id, fp in subarena:
            yield popcount, position, id, fp


from operator import itemgetter
undecorate = itemgetter(2, 3)


def make_merge_chunk_reader(filenames, format):
    # Open multiple files in parallel and merge assuming sorted by popcount
    merge_info = Metadata()

    compat_values, compat_filenames = start_compatibility()

    readers = []
    decorated_readers = []
    sources = []
    for position, filename in enumerate(filenames):
        reader = open_fingerprints(filename, format=format)
        readers.append(reader)
        try:
            check_compatibility(compat_values, compat_filenames, reader, filename)
        except TypeError as err:
            # Close all currently open files
            for r in readers:
                r.close()
            raise die(str(err))
        sources.extend(reader.metadata.sources)         # merge all sources

        if isinstance(reader, arena_module.FingerprintArena) and reader.popcount_indices:
            # Easy optimization to decorate this case
            decorated_reader = decorate_arena_with_popcount(reader, position)
        else:
            # Need to do the byte_popcount for this case.
            decorated_reader = decorate_with_popcount(reader, position)
            
        decorated_readers.append(decorated_reader)

    software = compat_values["software"]
    if software is _incompatible:
        software = None

    aromaticity = compat_values["aromaticity"]
    if aromaticity is _incompatible:
        aromaticity = None

    metadata = Metadata(
        num_bits = compat_values["num_bits"],
        num_bytes = compat_values["num_bytes"],
        sources = sources,
        software = software,
        aromaticity = aromaticity,
        #date = datetime.datetime.now(),
        #date = io.utcnow(),
        )

        
    def merge_chunk_reader(readers, id_fp_pairs):
        try:
            yield id_fp_pairs
        finally:
            for reader in readers:
                reader.close()

    return metadata, merge_chunk_reader(readers, imap(undecorate, heapq.merge(*decorated_readers)))
    

epilog = """

Examples:

fpcat can be used to merge multiple FPS files. For example, you might
have used GNU parallel to generate FPS files for each of the PubChem
files, which you want to merge into a single file.:

    fpcat Compound_*.fps -o pubchem.fps

The --merge option is experimental. Use it if the input fingerprints
are in popcount order, because sorted output is a simple merge sort of
the individual sorted inputs. However, this option opens all input
files at the same time, which may exceed your resource limit on file
descriptors. The current implementation also requires a lot of disk
seeks so is slow for many files.

    
"""



parser = argparse.ArgumentParser(
    description="Combine multiple fingerprint files into a single file.",
    epilog=epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
parser.add_argument(
    "--in", metavar="FORMAT", dest="input_format", choices=("fps", "fps.gz", "flush"),
    help="input fingerprint format. One of fps or fps.gz. (default guesses from filename or is fps)")
parser.add_argument(
    "--merge", action="store_true",
    help="assume the input fingerprint files are in popcount order and do a merge sort")
parser.add_argument(
    "-o", "--output", metavar="FILENAME",
    help="save the fingerprints to FILENAME (default=stdout)")

parser.add_argument(
    "--out", metavar="FORMAT", dest="output_format", choices=("fps", "fps.gz", "flush"),
    help="output fingerprint format. One of fps or fps.gz. (default guesses from output filename, or is 'fps')")
parser.add_argument(
    "--reorder", action="store_true",
    help="reorder the output fingerprints by popcount")
parser.add_argument(
    "--preserve-order", action="store_true",
    help="save the output fingerprints in the same order as the input (default for FPS output)")

parser.add_argument(
    "--show-progress", action="store_true",
    help="show progress")

_scales = {
    "K" : 1000,
    "KB": 1000,
    "M" : 1000*1000,
    "MB": 1000*1000,
    "G" : 1000*1000*1000,
    "GB": 1000*1000*1000,
    "T" : 1000*1000*1000*1000,
    "TB": 1000*1000*1000*1000,
    "P" : 1000*1000*1000*1000*1000,
    "PB": 1000*1000*1000*1000*1000,
    }

_leading_digit = re.compile(r"(\d+(\.\d*)?)(KB?|MB?|GB?|TB?|PB?)?$")

_MIN_SIZE = 20*1000*1000
_MIN_SIZE_STR = "20MB"

def fancy_size(size):
    s = size.upper()
    if s == "NONE":
        return None
    m = _leading_digit.match(s)
    if not m:
        raise argparse.ArgumentTypeError("Unable to convert %r into a memory size" % (size,))

    scalar = m.group(1)
    scale = m.group(3)
    if not scale:
        scale = 1
    else:
        scale = _scales[scale]
        
    if "." in scalar:
        # Could goo back/forth through float, but since I
        # have the decimal module, I'll use it.
        import decimal
        result = int(decimal.Decimal(scalar) * scale)
    else:
        result = int(scalar) * scale

    if result < _MIN_SIZE:
        raise argparse.ArgumentTypeError("Must be at least %s, not %s bytes" % (_MIN_SIZE_STR, size))
    return result
    
cmdsupport.add_version(parser)
parser.add_argument("filenames", metavar="filename", nargs="*",
                    help="input fingerprint filenames (default: use stdin)")


def run():
    cmdsupport.run(main)

def main(args=None):
    args = parser.parse_args(args)

    if args.preserve_order and args.reorder:
        parser.error("Cannot specify both --preserve-order and --reorder; they are incompatible")

    if not cmdsupport.has_chemfp_converters:
        if args.input_format == "flush":
            cmdsupport.die("--in format 'flush' not supported because the chemfp_converter module is not available")
        if args.output_format == "flush":
            cmdsupport.die("--out format 'flush' not supported because the chemfp_converter module is not available")
        
    # Do some checking before I start doing I/O
    if not args.filenames:
        # Read from stdin, which means that only FPS is supported.
        if args.input_format == "fpb":
            raise die("The FPB input reader only works on memory-mapped files, and not stdin")
    else:
        # This is a preliminary check, used to give early feedback.
        for filename in args.filenames:
            if not os.path.exists(filename):
                raise die("Fingerprint file %r does not exist" % (filename,))


    output = args.output
    output_format = args.output_format
    if output is None:
        # Save to stdout, which means that only FPS is supported.
        if output_format == "fpb":
            raise die("The FPB output writer only works with seekable files, and not stdout")
    else:
        # Note: if the filename is "abc.fpb", then the dirname is ""
        # Normally I prefer to just open and catch the error. But with a
        # memory writer, the open doesn't occur until the very end, so
        # this error may be too late.
        dirname = os.path.dirname(output)
        if dirname:
            if not os.path.exists(dirname):
                raise die("The output directory for %r does not exist" % (dirname,))
            if not os.path.isdir(dirname):
                raise die("The output directory for %r is not actually a directory" % (dirname,))
        
        format, compression = io.normalize_output_format(output, output_format, ("fps", ""))
        if format == "fpb":
            raise die("This version of chemfp does not support the FPB format.")
        if compression:
            if format == "fps":
                output_format = format+"."+compression
            elif format == "flush":
                raise die("Compression of flush files is not supported")
            else:
                raise die("Unsupported output fingerprint format %r" % (format,))
        else:
            output_format = format
            if output_format not in ("fpb", "fps", "fps.gz", "flush"):
                raise die("Unsupported output fingerprint format %r" % (format,))
        

    if args.reorder:
        reorder = True
    elif args.preserve_order:
        reorder = False
    else:
        # Select a default based on the output type
        if output_format == "fpb":
            reorder = True
        else:
            reorder = False

    # TODO: Check if the inputs and the output are in fpb format.  If
    # so, and if the inputs all have the same num_bytes and
    # storage_size, then there are faster ways to merge.

    # Create the input reader

    class progress:        # Placeholder to support an output-specific 'close' message
        close_msg = None   # so I don't have to worry if an input-specific progress is available.

    # NOTE: the FPS reader reads the metadata before returning
    if not args.filenames:
        reader = open_fingerprints(None, format=args.input_format)
        progress = SequentialProgress(len(args.filenames), outfile=sys.stderr)
        def stdin_chunk_reader(reader):
            yield reader
        metadata, chunk_reader = reader.metadata, stdin_chunk_reader(reader)
    else:
        if args.merge and len(args.filenames) >= 2:
            progress = MergeProgress(len(args.filenames), outfile=sys.stderr)
            metadata, chunk_reader = make_merge_chunk_reader(args.filenames, format=args.input_format)
        else:
            progress = SequentialProgress(len(args.filenames), outfile=sys.stderr)
            metadata, chunk_reader = make_sequential_chunk_reader(args.filenames, format=args.input_format,
                                                                  progress=progress)

    # Create the output writer
            
    try:
        # Always try to open the writer now so I can catch any errors early.
        try:
            writer = open_fingerprint_writer(output, metadata=metadata, format=output_format)
        except ValueError as err:
            raise die("Cannot open fingerprint writer: %s" % (err,))
        progress.close_msg = ""
        
        if reorder:
            # Close now, and use save() in the memory writer to actually save it.
            # I could pass in the already-open writer, but that would bypass the
            # fast code to save an arena as FPB files for chemfp 2.x or later.
            # I want even chemfp 1.x to have the same double-open behavior.
            writer.close()
            # Build an arena into memory then save the arena
            writer = make_memory_writer(output, metadata=metadata, format=output_format)
            progress.close_msg = "Writing fingerprints in FPS format, ordered by popcount."

    except IOError as err:
        chunk_reader.close()
        raise die("Unable to open fingerprint writer: %s" % (err,))


    try:
        if args.show_progress:
            # Progress is hard because I want to show some progress even
            # when the input is from a single file or when merging files.
            # (In both cases I don't know the total number of records.)

            progress.start()
            num_processed = 0
            progress.update_status(num_processed)
            for id_fp_pairs in chunk_reader:
                id_fp_pairs = iter(id_fp_pairs) # make sure it's an iterator, so I can ...
                while 1:
                    id_fp_pairs_list = list(itertools.islice(id_fp_pairs, 50000)) # .. read 50,000 at a time
                    if not id_fp_pairs_list:
                        break
                    writer.write_fingerprints(id_fp_pairs_list)
                    num_processed += len(id_fp_pairs_list)
                    progress.update_status(num_processed)
            progress.start_close()
            writer.close()
            progress.end()
            if args.filenames:
                if len(args.filenames) == 1:
                    where =  "1 file"
                else:
                    where = "%d files" % (len(args.filenames),)
            else:
                where = "stdin"
            sys.stderr.write("Done. Processed %d records from %s.\n" % (num_processed, where))
            sys.stderr.flush()

        else:
            for id_fp_pairs in chunk_reader:
                writer.write_fingerprints(id_fp_pairs)
            writer.close()

    except (ChemFPError, IOError) as err:
        chunk_reader.close()
        raise die("Unable to create fingerprints:" + str(err))

    

if __name__ == "__main__":
    main(sys.argv[1:])
