import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix


def plot_arrays(arrays, starts, ys, out_name="tmp"):
    ends = [start+array.size for start, array in zip(starts, arrays)]
    min_x, max_x = (min(starts), max(ends))
    min_y, max_y = (min(ys), max(ys))
    print(min_x, max_x)
    ends = [end-min_x for end in ends]
    starts = [start-min_x for start in starts]
    ys = ys-min_y
    max_value = max(np.max(array) for array in arrays)
    x_scale = 1
    y_scale = 2
    values = 0*(max_value*1.5)*np.ones((y_scale*(max_y+1-min_y)+10, (max_x-min_x)*x_scale))
    for start, end, array, y in zip(starts, ends, arrays, ys):
        values[(y_scale*(y)+5):(y_scale*(y+1)+5), (start*x_scale):(end*x_scale)] = np.repeat(array, x_scale)

    plt.imshow(values, cmap="Greens", interpolation="nearest")
    for start, end, array, y in zip(starts, ends, arrays, ys):
        s_x, e_x = (start+0.5)*x_scale, (end+0.5)*x_scale
        s_y, e_y = y_scale*(y+0.5)+5, y_scale*(y+1.5)+5
        # plt.plot([s_x, e_x, e_x, s_x, s_x],
        #          [s_y, s_y, e_y, e_y, s_y], color="black", linestyle="-", linewidth=0.1)
    plt.savefig(out_name+".pdf")


def get_ys(subgraph, node_ids):
    ys = np.zeros(subgraph.shape[0], dtype="int")
    wheres = np.zeros_like(ys)
    stack = [(0, 0)]
    while stack:
        node_id, y = stack.pop()
        ys[node_id] = y
        wheres[node_id] = 1
        next_nodes = subgraph[node_id].indices
        for i, next_node in enumerate(next_nodes):
            new_y = 2*i-next_nodes.size//2
            stack.append([next_node, new_y])
            # new_y = y+next_nodes.size-1-(subgraph[:, node_id].indices.size-1)
            # stack.append([next_node, new_y])
    return ys[wheres > 0]+1


def get_peak_positions(graph, lin_map, dense_pileup, subgraph, nodeids):
    print(subgraph)
    print(nodeids)
    node_arrays = [dense_pileup.values(node_id)
                   for node_id in nodeids]
    ends = []
    starts = []
    for i, node_id in enumerate(nodeids):
        base_start = lin_map.get_node_start(node_id)
        l = lin_map.get_node_end(node_id)-base_start
        diff = l-graph.node_size(node_id)
        # are_complete[i] = diff == 0
        starts.append(int(base_start+diff//2))
        ends.append(starts[-1]+l)
    ys = get_ys(subgraph, nodeids)
    return node_arrays, starts, ys


def test_plot():
    class Graph:
        @staticmethod
        def node_size(node_id):
            sizes = {1: 10, 2: 20, 3: 30, 4: 10}
            return sizes[node_id]

    class LinMap:
        @staticmethod
        def get_node_start(node_id):
            starts = {1: 0, 2: 11, 3: 11, 4: 42}
            return starts[node_id]

        @staticmethod
        def get_node_end(node_id):
            ends = {1: 11, 2: 42, 3: 42, 4: 53}
            return ends[node_id]

    class DensePileup:
        @staticmethod
        def values(node_id):
            values = {1: np.arange(10),
                      2: np.arange(5, 25),
                      3: np.arange(5, 35),
                      4: np.arange(10, 20)}
            return values[node_id]
    subgraph = csr_matrix(([10, 10, 25, 35], ([0, 0, 1, 2], [1, 2, 3, 3])),
                          shape=[4, 4])
    res = get_peak_positions(Graph, LinMap, DensePileup,
                             subgraph, [1, 2, 3, 4])
    print(res)
    plot_arrays(*res)


if __name__ == "__main__":
    test_plot()
    # plot_arrays([np.arange(10), np.arange(5, 15),
    #             np.arange(10, 20)],
    #            [0, 10, 20], [0, 1, 0])
