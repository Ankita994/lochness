import lochness.mindlamp
from lochness import config
import os
from pathlib import Path
import pandas as pd
pd.set_option('max_columns', 50)
pd.set_option('max_rows', 500)

import sys
lochness_root = Path(lochness.__path__[0]).parent
scripts_dir = lochness_root / 'scripts'
test_dir = lochness_root / 'tests'
sys.path.append(str(scripts_dir))
sys.path.append(str(test_dir))

from test_lochness import Args, Tokens, KeyringAndEncrypt, args, SyncArgs
from test_lochness import show_tree_then_delete, config_load_test
from test_lochness import initialize_metadata_test
from lochness_create_template import create_lochness_template

from sync import do

# from config.test_config import create_config
import LAMP
from typing import Tuple, List
from lochness.mindlamp import get_study_lamp, get_participants_lamp
from lochness.mindlamp import get_activities_lamp, get_sensors_lamp
from lochness.mindlamp import get_activity_events_lamp
from lochness.mindlamp import get_sensor_events_lamp
from lochness.mindlamp import sync, get_days_to_pull
import json
import base64
import time
from datetime import datetime, timedelta
import pytz

import pytest


class KeyringAndEncryptMindlamp(KeyringAndEncrypt):
    def __init__(self, tmp_dir):
        super().__init__(tmp_dir)
        token = Tokens()
        mindlamp_token, access_key, secret_key, api_url = \
                token.read_token_or_get_input('mindlamp')
        # mindlamp_token, access_key, secret_key, api_url = \
                # token.get_mindlamp_token()

        self.keyring['mindlamp.StudyA'] = {}
        self.keyring['mindlamp.StudyA']['ACCESS_KEY'] = access_key
        self.keyring['mindlamp.StudyA']['SECRET_KEY'] = secret_key
        self.keyring['mindlamp.StudyA']['URL'] = api_url

        self.write_keyring_and_encrypt()


def test_lamp_modules():
    token = Tokens()
    mindlamp_token, access_key, secret_key, api_url = \
            token.read_token_or_get_input('mindlamp')
    LAMP.connect(access_key, secret_key)
    print(LAMP.Study.all_by_researcher('me')['data'])
    # study_id, study_name = get_study_lamp(LAMP)
    study_id, study_name = get_study_lamp(LAMP)
    subject_ids = get_participants_lamp(LAMP, study_id)

    for subject_id in subject_ids:
        # if subject_id == 'U7045332804':
        if subject_id == 'U4518928219' or subject_id == 'U6198539134':
            print(subject_id)
            # activity_dicts = get_activities_lamp(LAMP, subject_id)
            activity_dicts = get_activity_events_lamp(LAMP, subject_id)
            # activity_events_dicts = LAMP.ActivityEvent.all_by_participant( subject_id, label_from = "1626806920000", to=1627578306405)
            # activity_events_dicts = LAMP.ActivityEvent.all_by_participant(
                    # subject_id, _from=None, to=None)
            print(activity_dicts)
            # print(activity_events_dicts)
            # sys.exit()

            break
            sensor_dicts = get_sensor_events_lamp(LAMP, subject_id)
            # print(activity_dicts)
            # print(sensor_dicts)

            with open(f'{subject_id}_activity_data.json', 'w') as f:
                json.dump(activity_dicts, f)

            with open(f'{subject_id}_sensor_data.json', 'w') as f:
                json.dump(sensor_dicts, f)
            # # break

    # print(os.popen('tree').read())
    # os.remove('activity_data.json')
    # os.remove('seonsor_data.json')


def test_sync_mindlamp(args):
    syncArgs = SyncArgs(args.outdir)
    syncArgs.studies = ['StudyA']
    sources = ['mindlamp']
    syncArgs.update_source(sources)

    create_lochness_template(args)
    syncArgs.config = args.outdir / 'config.yml'
    _ = KeyringAndEncryptMindlamp(args.outdir)


    phoenix_root = args.outdir / 'PHOENIX'
    information_to_add_to_metadata = {'mindlamp': {'subject_id': '1001',
                                                   'source_id': 'U7045332804'}}
    
    initialize_metadata_test(phoenix_root, 'StudyA',
                             information_to_add_to_metadata)
    Lochness = config_load_test(syncArgs.config)
    for subject in lochness.read_phoenix_metadata(Lochness, syncArgs.studies):
        sync(Lochness, subject, False)

    show_tree_then_delete('tmp_lochness')


def test_do_with_mindlamp(args):
    syncArgs = SyncArgs(args.outdir)
    sources = ['mindlamp']
    syncArgs.update_source(sources)

    create_lochness_template(args)
    syncArgs.config = args.outdir / 'config.yml'
    _ = KeyringAndEncryptMindlamp(args.outdir)


    phoenix_root = args.outdir / 'PHOENIX'
    information_to_add_to_metadata = {'mindlamp': {'subject_id': '1001',
                                                   'source_id': 'U7045332804'}}
    initialize_metadata_test(phoenix_root, 'StudyA',
                             information_to_add_to_metadata)
    
    syncArgs.input_sources = syncArgs.source
    do(syncArgs)
    show_tree_then_delete('tmp_lochness')



