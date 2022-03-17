import pandas as pd
from pathlib import Path
from typing import Union, List
import xnat
import pandas as pd
from boxsdk import Client, OAuth2
from typing import List
from multiprocessing import Pool
import tempfile as tf
from datetime import datetime
from pytz import timezone
from subprocess import Popen, DEVNULL, STDOUT
from lochness.box import get_access_token, walk_from_folder_object, \
        get_box_object_based_on_name
from lochness.utils.path_checker import check_file_path_df, print_deviation
from lochness.config import load
from lochness.email import send_detail
tz = timezone('EST')


def get_xnat_credentials_from_config(config_loc:str) -> dict:
    '''Get xnat credentials from the config_loc linked keyring'''
    Lochness = load(config_loc)
    xnat_k = Lochness['keyring']['xnat.PronetLA']

    return xnat_k


def get_keyring(config_loc:str) -> dict:
    '''Get keyring dictionary from the encrypted keyring file'''
    Lochness = load(config_loc)
    return Lochness['keyring']  #['box.PronetLA']


def get_box_client_from_box_keyrings(box_k: dict) -> Client:
    '''Get box client object by logging into box using credentials'''
    api_token = get_access_token(box_k['CLIENT_ID'],
                                 box_k['CLIENT_SECRET'],
                                 box_k['ENTERPRISE_ID'])
    auth = OAuth2(
        client_id=box_k['CLIENT_ID'],
        client_secret=box_k['CLIENT_SECRET'],
        access_token=api_token)

    client = Client(auth)

    return client


def check_list_all_xnat_subjects(keyring: dict,
                                 subject_list: List[str]) -> pd.DataFrame:
    '''Return a dataframe of experiments for target_site'''
    xnat_k = keyring['xnat.PronetLA']
    session = xnat.connect(xnat_k['URL'],
                           user=xnat_k['USERNAME'],
                           password=xnat_k['PASSWORD'])

    project_to_check = []
    for i in session.projects:
        if 'Pronet' in i:
            project_to_check.append(i)

    df = pd.DataFrame()
    for matching_project in project_to_check:
        project = session.projects[matching_project]

        for num, (id, subject) in enumerate(project.subjects.items(), 1):
            for exp_id, experiment in subject.experiments.items():
                df_tmp = pd.DataFrame({
                    'file_path': [f'XNAT/{project.id}/{subject.label}/'
                                  f'{experiment.label}'],
                    'subject': subject.label,
                    'project': project.id,
                    'experiment': experiment.label,
                    'date': experiment.date})
                df = pd.concat([df, df_tmp])

    df['modality'] = 'MRI'

    df['subject_check'] = df['subject'].str.match('^[A-Za-z]{2}\d{5}$')
    df['site'] = df['project'].str.split('_').str[0]

    df['exist_in_db'] = df['subject'].str.upper().isin(
            subject_list).fillna(False)
    df.loc[df[df['exist_in_db']].index,
           'notes'] = 'Subject missing from database'

    df['site_check'] = df['project'].str.match('^Pronet[A-Z]{2}_\w+$')
    df['file_check'] = df['experiment'].str.match(
            '^[A-Za-z]{2}\d{5}_MR_\d{4}_\d{2}_\d{2}_\d$')
    df['final_check'] = df[[
        'subject_check', 'site_check', 'file_check']].all(axis=1)
    df.reset_index(drop=True, inplace=True)
    return df


def check_if_pattern_matches(df: pd.DataFrame) -> List[bool]:
    '''Check if each row of experiments column conforms to SOP'''
    return df['experiment'].str.match('[A-Z]{2}\d{5}_MR_\d{4}_\d{2}_\d{2}_\d')


def get_df_walk(root_dir_name: str, root_obj: 'box.Folder') -> pd.DataFrame:
    '''return dataframe of all files under root_obj

    Columns in the output:
        path: path of a file, str.
        mtime: time of modification, str.
        ctime: time of creation, str.
        contact: name of the creator, str.
        contact_email: email address of the creator, str.

    '''
    box_df = pd.DataFrame()
    for root, dirs, files in walk_from_folder_object(root_dir_name, root_obj):
        print(f'Looking into box: {root}')
        for file in files:
            file_get = file.get()
            mtime = file_get['content_modified_at']
            ctime = file_get['content_created_at']
            owner_name = file_get['created_by']['name']
            owner_email = file_get['created_by']['login']
            box_df_tmp = pd.DataFrame({
                'path': [f"{root}/{file.name}"],
                'contact': owner_name,
                'contact_email': owner_email,
                'mtime': mtime,
                'ctime': ctime})
            box_df = pd.concat([box_df, box_df_tmp])

        # if len(box_df) > 3:
            # break

    return box_df


