import pandas as pd
from pathlib import Path


def load_klein():
    """
    Klein AM, Mazutis L, Akartuna I, Tallapragada N et al.
    Droplet barcoding for single-cell transcriptomics applied to embryonic
    stem cells. Cell 2015 May 21;161(5):1187-1201. PMID: 26000487
    GSE65525
    
    note: this data is modified from its origin.
    """
    datadir = Path(__file__).parent.joinpath('data/klein')
    profile = pd.read_csv(datadir.joinpath('profile.txt'), index_col=0)
    with open(str(datadir.joinpath('labels.txt').resolve()), 'r') as f:
        labels = f.read().split()
    return (profile, labels)
    

