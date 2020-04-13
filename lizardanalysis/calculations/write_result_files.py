# TODO: Needed results:
#           - GENERAL
#               - species, videoname, all individual results of the calculations
#           - SUMMARY
#               - species-wise, nb of videos, up count, down count, means of all calculations

def write_summary_result_files(config):
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

    try:
        os.makedirs(os.path.join(result_file_path, "analysis-summary"))
        print("folder for summary result files created")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    filelist = glob.glob(os.path.join(result_file_path, "*.csv"))
    print('filelist: ', filelist)
    filelist = [x.rsplit(os.sep, 1)[1] for x in filelist]
    print("flist after sep: ", filelist)

    # loop through all individual result files to generate summary
    # options: fort by species, and optional by direction
    # create overview plots and show in grid at the end

    print('DONE!!!')