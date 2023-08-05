from itertools import chain
import offsetbasedgraph as obg
from graph_peak_caller import CallPeaks, ExperimentInfo
from graph_peak_caller.util import create_linear_map


def create_reads(peak, read_length):
    starts = [0, 10, 20, 30]
    start_reads = [peak.get_subinterval(start, read_length+start)
                   for start in starts]
    peak_length = peak.length()
    end_reads = [peak.get_subinterval(
        peak_length - (read_length+start),
        peak_length - start).get_reverse()
                 for start in starts]
    return start_reads+end_reads

node_sizes = [100, 100, 50, 200, 100, 50, 100]
nodes = {i+1: obg.Block(node_size) for i, node_size in enumerate(node_sizes)}
edges = {1: [2, 3],
         2: [4],
         3: [4],
         4: [5, 6],
         5: [7],
         6: [7]}
graph = obg.Graph(nodes, edges)


peaks = [obg.Interval(50, 50, [1, 3, 4], graph=graph),
         obg.Interval(70, 20, [4, 5, 7], graph=graph)]
reads = chain.from_iter(create_reads(peak, 30) for peak in peaks)

info = ExperimentInfo(600, 150, 30)
create_linear_map(graph, "figures_lin_map.npz")

CallPeaks.run_from_intervals(
    graph, reads, experiment_info=info,
    out_file_base_name="figures_", linear_map="figures_lin_map.npz",
    has_control=False)
