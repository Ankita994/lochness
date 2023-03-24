from pathlib import Path
import os
import lochness.config as config
from lochness.cleaner import is_transferred_and_removed
from lochness.cleaner import get_ok2remove_df_from_s3_log
from lochness.cleaner import rm_transferred_files_under_phoenix
import pandas as pd

# pd.set_option('max_columns', 50)

def test_get_source_path_load_s3_log():
    phoenix_root = Path('/opt/software/Pronet_data_sync/PHOENIX')
    df_okay_to_remove = get_ok2remove_df_from_s3_log(phoenix_root,
                                                     days_to_keep=1)

    # rm_transferred_files_under_phoenix(phoenix_root,
                                       # days_to_keep=15,
                                       # removed_df_loc='removed_files.csv',
                                       # new_phoenix_root='haha')


    # Lochness = {'phoenix_root': phoenix_root}
    # for root, dirs, files in os.walk(phoenix_root):
        # for file in files:
            # file_path = Path(root) / file
            # is_removed = is_transferred_and_removed(Lochness,
                                                    # file_path,
                                                    # 'removed_files.csv')
            # if is_removed:
                # print(file_path)

def test_is_transferred_and_removed():
    file_path = Path('/mnt/prescient/Prescient_data_sync/PHOENIX/PROTECTED/PrescientME/raw/ME00005/mri/ME00005_MR_2021_12_08_1.zip')
    config_file = '/mnt/prescient/Prescient_data_sync/config.yml'
    Lochness = config.load(config_file, None)
    var = is_transferred_and_removed(Lochness, file_path)
    print(var)