def get_df_of_files_for_site(keyring, site):
    '''Get a dataframe of all files under box for a site'''
    client = get_box_client_from_box_keyrings(keyring)

    root_dir = client.folder(folder_id=127552835799).get()
    study_root_obj = get_box_object_based_on_name(client,
                                                  site,
                                                  127552835799)
    df = get_df_walk(f'/ProNET/{site}', study_root_obj)

    return df


def collect_box_files_info(keyring) -> pd.DataFrame:
    '''Box clean up function'''
    study_name_list = ['PronetCA', 'PronetCM', 'PronetGA', 'PronetHA',
                       'PronetBI', 'PronetKC', 'PronetMU', 'PronetMA',
                       'PronetMT', 'PronetSI', 'PronetNL', 'PronetNN',
                       'PronetOR', 'PronetPV', 'PronetPA', 'PronetPI',
                       'PronetSL', 'PronetSH', 'PronetTE', 'PronetIR',
                       'PronetLA', 'PronetSD', 'PronetSF', 'PronetNC',
                       'PronetWU', 'PronetYA']

    # study_name_list = ['PronetYA']
    box_keyrings = keyring['box.PronetLA']

    # run in parallel
    results = []
    def collect_out(df):
        results.append(df)

    pool = Pool(10)
    for site in study_name_list:
        pool.apply_async(get_df_of_files_for_site,
                         args=(box_keyrings, site,),
                         callback=collect_out,
                         error_callback=print)
    pool.close()
    pool.join()

    df = pd.concat(results)
    df.sort_values(by='path').reset_index(
            drop=True, inplace=True)

    return df


def load_mediaflux_df(csv_loc: Union[Path, str]) -> pd.DataFrame:
    '''Load csv file created from unimelb-mf-check'''
    diff_df = pd.read_csv(csv_loc)
    df = diff_df[['SRC_PATH']].dropna().copy()
    df.columns = ['file_path']
    df['file_path'] = df.file_path.str.split(
            'asset:/projects/proj-5070_prescient-1128.4.380/').str[1]

    return df


def load_box_df(csv_loc: Union[Path, str]) -> pd.DataFrame:
    '''Load csv file created from collect_box_files_info'''
    diff_df = pd.read_csv(csv_loc)
    df = diff_df[['path']].dropna().copy()
    df.columns = ['file_path']
    df['file_path'] = df.file_path.str.split('/ProNET/').str[1]

    return df


def highlight_incorrect(s):
    '''Highlight incorrect format cells'''
    return ['color: #d9544d' if x else 'color: black' for x in s=='Incorrect']


def send_source_qc_summary(qc_fail_df: pd.DataFrame,
                           lines,
                           Lochness: 'lochness') -> None:
    '''Send summary of qc failed files in sources'''
    title = 'List of files out of SOP'
    table_str = ''
    for site, x in qc_fail_df.groupby('Site'):
        table_str += f'<h2>{site}</h2>'
        for dt, y in x.groupby('Data Type'):
            table_str += f'<h4>{site} - {dt}</h4>'
            table_str += y.to_html(index=False)
        table_str += '<br>'

    send_detail(
        Lochness,
        Lochness['sender'],
        Lochness['file_check_notify'],
        'Files on source out of SOP',
        f'Daily updates {datetime.now(tz).date()}',
        'Dear team,<br><br>Please find the list of files on the source, which '
        'do not follow the SOP. Please move, rename or delete the files '
        'according to the SOP. Please do not hesitate to get back to us. '
        '<br><br>Best wishes,<br>DPACC<br><br><br>',
        table_str,
        lines,
        'Please let us know if any of the files above should have passed QC'
        )


