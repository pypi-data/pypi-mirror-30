# pylint: disable=missing-docstring
from resolwe.test import tag_process
from resolwe_bio.utils.test import BioProcessTestCase


class GenomeBrowserProcessorTestCase(BioProcessTestCase):

    @tag_process('igv')
    def test_igv_bam(self):
        with self.preparation_stage():
            bam = self.prepare_bam()

            inputs = {
                'src': 'reads.bam',
                'species': 'Homo sapiens',
                'build': 'hg19'
            }
            bam1 = self.run_process('upload-bam', inputs)

            inputs = {
                'genomeid': 'hg19',
                'bam': [bam.id, bam1.id],
                'locus': 'chr7:79439229-79481604'
            }

        igv_session = self.run_process('igv', inputs)

        # remove changing lines from the output
        def filter_resource(line):
            if b'<Resource path=' in line:
                return True

        self.assertFile(igv_session, 'igv_file', 'igv_session_bam.xml', file_filter=filter_resource)
