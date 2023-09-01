from lochness.xnat import sync_new


class Subject():
    def __init__(self):
        self.xnat = {'xnat.PronetSL': 'SL00005'}
        self.protected_folder = 'test_protected_folder'


def test_sync_new():
    Lochness = {'keyring': {
        'URL': 'XXXX',
        'USERNAME': 'XXXX',
        'PASSWORD': 'XXXX'}
                }
    subject = Subject()
    dry = False
    sync_new(Lochness, subject, dry=dry)
