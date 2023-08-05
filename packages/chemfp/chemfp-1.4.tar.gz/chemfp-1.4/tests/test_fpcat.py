import os
import sys
import tempfile
import re
import gzip

from support import get_tmpdir

import unittest2

import chemfp
import chemfp.commandline.fpcat
import argparse
from chemfp._compat import StringIO, BytesIO, string_types
from chemfp.bitops import hex_encode_as_bytes, hex_decode

import support
from support import has_chemfp_converters

def get_tmpfile(test_case, filename):
    dirname = get_tmpdir(test_case)
    return os.path.join(dirname, filename)

QUERIES_FPS = support.fullpath("queries.fps")
with open(QUERIES_FPS, "rb") as f:
    QUERIES_FPS_BYTES = f.read()
DRUGS_SMI = support.fullpath("drugs.smi")

INCOMPATIBLE_NUM_BITS = support.fullpath("queries_incompatible_num_bits.fps")
INCOMPATIBLE_NUM_BYTES = support.fullpath("queries_incompatible_num_bytes.fps")
INCOMPATIBLE_TYPE = support.fullpath("queries_incompatible_type.fps")
INCOMPATIBLE_SOFTWARE = support.fullpath("queries_incompatible_software.fps")
INCOMPATIBLE_AROMATICITY1 = support.fullpath("queries_incompatible_aromaticity1.fps")
INCOMPATIBLE_AROMATICITY2 = support.fullpath("queries_incompatible_aromaticity2.fps")

DRUGS_FLUSH = support.fullpath("drugs.flush")

real_stdin = sys.stdin
real_stdout = sys.stdout
real_stderr = sys.stderr

class CaptureOutput(object):
    def __init__(self, stdin_text=None, expect_exit=False):
        self.stdin_text = stdin_text
        self.expect_exit = expect_exit

    def __enter__(self):
        if self.stdin_text is not None:
            sys.stdin = BytesIO(self.stdin_text)
        sys.stdout = BytesIO()
        sys.stderr = StringIO()
        return self

    def __exit__(self, type, value, tb):
        self.stdout = sys.stdout.getvalue()
        self.stderr = sys.stderr.getvalue()
        self.stdin = real_stdin
        sys.stdout = real_stdout
        sys.stderr = real_stderr

class Output(object):
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr


def run(s, stdin_text=None, expect_exit=False):
    if isinstance(s, string_types):
        args = s.split()
    else:
        args = s
    try:
        with CaptureOutput(stdin_text) as capture:
            chemfp.commandline.fpcat.main(args)
    except SystemExit as err:
        if expect_exit:
            pass
        else:
            raise AssertionError("Did not expect to exit: %s\n%s" % (err, capture.stderr))
    else:
        if expect_exit:
            raise AssertionError("Expected to exit, but did not.")

    return Output(capture.stdout, capture.stderr)


class TestBadCommandlineArgs(unittest2.TestCase):
    def test_preserve_order_and_reorder(self):
        output = run("--preserve-order --reorder", expect_exit=True)
        self.assertIn("Cannot specify both --preserve-order and --reorder; they are incompatible\n",
                      output.stderr)

    def test_stdin_with_fpb_format(self):
        output = run("--in fpb", expect_exit=True)
        self.assertIn("--in: invalid choice: 'fpb' (choose from 'fps', 'fps.gz', 'flush')",
                      output.stderr)

    def test_stdout_with_fpb_format(self):
        output = run("--out fpb", expect_exit=True)
        self.assertIn("--out: invalid choice: 'fpb' (choose from 'fps', 'fps.gz', 'flush')",
                      output.stderr)

    def test_compressed_fpb_fails_output(self):
        filename = get_tmpfile(self, "wrong_compression.fpb.gz")
        output = run(["-o", filename], b"", expect_exit=True)
        self.assertIn("This version of chemfp does not support the FPB format.", output.stderr)
        
    def test_bad_extension(self):
        filename = get_tmpfile(self, "unknown_output_format.fpq")
        output = run(["-o", filename], b"", expect_exit=True)
        self.assertIn("Unsupported output fingerprint format 'fpq'", output.stderr)

    def test_bad_extension_compressed(self):
        filename = get_tmpfile(self, "unknown_output_format.fpq.gz")
        output = run(["-o", filename], b"", expect_exit=True)
        self.assertIn("Unsupported output fingerprint format 'fpq'", output.stderr)

