import logging
import numpy as np
from collections import defaultdict
from offsetbasedgraph import Interval, IntervalCollection, BlockArray


class DensePileupData:

    def __init__(self, graph, ndim=1, base_value=0, dtype=None, padding=0):
        self._padding = padding
        self._values = None
        self._node_indexes = None
        self._graph = graph
        self.min_node = None
        self._touched_nodes = set()
        self.ndim = ndim
        self.dtype = dtype
        self._create_empty(ndim, base_value=base_value)

    def _create_empty(self, ndim=1, base_value=0):
        logging.info("Sorting nodes")
        self._nodes = sorted(self._graph.blocks.keys())

        sorted_nodes = self._nodes
        self.min_node = sorted_nodes[0]
        max_node = sorted_nodes[-1]
        span = max_node - self.min_node + 1
        logging.info("Counting basepairs")
        n_elements = self._graph.number_of_basepairs()

        if self.dtype is not None:
            self._values = np.zeros(n_elements+self._padding)
        else:
            self._values = np.zeros(n_elements+self._padding)

        if base_value > 0:
            self._values += base_value

        if isinstance(self._graph.blocks, BlockArray):
            # Quicker way to make node_indexes array
            logging.info("Using quick way to init densepileup (using cumsum on np block array)")
            self._node_indexes = np.cumsum(self._graph.blocks._array, dtype=np.uint32)
            logging.info("Node indexes created...")
        else:
            print(span)
            self._node_indexes = np.zeros(span+1, dtype=np.uint32)
            offset = 0
            for i, node in enumerate(self._nodes):
                index = node - self.min_node
                self._node_indexes[index] = offset
                offset += self.node_size(node)
            self._node_indexes[-1] = offset
        logging.info("Dense pileup inited")

    def sum(self):
        return np.sum(self._values)

    def sanitize_node(self):
        return

    def node_size(self, node):
        return self._graph.node_size(node)

    def values(self, tmp_node):
        node = abs(tmp_node)
        sign = tmp_node//node
        index = node - self.min_node
        start = self._node_indexes[index]
        end = start + self.node_size(node)
        vals = self._values[start:end]
        if sign < 0:
            return vals[::-1]
        return vals

    def values_in_range(self, node, start, end):
        index = node - self.min_node
        array_start = self._node_indexes[index] + start
        array_end = self._node_indexes[index] + end
        return self._values[array_start:array_end]

    def node_range_to_value_indexes(self, node, start, end):
        if node < 0:
            node = -node
            new_start = self.node_size(node) - end
            end = self.node_size(node) - start
            start = new_start

        node_size = self.node_size(node)
        start = min(node_size, max(start, 0))
        end = max(0, min(node_size, end))

        index = node - self.min_node
        array_start = self._node_indexes[index] + start
        array_end = self._node_indexes[index] + end
        return array_start, array_end

    def set_values(self, node, start, end, value):
        index = node - self.min_node
        array_start = self._node_indexes[index] + start
        array_end = self._node_indexes[index] + end
        self._values[array_start:array_end] = value
        self._touched_nodes.add(node)

    def add_value(self, node, start, end, value):
        index = node - self.min_node
        array_start = self._node_indexes[index] + start
        array_end = self._node_indexes[index] + end
        self._values[array_start:array_end] += value
        self._touched_nodes.add(node)

    def add_value_to_full_node(self, node, value):
        index = node - self.min_node
        array_start = self._node_indexes[index]
        array_end = array_start + self.node_size(node)
        self._values[array_start:array_end] += value
        self._touched_nodes.add(node)

    def set_full_node_value(self, node, value):
        index = node - self.min_node
        array_start = self._node_indexes[index]
        array_end = array_start + self.node_size(node)
        self._values[array_start:array_end] = value
        self._touched_nodes.add(node)

    def get_subset_max_value(self, node_id, start, end):
        return np.max(self.values(node_id)[start:end])

    def get_subset_sum(self, node_id, start, end):
        return np.sum(self.values(node_id)[start:end])

    def score(self, node_id, start, end):
        return RpScore(self.get_subset_max_value(node_id, start, end),
                       self.get_subset_sum(node_id, start, end))

    def scale(self, factor):
        self._values *= factor

    def set_new_values(self, values):
        self._values = values

    def fill_existing_hole(self, node, start, end, value):
        assert np.all(self.values_in_range(node, start, end) == 0)
        self.set_values(node, start, end, value)

    def get_sparse_indexes_and_values(self, node):
        values = self.values(node)
        diffs = np.ediff1d(values, to_begin=np.array([1]))
        indexes = np.where(diffs != 0)
        values = values[indexes]
        indexes = np.append(indexes, self.node_size(node))
        return indexes, values

    def find_valued_areas(self, node, value, changes=None):
        # Return list[start, end, start2, end2,...] having this value inside
        index = node - self.min_node
        start = self._node_indexes[index]
        end = start + self.node_size(node)
        changes = np.nonzero(changes[start:end])[0]+1
        if changes.size and changes[-1] == end-start:
            changes = changes[:-1]
        # is_value = values == value
        # changes = np.nonzero(np.ediff1d(is_value))[0]+1
        if self._values[start] == value:
            if self._values[end-1] == value:
                return [0] + list(changes)+[end-start]
            return [0] + list(changes)
        if self._values[end-1]:
            return list(changes)+[end-start]
        return list(changes)

    def nodes(self):
        return self._touched_nodes

    def copy(self):
        new = DensePileupData(self._graph)
        new._values = self._values
        new._touched_nodes = self._touched_nodes
        return new

    def threshold_copy(self, cutoff):
        new = self.copy()
        new._values = new._values >= cutoff
        logging.info("Thresholding done.")
        return new

    def threshold(self, cutoff):
        self._values = self._values >= cutoff

    def index_value_pairs(self, node):
        indexes, values = self.get_sparse_indexes_and_values(node)
        assert len(indexes) >= 2
        assert len(values) >= 1
        lines = list(zip(
            indexes[:-1],
            indexes[1:],
            values
            ))
        assert len(lines) >= 1
        return lines

    def get_bed_graph_lines(self):
        for node in self.nodes():
            lines = self.index_value_pairs(node)
            for line in lines:
                yield "%s\t%s\t%s\t%s\n" % (node, line[0], line[1], line[2])

    def __len__(self):
        return len(self.nodes())

    def __eq__(self, other):
        for node in self.nodes():
            indexes, values = self.get_sparse_indexes_and_values(node)
            #print("   Checking node %d" % node)
            other_indexes, other_values = other.get_sparse_indexes_and_values(node)
            #print("   Values: %s / %s" % (values, other_values))
            print(indexes, other_indexes)
            if not np.all(indexes == other_indexes):
                print("Indices %s != %s" % (indexes, other_indexes))
                return False

            print(values, other_values)
            if np.any(np.abs(values -  other_values) > 1e-5):
                print("Values %s != %s" % (values, other_values))
                print()
                return False

        return True

    def get_interval_values(self, interval):

        values = np.zeros(interval.length())
        offset = 0
        if all([rp < 0 for rp in interval.region_paths]):
            # Reverse before finding
            # find_reversed = True
            interval = interval.get_reverse()

        for i, rp in enumerate(interval.region_paths):
            assert rp > 0, "Currently only implemented for forward directed intervals"
            start = 0
            end = self._graph.node_size(rp)
            if i == 0:
                start = interval.start_position.offset
            if i == len(interval.region_paths) - 1:
                end = interval.end_position.offset

            values_in_rp = self.values_in_range(rp, start, end)
            values[offset:offset + (end - start)] = values_in_rp

            offset += end-start

        return values

    def value_indexes_to_nodes_and_offsets(self, indexes):
        """
        Takes indexes referring to positions in self._values
        and returns list of (node, offset).
        Indexes must be sorted
        """

        positions = []
        # Map indexes to node and offset
        length_offset = 0
        nodes = self._nodes
        current_node_index = 0
        i = 0
        while i < len(indexes):
            index = indexes[i]
            current_node = nodes[current_node_index]
            node_size = self.node_size(current_node)
            next_node_start = length_offset + node_size
            if index >= next_node_start:
                current_node_index += 1
                length_offset += node_size
                continue

            if index < next_node_start:
                positions.append((current_node, index - length_offset))

            i += 1
        return positions


