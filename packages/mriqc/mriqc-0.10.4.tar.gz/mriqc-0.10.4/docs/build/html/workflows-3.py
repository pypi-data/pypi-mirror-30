import os.path as op
from mriqc.workflows.anatomical import anat_qc_workflow
datadir = op.abspath('data')
wf = anat_qc_workflow([op.join(datadir, 'sub-001/anat/sub-001_T1w.nii.gz')],
                      settings={'bids_dir': datadir,
                                'output_dir': op.abspath('out'),
                                'ants_nthreads': 1,
                                'no_sub': True})