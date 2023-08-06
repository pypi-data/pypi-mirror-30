# Behavioral Signals CLI

Command Line Interface for Behavioral Signals' Emotion and Behavior Recognition in the Cloud


* Free software: MIT license

## Install
```
pip install behavioral_signals_cli
```

## Getting Started

* First request your account id and token for the Behavioral Signals Web API by sending an email to nassos@behavioralsignals.com
* Export the following as environmental variables:
```
   export BEST_ID=your_id_on_service_api
   export BEST_TOKEN=your_token_for_service_api
```

* Run the CLI to submit your audio files:
```
   behaviorals_signals_cli send_audio [csv_file] [pids_log]
```
   The .csv file must have the following form (order matters):
path/to/file, number of channels, call direction, agentId, agentTeam, campaign Id, calltype, calltime, timezone, ANI. The [pids_log] file
is an empty file where the process ids of the created jobs will be written.

* Run the CLI to get the emotion/behavior recognition, diarization and other results:
```
   behaviorals_signals_cli get_results [pids_log] [results_dir]
```
   The results will be written as .json files inside [results_dir] (polling may be performed if results
   are not readily available).

* Run the CLI to get ASR results:
```
   behaviorals_signals_cli get_results_asr [pids_log] [results_dir]
```
   The results will be written as "[filename]_[pid]_words.json" files inside [results_dir] (polling may be performed if results
   are not readily available).


Type:
```
   behavioral_signals_cli --help 
```
for more info.


Features
--------
The CLI allows you to easily:

- Submit multiple audio files to API,
- Get behavior and emotion recognition results
- Get speech recognition results

* TODO

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage



=======
History
=======

0.1.0 (2017-11-17)
------------------

* First release on PyPI.


