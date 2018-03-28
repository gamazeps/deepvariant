# Copyright 2018 Google Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Tests for deepvariant.util.io.bed."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from absl.testing import absltest
from absl.testing import parameterized

from deepvariant.util.io import bed
from deepvariant.util.genomics import bed_pb2
from deepvariant.util import test_utils


class BedReaderTests(parameterized.TestCase):

  @parameterized.parameters('test_regions.bed', 'test_regions.bed.gz',
                            'test_regions.bed.tfrecord',
                            'test_regions.bed.tfrecord.gz')
  def test_iterate_bed_reader(self, bed_filename):
    bed_path = test_utils.genomics_core_testdata(bed_filename)
    expected = [('chr1', 10, 20), ('chr1', 100, 200)]
    with bed.BedReader(bed_path) as reader:
      records = list(reader.iterate())
    self.assertLen(records, 2)
    self.assertEqual([(r.reference_name, r.start, r.end) for r in records],
                     expected)

  @parameterized.parameters('test_regions.bed', 'test_regions.bed.gz')
  def test_native_bed_header(self, bed_filename):
    bed_path = test_utils.genomics_core_testdata(bed_filename)
    with bed.BedReader(bed_path) as reader:
      self.assertEqual(reader.header.num_fields, 12)
    with bed.NativeBedReader(bed_path) as native_reader:
      self.assertEqual(native_reader.header.num_fields, 12)


class BedWriterTests(parameterized.TestCase):
  """Tests for BedWriter."""

  def setUp(self):
    self.records = [
        bed_pb2.BedRecord(
            reference_name='chr1', start=30, end=40, name='first', score=55.5),
        bed_pb2.BedRecord(
            reference_name='chr2', start=32, end=38, name='second', score=0),
        bed_pb2.BedRecord(
            reference_name='chr3', start=40, end=50, name='third', score=99),
    ]

  @parameterized.parameters('test_raw.bed', 'test_zipped.bed.gz',
                            'test_raw.tfrecord', 'test_zipped.tfrecord.gz')
  def test_roundtrip_writer(self, filename):
    output_path = test_utils.test_tmpfile(filename)
    with bed.BedWriter(
        output_path, header=bed_pb2.BedHeader(num_fields=5)) as writer:
      for record in self.records:
        writer.write(record)

    with bed.BedReader(output_path) as reader:
      v2_records = list(reader.iterate())

    self.assertEqual(self.records, v2_records)


if __name__ == '__main__':
  absltest.main()