# Kumadefile for concurrent task runner

from pathlib import Path

import kumade as ku

# Simple task dependencies
#  [a]--->[b]--->[c]


@ku.task("simple.a")
@ku.depend("simple.b")
def simple_a() -> None:
    pass


@ku.task("simple.b")
@ku.depend("simple.c")
def simple_b() -> None:
    pass


@ku.task("simple.c")
def simple_c() -> None:
    pass


# Multi task dependencies
#  [a]--->[b]--->[d]
#   |      |      A
#   |      +---->[e]--->[f]
#   |             A      A
#   +---->[c]--->[g]     |
#          |             |
#          +-------------+


@ku.task("multi_dep.a")
@ku.depend("multi_dep.b", "multi_dep.c")
def multi_dep_a() -> None:
    pass


@ku.task("multi_dep.b")
@ku.depend("multi_dep.d", "multi_dep.e")
def multi_dep_b() -> None:
    pass


@ku.task("multi_dep.c")
@ku.depend("multi_dep.f", "multi_dep.g")
def multi_dep_c() -> None:
    pass


@ku.task("multi_dep.d")
def multi_dep_d() -> None:
    pass


@ku.task("multi_dep.e")
@ku.depend("multi_dep.d", "multi_dep.f")
def multi_dep_e() -> None:
    pass


@ku.task("multi_dep.f")
def multi_dep_f() -> None:
    pass


@ku.task("multi_dep.g")
@ku.depend("multi_dep.e")
def multi_dep_g() -> None:
    pass


# Multi targets
#  [a]--->[b]--->[c]
#          |
#          +---->[d]--->[e]
#                 A
#  [f]--->[g]-----+
#   |
#   +---->[h]--->[i]


@ku.task("multi_tgt.a")
@ku.depend("multi_tgt.b")
def multi_tgt_a() -> None:
    pass


@ku.task("multi_tgt.b")
@ku.depend("multi_tgt.c", "multi_tgt.d")
def multi_tgt_b() -> None:
    pass


@ku.task("multi_tgt.c")
def multi_tgt_c() -> None:
    pass


@ku.task("multi_tgt.d")
@ku.depend("multi_tgt.e")
def multi_tgt_d() -> None:
    pass


@ku.task("multi_tgt.e")
def multi_tgt_e() -> None:
    pass


@ku.task("multi_tgt.f")
@ku.depend("multi_tgt.g", "multi_tgt.h")
def multi_tgt_f() -> None:
    pass


@ku.task("multi_tgt.g")
@ku.depend("multi_tgt.d")
def multi_tgt_g() -> None:
    pass


@ku.task("multi_tgt.h")
@ku.depend("multi_tgt.i")
def multi_tgt_h() -> None:
    pass


@ku.task("multi_tgt.i")
def multi_tgt_i() -> None:
    pass


# Depend on path without creation task
# [a]--->[out.txt]--->[in.txt]
#        (task)       (not task)

assets_dir = Path(__file__).absolute().parent
in_file = assets_dir / "in.txt"
out_file = assets_dir / "out.txt"


@ku.task("path.a")
@ku.depend(out_file)
def path_a() -> None:
    pass


@ku.file(out_file)
@ku.depend(in_file)
def create_out_file() -> None:
    pass


# Error task


@ku.task("error_task")
def raise_error() -> None:
    raise RuntimeError("Error.")
