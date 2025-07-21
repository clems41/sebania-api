import os

from django.conf import settings

from sebania.tests.SebaniaTestCase import SebaniaTestCase


class TaskTestcase(SebaniaTestCase):
    data_directory = os.path.abspath(os.path.join(settings.FIXTURE_DIRS[0].as_posix(), "../../thomas_ai/tests/data/"))