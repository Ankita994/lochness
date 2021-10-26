import os
import yaml
import lochness
import logging
import zipfile
import shutil
from pathlib import Path
import tempfile as tf
import collections as col
import lochness.net as net
import lochness.tree as tree
from typing import List, Dict
import pandas as pd
import re
from lochness.redcap.process_piis import process_and_copy_db


yaml.SafeDumper.add_representer(
    col.OrderedDict, yaml.representer.SafeRepresenter.represent_dict)
logger = logging.getLogger(__name__)


def get_rpms_database(rpms_root_path: str) -> Dict[str, pd.DataFrame]:
    '''Return dictionary of RPMS database in pandas dataframes

    Based on the date in the file name, the most recent csv file exported by
    the RPMS is loaded as a dictionary to be stored in the phoenix directory.
    Other old csv files are moved to a temporary directory.

    Key arguments:
        rpms_root_path: root of the RPMS sync directory, str.

    Returns:
        all_df_dict: all measures loaded as pandas dataframe in dict.
                     key: name of the measure extracted from the file name.
                     value: pandas dataframe of the measure database
    '''
    all_df_dict = {}
    measure_date_dict = {}

    rpms_old_files_root = Path(rpms_root_path) / 'old_files'
    rpms_old_files_root.mkdir(exist_ok=True)
    
    measure_file_df = pd.DataFrame()
    for measure_file in Path(rpms_root_path).glob('*csv'):
        # measure_name = measure_file.name.split('.')[0]
        rpms_pattern = re.compile(
                r'PrescientStudy_Prescient_(\w+)_(\d{2}.\d{2}.\d{4}).csv',
                re.IGNORECASE)
        pattern_search = re.search(rpms_pattern, Path(measure_file).name)
        measure_name = pattern_search.group(1)
        measure_file_date = pd.to_datetime(pattern_search.group(2),
                                           dayfirst=True)
        measure_file_df_tmp = pd.DataFrame({
            'measure_file': [measure_file],
            'measure_name': measure_name,
            'measure_file_date': measure_file_date})
        measure_file_df = pd.concat([measure_file_df, measure_file_df_tmp])
    
    for measure_name, table in measure_file_df.groupby('measure_name'):
        n = 0
        for _, row in table.sort_values(
                'measure_file_date', ascending=False).iterrows():
            if n == 0:
                try:
                    df_tmp = pd.read_csv(row.measure_file)
                except pd.errors.EmptyDataError:  # ignore csv is empty
                    continue

                all_df_dict[measure_name] = df_tmp
                measure_date_dict[measure_name] = row.measure_file_date
            else:
                shutil.move(row.measure_file,
                            rpms_old_files_root / row.measure_file.name)
            n += 1

    return all_df_dict


def initialize_metadata(Lochness: 'Lochness object',
                        study_name: str,
                        rpms_id_colname: str,
                        rpms_consent_colname: str,
                        multistudy: bool = True,
                        upenn: bool = False) -> None:
    '''Initialize metadata.csv by pulling data from RPMS for Prescient project

    Key arguments:
        Lochness: Lochness object
        study_name: Name of the study, str.
        rpms_id_colname: Name of the ID field name in RPMS, str.
        rpms_consent_colname: Name of the consent date field name in RPMS,
                                str.
        multistudy: True if the rpms repo contains more than one study's data
        upenn: True if upenn redcap is included in the source list, bool.

    Note:
        Currently, this function only adds REDCap information for the UPENN
        Cognitive battery REDCap, and does not support adding other redcap
        sources into the metadata.
    '''
    rpms_root_path = Lochness['RPMS_PATH']

    # get list of csv files from the rpms root
    all_df_dict = get_rpms_database(rpms_root_path)

    df = pd.DataFrame()

    # all_df_dict - key: name of measure, value: pd.DataFrame of the whole file
    for measure, df_measure_all_subj in all_df_dict.items():
        # get the site information from the study name, eg. PrescientAD
        site_code_study = study_name[-2:]  # 'AD'
        project_name = study_name.split(site_code_study)[0]  # 'Prescient'

        # loop through each line of the RPMS database
        for index, df_measure in df_measure_all_subj.iterrows():
            if multistudy:
                # site of the subject for the line
                site_code_rpms_id = df_measure[rpms_id_colname][:2]

                # if the subject does not belong to the site, pass it
                print(site_code_rpms_id)
                if site_code_rpms_id != site_code_study:
                    continue

            subject_dict = {'Subject ID': df_measure[rpms_id_colname]}

            # Consent date
            if rpms_consent_colname in df_measure:
                subject_dict['Consent'] = df_measure[rpms_consent_colname]
            else:
                subject_dict['Consent'] = '1988-09-16'  # pseudo-random date

            # mediaflux source has its foldername as its subject ID
            subject_dict['RPMS'] = f'rpms.{study_name}:' + \
                                   df_measure[rpms_id_colname]
            subject_dict['Mediaflux'] = f'mediaflux.{study_name}:' + \
                                        df_measure[rpms_id_colname]

            # if mindlamp_id exists in the rpms table
            if 'mindlamp_id' in df_measure:
                subject_dict['mindlamp'] = f'mindlamp.{study_name}:' \
                        + df_measure[f'mindlamp_id']

            if upenn:
                subject_dict['REDCap'] = \
                    'redcap.UPENN:' + df_measure[rpms_id_colname]


            df_tmp = pd.DataFrame.from_dict(subject_dict, orient='index')
            df = pd.concat([df, df_tmp.T])


    # Each subject may have more than one arms, which will result in more than
    # single item for the subject in the RPMS pulled `content`
    # remove empty lables
    df_final = pd.DataFrame()
    for _, table in df.groupby(['Subject ID']):
        pad_filled = table.fillna(
                method='ffill').fillna(method='bfill').iloc[0]
        df_final = pd.concat([df_final, pad_filled], axis=1)
    df_final = df_final.T

    # register all of the lables as active
    df_final['Active'] = 1

    # reorder columns
    main_cols = ['Active', 'Consent', 'Subject ID']
    df_final = df_final[main_cols + \
            [x for x in df_final.columns if x not in main_cols]]

    general_path = Path(Lochness['phoenix_root']) / 'GENERAL'
    metadata_study = general_path / study_name / f"{study_name}_metadata.csv"

    df_final.to_csv(metadata_study, index=False)


