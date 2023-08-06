from unittest import TestCase

from qcodes.instrument.signalchain import addToSignalChain
from qcodes.instrument.signalchain import removeFromSignalChain
from qcodes.tests.instrument_mocks import DummyInstrument


dummy = DummyInstrument(name='dummy')
dummy.add_parameter('param_10',
                    set_cmd=lambda x: x,
                    get_cmd=lambda : 10)


class TestAdder(TestCase):

    def test_input_rejection(self):
