#!/usr/bin/python3

import sys, unittest

RE_REPOSITORY = "mk51fx2500re"
if RE_REPOSITORY not in sys.path:
    sys.path.insert(0, RE_REPOSITORY)

import emulator
from calculator import *
from keys import *
from program import Program


class TestCode(unittest.TestCase):
    def setUp(self):
        self.emulator = emulator.Emulator(Program.from_file())

    def press(self, keys):
        execute_seq(self.emulator, keys)

    def test_pi(self):
        self.emulator.call(0x0d4)
        self.assertEqual(decode_num(self.emulator.regs[0]),
                         Decimal("3.14159265"))


if __name__ == "__main__":
    unittest.main()
