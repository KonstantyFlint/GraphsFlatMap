from typing import Tuple, Callable

from list_utils.functional_list import FunctionalList as Fl
from list_utils.read_file import read_file
from list_utils.unpack import unpack as _

PARTIAL = ("cur", "prev", "path")
EDGE = ("a", "b", "l")

PARTIAL_WITH_EDGE = (PARTIAL, EDGE)


def make_edges_both_ways(edges: Fl) -> Fl:
    return edges.flat_map(_(EDGE, lambda a, b, l: Fl([(a, b, l), (b, a, l)])))


def filter_fl(l: Fl, predicate: Callable[[Tuple], bool]) -> Fl:
    return l.flat_map(
        lambda a: Fl([a]) if predicate(a) else Fl([])
    )


def expand(partials: Fl, edges: Fl, end: int) -> Tuple[Fl, Fl]:
    best_partials = filter_fl(partials, _(PARTIAL, lambda cur: cur == end))
    best_length = None
    if len(best_partials) > 0:
        best_length = best_partials[0][2]

    with_edges = partials.join_by_custom_key(
        edges,
        _(PARTIAL, lambda cur: cur),
        _(EDGE, lambda a: a)
    )
    expanded_with_info = with_edges.flat_map(
        _(
            PARTIAL_WITH_EDGE,
            lambda cur, prev, path, a, b, l: Fl([
                (cur, (prev, path, False)),
                (b, (cur, path + l, True))
            ])
        )
    )
    if best_length is not None:
        expanded_with_info = filter_fl(expanded_with_info, lambda x: x[1][1] <= best_length)

    reduced = expanded_with_info.reduce_by_key(
        lambda x, y: (x[0], x[1] ,x[2] and y[2]) if x[1] == y[1] else x if x[1] < y[1] else y
    )
    tp = ("w", ("x", "y", "z"))
    update_info = reduced.map(_(tp, lambda z: z))
    new_partials = reduced.map(_(tp, lambda w, x, y: (w, x, y)))

    return new_partials, update_info


def get_best(partials: Fl, index: int):
    best = None
    for partial in partials:
        cur, prev, l = partial
        if cur != index:
            continue
        if best is None or l < best[2]:
            best = partial
    return best


def collect_output(partials: Fl, end: int):
    node = get_best(partials, end)
    output = []
    while node is not None:
        output = [node[0]] + output
        node = get_best(partials, node[1])
    return output


def solve(edges: Fl, start: int, end: int) -> Fl:
    edges = make_edges_both_ways(edges)
    partials = Fl([(start, None, 0)])
    updated = True
    while updated:
        partials, update_info = expand(partials, edges, end)
        updated = any(update_info)
    return collect_output(partials, end)


problem = read_file("problem.txt", (int, int, int))
print(solve(problem, 1, 1000))
