# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import gzip

from fastr.datatypes import URLType


class NiftiImageFileCompressed(URLType):
    description = 'Compressed Nifti Image File format'
    extension = 'nii.gz'

    def checksum(self):
        """
        Return the checksum of this URL type

        :return: checksum string
        :rtype: str
        """
        contents = self.content(self.parsed_value)
        hasher = hashlib.new('md5')

        for path in contents:
            with gzip.open(path, 'rb') as file_handle:
                while True:
                    data = file_handle.read(32768)
                    if not data:
                        break
                    hasher.update(data)
        return hasher.hexdigest()