class TestFormatsAndFilenames(unittest2.TestCase):
    def test_bad_input_format(self):
        output = run("--in spam", expect_exit=True)
        self.assertIn("--in: invalid choice: 'spam' (choose from 'fps', 'fps.gz', 'flush')", output.stderr)

    def test_bad_input_filename(self):
        output = run([DRUGS_SMI], expect_exit=True)
        self.assertIn("Unable to determine fingerprint format type from", output.stderr)
        self.assertIn("drugs.smi'", output.stderr)

    def test_file_not_in_fps_format(self):
        output = run(["--in", "fps", DRUGS_SMI], expect_exit=True)
        # It doesn't really need to return this error. This is because it didn't find a tab.
        # However, an alternate implementation could also report that there are non-hex characters.
        self.assertIn("Missing fingerprint field", output.stderr)
        self.assertIn("drugs.smi'", output.stderr)
        self.assertIn("line 1", output.stderr)

    def test_stdin_not_in_fps_format(self):
        output = run(["--in", "fps"], b"ABCD\tAndrew\nBCDE\tDalke\nbad\tBAD\n", expect_exit=True)
        self.assertIn("Fingerprint field is in the wrong format", output.stderr)
        self.assertIn("<stdin>", output.stderr)
        self.assertIn("line 3", output.stderr)

    def test_file_not_in_fpb_format(self):
        output = run(["--in", "fpb", DRUGS_SMI], expect_exit=True)
        self.assertIn("--in: invalid choice: 'fpb' (choose from 'fps', 'fps.gz', 'flush')", output.stderr)

    def test_file_does_not_exist(self):
        output = run(["--in", "fps", "/path/to/a/file/which/does/not/exist.fps"], expect_exit=True)
        self.assertIn("Fingerprint file", output.stderr)
        self.assertIn("exist.fps'", output.stderr)
        self.assertIn("does not exist", output.stderr)

    def test_fps_file_is_not_readable(self):
        dirname = get_tmpdir(self)
        filename = os.path.join(dirname, "not_readable.fps")
        open(filename, "w").close()
        os.chmod(filename, 0)
        output = run([filename], expect_exit=True)
        self.assertIn("Permission denied", output.stderr)
        self.assertIn("not_readable.fps'", output.stderr)

    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_input_flush(self):
        output = run([DRUGS_FLUSH])
        lines = output.stdout.splitlines(False)
        self.assertEqual(lines[0], b"#FPS1")
        self.assertEqual(lines[1], b"#num_bits=4096")
        self.assertEqual(lines[2],
          b"008000010000000000000000080000400000000090000000000100000010200401000000000100000000020"
          b"000000000000040000000000000100100000001000004000000030000000000000000000000020000000000"
          b"000220010002000000000000040000000010800000000040000020000000008000000000000000000020000"
          b"000000004000002000000000000000000000040000041000100000010000000000010000060000000000000"
          b"004810000010000212000812000020000008000000040000000000000000000000040001000000000001000"
          b"000000000040000000010010400000000000009000000100100000000081000284200006008000000001008"
          b"000400000000000000000000000000000000204800820000000000000000000000800020000000000000001"
          b"000004000000108004000000040040000004000000040000008008009400000800000011000000000000000"
          b"00000000000000200000080001000040100000010002000000410000000020200000c000202000009000004"
          b"000000009000008000000010000180000c0408000000000000200028c000800000000002000000880000000"
          b"000008000000100000080844000000004080040000004000000000000000800401000000002000100080400"
          b"0000004040000000200100000000400000000002100000000000000000000400000\tacetsali")
        
        self.assertEqual(lines[-1],
          b"020008020020000000000040300000100000000000000000000200200000000002001400000000000000000"
          b"080400008000040000080002000041280000000000000002000000010000018120000088200000080000000"
          b"200900000004000000000000000002400800000800000200000001000000000000400010020000200040000"
          b"000410008000000018300000004800082000050000000000000000100001001020200001009000000800002"
          b"000000000000020000000000000008000000100402000804080900100000002200004000820000820002000"
          b"000000000180000000002000001000000000000000000020000211000000030000200000400020800000010"
          b"000000042000808000000100000200010000001805000000020020000008080004014000000001000000040"
          b"100000000080000001004020000040000000000000020020004000000040000000000000200000000000000"
          b"408900000005001002008008000008000000000040240000000000800000000000c02008003000000020040"
          b"000802008400100800020000408010040040000000000000000000000000100000000000000000000020000"
          b"00000000000010000020410000000000400000100000002000000000a0000002000c0000002018000000400"
          b"0800000000000020001020000800000004000082000000300200100000000000000\tcaffeine")

    @unittest2.skipIf(has_chemfp_converters, "chemfp_converters is installed")
    def test_input_flush_no_converter(self):
        output = run([DRUGS_FLUSH], expect_exit=True)
        self.assertIn("ERROR: Cannot read from flush files because the chemfp_converter module is not available", 
                      output.stderr)
        
    def test_output_fps_directory_does_not_exist(self):
        output = run(["-o", "/this/directory/also/does/not/exist/asdfasdf/output.fps"], b"AAAA\tAndrew\n",
                     expect_exit=True)
        self.assertIn("The output directory", output.stderr)
        self.assertIn("does not exist", output.stderr)

    def test_output_fpb_directory_does_not_exist(self):
        output = run(["-o", "/this/directory/also/does/not/exist/asdfasdf/output.fpb"], b"AAAA\tAndrew\n",
                     expect_exit=True)
        self.assertIn("The output directory", output.stderr)
        self.assertIn("does not exist", output.stderr)
        self.assertIn("asdfasdf'", output.stderr)

    def test_output_directory_is_not_a_directory(self):
        filename = get_tmpfile(self, "not_a_directory")
        open(filename, "w").close()
        bad_filename = os.path.join(filename, "fred.fpb")
        output = run(["-o", bad_filename], b"AAAA\tAAA auto\n",
                     expect_exit=True)
        
        self.assertIn("The output directory", output.stderr)
        self.assertIn("is not actually a directory", output.stderr)
        
        
    def test_output_directory_does_not_exit_with_reorder(self):
        output = run(["--reorder", "-o", "/does/NOT/exist/QQFP/input.fps"], b"AAAA\tAndrew\n",
                     expect_exit=True)
        self.assertIn("The output directory", output.stderr)
        self.assertIn("does not exist", output.stderr)
        self.assertIn("QQFP'", output.stderr)


    # -o output.fps with various --out options
    def test_fps_output_with_default_format(self):
        filename = get_tmpfile(self, "output.fps")
        run(["-o", filename], b"FFFF\tHi\n")
        with open(filename, "rb") as f:
            self.assertEqual(f.read(6), b"#FPS1\n")

    def test_fps_output_with_fps_format(self):
        filename = get_tmpfile(self, "output.fps")
        output = run(["--out", "fps", "-o", filename], b"FFFF\tHi\n")
        with open(filename, "rb") as f:
            self.assertEqual(f.read(6), b"#FPS1\n")
            
    def test_fps_output_with_fps_gz_format(self):
        filename = get_tmpfile(self, "output.fps")
        run(["--out", "fps.gz", "-o", filename], b"FFFF\tHi\n")
        f = gzip.open(filename, "rb")
        self.assertEqual(f.read(6), b"#FPS1\n")
        f.close()

    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_fps_output_with_flush_format(self):
        filename = get_tmpfile(self, "output.fps")
        run(["--out", "flush", "-o", filename], b"FFFF0123\tHi\n")
        from chemfp_converters import flush
        with flush.open_flush(filename) as reader:
            self.assertEqual(reader.metadata.num_bytes, 4)
            self.assertEqual(next(reader), ("Hi", b"\xff\xff\x01\x23"))
            with self.assertRaisesRegexp(StopIteration, ""):
                next(reader)
            
    # -o output.fps.gz with various --out options
    def test_fps_gz_output_with_default_format(self):
        filename = get_tmpfile(self, "output.fps.gz")
        run(["-o", filename], b"FFFF\tHi\n")
        f = gzip.open(filename, "rb")
        self.assertEqual(f.read(6), b"#FPS1\n")
        f.close()

    def test_fps_gz_output_with_fps_format(self):
        filename = get_tmpfile(self, "output.fps.gz")
        run(["--out", "fps", "-o", filename], b"FFFF\tHi\n")
        with open(filename, "rb") as f:
            self.assertEqual(f.read(6), b"#FPS1\n")
            
    def test_fps_gz_output_with_fps_gz_format(self):
        filename = get_tmpfile(self, "output.fps.gz")
        run(["--out", "fps.gz", "-o", filename], b"FFFF\tHi\n")
        f = gzip.open(filename, "rb")
        self.assertEqual(f.read(6), b"#FPS1\n")
        f.close()

    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_fps_gz_output_with_flush_format(self):
        filename = get_tmpfile(self, "output.fps.gz")
        run(["--out", "flush", "-o", filename], b"FFFF0123\tHi\n")
        from chemfp_converters import flush
        with flush.open_flush(filename) as reader:
            self.assertEqual(reader.metadata.num_bytes, 4)
            self.assertEqual(next(reader), ("Hi", b"\xff\xff\x01\x23"))
            with self.assertRaisesRegexp(StopIteration, ""):
                next(reader)
    
    # -o output.flush without a filename
    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_flush_output(self):
        filename = get_tmpfile(self, "output.flush")
        run(["-o", filename], b"FFFF0123\tHi\n")
        from chemfp_converters import flush
        with flush.open_flush(filename) as reader:
            self.assertEqual(reader.metadata.num_bytes, 4)
            self.assertEqual(next(reader), ("Hi", b"\xff\xff\x01\x23"))
            with self.assertRaisesRegexp(StopIteration, ""):
                next(reader)
            
    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_flush_output_bad_size(self):
        filename = get_tmpfile(self, "output.flush")
        output = run(["-o", filename], b"FFFF\tHi\n", expect_exit=True)
        self.assertEqual(output.stderr,
                         "ERROR: Cannot open fingerprint writer: metadata num_bytes (2) must be a multiple of 4\n")

    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_flush_output_bad_size_reorder(self):
        filename = get_tmpfile(self, "output.flush")
        output = run(["-o", filename, "--reorder"], b"FFFF\tHi\n", expect_exit=True)
        self.assertEqual(output.stderr,
                         "ERROR: Cannot open fingerprint writer: metadata num_bytes (2) must be a multiple of 4\n")
        
    @unittest2.skipUnless(has_chemfp_converters, "chemfp_converters is not installed")
    def test_flush_output_gz(self):
        filename = get_tmpfile(self, "output.flush.gz")
        output = run(["-o", filename], b"FFFF0123\tHi\n", expect_exit=True)
        self.assertEqual(output.stderr, "ERROR: Compression of flush files is not supported\n")
            

