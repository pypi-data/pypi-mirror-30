# a driver to interact with the foobar simulated instrument

from qcodes.instrument.visa import VisaInstrument


class FooBar(VisaInstrument):

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, **kwargs)

        self.connect_message()

        # self.visa_handle.write_termination = self._terminator
