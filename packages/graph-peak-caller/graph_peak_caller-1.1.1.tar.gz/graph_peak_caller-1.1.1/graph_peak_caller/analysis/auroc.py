from .motifenrichment import MotifMatcher


def write_roc_data(fasta_file, meme_file):
    out_name = fasta_file + ".roc"
    roc_data = MotifMatcher(fasta_file, meme_file).get_peak_labels()
    open(out_name, "w").write(", ".join(str(l) for l in roc_data))
