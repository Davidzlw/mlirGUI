from ui import UI


class SSA:
    def __init__(self):
        self.id = 0


class MLIR:
    def __init__(self):
        self.locs = []
        self.module = ""
        self.func = ""
        self.ret = ""


    def parse_line(self, line):

        line = line.strip()
        if line.startswith("#loc"):
            self.locs.append(line)
        elif line.startswith("module"):
            self.module = line
        elif line.startswith("func"):
            self.func = line
        elif line.startswith("return"):
            self.ret = line
        elif '%' in line:
            id = int(line[1: line.find('=')])
            op = line.split('"')[1]
            bufferLoc = line.find("bufferLoc")
            for i in range(line.count("bufferLoc")):
                pass
            print(id, op)



    def read_mlir(self, path):
        with open(path) as f:
            for line in f.readlines():
                self.parse_line(line)


class Record:
    def __init__(self, enq_id, start, end, size, addr):
        self.enq_id = enq_id
        self.start = start
        self.end = end
        self.size = size
        self.addr = addr


class Fragment:
    def __init__(self, id, addr, size):
        self.id = id
        self.addr = addr
        self.size = size


class State:
    def __init__(self, time):
        self.time = time
        self.frags = []


class L2_Recorder:
    def __init__(self):
        self.states = []
        self.recs = []

    def read_file(self):
        with open("./data/record.txt") as f:
            rec = f.readlines()
            for line in rec:
                if len(line.split()) == 5:
                    # print(line.split())
                    enq_id, start, end, size, addr = map(int, line.split())
                    self.recs.append(Record(enq_id, start, end, size, addr))

    def show_records(self):
        print(len(self.recs))
        for rec in self.recs:
            print(rec.enq_id, rec.start, rec.end, rec.size, rec.addr)

    def cal_states(self):
        max_time = max([rec.end for rec in self.recs])
        for t in range(max_time + 1):
            self.states.append(State(t))
        for rec in self.recs:
            for t in range(rec.start, rec.end):
                self.states[t].frags.append(Fragment(rec.enq_id, rec.addr, rec.size))

    def check_legal(self):
        print("time: ", len(self.states))
        for state in self.states:
            state.frags.sort(key=lambda x: x.addr)
            overlap = False
            pre_addr = 0
            for frag in state.frags:
                if frag.addr < pre_addr:
                    overlap = True
                    break
                pre_addr = frag.addr + frag.size
            if overlap:
                print("ERROR: overlap")
                return
        print("SUCC: check pass!")


if __name__ == '__main__':
    # mlir = MLIR()
    # mlir.read_mlir("./data/xba_buffer_schedule.mlir")

    L2 = L2_Recorder()
    L2.read_file()
    # L2.show_records()
    L2.cal_states()
    # L2.check_legal()
    ui = UI(L2)