FIRST_TWO_QUERY_LINES_UNSORTED = (
    b"102280000040a2240300048040020000210000b000c0c00000040000011420101e00100880a04017100e04102000000001a200029020c023000000800000a2100c9028080c14088002008a020a80021e00f0015000222040a880100140200004420400284008000201082000c0001cc000070180080d90020050048140040500\t22525101\n"
    b"10060046004082a403022e000000100400018c8000425a0001040084001020059e00408100c01041c00622180081c000012a030090207b0020811022040601200c22082804040000000021a02280061640b8c040400a3408408a9800800d04810f061028a10290220b908280611009600206014003091020289c04c300044100\t22525102\n"
    )

FIRST_TWO_QUERY_LINES_SORTED = (
    # The first three lines have popcounts of 16, 26, and 33
    b"00000004000000040000000000000000000000000000400000100000001000000000000000000000000a0000000000000000000010002100000000000000000008000800000000000000000000800000000000400000000000000000000000010004000000000000000000000000000000000000000000000000000000000000\t22525179\n"
    b"0000000000000224000000010000000000000080000000000000000000000000100000000000000100000000000000000100000000204003000000000000000008000800040400000000800200000000000000400000000008001000000000000004000000000000000000000000280000000000000000000000008100000000\t22525187\n"
    )
