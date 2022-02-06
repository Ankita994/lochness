from pathlib import Path
import os
import is_transferred_and_removed
import get_ok2remove_df_from_s3_log
import rm_transferred_files_under_phoenix

def test_get_source_path_load_s3_log():
    phoenix_root = Path('/opt/software/Pronet_data_sync/PHOENIX')
    # df_okay_to_remove = get_ok2remove_df_from_s3_log(phoenix_root,
                                                     # days_to_keep=15)
    # rm_transferred_files_under_phoenix(phoenix_root,
                                       # days_to_keep=15,
                                       # removed_df_loc='removed_files.csv',
                                       # new_phoenix_root='haha')


    Lochness = {'phoenix_root': phoenix_root}
    for root, dirs, files in os.walk(phoenix_root):
        for file in files:
            file_path = Path(root) / file
            is_removed = is_transferred_and_removed(Lochness, file_path, 'removed_files.csv')
            if is_removed:
                print(file_path)
