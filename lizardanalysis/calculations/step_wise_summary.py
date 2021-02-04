def read_DOKAoutput_files(config):
    # TODO: Bob write R script to rename all DOKA output files to have the same name pattern
    print('\nCREATING AND WRITING SUMMARY RESULT FILES...\n...')
    from pathlib import Path
    import os
    import errno
    import glob

    current_path = os.getcwd()
    config_file = Path(config).resolve()
    project_path = os.path.split(config_file)[0]

    result_file_path = os.path.join(current_path, project_path, "analysis-results")
    print('result filepath: ', result_file_path)
    summary_folder = os.path.join(result_file_path, "analysis-summary")

    try:
        os.makedirs(summary_folder)
        print("folder for summary result files created")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    filelist = glob.glob(os.path.join(result_file_path, "_resnet50_*.csv"))
    filelist_split = [x.rsplit(os.sep, 1)[1] for x in filelist]
    print(" + ", len(filelist_split), *filelist_split, sep='\n + ')

    return result_file_path, summary_folder, filelist_split, filelist


def summarize_stepwise(**kwargs):
    """
    REads in all DOKA output files and summarizes the data step-wise in one big csv document.
    :param kwargs:
    :return:
    """
    ### IMPORTS:
    import pandas as pd
    import os

    ### SETUP:
    config = kwargs.get("config")

    print("summarizing data step wise")
    # get a list of all DOKA output files:
    result_file_path, summary_folder, filelist_split, filelist = read_DOKAoutput_files(config=config)