LAST_SORTED_LINE = (
    # The last two lines have popcounts ... 337, 342
    b"182e01c720f002ec1b0e2e0242c34501a40704f018785a4041070080203400059e01640021c01061e00f073830c55401010a035294605f3d21c150b6040682285c702c3a27440c078000a1a202c88688f0dd414408223568cb18d80140dd2185571e3038e10576c20bf08a4241506960010711d00b0fd122389e04c301124804\t22525150\n"
)

class TestFPSOrderings(unittest2.TestCase):
    def test_stdin_to_stdout(self):
        output = run("", b"abcd\tAndrew\n")
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(b"\nabcd\tAndrew\n", output.stdout)

    def test_stdin_default_preserves_order(self):
        output = run("", b"abcd\tAndrew\n0000\tDalke\n")
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(b"\nabcd\tAndrew\n0000\tDalke\n", output.stdout)

    def test_stdin_specify_preserve_order(self):
        output = run("--preserve-order", b"abcd\tAndrew\n0000\tDalke\n")
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(b"\nabcd\tAndrew\n0000\tDalke\n", output.stdout)

    def test_stdin_specify_reorder(self):
        output = run("--reorder", b"abcd\tAndrew\n0000\tDalke\n")
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(b"\n0000\tDalke\nabcd\tAndrew\n", output.stdout)


    def test_fps_default_preserves_order(self):
        output = run([QUERIES_FPS], b"abcd\tAndrew\n0000\tDalke\n")
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(FIRST_TWO_QUERY_LINES_UNSORTED, output.stdout)

    def test_fps_specify_preserve_order(self):
        output = run(["--preserve-order", QUERIES_FPS])
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(FIRST_TWO_QUERY_LINES_UNSORTED, output.stdout)

    def test_fps_specify_reorder(self):
        output = run(["--reorder", QUERIES_FPS])
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertNotIn(FIRST_TWO_QUERY_LINES_UNSORTED, output.stdout)
        self.assertIn(FIRST_TWO_QUERY_LINES_SORTED, output.stdout)
        self.assertTrue(output.stdout.endswith(LAST_SORTED_LINE), output.stdout)


