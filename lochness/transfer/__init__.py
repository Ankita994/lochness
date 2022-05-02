from typing import List
import re
from pathlib import Path
from datetime import datetime
import os
import pandas as pd
import subprocess
from time import time
from datetime import datetime
import tempfile as tf
import sys
import paramiko
import tarfile
import shutil
import logging
from lochness import keyring

from typing import List, Tuple

logger = logging.getLogger(__name__)


def get_updated_files(phoenix_root: str,
                      timestamp_start: int,
                      timestamp_end: int,
                      general_only: bool = True) -> List[Path]:
    '''Return list of file paths updated between time window using GNU find

    In order to compress the new files with the original structure from the
    PHOENIX root, the absolute paths returned by GNU find is changed to
    relative path from the PHOENIX root.

    Key arguments:
        phoenix_root: PHOENIX root, str.
        timestamp_start: start of the GNU find search window in timestamp, int.
        timestamp_end: end of the GNU find search window in timestamp, int.
        general_only: only searches new files under GENERAL directory, bool.

    Returns:
        file_paths_relative: relative paths of new files, list of Path objects.

    '''
    date_time_start = datetime.fromtimestamp(timestamp_start).replace(
            microsecond=0)
    date_time_end = datetime.fromtimestamp(timestamp_end).replace(
            microsecond=0)

    if general_only:
        find_command = f'find {phoenix_root} ' \
                       f'-path {phoenix_root}/PROTECTED -prune -o ' \
                       f'\( -type f ' \
                       f'-newermt "{date_time_start}" ' \
                       f'! -newermt "{date_time_end}" \)'
    else:
        find_command = f'find {phoenix_root} ' \
                       f'-type f ' \
                       f'-newermt "{date_time_start}" ' \
                       f'! -newermt "{date_time_end}"'

    proc = subprocess.Popen(find_command, shell=True, stdout=subprocess.PIPE)
    proc.wait()

    outs, _ = proc.communicate()

    file_paths_absolute = outs.decode().strip().split('\n')
    file_paths_relative = [Path(x).relative_to(Path(phoenix_root).parent) for x
                           in file_paths_absolute]

    if general_only:
        # remove the PROTECTED DIR
        file_paths_relative = [x for x in file_paths_relative
                               if x.name != 'PROTECTED']

    return file_paths_relative


def compress_list_of_files(phoenix_root: str,
                           file_list: list,
                           out_tar_ball: str) -> None:
    '''Compress list of files using tar

    In order to compress the files in the original structure from the
    PHOENIX root, the function takes relative paths from the parent of the
    PHOENIX directory. Therefore, the tar execution location is changed to the
    parental directory of the PHOENIX root, and changed back after completing
    the compression.


    Key arguments:
        phoenix_root: PHOENIX directory
        file_list: list of file paths relative to parental directory of
                   PHOENIX root, list of str.
        out_tar_ball: tar file to save
    eg)
    ```
    file_list = ['PHOENIX/GENERAL/StudyA/StudyA_metadata.csv',
                 'PHOENIX/GENERAL/StudyB/StudyB_metadata.csv']
    ```

    PHOENIX/
    └── GENERAL
        ├── StudyA
        │   └── StudyA_metadata.csv
        └── StudyB
            └── StudyB_metadata.csv

    Read docstring for get_updated_files().
    '''

    # convert the out_tar_ball to absolute path
    out_tar_ball_absolute = Path(out_tar_ball).absolute()

    # move to parent directory of the root
    pwd = os.getcwd()
    os.chdir(Path(phoenix_root).parent)

    tar = tarfile.open(out_tar_ball_absolute, "w")
    for file_path in file_list:
        tar.add(file_path)
    tar.close()

    # move back to original directory
    os.chdir(pwd)


