from ui import UI
import csv

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
    def __init__(self, ctx, start, dur, deq, cname, cid, name, node, group, send, wait, addr, size):
        self.ctx = int(ctx)
        self.start = int(start)
        self.dur = int(dur)
        self.deq = int(deq)
        self.cname = cname
        self.cid = int(cid) if cid else -1
        self.name = name
        self.node = node
        self.group = group
        self.send = send
        self.wait = wait
        self.addr = int(addr)
        self.size = int(size)
        self.ifmLoc = ""
        self.ofmLoc = ""
        self.set_buffer_loc()
        # self.attrs = attrs

    def set_buffer_loc(self):
        if self.group == "Workload":
            self.ifmLoc = "L1"
            self.ofmLoc = "L1"
        else:
            self.ifmLoc = self.group.split(">>")[0]
            self.ofmLoc = self.group.split(">>")[1]


class Fragment:
    def __init__(self, node, buffer, cid, addr, size):
        self.node = node
        self.buffer = buffer
        self.cid = cid
        self.addr = addr
        self.size = size


class Task:
    def __init__(self, node, stream, start, end):
        self.node = node
        self.stream = stream
        self.start = start
        self.end = end


class State:
    def __init__(self, time):
        self.time = time
        self.L1_frags = []
        self.L2_frags = []
        self.tasks = []


class CostRecorder:
    def __init__(self):
        self.states = []
        self.recs = []
        self.time_stamp = []
        self.time_map = {}

    def init(self):
        self.states = []
        self.recs = []
        self.time_stamp = []
        self.time_map = {}

    def read_file(self, path):
        with open(path, newline='') as f:
            spamreader = csv.reader(f, delimiter=',', quotechar='|')
            for row in spamreader:
                if len(row) > 13 and row[0] != "ctx":
                    record = Record(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                    row[7], row[8], row[9], row[10], row[11], row[12])
                    self.recs.append(record)

    def show_records(self):
        print("total records num: ", len(self.recs))
        cnt = 10  # show num
        for rec in self.recs:
            print(rec.node, self.time_map[rec.start], self.time_map[rec.deq], rec.ofmLoc, rec.cid, rec.addr, rec.size)
            cnt -= 1
            if cnt == 0:
                break

    def cal_time_map(self):
        time_set = set()
        for rec in self.recs:
            time_set.add(rec.start)
            time_set.add(rec.start + rec.dur)
            time_set.add(rec.deq)
        self.time_stamp = sorted(list(time_set))

        for i in range(len(self.time_stamp)):
            self.time_map[self.time_stamp[i]] = i
        print("total stamp num: ", len(self.time_stamp))

    def cal_states(self):
        max_time = max([rec.deq for rec in self.recs])
        max_stamp = max([self.time_map[rec.deq] for rec in self.recs])
        for t in range(max_stamp + 1):
            self.states.append(State(t))

        for rec in self.recs:
            if rec.name == "View":
                continue
            for t in range(self.time_map[rec.start], self.time_map[rec.deq]):
                new_frag = Fragment(rec.node, rec.ofmLoc, rec.cid, rec.addr, rec.size)
                if new_frag.buffer == "L1" and new_frag.cid == 0:
                    self.states[t].L1_frags.append(new_frag)
                elif new_frag.buffer == "L2" and new_frag.cid <= 0:
                    self.states[t].L2_frags.append(new_frag)
            for t in range(self.time_map[rec.start], self.time_map[rec.start + rec.dur]):
                if rec.cid <= 0:
                    new_task = Task(rec.node, rec.group, rec.start, rec.start + rec.dur)
                    self.states[t].tasks.append(new_task)

    def check_legal(self):
        print("checking addr overlap...")

        def find_overlap(frags):
            pre_addr = 0
            for frag in frags:
                if frag.addr < pre_addr:
                    print("ERROR: overlap")
                    return True
                pre_addr = frag.addr + frag.size
            return False

        for state in self.states:
            l1_frags = sorted([frag for frag in state.L1_frags], key=lambda x: x.addr)
            l2_frags = sorted([frag for frag in state.L2_frags], key=lambda x: x.addr)
            if find_overlap(l1_frags) or find_overlap(l2_frags):
                return
        print("SUCC: check pass!")

    def run(self, path):
        self.init()
        self.read_file(path)
        self.cal_time_map()
        self.cal_states()
        self.check_legal()
        # self.show_records()


if __name__ == '__main__':

    recorder = CostRecorder()
    # recorder.run("../data/avm_front_test.csv")
    ui = UI(recorder)