FIRST_UNSORTED_RECORD = (
    "22525101", hex_decode("102280000040a2240300048040020000210000b000c0c00000040000011420101e00100880a04017100e04102000000001a200029020c023000000800000a2100c9028080c14088002008a020a80021e00f0015000222040a880100140200004420400284008000201082000c0001cc000070180080d90020050048140040500"))

FIRST_SORTED_RECORD = (
    "22525179", hex_decode("00000004000000040000000000000000000000000000400000100000001000000000000000000000000a0000000000000000000010002100000000000000000008000800000000000000000000800000000000400000000000000000000000010004000000000000000000000000000000000000000000000000000000000000"))

LAST_SORTED_RECORD = (
    "22525150", hex_decode("182e01c720f002ec1b0e2e0242c34501a40704f018785a4041070080203400059e01640021c01061e00f073830c55401010a035294605f3d21c150b6040682285c702c3a27440c078000a1a202c88688f0dd414408223568cb18d80140dd2185571e3038e10576c20bf08a4241506960010711d00b0fd122389e04c301124804"))
    

def _create_file(dirname, filename, data):
    filename = os.path.join(dirname, filename)
    with open(filename, "wb") as f:
        f.write(data)
    return filename

class TestMerge(unittest2.TestCase):
    def test_simple_merge(self):
        dirname = get_tmpdir(self)
        filenames = []
        A = filenames.append
        A(_create_file(dirname, "input1.fps", b"0000\tfirst\n0101\tthird\n"))
        A(_create_file(dirname, "input2.fps", b"1000\tsecond\n0103\tfourth\n"))
        A(_create_file(dirname, "input3.fps", b"0aaa\tpenultimate\nfffe\tlast\n"))
        A(_create_file(dirname, "empty.fps", b""))
        A(_create_file(dirname, "input4.fps", b"ABCD\tfifth\nABCF\tsixth\n"))
        output = run(["--merge"] + filenames)

    def test_unsorted_merge(self):
        dirname = get_tmpdir(self)
        filenames = []
        A = filenames.append
        # The first file is out-of-order.
        # All I promise in that case is that 'third' will come before 'first' in the output.
        A(_create_file(dirname, "input1.fps", b"0101\tthird\n0000\tfirst\n"))
        A(_create_file(dirname, "input2.fps", b"1000\tsecond\n0103\tfourth\n"))
        output = run(["--merge"] + filenames)
        pat = re.compile(b"second.*third.*first", re.DOTALL)
        self.assertTrue(pat.search(output.stdout), output.stdout)

        # Double-check that the default does the first then the second
        output = run(filenames)
        pat = re.compile(b"third.*first.*second.*fourth", re.DOTALL)
        self.assertTrue(pat.search(output.stdout), output.stdout)

        # and that ordered gives 
        output = run(["--reorder"] + filenames)
        pat = re.compile(b"first.*second.*third.*fourth", re.DOTALL)
        self.assertTrue(pat.search(output.stdout), output.stdout)


