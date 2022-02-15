import os
import sys
import re
import json
import lochness
import logging
import requests
import lochness.net as net
import collections as col
import lochness.tree as tree
from pathlib import Path
import pandas as pd
import datetime
from typing import List, Union
import tempfile as tf
from lochness.redcap.process_piis import process_and_copy_db

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


logger = logging.getLogger(__name__)


def get_field_names_from_redcap(api_url: str,
                                api_key: str,
                                study_name: str) -> list:
    '''Return all field names from redcap database'''

    record_query = {
        'token': api_key,
        'content': 'exportFieldNames',
        'format': 'json',
    }

    # pull field names from REDCap for the study
    content = post_to_redcap(api_url,
                             record_query,
                             f'initializing data {study_name}')

    # load pulled information as list of dictionary : data
    with tf.NamedTemporaryFile(suffix='tmp.json') as tmpfilename:
        lochness.atomic_write(tmpfilename.name, content)
        with open(tmpfilename.name, 'r') as f:
            data = json.load(f)

    field_names = []
    for item in data:
        field_names.append(item['original_field_name'])

    return field_names


def initialize_metadata(Lochness: 'Lochness object',
                        study_name: str,
                        redcap_id_colname: str,
                        redcap_consent_colname: str,
                        multistudy: bool = True,
                        upenn: bool = False) -> None:
    '''Initialize metadata.csv by pulling data from REDCap for Pronet network

    Key arguments:
        Lochness: Lochness object
        study_name: Name of the study, str. eg) PronetLA
        redcap_id_colname: Name of the ID field name in REDCap, str.
        redcap_consent_colname: Name of the consent date field name in REDCap,
                                str.
        multistudy: True if the redcap repo contains multisite data, bool.
        upenn: True if upenn redcap is included in the source list, bool.
    '''
    # specific to DPACC project
    site_code_study = study_name[-2:]  # 'LA'
    project_name = study_name.split(site_code_study)[0]  # 'Pronet'

    # use redcap_project function to load the redcap keyrings for the project
    _, api_url, api_key = next(redcap_projects(
        Lochness, study_name, f'redcap.{project_name}'))

    # sources to add to the metadata, apart from REDCap, XNAT, and Box
    source_source_name_dict = {'mindlamp': ['Mindlamp', 'chrdig_lamp_id']}

    record_query = {'token': api_key,
                    'content': 'record',
                    'format': 'json',
                    'fields[0]': redcap_id_colname}

    # only pull source_names
    # mindlamp id is manually added to "chrdig_lamp_id" field
    field_num = 2
    for source, (source_name, source_field_name) in \
            source_source_name_dict.items():
        record_query[f"fields[{field_num}]"] = source_field_name

    # pull all records from the project's REDCap repo
    try:
        content = post_to_redcap(api_url,
                                 record_query,
                                 f'initializing data {study_name}')
    except:  # if subject ID field name are not set, above will raise error
        record_query = {
            'token': api_key,
            'content': 'record',
            'format': 'json',
        }
        content = post_to_redcap(api_url,
                                 record_query,
                                 f'initializing data {study_name}')

    # load pulled information as a list of dictionaries
    with tf.NamedTemporaryFile(suffix='tmp.json') as tmpfilename:
        lochness.atomic_write(tmpfilename.name, content)
        with open(tmpfilename.name, 'r') as f:
            data = json.load(f)

    df = pd.DataFrame()
    # extract subject ID and source IDs for each sources
    for item in data:
        if multistudy:  # filter out data from other sites
            site_code_redcap_id = item[redcap_id_colname][:2]
            if site_code_redcap_id != site_code_study:
                continue

        subject_dict = {'Subject ID': item[redcap_id_colname]}

        # Consent date
        try:
            subject_dict['Consent'] = item[redcap_consent_colname]
        except:
            subject_dict['Consent'] = '1900-01-01'

        # Redcap default information
        subject_dict['REDCap'] = \
                f'redcap.{project_name}:{item[redcap_id_colname]}'
        if upenn:
            subject_dict['REDCap'] += \
                    f';redcap.UPENN:{item[redcap_id_colname]}'  # UPENN REDCAP

        subject_dict['Box'] = f'box.{study_name}:{item[redcap_id_colname]}'
        subject_dict['XNAT'] = f'xnat.{study_name}:*:{item[redcap_id_colname]}'

        for source, (source_name, source_field_name) \
                in source_source_name_dict.items():
            # if mindlamp_id field is available in REDCap record
            source_id = item[source_field_name]
            if source_id != '':
                subject_dict[source_name] = \
                        f"{source}.{study_name}:{source_id}"
            else:
                pass

        df_tmp = pd.DataFrame.from_dict(subject_dict, orient='index')
        df = pd.concat([df, df_tmp.T])

    if len(df) == 0:
        logger.warn(f'There are no records for {site_code_study}')
        return

    # Each subject may have more than one arms, which will result in more than
    # single item for the subject in the redcap pulled `content`
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


