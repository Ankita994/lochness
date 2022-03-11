import pandas as pd
import re
from pathlib import Path
from typing import List


def nth_item_from_path(df: pd.DataFrame, n: int) -> pd.Series:
    '''Return n th item from pd.Series of paths'''
    return df['file_path'].str.split('/').str[n]


def update_eeg_check(df: pd.DataFrame) -> None:
    '''Check logics in rows for EEG modality'''
    eeg_index = df[df['modality'] == 'EEG'].index
    eeg_df = df.loc[eeg_index]
    eeg_df['file_check'] = eeg_df['file_name'].str.match(
            '[A-Z]{2}\d{5}_eeg_\d{4}\d{2}\d{2}\.*')

    df.loc[eeg_index] = eeg_df


def update_mri_check(df: pd.DataFrame) -> pd.DataFrame:
    '''Check logics in rows for MRI modality'''
    mri_index = df[df['modality'] == 'MRI'].index
    mri_df = df.loc[mri_index]
    mri_df['file_check'] = mri_df['file_name'].str.match(
            '[A-Z]{2}\d{5}_MR_\d{4}_\d{2}_\d{2}_\d.zip')

    df.loc[mri_index] = mri_df


def update_actigraphy_check(df: pd.DataFrame) -> pd.DataFrame:
    '''Check logics in rows for Actigraphy modality'''
    act_index = df[df['modality'] == 'Actigraphy'].index
    act_df = df.loc[act_index]
    act_df['file_check'] = act_df['file_name'].str.match(
            '[A-Z]{2}\d{5}_\d{5}_\d{4}\d{2}\d{2}.cwa')

    df.loc[act_index] = act_df


def update_interviews_check(df: pd.DataFrame) -> pd.DataFrame:
    '''Check logics in rows for Interviews modality'''
    int_index = df[df['modality'] == 'Interviews'].index

    # subject location is different
    int_df = df.loc[int_index]
    int_df['subject'] = nth_item_from_path(int_df, 3)
    int_df['subject_check'] = int_df['subject'].str.match(
            '[A-Z]{2}\d{5}').fillna(False)

    df.loc[int_index] = int_df


def update_interviews_transcript_check(df: pd.DataFrame) -> pd.DataFrame:
    '''Check logics in rows for Interviews transcripts'''
    transcript_int_index = df[
            (df.modality=='Interviews') &
            (df.subject.isin(['For_review', 'Approved']))].index

    transcript_int_df = df.loc[transcript_int_index]
    transcript_int_df['subject'] = nth_item_from_path(transcript_int_df, 4)
    transcript_int_df['subject_check'] = transcript_int_df['subject'
            ].str.match('[A-Z]{2}\d{5}').fillna(False)

    # check site and AMPSCZ IDs in the transcript file name
    for index, row in transcript_int_df.iterrows():
        if not row['subject_check']:
            transcript_int_df.loc[index, 'subject'] = re.search(
                r'[A-Z]{2}\d{5}', row['subject']).group(0)
            row['subject'] = transcript_int_df.loc[index, 'subject']

        subject = row['subject']
        site = row['site']
        transcript_int_df.loc[index, 'file_check'] = re.match(
                f'{site}_{subject}_'
                'interviewAudioTranscript_open_day\d+_session\d+.txt',
                row['file_name'])

    df.loc[transcript_int_index] = transcript_int_df


def update_interviews_video_check(df: pd.DataFrame) -> pd.DataFrame:
    '''Check logics in rows for Interviews video'''
    # interviews transcript
    video_int_index = df[
            (df.modality=='Interviews') &
            ((df.file_name.str.endswith('.mp4')) |
             (df.file_name=='recording.conf'))
            ].index

    video_int_df = df.loc[video_int_index]

    video_int_df['zoom_name'] = video_int_df['parent_dir'].str.extract(
            '\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2} (.+)')

    # video files must be under the zoom folder
    video_int_df['file_check'] = ~video_int_df['zoom_name'].isnull()

    df.loc[video_int_index] = video_int_df


