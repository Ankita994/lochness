import lochness
from pathlib import Path
import sys
lochness_root = Path(lochness.__path__[0]).parent
scripts_dir = lochness_root / 'scripts'
test_dir = lochness_root / 'tests'
sys.path.append(str(scripts_dir))
sys.path.append(str(test_dir))

from lochness.utils.source_check import check_list_all_penn_cnb_subjects, \
        collect_mediaflux_files_info, get_subject_list_from_metadata

def test_upenn_inclusive_id():
    from lochness.config import load
    config_loc = '/mnt/ProNET/Lochness/config.yml'
    Lochness = load(config_loc)

    # get URL
    keyring = Lochness['keyring']

    subject_id_list = get_subject_list_from_metadata(Lochness)
    project_name = 'Pronet'
    keyring = Lochness['keyring']
    penn_cnb_df = check_list_all_penn_cnb_subjects(
            project_name, keyring, subject_id_list)

    print(penn_cnb_df)
    penn_cnb_df.to_csv('test.csv')
