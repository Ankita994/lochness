Mediaflux source
================

For Keyring
-----------
Please note following items required for mediaflux. ::

    "HOST": "mediaflux.researchsoftware.unimelb.edu.au",
    "PORT": "443",
    "TRANSPORT": "https",
    "DOMAIN": "local",
    "USER": "kevin.cho",
    "PASSWORD": "****"


Data structure on Mediaflux
---------------------------
Planned data structure on Mediaflux account (the source itself) looks like below ::

    Prescient
    ├── PrescientAB
    │   ├── PrescientAB_Interviews
    │   │   ├── OPEN
    │   │   │   └── AB00001
    │   │   │       └── 2021-12-10 16.01.56 Kevin Cho's Zoom Meeting
    │   │   │           ├── video2515225130.mp4
    │   │   │           ├── video1515225130.mp4
    │   │   │           ├── audio2515225130.mp4
    │   │   │           ├── audio1515225130.mp4
    │   │   │           └── Audio Record
    │   │   │               └── Audio Record
    │   │   │                   ├── audioKevinCho42515225130.m4a
    │   │   │                   ├── audioKevinCho21515225130.m4a
    │   │   │                   ├── audioAnotherPerson11515225130.m4a
    │   │   │                   └── audioAnotherPerson32515225130.m4a
    │   │   ├── PSYCHS
    │   │   │   ├── AB00001
    │   │   │   └── ...
    │   │   └── transcripts
    │   │       ├── Approved
    │   │       │   ├── AB00001
    │   │       │   │   ├── PrescientAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │   │       │   │   └── PrescientAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │   │       │   └── ...
    │   │       └── For_review
    │   │           ├── AB00001
    │   │           │   ├── PrescientAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │   │           │   └── PrescientAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │   │           └── ...
    │   ├── PrescientAB_EEG
    │   │       └── AB00001
    │   │           └── AB00001_eeg_20220101.zip
    │   ├── PrescientAB_MRI
    │   │       └── AB00001
    │   │           └── AB00001_mri_20220101
    │   ├── PrescientAB_Actigraphy
    │   │       └── AB00001
    │   │           └── ...
    └── ...


Data structure on corresponding PHOENIX
---------------------------------------
Planned data structure on Mediaflux account (the source itself) looks like below ::

    Prescient
    ├── PrescientAB
    │   └── raw
    │       ├── AB00009
    │       │   ├── actigraphy
    │       │   ├── eeg
    │       │   │   └── AB00009_eeg_20211102.eeg
    │       │   ├── mri
    │       │   │   └── AB00001_mri_20220101
    │       │   ├── interviews
    │       │   │   ├── open
    │       │   │   │   └── 2021-12-10 16.01.56 Kevin Cho's Zoom Meeting
    │       │   │   │       ├── Audio Record
    │       │   │   │       │   └── Audio Record
    │       │   │   │       │       ├── audioKevinCho42515225130.m4a
    │       │   │   │       │       ├── audioKevinCho21515225130.m4a
    │       │   │   │       │       ├── audioAnotherPerson11515225130.m4a
    │       │   │   │       │       └── audioAnotherPerson32515225130.m4a
    │       │   │   │       ├── video2515225130.mp4
    │       │   │   │       ├── audio2515225130.mp4
    │       │   │   │       ├── video1515225130.mp4
    │       │   │   │       └── audio1515225130.mp4
    │       │   │   ├── psychs
    │       │   │   │   └── ...
    │       │   │   └── transcripts
    │       │   │       ├── PrescientAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │       │   │       └── PrescientAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │       │   └── surveys
    │       │       └── AB00009.Prescient.json
    │       └── ...
    └── ..


