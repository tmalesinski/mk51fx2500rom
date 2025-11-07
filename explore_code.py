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

class KeyEntry:
    def __init__(self, desc):
        self.desc = desc

    def describe(self, em):
        if isinstance(self.desc, str):
            return self.desc
        return self.desc(em)

key_entries = {
    0x2dd: KeyEntry("X<->Y"),
    0x2df: KeyEntry("X<->M"),
    0x2cb: KeyEntry("sum x"),
    0x34d: KeyEntry(lambda em: f"digit {em.regs[2][0]}"),
    0x3e4: KeyEntry("AC"),
    0x3e6: KeyEntry("MAC/SAC"),
    0x3e7: KeyEntry("AC (stat)"),
    0x2b4: KeyEntry("log/ln"),
    0x2b6: KeyEntry("10^x/e^x"),
    0x2c8: KeyEntry("sqrt"),
    0x2ca: KeyEntry("x^2"),
    0x333: KeyEntry("C"),
    0x30d: KeyEntry(")]"),
    0x318: KeyEntry("avg x"),
    0x30f: KeyEntry("[("),
    0x31a: KeyEntry("n (stat)"),
    0x345: KeyEntry("."),
    0x3df: KeyEntry("inv"),
    0x2ec: KeyEntry("1/x"),
    0x2ee: KeyEntry("n!"),
    0x34b: KeyEntry("sum x^2"),
    0x36c: KeyEntry("exp/pi"),
    0x36d: KeyEntry("pi"),
    0x2de: KeyEntry("M in"),
    0x33b: KeyEntry("??? std"),
    0x2bc: KeyEntry("dms"),
    0x3dd: KeyEntry("MODE"),
    0x354: KeyEntry("+/-"),
    0x2dc: KeyEntry("MR"),
    0x296: KeyEntry(
        lambda em: ["pow", "root", "/", "*", "-", "+"][em.regs[2][14] - 2]),
    0x221: KeyEntry("trig"),
    0x187: KeyEntry("inv trig"),
    0x2ac: KeyEntry(lambda em: "=" if em.regs[2][14] == 5 else "M+"),
    0x2ae: KeyEntry("ins/del (sd)"),
    0x319: KeyEntry("MC"),
    0x3dc: KeyEntry("INV"),
    0x3d8: KeyEntry("F1"),
    0x3df: KeyEntry("F2"),
}

def describe_key_entries():
    print("   ",
          " ".join(f"{prefix:9s}"
                   for prefix in ["", "INV", "F1", "F2",
                                  "SD", "SD INV", "SD F2"]))
    for row in range(8):
        for col in range(1, 6):
            key = row * 10 + col
            ent = []
            for prefix in [[], [KINV], [KF1], [KF2], [KINV, KMODE],
                           [KINV, KMODE, KINV], [KINV, KMODE, KF2]]:
                emul = create_emulator()
                execute_seq(emul, prefix, print_disp=False)
                emul.keycode = 0
                emul.until(0x3c5)
                emul.keycode = key
                for i in range(200):
                    emul.step()
                    if emul.pc in key_entries:
                        ent.append(key_entries[emul.pc].describe(emul))
                        break
                else:
                    ent.append("???")
            estr = " ".join(f"{d:9s}" for d in ent)
            print(f"{key:-2d}: {estr}")

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