class DensePileup:
    def __init__(self, graph, ndim=1, base_value=0, dtype=None):
        logging.info("Initing dense pileup")
        self.graph = graph
        self.data = DensePileupData(
            graph, ndim=ndim, base_value=base_value, dtype=dtype)

    @classmethod
    def from_base_value(cls, graph, base_value):
        pileup = cls(graph, base_value=base_value)
        return pileup

    def __str__(self):
        out = "Densepileup \n"
        for node in self.data._touched_nodes:
            out += "  Node %d: %s\n" % (
                node, 
                self.data.get_sparse_indexes_and_values(node))

        return out

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.data == other.data

    @classmethod
    def from_intervals(cls, graph, intervals):
        starts, ends = intervals_to_start_and_ends(graph, intervals)
        return cls.from_starts_and_ends(graph, starts, ends)

    @classmethod
    def from_starts_and_ends(cls, graph, starts, ends, dtype=bool):
        pileup = cls(graph)
        for node in starts:
            for i, start in enumerate(starts[node]):
                end = ends[node][i]
                pileup.data.add_value(node, start, end, 1)

        return pileup

    def to_bed_graph(self, filename):
        f = open(filename, "w")
        i = 0
        for line in self.data.get_bed_graph_lines():
            f.write(line)
            i += 1
        f.close()
        self.filename = filename
        self.is_written = True
        return filename

    def to_bed_file(self, filename):
        f = open(filename, "w")
        areas = self.find_valued_areas(True)
        for node_id, idxs in areas.items():
            for i in range(len(idxs)//2):
                interval = (node_id, idxs[2*i], idxs[2*i+1])
                f.write("%s\t%s\t%s\t.\t.\t.\n" % interval)
        f.close()
        return filename

    @classmethod
    def create_from_old_sparsepileup(cls, old_pileup):
        # TMP method for tests to pass
        graph = old_pileup.graph
        pileup = DensePileup(graph)

        for node in old_pileup.data:

            values = old_pileup.data[node].all_values()
            indexes = old_pileup.data[node].all_idxs()

            i = 0
            for start, end in zip(indexes[0:-1], indexes[1:]):
                value = values[i]
                pileup.data.set_values(node, start, end, value)
                i += 1

        return pileup

    def equals_old_sparse_pileup(self, old_pileup):
        # For tests to pass temporarily
        for node in self.data.nodes():
            indexes, values = self.data.get_sparse_indexes_and_values(node)
            other_indexes = old_pileup.data[node].all_idxs()
            if not np.all(indexes == other_indexes):
                return False

            other_values = old_pileup.data[node].all_values()
            if not np.allclose(values, other_values):
                return False

        return True

    @classmethod
    def create_from_binary_continous_areas(cls, graph, areas_list):
        pileup = cls(graph, dtype=np.uint8)
        i = 0
        for areas in areas_list:
            if i % 5000 == 0:
                logging.info("Processing read %d" % i)
            i += 1
            pileup.add_area(areas)

        return pileup

    @classmethod
    def from_sparse_files(cls, graph, base_file_name):
        # TODO: Use np.save(...)
        pileup = cls(graph)
        indexes = np.load(base_file_name + "_indexes.npy")
        last = indexes[-1]
        indexes = indexes[:-1]  # Remove length added to end
        values = np.load(base_file_name + "_values.npy")

        # Hack. Sometimes densepileup comes from sparsevalues and
        # have two sizes at end.
        if last == indexes[-1]:
            indexes = indexes[:-1]
            values = values[:-1]

        assert np.all(indexes >= 0)
        if isinstance(values[0], np.bool_):
            logging.warning("Converting from bool to uint8 to allow reading.")
            values = values.astype(np.int8)

        diffs = np.ediff1d(values, to_begin=[values[0]])
        pileup_vals = pileup.data._values
        pileup_vals[indexes] = diffs
        pileup_vals = np.cumsum(pileup_vals)
        pileup.data._values = pileup_vals
        try:
            touched_nodes = np.load(
                base_file_name + "_touched_nodes.npy")
            pileup.data._touched_nodes = set(list(touched_nodes))
        except FileNotFoundError:
            logging.warning("Touched nodes not found on file. Not setting touched nodes")

        return pileup

    def to_sparse_files(self, file_base_name):
        vals = self.data._values
        diffs = np.ediff1d(vals, to_begin=[1])
        indexes = np.nonzero(diffs)[0]
        values = vals[indexes]

        # Add length to end and 0 to start
        indexes = np.append(indexes, len(self.data._values))

        np.save(file_base_name + "_touched_nodes.npy",
                np.array(list(self.data._touched_nodes)))
        np.save(file_base_name + "_indexes.npy", indexes)
        np.save(file_base_name + "_values.npy", values)

        logging.info("Saved p values indexes/values to files")


def intervals_to_start_and_ends(graph, intervals):
    # Returns two dict on rp => positions (start/ends)
    starts = defaultdict(list)
    ends = defaultdict(list)

    for interval in intervals:
        for i, region_path in enumerate(interval.region_paths):
            start = 0
            end = graph.node_size(region_path)
            if i == 0:
                start = interval.start_position.offset
            if i == len(interval.region_paths)-1:
                end = interval.end_position.offset

            if region_path < 0:
                new_start = graph.node_size(region_path) - end
                new_end = graph.node_size(region_path) - start
                start = new_start
                end = new_end

                region_path = -region_path

            starts[region_path].append(start)
            ends[region_path].append(end)

    for rp in starts:
        starts[rp] = np.array(starts[rp])

    for rp in ends:
        ends[rp] = np.array(ends[rp])

    return starts, ends
