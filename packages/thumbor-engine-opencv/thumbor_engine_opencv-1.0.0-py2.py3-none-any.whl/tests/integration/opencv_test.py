from integration_tests import EngineCase
from integration_tests.urls_helpers import single_dataset


class OpenCVTest(EngineCase):
    engine = 'thumbor_engine_opencv'

    def test_single_params(self):
        single_dataset(self.retrieve, with_gif=False)