def get_ts_and_db(timestamp_db: str) -> Tuple[float, float, pd.DataFrame]:
    '''Get timestamp for the last data compression, current time and database

    Key arguments:
        timestamp_db: path of a csv file, which contains timestamp of each
                      lochness to lochness sync attempt (compression), str.
                      eg) lochness_sync_history.csv
                      timestamp
                      1621470407.030176
                      1621470455.6350138

    Returns:
        last_compress_timestamp: the timestamp for the last data compression.
                                 If the compress_db does not exist, a pseudo-
                                 random timestamp is returned to execute sync
                                 for all of the data under PHOENIX.
        now: timestamp for the current time
        compress_df: table with the history of data compression including
                     the current time stamp.
    '''
    tmp_timestamp = 590403600   # psedu-random timestamp in the past 1988-09-16
    if Path(timestamp_db).is_file():
        compress_df = pd.read_csv(timestamp_db, index_col=0)
        try:
            last_compress_timestamp = compress_df['timestamp'].max()
        except KeyError:
            last_compress_timestamp = tmp_timestamp
    else:
        compress_df = pd.DataFrame({'timestamp': [tmp_timestamp]})
        last_compress_timestamp = tmp_timestamp

    # get current time and update the database
    now = time()
    compress_df = pd.concat([compress_df,
                             pd.DataFrame({'timestamp': [now]})])

    return last_compress_timestamp, now, compress_df


def compress_new_files(compress_db: str, phoenix_root: str,
                       out_tar_ball: str, general_only: bool = True) -> None:
    '''Find a list of new files from the last lochness to lochness sync

    Key arguments:
        compress_db: path of a csv file, which contains timestamp of each
                     lochness to lochness sync attempt (compression), str.
                     eg) lochness_sync_history.csv
                     timestamp
                     1621470407.030176
                     1621470455.6350138
        phoenix_root: PHOENIX root, str.
        out_tar_ball: compressed tarball output path, str.
        general_only: only compress the data under GENERAL if True, bool.

    Returns:
        None
    '''
    last_compress_timestamp, now, compress_df = get_ts_and_db(compress_db)

    # find new files and zip them
    new_file_lists = get_updated_files(phoenix_root,
                                       last_compress_timestamp,
                                       now,
                                       general_only)

    compress_list_of_files(phoenix_root, new_file_lists, out_tar_ball)

    # save database when the process completes
    compress_df.to_csv(compress_db, index=False)


def send_data_over_sftp(Lochness, file_to_send: str):
    '''Send data over sftp'''

    sftp_keyring = Lochness['keyring']['lochness_sync']
    host = sftp_keyring['HOST']
    username = sftp_keyring['USERNAME']
    password = sftp_keyring['PASSWORD']
    path_in_host = sftp_keyring['PATH_IN_HOST']
    port = sftp_keyring['PORT']

    transport = paramiko.Transport((host, int(port)))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.put(file_to_send, str(Path(path_in_host) / Path(file_to_send).name))
    sftp.close()
    transport.close()


def lochness_to_lochness_transfer_sftp(Lochness, general_only: bool = True):
    '''Lochness to Lochness transfer

    Key arguments:
        Lochness: Lochness config.load object
        general_only: only searches new files under GENERAL directory, bool.
                      default = True.
    '''
    with tf.NamedTemporaryFile(suffix='tmp.tar',
                               delete=False,
                               dir='.') as tmpfilename:
        # compress
        compress_new_files(Lochness['lochness_sync_history_csv'],
                           Lochness['phoenix_root'],
                           tmpfilename.name,
                           general_only)

        # send to remote server
        send_data_over_sftp(Lochness, tmpfilename.name)