def get_subject_data(all_df_dict: Dict[str, pd.DataFrame],
                     subject: object,
                     id_colname: str) -> Dict[str, pd.DataFrame]:
    '''Get subject data from the pandas dataframes in the dictionary'''

    subject_df_dict = {}
    for measure, measure_df in all_df_dict.items():
        measure_df[id_colname] = measure_df[id_colname].astype(str)
        subject_df = measure_df[measure_df[id_colname] == subject.id]
        subject_df_dict[measure] = subject_df

    return subject_df_dict


@net.retry(max_attempts=5)
def sync(Lochness, subject, dry=False):
    logger.debug(f'exploring {subject.study}/{subject.id}')

    # for each subject
    subject_id = subject.id
    study_name = subject.study
    rpms_root_path = Lochness['RPMS_PATH']

    # source data
    all_df_dict = get_rpms_database(rpms_root_path)
    subject_df_dict = get_subject_data(all_df_dict,
                                       subject,
                                       Lochness['RPMS_id_colname'])

    for measure, source_df in subject_df_dict.items():
        # target data
        dirname = tree.get('surveys',
                           subject.protected_folder,
                           processed=False,
                           BIDS=Lochness['BIDS'])
        target_df_loc = Path(dirname) / f"{subject_id}_{measure}.csv"

        proc_folder = tree.get('surveys',
                               subject.general_folder,
                               processed=True,
                               BIDS=Lochness['BIDS'])
        proc_dst = Path(proc_folder) / f"{subject_id}_{measure}.csv"

        # load the time of the lastest data pull from daris
        # estimated from the mtime of the zip file downloaded
        if Path(target_df_loc).is_file():
            latest_pull_mtime = target_df_loc.stat().st_mtime
        else:
            latest_pull_mtime = 0

        # if last_modified date > latest_pull_mtime, pull the data
        source_df['LastModifiedDate'] = pd.to_datetime(
                source_df['LastModifiedDate'])
        if not source_df['LastModifiedDate'].max() > \
                pd.to_datetime(latest_pull_mtime):
            print('No new updates')
            break

        if not dry:
            Path(dirname).mkdir(exist_ok=True)
            os.chmod(dirname, 0o0755)
            source_df.to_csv(target_df_loc, index=False)
            os.chmod(target_df_loc, 0o0755)
            # process_and_copy_db(Lochness, subject, target_df_loc, proc_dst)


def update_study_metadata(subject, content: List[dict]) -> None:
    '''update metadata csv based on the rpms content: source_id'''

    sources = ['XNAT', 'Box', 'Mindlamp', 'Mediaflux', 'Daris']

    orig_metadata_df = pd.read_csv(subject.metadata_csv)

    subject_bool = orig_metadata_df['Subject ID'] == subject.id
    subject_index = orig_metadata_df[subject_bool].index
    subject_series = orig_metadata_df.loc[subject_index]
    other_metadata_df = orig_metadata_df[~subject_bool]

    updated = False
    for source in sources:
        if f"{source.lower()}_id" in content[0]:  # exist in the rpms
            source_id = content[0][f"{source.lower()}_id"]
            if source not in subject_series:
                subject_series[source] = f'{source.lower()}.{source_id}'
                updated = True

            # subject already has the information
            elif subject_series.iloc[0][source] != f'{source.lower()}.{source_id}':
                subject_series.iloc[0][source] = \
                        f'{source.lower()}.{source_id}'
                updated = True
            else:
                pass

    if updated:
        new_metadata_df = pd.concat([other_metadata_df, subject_series])

        # overwrite metadata
        new_metadata_df.to_csv(subject.metadata_csv, index=False)

