import sys

RE_REPOSITORY = "mk51fx2500re"
if RE_REPOSITORY not in sys.path:
    sys.path.insert(0, RE_REPOSITORY)

from emulator import Emulator
from keys import *
from program import Program
from analyze import decode_instr
from calculator import execute_seq, decode_num

def create_emulator():
    return Emulator(Program.from_file())

def reg_str(r):
    return "".join(f"{d:x}" for d in reversed(r))

def test_pi():
    e = create_emulator()
    e.call(0x0d4)
    return decode_num(e.regs[0])

def test_pi180():
    e = create_emulator()
    e.call(0x277)
    return decode_num(e.regs[1])

def test_ln10():
    e = create_emulator()
    e.call(0x26c)
    return decode_num(e.regs[1])

def test_ln_cordic():
    res = []
    for i in range(15):
        e = create_emulator()
        e.regs[0][0] = i
        e.call(0x028)
        res.append(decode_num(e.regs[1]))
    return res

def test_tan_cordic():
    res = []
    for i in range(15):
        e = create_emulator()
        e.regs[0][0] = i
        e.call(0x1)
        res.append(decode_num(e.regs[1]))
    return res

def get_key_trace(e, key):
    e.keycode = 0
    e.until(0x3c5)
    e.keycode = key
    trace = []
    for i in range(200):
        e.step()
        trace.append(e.pc)
    return trace

def find_entry(key_trace, program):
    key_acc = False
    entry = key_trace[0]
    for a in key_trace:
        if a in [0x3ad, 0x380]: break
        if key_acc:
            entry = a
        instr = decode_instr(a, program.get(a))
        key_acc = False
        mod = False
        for m in ["ADD", "AND"]:
            if instr.startswith(m):
                mod = True
        if not mod:
            for p in ["R2 [14]", "R2 [13]", "R3 [14]"]:
                if p in instr:
                    key_acc = True
                    break
    return entry

def get_key_entries():
    traces = []
    for row in range(8):
        for col in range(1, 6):
            key = row * 10 + col
            e = []
            for prefix in [[], [KF], [41], [61], [KF, KMODE]]:
                emul = create_emulator()
                execute_seq(emul, prefix, print_disp=False)
                trace = get_key_trace(emul, key)
                e.append(find_entry(trace, emul.prog))
            estr = " ".join(f"{a:03x}" for a in e)
            print(f"{key}: {estr}")

def display(e):
    num = ""
    ind = ""
    for i in range(9):
        d = e.regs[0][12 - i]
        if d <= 9:
            num += str(d)
        elif d == 13:
            num += "E"
        elif d == 14:
            num += "-"
        else:
            num += " "
        p = e.regs[1][12 - i]
        if p & 8:
            num += "."
        ind += str(i) if p & 4 else "_"
    return f"|{num}| {ind}"

def get_disp_after_keys():
    for row in range(8):
        for col_code in range(1, 15):
            if col_code >= 4 and col_code & 3 != 0: continue
            e = create_emulator()
            e.add_break(0x3c5)
            e.cont()
            e.del_all_breaks()
            e.keycode = (row, col_code)
            e.add_break(0x3c3)
            e.cont()
            print(row, f"{col_code:x}", display(e))
