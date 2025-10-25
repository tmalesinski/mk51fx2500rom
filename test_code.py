#!/usr/bin/python3

import sys, unittest

RE_REPOSITORY = "mk51fx2500re"
if RE_REPOSITORY not in sys.path:
    sys.path.insert(0, RE_REPOSITORY)

import emulator
from calculator import *
from keys import *
from program import Program
from bits import bit

class TestCode(unittest.TestCase):
    def setUp(self):
        self.emulator = emulator.Emulator(Program.from_file())

    def press(self, keys):
        execute_seq(self.emulator, keys, print_disp=False)

    def displayed_num(self):
        return get_display_num(self.emulator)

    def regstr(self, r):
        return "".join(f"{self.emulator.regs[r][i]:x}" for i in range(14))

    def test_pi(self):
        self.emulator.call(0x0d4)
        self.assertEqual(decode_num(self.emulator.regs[0]),
                         Decimal("3.14159265"))

    def test_mode_state(self):
        def mode():
            return self.emulator.regs[4][14] & 3

        self.assertEqual(mode(), 0)
        self.press([KMODE])
        self.assertEqual(mode(), 1)
        self.press([KMODE])
        self.assertEqual(mode(), 2)
        self.press([KMODE])
        self.assertEqual(mode(), 0)

    def test_fx2500_inv_fun(self):
        # INV sqrt is a square function.
        self.press([K4, 61, KSQRT])
        self.assertEqual(self.displayed_num(), 16)

    def test_fx2500_inv_digit(self):
        # INV digit just enters the digit.
        self.press([K4, 61, K8])
        self.assertEqual(self.displayed_num(), 48)

    def test_fx48_f2_digit(self):
        # F2 8 is square.
        self.press([K4, 51, K8])
        self.assertEqual(self.displayed_num(), 16)

    def test_fx48_f1_digit(self):
        # F1 8 is square root.
        self.press([K4, 41, K8])
        self.assertEqual(self.displayed_num(), 2)

    def test_fx2500_inv_state(self):
        def state():
            return bit(self.emulator.regs[3][14], 3)

        self.assertEqual(state(), 0)
        self.press([61])
        self.assertEqual(state(), 1)
        self.press([61])
        self.assertEqual(state(), 0)

    def test_fx48_f1_state(self):
        def state():
            return bit(self.emulator.regs[3][14], 0)

        self.assertEqual(state(), 0)
        self.press([41])
        self.assertEqual(state(), 1)
        self.press([41])
        self.assertEqual(state(), 0)

    def test_fx48_f2_state(self):
        def state():
            return bit(self.emulator.regs[3][14], 1)

        self.assertEqual(state(), 0)
        self.press([51])
        self.assertEqual(state(), 1)
        self.press([51])
        self.assertEqual(state(), 0)

    def test_sd_state(self):
        def state():
            return bit(self.emulator.regs[4][14], 3)

        self.assertEqual(state(), 0)
        self.press([61, KMODE])
        self.assertEqual(state(), 1)
        self.press([61, KMODE])
        self.assertEqual(state(), 0)

    def test_bin_op_nums(self):
        def opnum():
            return self.emulator.regs[7][14]

        self.press([KC, K1, KPLUS])
        self.assertEqual(opnum(), 7)
        self.press([KC, K1, KMINUS])
        self.assertEqual(opnum(), 6)
        self.press([KC, K1, KMUL])
        self.assertEqual(opnum(), 5)
        self.press([KC, K1, KDIV])
        self.assertEqual(opnum(), 4)
        self.press([KC, K1, KPOW])
        self.assertEqual(opnum(), 3)
        self.press([KC, K1, 61, KPOW])  # root
        self.assertEqual(opnum(), 2)

    # def test_swap_reg(self):
    #     self.press([K4, K5, K6])
    #     for i in range(8):
    #         print(self.regstr(i))
    #     print()
    #     self.press([KSWAP])
    #     for i in range(8):
    #         print(self.regstr(i))


    # def test_fx2500_inv_state(self):
    #     for i in range(5):
    #         print("".join(str(self.emulator.regs[j][14]) for j in range(8)))
    #         self.press([61])


if __name__ == "__main__":
    unittest.main()