def get_run_sheets_for_datatypes(json_path: Union[Path, str]) -> None:
    '''Extract run sheet information from REDCap JSON and save as csv file

    For each data types, there should be Run Sheets completed by RAs on REDCap.
    This information is extracted and saved as a csv flie in the 
        PHOENIX/PROTECTED/raw/
            {STUDY}/{DATATYPE}/{subject}.{study}.Run_sheet_{DATATYPE}.csv

    Key Arguments:
        - json_path: REDCap json path, Path.

    Returns:
        - None
    '''
    if not json_path.is_file():
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    if type(data) == list:  # most cases, because U24 has follow up data
        pass
    elif type(data) == dict:  # single timepoint cases
        data = [data]
    else:
        raise TypeError(f'Type of the data in {json_path} is not correct')


    raw_path = Path(json_path).parent.parent

    modality_fieldname_dict = {'eeg': 'chreeg_',
                               'actigraphy': 'chrax_',
                               'mri': 'chrmri_',
                               'phone': 'chrdig_',
                               'survey': 'chrpenn_'}
    for modality, fieldname in modality_fieldname_dict.items():
        modality_df = pd.DataFrame()
        raw_modality_path = raw_path / modality
        for data_num, data_timepoint in enumerate(data):
            modality_key_names = [x for x in data_timepoint.keys()
                    if fieldname in x.lower()]
            for _, modality_key_name in enumerate(modality_key_names):
                modality_df_tmp = pd.DataFrame({
                    'data_num': [data_num],
                    'field name': modality_key_name,
                    'field value': data_timepoint[modality_key_name]})
                modality_df = pd.concat([modality_df, modality_df_tmp])

        if 'field value' in modality_df.columns:
            # if all value is empty, don't load it
            if (modality_df['field value'] == '').all():
                continue

            elif (modality_df[modality_df['field value'] != ''][
                'field name'].str.contains('sheet_complete').all()):
                continue

            raw_modality_path.mkdir(exist_ok=True, parents=True)
            output_name = Path(json_path).name.split('.json')[0]

            if modality == 'survey':
                modality_df.to_csv(raw_modality_path /
                                   f'{output_name}.Run_sheet_PennCNB.csv')
            else:
                modality_df.to_csv(raw_modality_path /
                                   f'{output_name}.Run_sheet_{modality}.csv')



def check_if_modified(subject_id: str,
                      existing_json: str,
                      df: pd.DataFrame) -> bool:
    '''Check if subject data has been modified in the data entry trigger db

    Comparing unix times of the json modification and lastest redcap update
    '''

    json_modified_time = Path(existing_json).stat().st_mtime  # in unix time

    subject_df = df[df.record == subject_id]

    # if the subject does not exist in the DET_DB, return False
    if len(subject_df) < 1:
        return False

    lastest_update_time = subject_df.loc[
            subject_df['timestamp'].idxmax()].timestamp

    if lastest_update_time > json_modified_time:
        return True
    else:
        return False


def get_data_entry_trigger_df(Lochness: 'Lochness') -> pd.DataFrame:
    '''Read Data Entry Trigger database as dataframe'''
    if 'redcap' in Lochness:
        if 'data_entry_trigger_csv' in Lochness['redcap']:
            db_loc = Lochness['redcap']['data_entry_trigger_csv']
            if Path(db_loc).is_file():
                db_df = pd.read_csv(db_loc)
                try:
                    db_df['record'] = db_df['record'].astype(str)
                except KeyError:
                    db_df = pd.DataFrame({'record':[]})
                return db_df

    db_df = pd.DataFrame({'record':[]})
    # db_df = pd.DataFrame()
    return db_df


