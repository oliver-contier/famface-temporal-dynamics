#!/usr/bin/python

"""
Run simulation over our data
"""


# def simulate_run(infile, outfile, lfnl=3.0, hfnl=None):
def simulate_run(infile, outfile):
    """
    Copy from shambrain.py (2017/05/22)
    """
    from nipype.interfaces import fsl

    # perform motion correction using mcflirt implemented by nipype
    # fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

    mcfile = outfile.replace('.nii.gz', '_mc.nii.gz')
    mcflt = fsl.MCFLIRT(in_file=infile, out_file=mcfile)
    mcflt.run()

    # load the preprocessed nifti as pymvpa data set
    from mvpa2.datasets.mri import fmri_dataset, map2nifti
    ds = fmri_dataset(mcfile)

    # get TR from sample attributes
    # float(ds.sa['time_coords'][1] - ds.sa['time_coords'][0])

    # or manually
    tr = 2.0

    # convert to sampling rate in Hz
    sr = 1.0 / tr
    cutoff = 1.0 / (2.0 * tr)

    # produce simulated 4D fmri data
    # mandatory inputs are dataset, sampling rate (Hz),
    # and cutoff frequency of the low-pass filter.
    # optional inputs are low frequency noise (%) (lfnl)
    # and high frequency noise (%) (hfnl)

    from mvpa2.misc.data_generators import autocorrelated_noise
    shambold = autocorrelated_noise(ds, sr, cutoff)

    # save to nifti file
    image = map2nifti(shambold)
    image.to_filename(outfile)


def run4famface(ofmri_dir, out_dir, sub_id):
    """ run the simulation from shambrain.py over our famface data
    
    Parameters
    ----------
    ofmri_dir:  str
        openfmri directory. Should contain data/sub001/ etc.
    out_dir:    str
        output directory. Will mirror the organization of the
        openfmri data directory

    """

    # source FSL via command line
    # import subprocess
    # process = subprocess.Popen(['echo', 'hello'])
    # output, error = process.communicate()
    # subprocess.Popen(['source', '/etc/fsl/fsl.sh'])

    import os

    # subs = [directory for directory in
    #         os.listdir(os.path.join(ofmri_dir, 'data'))
    #         if directory.startswith('sub')]

    funcdirs = [directory for directory in os.listdir(os.path.join(ofmri_dir, 'data', sub_id, 'BOLD'))]

    for funcdir in funcdirs:
        func = os.path.join(ofmri_dir, 'data', sub_id, 'BOLD',
                            funcdir, 'bold.nii.gz')

        out = func.replace(ofmri_dir, out_dir)

        # make output directories
        if not os.path.exists(out):
            os.makedirs(out.replace('bold.nii.gz', ''))

        simulate_run(func, out)
        #print(func)
        #print(out)


if __name__ == "__main__":
    # define input/output paths

    # on hydra
    ofmridir = '/data/famface/openfmri'
    outdir = '/data/famface/openfmri/oli/simulation'

    # on my machine
    # ofmridir = '/host/shambrain/shambrain/data/openfmri'
    # outdir = '/host/shambrain/shambrain/data/openfmri/simulation'

    # get sub id from command line arguments
    # should be: python famface_simulation.py sub001
    import sys
    subarg = sys.argv[1]

    # run
    run4famface(ofmridir, outdir, subarg)
