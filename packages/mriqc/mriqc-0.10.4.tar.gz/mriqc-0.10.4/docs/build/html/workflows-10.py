import os.path as op
from mriqc.workflows.functional import fmri_qc_workflow
datadir = op.abspath('data')
wf = fmri_qc_workflow([op.join(datadir, 'sub-001/func/sub-001_task-rest_bold.nii.gz')],
                      settings={'bids_dir': datadir,
                                'output_dir': op.abspath('out'),
                                'no_sub': True})