"""
This script was written to design a workflow for 2nd level analysis to
model run effects. Regressor values and contrasts are input from text
files. Input path is defined in the variable 'runmodel_dir'. 
"""


def create_run_flow(name='run_flow'):
    """custom made fixed_effects_workflow for investigating run effects
    
    Inputs:

         inputspec.copes : list of list of cope files (one list per contrast)
         inputspec.varcopes : list of list of varcope files (one list per
                              contrast)
         inputspec.dof_files : degrees of freedom files for each run

    Outputs:

         outputspec.res4d : 4d residual time series
         outputspec.copes : contrast parameter estimates
         outputspec.varcopes : variance of contrast parameter estimates
         outputspec.zstats : z statistics of contrasts
         outputspec.tstats : t statistics of contrasts
    """
    from nipype.interfaces.utility import Function
    from nipype.interfaces import fsl
    from nipype import Node, MapNode, Workflow
    from nipype.interfaces.utility import IdentityInterface

    """
    Instantiate Workflow
    """
    runmodel_dir = '/data/famface/openfmri/data/run-groups/'
    run_flow = Workflow(name=name)
    inputspec = Node(IdentityInterface(fields=['copes',
                                               'varcopes',
                                               'dof_files'
                                               ]),
                     name='inputspec')

    """
    Merge the copes and varcopes for each condition
    """

    copemerge = MapNode(interface=fsl.Merge(dimension='t'),
                           iterfield=['in_files'],
                           name="copemerge")

    varcopemerge = MapNode(interface=fsl.Merge(dimension='t'),
                              iterfield=['in_files'],
                              name="varcopemerge")

    """
    Oli wrote this function to read the EVs / contrasts for the run model from
    a text file and bring them into shape for level2model
    """

    def get_run_contrast(con_file, ev_file):
        """
        Read the files containing regressor values and contrasts for
        2nd level analysis. Returns them in a shape that is accepted by
        'fsl.MultipleRegressDesign()'.
        
        Parameters
        ----------
        con_file:   file
            text file containing the 2nd lvl contrasts. Each row in file is a
            contrast. 
        ev_file:    file
            text file containing regressor values. Header will be ignored.
            First column represents input name (here: run number). Further
            columns represent regressor values. Columns seperated by tabs.
        Returns
        -------
        evdict:     dict
            containing 2nd lvl regressors
        runtrast:   list
            containing 2nd lvl contrasts. 
        """
        # create regressor dict
        with open(ev_file, 'rt') as f:
            evlines = [line.split() for line in f.readlines()]
        evnames = evlines[0][1:]
        evweights = [list(map(float, i[1:])) for i in evlines[1:]]
        evdict = dict()
        for name in evnames:
            evdict[name] = ([i[evnames.index(name)] for i in evweights])

        # create contrast list
        # TODO: this works with simple main effects. Should be made more flexible later on.
        with open(con_file, 'rt') as f:
            conlines = [i.split() for i in f.readlines()]
        runtrast = []
        for conline in conlines:
            if conline[0] == '#':
                continue
            # if contrast is a T-Test
            elif conline[1]=='T':
                runtrast.append(tuple(conline[0:2] + [[conline[2]]] + [[float(conline[3])]]))
            # if contrast is an F-Test
            elif 'F' in conline:
                runtrast.append((conline[0], conline[1], [(conline[2], conline[3], [conline[4]], [float(conline[5])])]))
        return evdict, runtrast

    run_contrast = Node(Function(input_names=['con_file', 'ev_file'],
                                 output_names=['evdict', 'runtrast'],
                                 function=get_run_contrast),
                        name='run_contrast')

    run_contrast.inputs.con_file = runmodel_dir + 'runcontrast.txt'
    run_contrast.inputs.ev_file = runmodel_dir + 'behav.txt'

    """
    Generate subject and condition specific level 2 model design files
    """
    level2model = Node(interface=fsl.MultipleRegressDesign(),
                       name='runmodel')

    """
    Estimate a second level model
    """

    flameo = MapNode(interface=fsl.FLAMEO(run_mode='fe'), name="flameo",
                     iterfield=['cope_file', 'var_cope_file'])

    def get_dofvolumes(dof_files, cope_files):
        import os
        import nibabel as nb
        import numpy as np
        img = nb.load(cope_files[0])
        if len(img.shape) > 3:
            out_data = np.zeros(img.shape)
        else:
            out_data = np.zeros(list(img.shape) + [1])
        for i in range(out_data.shape[-1]):
            dof = np.loadtxt(dof_files[i])
            out_data[:, :, :, i] = dof
        filename = os.path.join(os.getcwd(), 'dof_file.nii.gz')
        newimg = nb.Nifti1Image(out_data, None, img.header)
        newimg.to_filename(filename)
        return filename

    gendof = Node(Function(input_names=['dof_files', 'cope_files'],
                                output_names=['dof_volume'],
                                function=get_dofvolumes),
                  name='gendofvolume')

    """
    Connect all the Nodes in the workflow
    """

    outputspec = Node(IdentityInterface(fields=['res4d',
                                                     'copes', 'varcopes',
                                                     'zstats', 'tstats', 'fstats']),
                      name='outputspec')

    run_flow.connect([(inputspec, copemerge, [('copes', 'in_files')]),
                      (inputspec, varcopemerge, [('varcopes', 'in_files')]),
                      (inputspec, gendof, [('dof_files', 'dof_files')]),
                      (copemerge, gendof, [('merged_file', 'cope_files')]),
                      (copemerge, flameo, [('merged_file', 'cope_file')]),
                      (varcopemerge, flameo, [('merged_file',
                                               'var_cope_file')]),
                      (run_contrast, level2model, [('evdict', 'regressors'),
                                                       ('runtrast', 'contrasts')]),
                      (level2model, flameo, [('design_mat', 'design_file'),
                                             ('design_con', 't_con_file'),
                                             ('design_fts', 'f_con_file'),
                                             ('design_grp', 'cov_split_file')]),
                      (gendof, flameo, [('dof_volume', 'dof_var_cope_file')]),
                      (flameo, outputspec, [('res4d', 'res4d'),
                                            ('copes', 'copes'),
                                            ('var_copes', 'varcopes'),
                                            ('zstats', 'zstats'),
                                            ('tstats', 'tstats'),
                                            ('fstats', 'fstats')
                                            ])
                      ])
    return run_flow
