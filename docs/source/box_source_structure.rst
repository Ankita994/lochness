Box source
==========

A Box app needs to be created with ``OAuth 2.0 with Client Credentials Grant``
and needs to be authorized by Box admin.



For Keyring
-----------
Make note of ``ENTERPRISE_ID``, ``CLIENT_ID`` and ``CLIENT_SECRET`` in the Boxp
developer webpage.



Data structure on Box
---------------------
Planned data structure on Box account (the source itself) looks like below ::

    ProNET
    ├── PronetAB
    │   ├── PronetAB_Interviews
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
    │   │       │   │   ├── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │   │       │   │   └── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │   │       │   └── ...
    │   │       └── For_review
    │   │           ├── AB00001
    │   │           │   ├── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │   │           │   └── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │   │           └── ...
    │   ├── PronetAB_EEG
    │   │       └── AB00001
    │   │           └── AB00001_eeg_20220101.zip
    │   └── PronetAB_Actigraphy
    │   │       └── AB00001
    │   │           └── ...
    └── ...


Data structure on corresponding PHOENIX
---------------------------------------
Planned data structure on Box account (the source itself) looks like below ::

    ProNET
    ├── PronetAB
    │   └── raw
    │       ├── AB00009
    │       │   ├── actigraphy
    │       │   ├── eeg
    │       │   │   └── AB00009_eeg_20211102.eeg
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
    │       │   │       ├── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │       │   │       └── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │       │   └── surveys
    │       │       └── AB00009.Pronet.json
    │       └── ...
    └── ..


