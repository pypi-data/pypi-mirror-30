import logging
import numpy as np
from offsetbasedgraph import IntervalCollection, DirectedInterval
from .mindense import DensePileup
from .sampleandcontrolcreator import SampleAndControlCreator
from .sparsepvalues import PValuesFinder, PToQValuesMapper, QValuesFinder
from .postprocess import HolesCleaner, SparseMaxPaths
from .sparsediffs import SparseValues
from .reporter import Reporter
IntervalCollection.interval_class = DirectedInterval


class Configuration:
    def __init__(self, skip_filter_duplicates=False,
                 graph_is_partially_ordered=False,
                 skip_read_validation=False,
                 save_tmp_results_to_file=False,
                 p_val_cutoff=0.1,
                 use_global_min_value=None):
        self.skip_filter_duplicates = skip_filter_duplicates
        self.graph_is_partially_ordered = graph_is_partially_ordered
        self.skip_read_validation = skip_read_validation
        self.save_tmp_results_to_file = save_tmp_results_to_file
        self.p_val_cutoff = p_val_cutoff
        self.use_global_min_value = use_global_min_value

    @classmethod
    def default(cls):
        return cls()


class CallPeaks(object):

    def __init__(self, graph, out_file_base_name):
        self.graph = graph
        self.out_file_base_name = out_file_base_name

        self.sample_intervals = None
        self.control_intervals = None
        self.sample_pileup = None
        self.control_pileup = None
        self.p_values_pileup = None
        self.p_to_q_values_mapping = None
        self.q_values_pileup = None
        self.peaks_as_subgraphs = None
        self.touched_nodes = None
        self.max_path_peaks = None
        self._reporter = Reporter(self.out_file_base_name)

    def run_pre_callpeaks(self, has_control, experiment_info,
                          linear_map, configuration=None):
        if configuration is None:
            configuration = Configuration.default()
            logging.warning("Config is not set. Setting to default")
        creator = SampleAndControlCreator(
            self.graph,
            self.sample_intervals,
            self.control_intervals,
            experiment_info,
            out_file_base_name=self.out_file_base_name,
            has_control=has_control,
            linear_map=linear_map,
            configuration=configuration
            )
        creator.run()
        self.sample_pileup = creator._sample_pileup
        self.control_pileup = creator._control_pileup
        self.touched_nodes = creator.touched_nodes

    def get_p_values(self):
        assert self.sample_pileup is not None
        assert self.control_pileup is not None
        self.p_values_pileup = PValuesFinder(
            self.sample_pileup, self.control_pileup).get_p_values_pileup()
        self.p_values_pileup.track_size = self.graph.node_indexes[-1]
        self.sample_pileup = None
        self.control_pileup = None

    def get_p_to_q_values_mapping(self):
        assert self.p_values_pileup is not None
        finder = PToQValuesMapper.from_p_values_pileup(
            self.p_values_pileup)
        self.p_to_q_values_mapping = finder.get_p_to_q_values()

    def get_q_values(self):
        assert self.p_values_pileup is not None
        assert self.p_to_q_values_mapping is not None
        finder = QValuesFinder(self.p_values_pileup,
                               self.p_to_q_values_mapping)
        self.q_values_pileup = finder.get_q_values()
        self.q_values_pileup.track_size = self.p_values_pileup.track_size
        self._reporter.add("qvalues", self.q_values_pileup)

    def call_peaks_from_q_values(self, experiment_info, config=None):
        assert self.q_values_pileup is not None
        caller = CallPeaksFromQvalues(
            self.graph, self.q_values_pileup,
            experiment_info, self.out_file_base_name,
            touched_nodes=self.touched_nodes,
            config=config
            )
        caller.callpeaks()
        self.max_path_peaks = caller.max_paths

    def save_max_path_sequences_to_fasta_file(self, file_name,
                                              sequence_retriever):
        assert self.max_path_peaks is not None
        f = open(self.out_file_base_name + file_name, "w")
        i = 0
        for max_path in self.max_path_peaks:
            seq = sequence_retriever.get_interval_sequence(max_path)
            f.write(">peak" + str(i) + " " +
                    max_path.to_file_line() + "\n" + seq + "\n")
            i += 1
        f.close()
        logging.info("Wrote max path sequences to fasta file: %s" % (
            self.out_file_base_name + file_name))

    @classmethod
    def run_from_intervals(
            cls, graph, sample_intervals,
            control_intervals=None, experiment_info=None,
            out_file_base_name="", has_control=True,
            linear_map=None, configuration=None, stop_after_p_values=False):
        caller = cls(graph, out_file_base_name)
        caller.sample_intervals = sample_intervals
        caller.control_intervals = control_intervals

        caller.run_pre_callpeaks(has_control, experiment_info,
                                 linear_map, configuration)
        caller.get_p_values()
        caller.p_values_pileup.track_size = graph.node_indexes[-1]
        if stop_after_p_values:
            np.save(out_file_base_name + "touched_nodes.npy",
                    np.array(list(caller.touched_nodes), dtype="int"))
            return caller.p_values_pileup.to_sparse_files(
                out_file_base_name + "pvalues")

        caller.get_p_to_q_values_mapping()
        caller.get_q_values()
        caller.call_peaks_from_q_values(experiment_info, configuration)
        return caller