def lochness_to_lochness_transfer_rsync(Lochness, general_only: bool = True):
    '''Lochness to Lochness transfer using rsync

    Key arguments:
        Lochness: Lochness config.load object
        general_only: only searches new files under GENERAL directory, bool.
                      default = True.

    Requirements:
        In the keyring file, add following information.

        "rsync": {
            "ID": "RSYNC_SERVER_ID",
            "SERVER": "RSYNC_SERVER_ADDRESS",
            "PASSWORD": "RSYNC_SERVER_PASSWORD",
            "PHOENIX_PATH_RSYNC": "PHOENIX/PATH/RSYNC"
            }

            - PHOENIX/PATH/RSYNC must exist in the RSYNC target server


        The section above will add following information to the Lochness obj.
            Lochness['keyring'][f'rsync']['ID']
            Lochness['keyring'][f'rsync']['SERVER']
            Lochness['keyring'][f'rsync']['PASSWORD']
            Lochness['keyring'][f'rsync']['PHOENIX_PATH_RSYNC']
    '''

    rsync_id, rsync_server, rsync_password, phoenix_path_rsync = \
            keyring.rsync_token(Lochness, 'rsync')

    source_directory = Path(Lochness["phoenix_root"]) / 'GENERAL' \
            if general_only else Lochness["phoenix_root"]

    phoenix_path_rsync = Path(phoenix_path_rsync) / 'GENERAL' \
            if general_only else Lochness['phoenix_root']

    command = f'rsync -avz \
            {source_directory}/ \
            {rsync_id}@{rsync_server}:{phoenix_path_rsync}'

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    proc.wait()

    outs, _ = proc.communicate()


def lochness_to_lochness_transfer_s3(Lochness, general_only: bool = True):
    '''Lochness to Lochness transfer using aws s3 sync

    Key arguments:
        Lochness: Lochness config.load object
        general_only: only searches new files under GENERAL directory, bool.
                      default = True.

    Requirements:
        - AWS CLI needs to be set with the correct credentials before executing
        this module.
            $ aws configure
        - s3 bucket needs to be linked to the ID
        - The name of the s3 bucket needs to be in the config.yml
            eg) AWS_BUCKET_NAME: ampscz-dev
                AWS_BUCKET_PHOENIX_ROOT: TEST_PHOENIX_ROOT

    '''

    s3_bucket_name = Lochness['AWS_BUCKET_NAME']
    s3_phoenix_root = Lochness['AWS_BUCKET_ROOT']

    source_directory = Path(Lochness["phoenix_root"]) / 'GENERAL' \
            if general_only else Lochness["phoenix_root"]

    s3_phoenix_root = Path(s3_phoenix_root) / 'GENERAL' \
            if general_only else Lochness['phoenix_root']

    command = f'aws s3 sync \
            {source_directory}/ \
            s3://{s3_bucket_name}/{s3_phoenix_root} --delete'

    logger.debug('Executing aws s3 sync function')

    # save aws 3 sync cmd stdout to a file
    s3_sync_stdout = Path(Lochness['phoenix_root']) / 'aws_s3_sync_stdouts.log'
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(s3_sync_stdout, 'a') as fp:
        command_str = '\n'.join([f'{current_time} {x}' for x in
                            os.popen(command).read().split('\n')])
        fp.write(command_str)

    logger.debug(command_str)
    logger.debug('aws rsync completed')


