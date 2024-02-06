import lochness
from pathlib import Path
import sys
import pandas as pd
lochness_root = Path(lochness.__path__[0]).parent
scripts_dir = lochness_root / 'scripts'
test_dir = lochness_root / 'tests'
sys.path.append(str(scripts_dir))
sys.path.append(str(test_dir))

from lochness.utils.path_checker import nth_item_from_path, \
        ampscz_id_validate, update_interviews_transcript_check, \
        check_file_path_df, update_by_removing_unused_files, \
        update_eeg_check
from lochness.utils.source_check import collect_mediaflux_files_info, \
        get_subject_list_from_metadata


def test_update_interviews_transcript_check():
    from lochness.config import load
    config_loc = '/mnt/prescient/Prescient_production/config.yml'
    Lochness = load(config_loc)

    subject_id_list = get_subject_list_from_metadata(Lochness)
    ignore_id_list = []

    if Lochness.get('id_list_csv', False):
        # Prescient network read full subject list from RPMS
        check_only_subject_id_list = True
        unique_subjects = []
        for csv in Path(Lochness['RPMS_PATH']).glob('*csv'):
            try:
                [unique_subjects.append(x) for x in
                        pd.read_csv(csv)[Lochness['RPMS_id_colname']]
                        if x not in unique_subjects]
            except:
                pass
        ignore_id_list += [x for x in unique_subjects
                if x not in subject_id_list]
        ignore_id_list = [x for x in ignore_id_list if type(x) == str]

    if Path('mediaflux_df_test.csv').is_file():
        mediaflux_df = pd.read_csv('mediaflux_df_test.csv', index_col=0)
    else:
        mediaflux_df = collect_mediaflux_files_info(Lochness, ignore_id_list)
        mediaflux_df.to_csv('mediaflux_df_test.csv')

    df = mediaflux_df.copy()
    all_df = check_file_path_df(df, subject_id_list)

    df_tmp.to_csv('test.csv')
