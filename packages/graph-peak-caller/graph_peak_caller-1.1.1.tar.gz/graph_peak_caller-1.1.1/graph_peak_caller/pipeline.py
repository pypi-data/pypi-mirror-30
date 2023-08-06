from .sample import get_fragment_pileup
from .control import get_background_track_from_control,\
    get_background_track_from_input


def simple_pipeline(graph, input_reads, control_reads, linear_map, info, config):
    fragment_pileup = get_fragment_pileup(graph, input_reads, info)
    creator = get_background_track_from_control
    if not config.has_control:
        creator = get_background_track_from_input
    background_track = creator(graph, linear_map, info.fragment_length,
                               control_reads, fragment_pileup.touched_nodes)
    fragment_pileup, background_track = scale_tracks(fragment_pileup,
                                                     background_track,
                                                     input_reads, control_reads)
    p_scores = get_p_scores(fragment_pileup, background_track)
    q_scores = get_q_scores(p_values)
    peaks = q_values >= -np.log10(info.cutoff)
    joined_peaks = clean_holes(peaks, info.read_length)
    max_paths = get_max_paths(joined_peaks)