def create_s3_transfer_table(Lochness, rewrite=False) -> None:
    '''Extract s3 transfer information from the lochness log file

    Key arguments:
        Lochness: lochness object
        rewrite: rewrite s3_log.csv if True, bool

    Uses timestamp from the Lochness log file to create an s3_log.csv file under
    PHOENIX root. This csv file has the following columns:
        - timestamp
        - source
        - destination
        - filename
        - protected
        - study
        - processed
        - subject
        - datatypes
        - ctime

    If s3_log.csv file exists, it loads the latest timepoint from the csv
    file and appends rows of more recent data transfer information to
    that file.
    '''
    log_file = Lochness['log_file']
    log_file = Path(Lochness['phoenix_root']) / 'aws_s3_sync_stdouts.log'
    out_file = Path(Lochness['phoenix_root']) / 's3_log.csv'

    if Path(out_file).is_file() and not rewrite:
        df_prev = pd.read_csv(out_file, index_col=0)
        max_ts_prev_df = pd.to_datetime(df_prev['timestamp']).max()
    else:
         df_prev = pd.DataFrame()
         max_ts_prev_df = pd.to_datetime('2000-01-01')

    df = pd.DataFrame()
    with open(log_file, 'r') as fp:
        for line in fp.readlines():
            ts = re.search(r'^(\S+ \w+:\w+:\w+)', line).group(1)
            ts = pd.to_datetime(ts)
            more_recent = ts > max_ts_prev_df

            if line.startswith(f'{ts} upload: '):
                if not more_recent:
                    continue
                try:
                    source = re.search(r'upload: (\S+)', line).group(1)
                     # do not save metadata.csv update since it
                     # gets updated every pull
                    if 'metadata.csv' in source:
                        continue
                    target = re.search(r'upload: (\S+) to (\S+)',
                                       line).group(2)

                    df_tmp = pd.DataFrame({'timestamp': [ts],
                                           'source': Path(source),
                                           'destination': Path(target)})

                    df = pd.concat([df, df_tmp])
                except AttributeError:
                    pass

    if len(df) == 0:
        print('No new data has been transferred to s3 bucket since last'
              's3 sync according to the s3_log database')
        return

    # register datatypes, study and subject
    df['filename'] = df['source'].apply(lambda x: x.name)
    df['protected'] = df['source'].apply(lambda x: x.parts[1])
    df['study'] = df['source'].apply(lambda x: x.parts[2])
    df['processed'] = df['source'].apply(lambda x: x.parts[3])
    df['subject'] = df['source'].apply(lambda x: x.parts[4]
                                       if len(x.parts) > 4 else '')
    df['datatypes'] = df['source'].apply(lambda x: x.parts[5]
                                         if len(x.parts) > 5 else '')

    # add ctime
    df['ctime'] = df['source'].apply(lambda x: \
            datetime.fromtimestamp(
                os.path.getctime(Path(Lochness['phoenix_root']).parent / x)))
    df['ctime'] = pd.to_datetime(df['ctime'])

    # clean up rows for metadata.csv
    df.loc[df[df['processed'].str.contains('metadata.csv')].index,
           'processed'] = ''
    df.timestamp = pd.to_datetime(df.timestamp)

    # append the df for new transfers to df_prev
    df = pd.concat([df_prev, df.reset_index().drop('index', axis=1)])

    # save outputs
    df.to_csv(out_file)


def lochness_to_lochness_transfer_s3_protected(Lochness):
    '''Lochness to Lochness transfer using aws s3 sync for protected data

    Key arguments:
        Lochness: Lochness config.load object

    Requirements:
        - AWS CLI needs to be set with the correct credentials before executing
        this module.
            $ aws configure
        - s3 bucket needs to be linked to the ID
        - The name of the s3 bucket needs to be in the config.yml
            eg) AWS_BUCKET_NAME: ampscz-dev
                AWS_BUCKET_PHOENIX_ROOT: TEST_PHOENIX_ROOT

    Notes:
        - do not share .mp3 files from phone data
    '''

    s3_bucket_name = Lochness['AWS_BUCKET_NAME']
    s3_phoenix_root = Lochness['AWS_BUCKET_ROOT']

    # save aws 3 sync cmd stdout to a file
    s3_sync_stdout = Path(Lochness['phoenix_root']) / 'aws_s3_sync_stdouts.log'

    for datatype in Lochness['s3_selective_sync']:
        # phoenix_root / PROTECTED / site / raw / subject / datatype
        source_directories = Path(Lochness['phoenix_root']).glob(
                    f'PROTECTED/*/*/*/{datatype}')

        # for all studies and subjects
        for source_directory in source_directories:
            if source_directory.is_dir():
                s3_phoenix_root_dtype = re.sub(Lochness['phoenix_root'],
                                               s3_phoenix_root,
                                               str(source_directory))
                command = f"aws s3 sync \
                        {source_directory}/ \
                        s3://{s3_bucket_name}/{s3_phoenix_root_dtype} \
                        --exclude '*.mp3' --delete"

                logger.debug('Executing aws s3 sync function for '
                             f'{source_directory}')
                logger.debug(re.sub(r'\s+', r' ', command))

                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                with open(s3_sync_stdout, 'a') as fp:

                    command_str = '\n'.join([f'{current_time} {x}' for x in
                                        os.popen(command).read().split('\n')])
                    fp.write(command_str)

                logger.debug(command_str)
                logger.debug('aws rsync completed')

    # interview run sheets
    # phoenix_root / PROTECTED / site / raw / subject / datatype
    interview_dirs = Path(Lochness['phoenix_root']).glob(
        f'PROTECTED/*/raw/*/interviews')

    for interview_dir in interview_dirs:
        s3_target = re.sub(Lochness['phoenix_root'],
                           s3_phoenix_root,
                           str(interview_dir))
        command = f"aws s3 sync \
                {interview_dir} \
                s3://{s3_bucket_name}/{s3_target} --delete \
                --exclude='*' --include='*Run_sheet_interviews_*.csv'"

        logger.debug('Executing aws s3 sync function for '
                     f'{interview_dir} Run sheet only')
        logger.debug(re.sub(r'\s+', r' ', command))

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(s3_sync_stdout, 'a') as fp:
            command_str = '\n'.join([f'{current_time} {x}' for x in
                                os.popen(command).read().split('\n')])
            fp.write(command_str)

        logger.debug(command_str)
        logger.debug('aws rsync completed')