class TestProgress(unittest2.TestCase):
    def test_progress_with_stdin(self):
        output = run(["--show-progress"], QUERIES_FPS_BYTES)
        # Make sure the expected output is unchanged
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(FIRST_TWO_QUERY_LINES_UNSORTED, output.stdout)
        # And that it also has processing information
        self.assertIn("Done. Processed 100 records from stdin.\n", output.stderr)

    def test_progress_with_one_file(self):
        output = run(["--show-progress", QUERIES_FPS])
        # Make sure the expected output is unchanged
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(FIRST_TWO_QUERY_LINES_UNSORTED, output.stdout)
        # And that it also has processing information
        self.assertIn("Done. Processed 100 records from 1 file.\n", output.stderr)

    def test_progress_with_the_same_file_twice(self):
        output = run(["--show-progress", QUERIES_FPS, QUERIES_FPS])
        # Make sure the expected output is unchanged
        self.assertIn(b"#FPS1\n", output.stdout)
        self.assertIn(FIRST_TWO_QUERY_LINES_UNSORTED, output.stdout)
        # And that it also has processing information
        self.assertIn("Done. Processed 200 records from 2 files.\n", output.stderr)

    def test_progress_with_51000_records(self):
        output = run(["--show-progress"] + [QUERIES_FPS] * 501)
        self.assertIn("\r300 records. File 3/501: ", output.stderr)
        self.assertIn("\r400 records. File 4/501: ", output.stderr)
        self.assertIn("\rDone. Processed 50100 records from 501 files.\n", output.stderr)

