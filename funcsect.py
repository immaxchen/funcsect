import argparse


def indent(line):
    return len(line) - len(line.lstrip())


def checks(line):
    isempt = line.strip() == ""
    iscomt = line.strip().startswith("#")
    isdeco = line.strip().startswith("@")
    isfunc = line.strip().startswith("def ")
    isargs = line.strip().startswith(")")
    return isempt, iscomt, isdeco, isfunc, isargs


def funcsect(inputfile, outputfile, marker=None, masker=None):
    if marker is None: marker = lambda lines: False
    if masker is None: masker = lambda lines: False

    def flush_comt():
        for s in comt_buffer: print(s, end="", file=outputfile)
        comt_buffer.clear()

    def flush_func():
        if marker(func_buffer): print(" " * indent_func + "# Func Start #", file=outputfile)
        for s in comt_buffer: print(s, end="", file=outputfile)
        for s in deco_buffer: print(s, end="", file=outputfile)
        for s in func_buffer: print(s, end="", file=outputfile)
        if marker(func_buffer): print(" " * indent_func + "# Func End #", file=outputfile)
        clear_buff()

    def clear_buff():
        comt_buffer.clear()
        deco_buffer.clear()
        func_buffer.clear()

    indent_func = 0
    comt_buffer = []
    deco_buffer = []
    func_buffer = []

    for line in inputfile.readlines():
        isempt, iscomt, isdeco, isfunc, isargs = checks(line)

        if comt_buffer and not (iscomt or isdeco or isfunc or deco_buffer or func_buffer):
            flush_comt()
        if func_buffer and not (isargs or isempt or indent(line) > indent_func):
            clear_buff() if masker(func_buffer) else flush_func()

        if iscomt and not (deco_buffer or func_buffer):
            comt_buffer.append(line)
        elif (isdeco or (deco_buffer and not isfunc)) and not func_buffer:
            deco_buffer.append(line)
        elif isfunc and not func_buffer:
            indent_func = indent(line)
            func_buffer.append(line)
        elif func_buffer and (isargs or isempt or indent(line) > indent_func):
            func_buffer.append(line)
        else:
            print(line, end="", file=outputfile)

    if func_buffer: clear_buff() if masker(func_buffer) else flush_func()
    if comt_buffer: flush_comt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ipath", help="file path for input")
    parser.add_argument("opath", help="file path for output")
    parser.add_argument("--marker", help="marker function", default="None")
    parser.add_argument("--masker", help="masker function", default="None")
    args = parser.parse_args()

    with open(args.ipath, "r") as ifile, open(args.opath, "w") as ofile:
        funcsect(ifile, ofile, marker=eval(args.marker), masker=eval(args.masker))