def test_sound_download(args):
    token = Tokens()
    mindlamp_token, access_key, secret_key, api_url = \
            token.read_token_or_get_input('mindlamp')
    LAMP.connect(access_key, secret_key)
    print(LAMP.Study.all_by_researcher('me')['data'])
    # study_id, study_name = get_study_lamp(LAMP)
    study_id, study_name = get_study_lamp(LAMP)
    subject_ids = get_participants_lamp(LAMP, study_id)

    for subject_id in subject_ids:
        if subject_id == 'U6198539134':
            activity_events_dicts = LAMP.ActivityEvent.all_by_participant(
                    subject_id,
                    _from="1626806920000",
                    to=1627578306405)

            print(activity_events_dicts['data'][0])
            print()
            print()
            print(activity_events_dicts['data'][1])

            import base64
            audio = activity_events_dicts['data'][0]['static_data']['url']
            decode_bytes = base64.b64decode(audio.split(',')[1])
            with open('prac2.mp3', 'wb') as f:
                f.write(decode_bytes)


def test_timestamp_to_UTC_0_24():
    timestamp1 = time.mktime(datetime.now().timetuple())
    print(timestamp1)
    print(datetime.utcfromtimestamp(timestamp1))

    # naive vs aware
    
    # current time in UTC
    ct_utc = datetime.now(pytz.timezone('UTC'))
    ct_utc_00 = ct_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    ct_utc_00 = ct_utc_00 - timedelta(days=1)
    ct_utc_00_ts = time.mktime(ct_utc_00.timetuple()) * 1000
    ct_utc_24 = ct_utc_00 + timedelta(hours=24)
    ct_utc_24_ts = time.mktime(ct_utc_24.timetuple()) * 1000

    print(ct_utc_24.strftime('%Y_%m_%d'))
    return


    token = Tokens()
    mindlamp_token, access_key, secret_key, api_url = \
            token.read_token_or_get_input('mindlamp')
    LAMP.connect(access_key, secret_key)
    print(LAMP.Study.all_by_researcher('me')['data'])
    # study_id, study_name = get_study_lamp(LAMP)
    study_id, study_name = get_study_lamp(LAMP)
    subject_ids = get_participants_lamp(LAMP, study_id)

    for subject_id in subject_ids:
        if subject_id == 'U6198539134':
            activity_events_dicts = LAMP.ActivityEvent.all_by_participant(
                    subject_id,
                    _from=ct_utc_00_ts,
                    to=ct_utc_24_ts)
            # activity_events_dicts = LAMP.ActivityEvent.all_by_participant(
                    # subject_id)
            print(activity_events_dicts)



@pytest.fixture
def args_and_Lochness():
    args = Args('tmp_lochness')
    args.studies = ['PronetLA', 'PronetSL']

    create_lochness_template(args)
    keyring = KeyringAndEncrypt(args.outdir)
    for study in args.studies:
        # for pronet & prescient
        project_name = study[:-2]
        keyring.update_for_redcap(project_name)

    lochness_obj = config_load_test('tmp_lochness/config.yml', '')

    return args, lochness_obj


# def test_initialize_metadata_then_sync(args_and_Lochness):
def test_get_days_to_pull(args_and_Lochness):
    print()
    args, Lochness = args_and_Lochness
    Lochness['mindlamp_days_to_pull'] = None
    days_to_pull = get_days_to_pull(Lochness)
    assert days_to_pull == 10

    Lochness['mindlamp_days_to_pull'] = 5
    days_to_pull = get_days_to_pull(Lochness)
    assert days_to_pull == 5


def test_sync_mindlamp(args):
    syncArgs = SyncArgs(args.outdir)
    syncArgs.studies = ['StudyA']
    sources = ['mindlamp']
    syncArgs.update_source(sources)

    create_lochness_template(args)
    syncArgs.config = args.outdir / 'config.yml'
    _ = KeyringAndEncryptMindlamp(args.outdir)


    phoenix_root = args.outdir / 'PHOENIX'
    information_to_add_to_metadata = {'mindlamp': {'subject_id': '1001',
                                                   'source_id': 'U6198539134'}}
    
    initialize_metadata_test(phoenix_root, 'StudyA',
                             information_to_add_to_metadata)
    Lochness = config_load_test(syncArgs.config)
    for subject in lochness.read_phoenix_metadata(Lochness, syncArgs.studies):
        sync(Lochness, subject, False)

    # show_tree_then_delete('tmp_lochness')