class CallPeaksFromQvalues:
    def __init__(self, graph, q_values_pileup,
                 experiment_info,
                 out_file_base_name="",
                 cutoff=0.1, raw_pileup=None, touched_nodes=None,
                 config=None, q_values_max_path=False):
        self.graph = graph
        self.q_values = q_values_pileup
        self.info = experiment_info
        self.out_file_base_name = out_file_base_name
        self.cutoff = cutoff
        self.raw_pileup = raw_pileup
        self.touched_nodes = touched_nodes
        self.save_tmp_results_to_file = False
        self.graph_is_partially_ordered = False
        self.q_values_max_path = q_values_max_path

        if config is not None:
            self.cutoff = config.p_val_cutoff
            self.graph_is_partially_ordered = config.graph_is_partially_ordered
            self.save_tmp_results_to_file = config.save_tmp_results_to_file
        self._reporter = Reporter(self.out_file_base_name)

        self.info.to_file(self.out_file_base_name + "experiment_info.pickle")
        logging.info("Using p value cutoff %.4f" % self.cutoff)

    def __threshold(self):
        threshold = -np.log10(self.cutoff)
        logging.info("Thresholding peaks on q value %.4f" % threshold)
        self.pre_processed_peaks = self.q_values.threshold_copy(threshold)
        self._reporter.add("thresholded", self.pre_processed_peaks)

    def __postprocess(self):
        logging.info("Filling small Holes")
        self.pre_processed_peaks = HolesCleaner(
            self.graph,
            self.pre_processed_peaks,
            self.info.read_length,
            self.touched_nodes
        ).run()
        self._reporter.add("hole_cleaned", self.pre_processed_peaks)

        logging.info("Not removing small peaks")
        self.filtered_peaks = self.pre_processed_peaks

    def __get_max_paths(self):
        logging.info("Getting maxpaths")
        if not self.q_values_max_path:
            _pileup = SparseValues.from_sparse_files(
                self.out_file_base_name+"direct_pileup")
            self.raw_pileup = _pileup
        else:
            _pileup = self.q_values

        logging.info("Running Sparse Max Paths")
        max_paths, sub_graphs = SparseMaxPaths(
            self.filtered_peaks, self.graph, _pileup).run()

        self._reporter.add("all_max_paths", max_paths)
        logging.info("All max paths found")
        self.q_values = DensePileup(
            self.graph, self.q_values.to_dense_pileup(
                self.graph.node_indexes[-1]))

        for max_path in max_paths:
            max_path.set_score(np.max(
                self.q_values.get_interval_values(max_path)))
        pairs = list(zip(max_paths, sub_graphs))
        pairs.sort(key=lambda p: p[0].score, reverse=True)
        logging.info("N unfiltered peaks: %s", len(max_paths))
        pairs = [p for p in pairs if
                 p[0].length() >= self.info.fragment_length]
        logging.info("N filtered peaks: %s", len(pairs))
        self._reporter.add("sub_graphs", [pair[1] for pair in pairs])
        self.max_paths = [p[0] for p in pairs]
        self._reporter.add("max_paths", self.max_paths)

    def callpeaks(self):
        logging.info("Calling peaks")
        self.__threshold()
        self.__postprocess()
        self.__get_max_paths()

    def save_max_path_sequences_to_fasta_file(self, file_name, sequence_retriever):
        assert self.max_paths is not None, \
                "Max paths has not been found. Run peak calling first."
        assert sequence_retriever is not None
        # assert isinstance(sequence_retriever, vg.sequences.SequenceRetriever)
        f = open(self.out_file_base_name + file_name, "w")
        i = 0
        for max_path in self.max_paths:
            seq = sequence_retriever.get_interval_sequence(max_path)
            f.write(">peak" + str(i) + " " +
                    max_path.to_file_line() + "\n" + seq + "\n")
            i += 1
        f.close()
        logging.info("Wrote max path sequences to fasta file: %s" % (self.out_file_base_name + file_name))

    @staticmethod
    def intervals_to_fasta_file(interval_collection, out_fasta_file_name, sequence_retriever):
        f = open(out_fasta_file_name, "w")
        i = 0
        for max_path in interval_collection.intervals:
            seq = sequence_retriever.get_interval_sequence(max_path)
            f.write(">peak" + str(i) + " " +
                    max_path.to_file_line() + "\n" + seq + "\n")
            i += 1
            if i % 100 == 0:
                logging.info("Writing sequence # %d" % i)
        f.close()