def collect_mediaflux_files_info(Lochness: 'lochness') -> pd.DataFrame:
    '''Collect list of files from mediaflux in a pandas dataframe'''
    mflux_cfg = Path(Lochness['phoenix_root']) / 'mflux.cfg'
    mf_remote_root = '/projects/proj-5070_prescient-1128.4.380'
    with tf.TemporaryDirectory() as tmpdir:
        print('Getting mediaflux information')
        diff_path = Path(tmpdir) / 'diff.csv'
        cmd = (' ').join(['unimelb-mf-check',
                          f'--mf.config {mflux_cfg}',
                          '--nb-retries 5',
                          '--direction down', tmpdir,
                          mf_remote_root,
                          f'-o {diff_path}'])
        
        p = Popen(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
        p.wait()

        mediaflux_df = load_mediaflux_df(diff_path)
        return mediaflux_df


def get_subject_list_from_metadata(Lochness: 'lochness') -> List[str]:
    '''Get list of subjects form metadata under GENERAL directories'''
    general_path = Path(Lochness['phoenix_root']) / 'GENERAL'
    metadata_file_paths = general_path.glob('*/*_metadata.csv')

    subject_id_list = []
    for metadata_file in metadata_file_paths:
        subject_id_list += pd.read_csv(metadata_file)['Subject ID'].to_list()

    return subject_id_list


def check_source(Lochness: 'lochness', test: bool = False) -> None:
    '''Check if there is any file that deviates from SOP'''

    subject_id_list = get_subject_list_from_metadata(Lochness)

    if Lochness['project_name'] == 'Prescient':
        db_string = 'RPMS'
        mediaflux_df = collect_mediaflux_files_info(Lochness)
        all_df = check_file_path_df(mediaflux_df, subject_id_list)
        all_df = all_df[all_df['site'].str.startswith('Prescient')]

    elif Lochness['project_name'] == 'ProNET':
        db_string = 'REDCap'
        keyring = Lochness['keyring']

        # xnat
        print('Loading data list from XNAT')
        xnat_df = check_list_all_xnat_subjects(keyring, subject_id_list)

        # box
        print('Loading data list from BOX')
        tmp_box_db = Path(Lochness['phoenix_root']) / \
                '.tmp_box_source_files.csv'
        if test:
            box_files_df = pd.read_csv(tmp_box_db)
        else:
            box_files_df = collect_box_files_info(keyring)
            box_files_df.to_csv(tmp_box_db)

        with tf.NamedTemporaryFile(delete=True) as f:
            box_files_df.to_csv(f.name, index=False)
            box_df = load_box_df(f.name)
            box_df_checked = check_file_path_df(box_df, subject_id_list)

        # merge xnat and box check files
        all_df = pd.concat([xnat_df, box_df])

    else:
        return


    # select final_check failed files, and clean up
    qc_fail_df = all_df[
            (~all_df['final_check']) | 
            (~all_df['exist_in_db']) |
            (~all_df['subject_check'])
            # (~all_df['file_name'].str.contains('.dcm|._dicom_series'))
            ]

    qc_fail_df['subject_check'] = qc_fail_df['subject_check'].map(
            {True: f'Correct', False: f'Incorrect'})

    qc_fail_df['exist_in_db'] = qc_fail_df['exist_in_db'].map(
            {True: f'Exist in {db_string}', False: f'Missing in {db_string}'})

    qc_fail_df['final_check'] = qc_fail_df['final_check'].map(
            {True: 'Correct', False: 'Incorrect'})

    cols_to_show = ['file_path', 'site', 'subject', 'modality',
                    'subject_check', 'exist_in_db', 'final_check']

    qc_fail_df = qc_fail_df[cols_to_show]
    qc_fail_df.columns = ['File Path', 'Site', 'Subject',
                          'Data Type', 'AMPSCZ-ID checksum',
                          'Subject ID in database', 'Format']

    lines = []
    send_source_qc_summary(qc_fail_df, lines, Lochness)


if __name__ == '__main__':
    # testing purposes
    # config_loc = '/mnt/prescient/Prescient_data_sync/config.yml'
    config_loc = '/opt/software/Pronet_data_sync/config.yml'
    Lochness = load(config_loc)
    Lochness['file_check_notify']['__global__'] = ['kevincho@bwh.harvard.edu']
    check_source(Lochness, test=True)