def lochness_to_lochness_transfer_receive_sftp(Lochness):
    '''Get newly transferred file and decompress to PHOENIX

    Key arguments:
        Lochness: Lochness object loaded from the config.load, object.

    Structure needed in the Lochness['keyring']
        Lochness['keyring'] = {
            'lochness_sync': {
                'PATH_IN_HOST': '/SFTP/DATA/REPO'
            }
        }
        Lochness['lochness_sync_history_csv']: '/SYNC/HISTORY.csv'

    TODO: move PATH_IN_HOST to config?
    '''

    sftp_keyring = Lochness['keyring']['lochness_sync']
    path_in_host = sftp_keyring['PATH_IN_HOST']

    target_phoenix_root = Lochness['phoenix_root']
    sync_db = Lochness['lochness_sync_history_csv']

    last_sync_timestamp, _, sync_df = get_ts_and_db(sync_db)

    for root, _, files in os.walk(path_in_host):
        for file in files:
            file_p = Path(root) / file
            # if the file is transferred after the last transfer
            if file_p.stat().st_mtime > last_sync_timestamp \
                    and file.endswith('.tar'):
                decompress_transferred_file_and_copy(target_phoenix_root,
                                                     file_p)

    sync_df.to_csv(sync_db, index=False)


def decompress_transferred_file_and_copy(target_phoenix_root: str,
                                         tar_file_trasferred: str):
    '''Decompress the tar file and arrange the new data into PHOENIX structure

    Decompress the tar file transferred and arrange the new data into the
    corresponding structure under the PHOENIX structure.

    Key arguments:
        target_phoenix_root: path of the PHOENIX directory, str.
        tar_file_trasferred: path of the tar file transferred from another
                             lochness using lochness_sync, str.
    '''
    tar = tarfile.open(tar_file_trasferred)

    with tf.TemporaryDirectory(suffix='tmp', dir='.') as tmpdir:
        tar.extractall(path=tmpdir)

        for root, _, files in os.walk(tmpdir):
            for file in files:
                relative_root = root.split(tmpdir + '/PHOENIX/')[1]
                target_path = Path(target_phoenix_root) / relative_root / file
                target_path.parent.mkdir(exist_ok=True, parents=True)

                # this overwrites exsiting file
                shutil.copy(Path(root) / file, target_path)

                # permission change
                os.chmod(target_path, 0o0644)

    os.remove(tar_file_trasferred)
