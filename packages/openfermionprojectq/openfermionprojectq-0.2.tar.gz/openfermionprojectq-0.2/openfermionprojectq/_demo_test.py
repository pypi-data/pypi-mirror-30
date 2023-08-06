#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Tests the code in the examples directory of the git repo."""
import nbformat
import os
import subprocess
import sys
import tempfile
import unittest


class ExampleTest(unittest.TestCase):

    def setUp(self):
        this_directory = os.path.realpath(__file__)
        string_length = len(this_directory)
        directory = this_directory[:(string_length - 33)] + '/examples/'
        demo_name = 'openfermionprojectq_demo.ipynb'
        self.path = directory + demo_name

    def test_demo(self):
        """Execute a notebook via nbconvert and collect output."""

        # Determine if python 2 or 3 is being used.
        major_version, minor_version = sys.version_info[:2]
        if major_version == 2 or minor_version == 6:
            version = str(major_version)

            # Run ipython notebook.
            with tempfile.NamedTemporaryFile(suffix='.ipynb') as output_file:
                args = ['jupyter',
                        'nbconvert',
                        '--to',
                        'notebook',
                        '--execute',
                        '--ExecutePreprocessor.timeout=600',
                        '--ExecutePreprocessor.kernel_name=python{}'.format(
                            version),
                        '--output',
                        output_file.name,
                        self.path]
                subprocess.check_call(args)
                output_file.seek(0)
                nb = nbformat.read(output_file, nbformat.current_nbformat)

            # Parse output and make sure there are no errors.
            errors = [output for cell in nb.cells if "outputs" in cell for
                      output in cell["outputs"] if
                      output.output_type == "error"]
        else:
            errors = []
        self.assertEqual(errors, [])