class TestCompatibilityIssues(unittest2.TestCase):
    def test_incompatible_num_bits_sequential(self):
        output = run([QUERIES_FPS, INCOMPATIBLE_NUM_BITS], expect_exit=True)
        self.assertIn("has a num_bits of 1024, which is not compatible with", output.stderr)
        self.assertIn("which has a num_bits of 1021", output.stderr)

    def test_incompatible_num_bits_merge(self):
        output = run(["--merge", QUERIES_FPS, INCOMPATIBLE_NUM_BITS], expect_exit=True)
        self.assertIn("has a num_bits of 1024, which is not compatible with", output.stderr)
        self.assertIn("which has a num_bits of 1021", output.stderr)
        
    def test_incompatible_num_bytes_sequential(self):
        output = run([QUERIES_FPS, INCOMPATIBLE_NUM_BYTES], expect_exit=True)
        self.assertIn("has a num_bits of 992, which is not compatible with", output.stderr)
        self.assertIn("which has a num_bits of 1021", output.stderr)

    def test_incompatible_num_bytes_merge(self):
        output = run(["--merge", QUERIES_FPS, INCOMPATIBLE_NUM_BYTES], expect_exit=True)
        self.assertIn("has a num_bits of 992, which is not compatible with", output.stderr)
        self.assertIn("which has a num_bits of 1021", output.stderr)
    
    def test_incompatible_type_sequential(self):
        output = run([QUERIES_FPS, INCOMPATIBLE_TYPE], expect_exit=True)
        self.assertIn("has a type of 'OpenBabel-FP2/2', which is not compatible with", output.stderr)
        self.assertIn("which has a type of 'OpenBabel-FP2/1'", output.stderr)

    def test_incompatible_type_merge(self):
        output = run(["--merge", QUERIES_FPS, INCOMPATIBLE_TYPE], expect_exit=True)
        self.assertIn("has a type of 'OpenBabel-FP2/2', which is not compatible with", output.stderr)
        self.assertIn("which has a type of 'OpenBabel-FP2/1'", output.stderr)
        
    def test_incompatible_software_sequential(self):
        output = run([QUERIES_FPS, INCOMPATIBLE_SOFTWARE], expect_exit=False)
        # toolkit mismatch does not generate a warning
        self.assertEqual("", output.stderr)
        # Sequential output grabs the first software.
        self.assertIn(b"#software=OpenBabel/2.2.0\n", output.stdout)
        
    def test_incompatible_software_merge(self):
        output = run(["--merge", QUERIES_FPS, INCOMPATIBLE_SOFTWARE], expect_exit=False)
        # toolkit mismatch does not generate a warning
        self.assertEqual("", output.stderr)
        # Merge output can compare all of the headers at once, and realize that these
        # are not compatibile.
        self.assertNotIn(b"#software", output.stdout)
        
    def test_incompatible_aromaticity_sequential(self):
        output = run([INCOMPATIBLE_AROMATICITY1, INCOMPATIBLE_AROMATICITY2], expect_exit=False)
        self.assertIn("WARNING: ", output.stderr)
        self.assertIn("has a aromaticity of 'cheese', which is not compatible with ", output.stderr)
        self.assertIn("which has a aromaticity of 'stinky'", output.stderr)
        
    def test_incompatible_aromaticity_merge(self):
        output = run(["--merge", INCOMPATIBLE_AROMATICITY1, INCOMPATIBLE_AROMATICITY2], expect_exit=False)
        self.assertIn("WARNING: ", output.stderr)
        self.assertIn("has a aromaticity of 'cheese', which is not compatible with ", output.stderr)
        self.assertIn("which has a aromaticity of 'stinky'", output.stderr)

    def test_incompatible_aromaticity_generates_only_one_warning(self):
        output = run([INCOMPATIBLE_AROMATICITY1, INCOMPATIBLE_AROMATICITY2]*4, expect_exit=False)
        self.assertEqual(output.stderr.count("WARNING"), 1, output.stderr)
        
        
class TestFileErrors(unittest2.TestCase):
    def test_cannot_open_output_fps(self):
        filename = get_tmpfile(self, "not_writeable.fps")
        open(filename, "w").close()
        os.chmod(filename, 0)
        output = run(["-o", filename],
                     b"ABCABC\tAndrew\n543210\tDalke\n",
                     expect_exit=True)
        self.assertIn("Unable to open fingerprint writer: ", output.stderr)
        self.assertIn("not_writeable.fps'", output.stderr)

if __name__ == "__main__":
    unittest2.main()
    
