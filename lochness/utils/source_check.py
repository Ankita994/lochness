import pandas as pd
from pathlib import Path
from typing import Union
import xnat
import pandas as pd
from lochness.config import load
from lochness.email import send_detail
from boxsdk import Client, OAuth2
from lochness.box import get_access_token, walk_from_folder_object, \
        get_box_object_based_on_name
from typing import List
from multiprocessing import Pool
from lochness.utils.path_checker import check_file_path_df, print_deviation
import tempfile as tf
from datetime import datetime
from pytz import timezone
from subprocess import Popen, DEVNULL, STDOUT
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


def check_list_all_xnat_subjects(keyring: dict) -> pd.DataFrame:
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
    folder_dict = {'PronetCA':147568280050, 'PronetCM':147569025780,
                   'PronetGA':147569449803, 'PronetHA':147568610087,
                   'PronetBI':147568078480, 'PronetKC':147568869324,
                   'PronetMU':147568909879, 'PronetMA':147568873738,
                   'PronetMT':147567624284, 'PronetSI':147568159676,
                   'PronetNL':147569038268, 'PronetNN':147567284495,
                   'PronetOR':147569330828, 'PronetPV':147568884538,
                   'PronetPA':147568159035, 'PronetPI':147568919154,
                   'PronetSL':147568683922, 'PronetSH':147568092207,
                   'PronetTE':147567344512, 'PronetIR':147568662381,
                   'PronetLA':147568723651, 'PronetSD':147568290916,
                   'PronetSF':147567284569, 'PronetNC':147568636984,
                   'PronetWU':147568356792, 'PronetYA':147567323985}

    # folder_dict = {'PronetYA':147568280050}
    box_keyrings = keyring['box.PronetLA']

    # run in parallel
    results = []
    def collect_out(df):
        results.append(df)

    pool = Pool(4)
    for site, site_num in folder_dict.items():
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


def send_source_qc_summary(qc_fail_df: pd.DataFrame,
                           lines,
                           Lochness: 'lochness') -> None:
    '''Send summary of qc failed files in sources'''
    title = 'List of files out of SOP'
    send_detail(
        Lochness,
        'Files on source out of SOP',
        f'Daily updates {datetime.now(tz).date()}',
        'Dear team,<br><br>Please find the list of files on the source, which '
        'do not follow the SOP. Please move, rename or delete the files '
        'according to the SOP. Please do not hesitate to get back to us. '
        '<br><br>Best wishes,<br>DPACC',
        qc_fail_df.to_html(index=False),
        lines,
        'Please let us know if any of the files above '
        'should have passed QC')


def collect_mediaflux_files_info(Lochness: 'lochness') -> pd.DataFrame:
    '''Collect list of files from mediaflux in a pandas dataframe'''
    mflux_cfg = Path(Lochness['phoenix_root']) / 'mflux.cfg'
    mf_remote_root = '/projects/proj-5070_prescient-1128.4.380'
    with tf.TemporaryDirectory() as tmpdir:
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


def check_source(Lochness: 'lochness') -> None:
    '''Check if there is any file that deviates from SOP'''

    if Lochness['project_name'] == 'Prescient':
        mediaflux_df = collect_mediaflux_files_info(Lochness)
        all_df = check_file_path_df(mediaflux_df)

    elif Lochness['project_name'] == 'Prescient':
        keyring = Lochness['keyring']

        # xnat
        xnat_df = check_list_all_xnat_subjects(keyring)

        # box
        box_files_df = collect_box_files_info(keyring)
        with tf.NamedTemporaryFile(delete=True) as f:
            box_files_df.to_csv(f.name, index=False)
            box_df = load_box_df(f.name)
            box_df_checked = check_file_path_df(box_df)

        # merge xnat and box check files
        all_df = pd.concat([xnat_df, box_df])

    else:
        return

    # select final_check failed files, and clean up
    qc_fail_df = all_df[
            (~all_df['final_check']) & 
            (all_df['site'].str.startswith('Prescient')) &
            (~all_df['file_name'].str.contains('.dcm|._dicom_series'))
            ]
    qc_fail_df['final_check'] = 'Incorrect'
    cols_to_show = ['file_path', 'site', 'subject', 'modality', 'final_check']
    qc_fail_df = qc_fail_df[cols_to_show]
    qc_fail_df.columns = ['File Path', 'Site', 'Subject',
                          'Data Type', 'Format']

    # temporary change email receipient
    Lochness['notify']['__global__'] = ['kevincho@bwh.harvard.edu']

    lines = []
    send_source_qc_summary(qc_fail_df, lines, Lochness)


if __name__ == '__main__':
    config_loc = '/mnt/prescient/Prescient_data_sync/config.yml'
    Lochness = load(config_loc)
    check_source(Lochness)