@net.retry(max_attempts=5)
def sync(Lochness, subject, dry=False):

    # load dataframe for redcap data entry trigger
    db_df = get_data_entry_trigger_df(Lochness)

    logger.debug(f'exploring {subject.study}/{subject.id}')
    deidentify = deidentify_flag(Lochness, subject.study)

    logger.debug(f'deidentify for study {subject.study} is {deidentify}')

    for redcap_instance, redcap_subject in iterate(subject):
        for redcap_project, api_url, api_key in redcap_projects(
                Lochness, subject.study, redcap_instance):
            # process the response content
            _redcap_project = re.sub(r'[\W]+', '_', redcap_project.strip())

            # default location to protected folder
            dst_folder = tree.get('surveys',
                                  subject.protected_folder,
                                  processed=False,
                                  BIDS=Lochness['BIDS'])
            fname = f'{redcap_subject}.{_redcap_project}.json'
            dst = Path(dst_folder) / fname

            # PII processed content to general processed
            proc_folder = tree.get('surveys',
                                   subject.general_folder,
                                   processed=True,
                                   BIDS=Lochness['BIDS'])

            proc_dst = Path(proc_folder) / fname

            # check if the data has been updated by checking the redcap data
            # entry trigger db
            if dst.is_file():
                if check_if_modified(redcap_subject, dst, db_df):
                    pass  # if modified, carry on
                else:
                    logger.debug(f"{subject.study}/{subject.id} "
                                 "No DET updates")
                    # break  # if not modified break

            logger.debug("Downloading REDCap data")
            _debug_tup = (redcap_instance, redcap_project, redcap_subject)

            if 'UPENN' in redcap_instance:
                # UPENN REDCap is set up with its own record_id, but have added
                # "session_subid" field to note AMP-SCZ ID
                redcap_subject_sl = redcap_subject.lower()
                record_query = {
                    'token': api_key,
                    'content': 'record',
                    'format': 'json',
                    'filterLogic': f"[session_subid] = '{redcap_subject}' or "
                                   f"[session_subid] = '{redcap_subject_sl}'"
                }

            else:
                record_query = {
                    'token': api_key,
                    'content': 'record',
                    'format': 'json',
                    'records': redcap_subject
                }

            if deidentify:
                # get fields that aren't identifiable and narrow record query
                # by field name
                metadata_query = {
                    'token': api_key,
                    'content': 'metadata',
                    'format': 'json'
                }

                content = post_to_redcap(api_url, metadata_query, _debug_tup)
                metadata = json.loads(content)
                field_names = []
                for field in metadata:
                    if field['identifier'] != 'y':
                        field_names.append(field['field_name'])
                record_query['fields'] = ','.join(field_names)

            # post query to redcap
            content = post_to_redcap(api_url, record_query, _debug_tup)

            # check if response body is nothing but a sad empty array
            if content.strip() == b'[]':
                logger.info(f'no redcap data for {redcap_subject}')
                continue

            if not dry:
                if not os.path.exists(dst):
                    logger.debug(f'saving {dst}')
                    lochness.atomic_write(dst, content)
                    get_run_sheets_for_datatypes(dst)
                    # process_and_copy_db(Lochness, subject, dst, proc_dst)
                    # update_study_metadata(subject, json.loads(content))
                    
                else:
                    # responses are not stored atomically in redcap
                    crc_src = lochness.crc32(content.decode('utf-8'))
                    crc_dst = lochness.crc32file(dst)

                    if crc_dst != crc_src:
                        logger.info('different - crc32: downloading data')
                        logger.warn(f'file has changed {dst}')
                        # lochness.backup(dst)
                        logger.debug(f'saving {dst}')
                        lochness.atomic_write(dst, content)

                        # Extract run sheet information
                        get_run_sheets_for_datatypes(dst)
                        # process_and_copy_db(Lochness, subject, dst, proc_dst)
                        # update_study_metadata(subject, json.loads(content))
                    else:
                        logger.info('No new update in newly downloaded '
                                    'content for {redcap_subject}. '
                                    'Not saving the data')
                        # update the dst file's mtime so it can prevent the
                        # same file being pulled from REDCap
                        # os.utime(dst)


class REDCapError(Exception):
    pass


