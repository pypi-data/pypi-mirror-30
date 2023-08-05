from pathlib import Path
import numpy as np
import subprocess
import sys
import tempfile

from tmscc import JARFILE_PATH
from sampler import GibbsSampler


class TopicModelBase(object):
    def __init__(self, outdir, sampler='default'):
        self.outdir = Path(outdir).expanduser().resolve()
        if not self.outdir.is_dir():
            raise AssertionError('{0} is not an directory.'.format(self.outdir))
        if sampler == 'default':
            self.sampler = GibbsSampler(n_iter=1000, n_burnin=100)
        else:
            self.sampler = sampler


class LDA(TopicModelBase):
    def __init__(self, n_topics, profile, outdir, sampler='default'):
        """
        params:
        n_topics:
            the number of topics
        profile:
            gene expression profile,
            a pandas dataframe whose shape is (n_genes, n_cells)
            profile's index should be the gene names
        """
        super(LDA, self).__init__(outdir, sampler)
        self.n_topics = int(n_topics)
        self.profile = profile

        outputfile_fmt = str(self.outdir.resolve()) + '/{0}-{1}'
        self.profile_file = self.outdir.joinpath('profile.txt')

        profile.to_csv(
            str(self.profile_file.resolve()), sep=',',
            index=False, header=False)
        self.gene_file = self.outdir.joinpath('genes.txt')
        with open(self.gene_file, 'w') as fp:
            fp.write(','.join(self.profile.index.tolist()))

        self.theta_file = Path(
            outputfile_fmt.format(self.n_topics, 'theta.txt'))
        self.phi_file = Path(
            outputfile_fmt.format(self.n_topics, 'phi.txt'))

        self.is_trained = False

    def _estimate_mallet(self):
        """
        the result will be stored in the outdir you specified
        """
        cmd = ['java',
               '-jar',
               str(JARFILE_PATH.resolve()),
               str(self.n_topics),
               str(self.profile_file.resolve()),
               str(self.gene_file.resolve()),
               str(self.theta_file.resolve()),
               str(self.phi_file.resolve()),
               str(self.sampler.n_thread),
               str(self.sampler.n_iter),
               str(self.sampler.n_burnin)]
        
        sys.stderr.write('executing commands...')
        proc = subprocess.Popen(' '.join(cmd), shell=True)
        proc.wait()
        sys.stderr.write('\ndone!')

    def _estimate_celltree(self):
        # TODO
        pass

    def estimate(self):
        self.is_trained = True
        if isinstance(self.sampler, GibbsSampler):
            self._estimate_mallet()
        else:
            self._estimate_celltree()

    def theta(self):
        if not self.theta_file.exists():
            raise AssertionError('execute estimate() before calling this'
                                 'method.')
        else:
            theta = np.loadtxt(self.theta_file.resolve(), delimiter=',')
            return theta

    def _phi_to_mat(self):
        mask = 2 ** (self.n_topics-1).bit_length() - 1
        mask_len = mask.bit_length()

        with open(self.phi_file, 'r') as f:
            phidata = [
                [int(i) for i in l[:-1].split(',')] for l in f.readlines()
            ]

        phi = [
            [
                (v & mask, v >> mask_len) for v in lst if v != 0
            ]
            for lst in phidata
        ]

        phi_mat = np.zeros([len(phi), self.n_topics])
        for i, lst in enumerate(phi):
            for topic, count in lst:
                try:
                    phi_mat[i][topic] = count
                except:
                    print(i, topic, n_topics)

        return phi_mat

    def phi(self):
        if not self.phi_file.exists():
            raise AssertionError('execute estimate() before calling this'
                                 'method.')
        else:
            return self._phi_to_mat()


    def __repr__(self):
        return '''
        LDA Model:
        n_topics: {0}
        trained: {1},
        sampler: {2}
        '''.format(self.n_topics, self.is_trained, self.sampler)