def update_interviews_audio_check(df: pd.DataFrame) -> pd.DataFrame:
    '''Check logics in rows for Interviews audio'''
    # interviews audio
    audio_int_index = df[(df.modality=='Interviews') &
                         (df.file_name.str.endswith('.m4a'))].index

    audio_int_df = df.loc[audio_int_index]
    audio_int_df['zoom_name'] = audio_int_df['parent_dir'].str.extract(
            '\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2} (.+)')

    # audio files need to be under either the zoom or Audio Record folder
    audio_int_df['file_check_1'] = ~audio_int_df['zoom_name'].isnull()
    audio_int_df['file_check_2'] = audio_int_df['parent_dir'] == 'Audio Record'
    audio_int_df['file_check'] = audio_int_df[
        ['file_check_1', 'file_check_2']].any(axis=1)
    audio_int_df.drop(['file_check_1', 'file_check_2'], axis=1, inplace=True)

    df.loc[audio_int_index] = audio_int_df


    # ignore playback.m3u audio files
    audio_int_index = df[(df.modality=='Interviews') &
                         (df.file_name == 'playback.m3u')].index
    audio_int_df = df.loc[audio_int_index]
    audio_int_df['file_check'] = True
    df.loc[audio_int_index] = audio_int_df


def update_by_adding_notes(df: pd.DataFrame) -> None:
    '''Add notes to the table'''
    pass


def update_by_removing_unused_files(df: pd.DataFrame) -> None:
    '''Remove unused files'''
    # .DS_Store
    ds_store_index = df[df.file_name == '.DS_Store'].index
    df.drop(ds_store_index, inplace=True)


def update_by_checking_against_subject_list(
        df: pd.DataFrame,
        subject_id_list: List[str]) -> None:
    '''pass'''
    df['exist_in_db'] = df['subject'].isin(subject_id_list).fillna(False)

    df.loc[df[df['exist_in_db']].index,
           'notes'] = 'Subject missing from database'


def check_file_path_df(df: pd.DataFrame,
                       subject_id_list: list) -> pd.DataFrame:
    '''Check file_path column for deviations from SOP'''

    df['site'] = nth_item_from_path(df, 0)

    df['modality_dir'] = nth_item_from_path(df, 1)
    df['modality'] = df['modality_dir'].str.split('_').str[1]

    # subject
    df['subject'] = nth_item_from_path(df, 2)
    df['file_name'] = nth_item_from_path(df, -1)
    df['parent_dir'] = nth_item_from_path(df, -2)

    # main check logics start here
    df['site_check'] = df.site.str.match('Prescient|Pronet')
    df['subject_check'] = df['subject'].str.match(
            '[A-Z]{2}\d{5}').fillna(False)

    df['modality_check'] = df['modality'].str.contains(
            'MRI|EEG|Actigraphy|Interviews').fillna(False)

    # file name pattern checks
    df['file_check'] = False
    update_eeg_check(df)
    update_actigraphy_check(df)
    update_mri_check(df)

    update_interviews_check(df)
    update_interviews_transcript_check(df)
    update_interviews_video_check(df)
    update_interviews_audio_check(df)

    # ignore .DS_Store files
    update_by_removing_unused_files(df)

    # check if the subject exist in metadata
    update_by_checking_against_subject_list(df, subject_id_list)

    # check if the letters in front of the subject matches the site
    site_mismatch = df[df['subject'].str[:2] != df['site'].str[-2:]].index
    df.loc[site_mismatch, 'subject_check'] = False

    # add notes
    update_by_adding_notes(df)

    # fill na as False for the check columns
    for i in ['modality', 'subject', 'file']:
        df[f"{i}_check"] = df[f"{i}_check"].fillna(False)


    df['final_check'] = df[
            ['modality_check', 'subject_check', 'file_check']
        ].all(axis=1)

    return df


def print_deviation(df):
    '''Print deviations from the df'''
    prev_row = 'x'
    num = 0

    lines = []
    for index, row in df[(~df.final_check) &
                         (~df.file_path.str.endswith('dcm'))
                     ].sort_values('file_path').iterrows():

        new_string = re.sub(prev_row, ' '*len(prev_row), row['file_path'])
        print(new_string)
        lines.append(new_string)
        prev_row = str(Path(row['file_path']).parent) + '/'

    return lines