def redcap_projects(Lochness, phoenix_study, redcap_instance):
    '''get redcap api_url and api_key for a phoenix study

    Key Arguments:
        Lochness: Lochness object.
        phoenix_study: name of the study, str. eg) PronetLA
        redcap_instance: name of the redcap field for the study in the keyring,
                         str. eg) redcap.PronetLA

    Yields:
        project: name of the redcap project field in the keyring file, str.
                 eg) "Pronet" when the lochness keyring file has
                     "redcap.Pronet" : {"URL": ***, API_TOKEN: ...}
        api_url: REDCap API url, str
        api_key: REDCap API key, str
    '''
    Keyring = Lochness['keyring']

    # Check for mandatory keyring items
    # part 1 - checking for REDCAP field right below the 'lochness' in keyring
    if 'REDCAP' not in Keyring['lochness']:
        raise KeyringError("lochness > REDCAP not found in keyring")

    # part 2 - check for study under 'REDCAP' field
    if phoenix_study not in Keyring['lochness']['REDCAP']:
        raise KeyringError(f'lochness > REDCAP > {phoenix_study}'
                           'not found in keyring')

    if redcap_instance not in Keyring['lochness']['REDCAP'][phoenix_study]:
        raise KeyringError(f'lochness > REDCAP > {phoenix_study} '
                           f'> {redcap_instance} not found in keyring')

    # part 3 - checking for redcap_instance
    if redcap_instance not in Keyring:
        raise KeyringError(f"{redcap_instance} not found in keyring")

    if 'URL' not in Keyring[redcap_instance]:
        raise KeyringError(f"{redcap_instance} > URL not found in keyring")

    if 'API_TOKEN' not in Keyring[redcap_instance]:
        raise KeyringError(f"{redcap_instance} > API_TOKEN "
                           " not found in keyring")

    # get URL
    api_url = Keyring[redcap_instance]['URL'].rstrip('/') + '/api/'

    # begin generating project,api_url,api_key tuples
    for project in Keyring['lochness']['REDCAP']\
            [phoenix_study][redcap_instance]:
        if project not in Keyring[redcap_instance]['API_TOKEN']:
            raise KeyringError(f"{redcap_instance} > API_TOKEN > {project}"
                               " not found in keyring")
        api_key = Keyring[redcap_instance]['API_TOKEN'][project]
        yield project, api_url, api_key


def post_to_redcap(api_url, data, debug_tup):
    r = requests.post(api_url, data=data, stream=True, verify=False)
    if r.status_code != requests.codes.OK:
        raise REDCapError(f'redcap url {r.url} responded {r.status_code}')
    content = r.content

    # you need the number bytes read before any decoding
    content_len = r.raw._fp_bytes_read

    # verify response content integrity
    if 'content-length' not in r.headers:
        logger.warn('server did not return a content-length header, '
                    f'can\'t verify response integrity for {debug_tup}')
    else:
        expected_len = int(r.headers['content-length'])
        if content_len != expected_len:
            raise REDCapError(
                    f'content length {content_len} does not match '
                    f'expected length {expected_len} for {debug_tup}')
    return content


class KeyringError(Exception):
    pass


def deidentify_flag(Lochness, study):
    ''' get study specific deidentify flag with a safe default '''
    value = Lochness.get('redcap', dict()) \
                    .get(study, dict()) \
                    .get('deidentify', False)

    # if this is anything but a boolean, just return False
    if not isinstance(value, bool):
        return False
    return value


def iterate(subject):
    '''generator for redcap instance and subject'''
    for instance, ids in iter(subject.redcap.items()):
        for id_inst in ids:
            yield instance, id_inst



def update_study_metadata(subject, content: List[dict]) -> None:
    '''update metadata csv based on the redcap content: source_id'''

    sources = ['XNAT', 'Box', 'Mindlamp', 'Mediaflux', 'Daris']

    orig_metadata_df = pd.read_csv(subject.metadata_csv)

    subject_bool = orig_metadata_df['Subject ID'] == subject.id
    subject_index = orig_metadata_df[subject_bool].index
    subject_series = orig_metadata_df.loc[subject_index]
    other_metadata_df = orig_metadata_df[~subject_bool]

    updated = False
    for source in sources:
        if f"{source.lower()}_id" in content[0]:  # exist in the redcap
            source_id = content[0][f"{source.lower()}_id"]
            if source not in subject_series:
                subject_series[source] = f'{source.lower()}.{source_id}'
                updated = True

            # subject already has the information
            elif subject_series.iloc[0][source] != \
                    f'{source.lower()}.{source_id}':
                subject_series.iloc[0][source] = \
                        f'{source.lower()}.{source_id}'
                updated = True
            else:
                pass

    if updated:
        new_metadata_df = pd.concat([other_metadata_df, subject_series])

        # overwrite metadata
        new_metadata_df.to_csv(subject.metadata_csv, index=False)
