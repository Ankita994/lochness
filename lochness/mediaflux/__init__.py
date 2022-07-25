import os, sys
import gzip
import logging
import importlib
import lochness
import tempfile as tf
import cryptease as crypt
import lochness.net as net
from typing import Generator, Tuple
from pathlib import Path
import hashlib
from io import BytesIO
import lochness.keyring as keyring
from os.path import join as pjoin, basename, dirname, isfile
import cryptease as enc
import re
from subprocess import Popen, DEVNULL, STDOUT
import pandas as pd
from numpy import nan
from distutils.spawn import find_executable
import lochness.tree as tree
from lochness.cleaner import is_transferred_and_removed

logger = logging.getLogger(__name__)
Module = lochness.lchop(__name__, 'lochness.')
Basename = lochness.lchop(__name__, 'lochness.mediaflux.')

CHUNK_SIZE = 65536


def base(Lochness, study_name):
    '''get study-specific namespace directory'''
    return Lochness.get('mediaflux', {}) \
                   .get(study_name, {}) \
                   .get('namespace', '')


class PatternError(Exception):
    pass


def sync_module(Lochness: 'lochness.config',
                subject: 'subject.metadata',
                study_name: 'mediaflux.study_name',
                dry: bool):
    '''sync mediaflux data for the subject'''

    if dry:
        raise NotImplementedError('--dry option is not implemented')

    study_basename = study_name.split('.')[1]

    for mf_subid in subject.mediaflux[study_name]:
        logger.debug(f'exploring {subject.study}/{subject.id}')
        _passphrase = keyring.passphrase(Lochness, subject.study)
        enc_key = enc.kdf(_passphrase)

        mflux_cfg = keyring.mediaflux_api_token(Lochness, study_name)
        
        mf_base = base(Lochness, study_basename)

        for datatype, products in \
            iter(Lochness['mediaflux'][study_basename][
                'file_patterns'].items()):
            '''
            file_patterns:
                actigraphy:
                    - vendor: Activinsights
                      product: GENEActiv
                      data_dir: PrescientXX_Actigraphy
                      pattern: '*'
                interviews:
                    - product: open
                      data_dir: PrescientXX_Interviews/OPEN
                      out_dir: open
                      pattern: '*'
            '''
            for prod in products:
                for patt in prod['pattern'].split(','):
                    # consider the case with space
                    # pattern: 'GENEActiv/*bin, GENEActiv/*csv'
                    patt = patt.strip()

                    if '*' not in patt:
                        raise PatternError('Mediaflux pattern must include an '
                            'asterisk e.g. *csv or GENEActiv/*csv')

                    # construct mediaflux remote dir
                    mf_remote_root = pjoin(
                            mf_base, prod['data_dir'], mf_subid)

                    mf_remote_pattern = pjoin(
                            mf_base, prod['data_dir'], mf_subid, patt)

                    # obtain mediaflux remote paths
                    with tf.TemporaryDirectory() as tmpdir:
                        diff_path= pjoin(tmpdir,'diff.csv')
                        cmd = (' ').join(['unimelb-mf-check',
                                          '--mf.config', mflux_cfg,
                                          '--nb-retries 5',
                                          '--direction down', tmpdir,
                                          mf_remote_root,
                                          '-o', diff_path])
                        
                        p = Popen(cmd, shell=True,
                                  stdout=DEVNULL, stderr=STDOUT)
                        p.wait()

                        # ENH
                        # if dry: exit()
                        if not isfile(diff_path):
                            continue

                        df = pd.read_csv(diff_path)
                        for remote in df['SRC_PATH'].values:
                            if remote is nan:
                                continue

                            if not re.search(patt.replace('*', '(.+?)'),
                                             remote):
                                continue
                            else:
                                remote = remote.split(':')[1]

                            # To keep the folder structures of the mediaflux
                            # subpath of the data under mf_remote_root
                            # eg) When full remote and mf_remote_root are
                            # full remote: 
                            # /projects/proj-5070/
                            #   PrescientME/Interview_recordings/ME00077/
                            #       Audio Record/OS_ZZ04139.m4a
                            # mf_remote_root:
                            # /projects/proj-5070/
                            #   PrescientME/Interview_recordings/ME00077/
                            # Then
                            # subpath: Audio Records/OS_ZZ04139.m4a
                            subpath = Path(remote).relative_to(
                                    Path(mf_remote_root))

                            # construct local path
                            protect = prod.get('protect', True)
                            processed =  prod.get('processed', False)
                            key = enc_key if protect else None
                            subj_dir = subject.protected_folder \
                                if protect else subject.general_folder

                            mf_local = tree.get(datatype,
                                                subj_dir,
                                                processed=processed,
                                                BIDS=Lochness['BIDS'])

                            mf_local = str(mf_local / prod['out_dir'] \
                                    if 'out_dir' in prod else mf_local) / \
                                        subpath.parent

                            # do not re-download already transferred &
                            # removed data
                            if is_transferred_and_removed(
                                    Lochness, Path(mf_local) / subpath.name):
                                continue

                            # ENH set different permissions
                            # GENERAL: 0o755, PROTECTED: 0700
                            os.makedirs(mf_local, exist_ok=True)
                            os.chmod(mf_local, 0o0770)

                            # subprocess call unimelb-mf-download
                            cmd = (' ').join(['unimelb-mf-download',
                                              '--mf.config', mflux_cfg,
                                              '-o', f'"{mf_local}"',
                                              '--nb-retries 5',
                                              f'\"{remote}\"'])

                            p = Popen(cmd, shell=True,
                                      stdout=DEVNULL, stderr=STDOUT)

                            p.wait()
                            # verify checksum after download completes if
                            # checksum does not match, data will be downloaded
                            # again ENH should we verify checksum 5 times?
                            cmd += ' --csum-check'
                            p = Popen(cmd, shell=True,
                                      stdout=DEVNULL, stderr=STDOUT)
                            p.wait()

                            # for A/V related files, force permission to 770
                            # so A/V pipeline can work
                            if 'interviews' in str(mf_local):
                                for root, dirs, files in os.walk(mf_local):
                                    for file in files:
                                        file_p = Path(root) / file
                                        perm = oct(file_p.stat().st_mode)[-3:]
                                        if perm != '770':
                                            os.chmod(file_p, 0o0770)


def sync(Lochness, subject, dry):
    '''call sync on the correct sub-module'''
    
    # check availability of unimelb-mf-clients in PATH 
    for cmd in ['unimelb-mf-download','unimelb-mf-check']:
        exe= find_executable(cmd)
        if not exe:
            raise EnvironmentError(f'''

{cmd} not found in PATH. To resolve this:
* Download Linux 64bit unimelb-mf-clients client from
  https://gitlab.unimelb.edu.au/resplat-mediaflux/unimelb-mf-clients/-/tags
* Unzip it
* Finally, export the unimelb-mf-clients to your PATH
  export PATH=`pwd`/unimelb-mf-clients-0.5.8/bin/unix/:$PATH

''')

    for module_name in subject.mediaflux:
        sync_module(Lochness, subject, module_name, dry)
