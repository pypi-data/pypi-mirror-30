# -*- coding: utf-8 -*-

"""Main module."""
import csv
import os
import os.path
import logging
import requests
import json
import time
from dotmap import DotMap
import behavioral_signals_swagger_client as swagger_client
from datetime import datetime
from dateutil.parser import parse
import cliargs
import utils
from utils import die

POLLING_SLEEP_TIME = 5  # in seconds
opts = {}

def get_json_results_for_pid(pid, json_file):
    # Configuration
    api_instance = swagger_client.DefaultApi()
    api_instance.api_client.configuration.host = opts.apiurl
    api_instance.api_client.configuration.api_key['X-Auth-Token'] = opts.apitoken
    api_response = api_instance.get_process_info(opts.apiid, pid)
    if api_response.status == 2:
        api_results = api_instance.get_process_results(opts.apiid, pid)
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_for_pid_after_polling(pid, json_dir):
    # Configuration
    api_instance = swagger_client.DefaultApi()
    api_instance.api_client.configuration.host = opts.apiurl
    api_instance.api_client.configuration.api_key['X-Auth-Token'] = opts.apitoken

    api_response = api_instance.get_process_info(opts.apiid, pid)
    elapsed_time = 0
    while api_response.status == 0 or api_response.status == 1:
        api_response = api_instance.get_process_info(opts.apiid, pid)
        time.sleep(POLLING_SLEEP_TIME)
        elapsed_time += POLLING_SLEEP_TIME

    logging.info("Polling for process {} lasted {} seconds".format(pid,
                                                                   elapsed_time))

    if api_response.status == 2:
        fname = os.path.splitext(os.path.basename(api_response.source))[0]
        api_results = api_instance.get_process_results(opts.apiid, pid)
        json_file = os.path.join(json_dir, "{}_{}.json".format(fname, pid))
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(
            pid, api_response.status))

    return api_response.status


# -- collect results for all pids
def get_json_results_for_pid_list(pid_file, json_dir):
    missing_pids = []
    for pid in utils.words(pid_file):
        status = get_json_results_for_pid_after_polling(pid, json_dir)
        if status != 2:
            missing_pids.append(pid)

    return missing_pids


def get_json_results_frames_for_pid(pid, json_file):
    # Configuration
    api_instance = swagger_client.DefaultApi()
    api_instance.api_client.configuration.host = opts.apiurl
    api_instance.api_client.configuration.api_key['X-Auth-Token'] = opts.apitoken
    api_response = api_instance.get_process_info(opts.apiid, pid)
    if api_response.status == 2:
        api_results = api_instance.get_process_results_frames(opts.apiid, pid)
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(
            pid, api_response.status))

    return api_response.status


def get_json_results_frames_for_pid_after_polling(pid, json_dir):
    # Configuration
    api_instance = swagger_client.DefaultApi()
    api_instance.api_client.configuration.host = opts.apiurl
    api_instance.api_client.configuration.api_key['X-Auth-Token'] = opts.apitoken

    api_response = api_instance.get_process_info(opts.apiid, pid)
    elapsed_time = 0
    while api_response.status == 0 or api_response.status == 1:
        api_response = api_instance.get_process_info(opts.apiid, pid)
        time.sleep(POLLING_SLEEP_TIME)
        elapsed_time += POLLING_SLEEP_TIME

    logging.info("Polling for process {} lasted {} seconds".format(pid,
                                                                   elapsed_time))

    if api_response.status == 2:
        fname = os.path.splitext(os.path.basename(api_response.source))[0]
        api_results = api_instance.get_process_results_frames(opts.apiid, pid)
        json_file = os.path.join(json_dir, "{}_{}.json".format(fname, pid))
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(
            pid, api_response.status))

    return api_response.status


def get_json_results_frames_for_pid_list(pid_file, json_dir):
    missing_pids = []
    for pid in utils.words(pid_file):
        status = get_json_results_frames_for_pid_after_polling(pid, json_dir)
        if status != 2:
            missing_pids.append(pid)

    return missing_pids


def get_json_results_asr_for_pid(pid, json_file):
    # Configuration
    api_instance = swagger_client.DefaultApi()
    api_instance.api_client.configuration.host = opts.apiurl
    api_instance.api_client.configuration.api_key['X-Auth-Token'] = opts.apitoken
    api_response = api_instance.get_process_info(opts.apiid, pid)
    if api_response.status == 2:
        api_results = api_instance.get_process_results_asr(opts.apiid, pid)
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(
            pid, api_response.status))

    return api_response.status


def get_json_results_asr_for_pid_after_polling(pid, json_dir):
    # Configuration
    api_instance = swagger_client.DefaultApi()
    api_instance.api_client.configuration.host = opts.apiurl
    api_instance.api_client.configuration.api_key['X-Auth-Token'] = opts.apitoken

    api_response = api_instance.get_process_info(opts.apiid, pid)
    elapsed_time = 0
    while api_response.status == 0 or api_response.status == 1:
        api_response = api_instance.get_process_info(opts.apiid, pid)
        time.sleep(POLLING_SLEEP_TIME)
        elapsed_time += POLLING_SLEEP_TIME

    logging.info("Polling for process {} lasted {} seconds".format(
        pid, elapsed_time))

    if api_response.status == 2:
        fname = os.path.splitext(os.path.basename(api_response.source))[0]
        # -- handle transport/service errors
        try:
            api_results = api_instance.get_process_results_asr(opts.apiid, pid)
        except Exception as e:
            if e.status == 405 or e.status == 503:
                msg = getResponse(e.body, 'message')
                logging.warning("{}: {}".format(pid, msg))
                return None
            raise

        json_file = os.path.join(
            json_dir, "{}_{}_words.json".format(fname, pid))
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(
            pid, api_response.status))

    return api_response.status


def get_json_results_asr_for_pid_list(pid_file, json_dir):
    missing_pids = []
    for word in utils.words(pid_file):
        status = get_json_results_asr_for_pid_after_polling(pid, json_dir)
        if status != 2:
            missing_pids.append(pid)
            logging.warning("{}: skipping".format(pid))

    return missing_pids


# -- for a user URI
def get_user_uri():
    return '{}/client/{}'.format(opts.apiurl, opts.apiid)


def get_process_audio_uri():
    return '{}/process/audio'.format(get_user_uri())


# -- submit one audio file
def submit_single_file(file_name, data):
    headers = {'X-Auth-Token': opts.apitoken, 'Accept': "application/json"}
    files = {'file': open(file_name, 'rb')}

    # Validate if number of channels and call direction are correct
    if 'channels' not in data or (data['channels'] != 1
                                  and data['channels'] != 2):
        data['channels'] = 1
        logging.warn('Set value for channels to default')

    if 'calldirection' not in data or (data['calldirection'] != '1'
                                       and data['calldirection'] != '2'):
        data['calldirection'] = '1'
        logging.warn('Set value for call direction to default')

    showRequest(data, files, headers)
    response = requests.post(get_process_audio_uri(),
                             params=data, files=files, headers=headers)
    showResponse(response)
    return response


def showRequest(data, files, headers):
    logging.debug("sending a post request")
    logging.debug("\t %12s: %s", 'headers', headers)
    logging.debug("\t %12s: %s", 'data', data)
    logging.debug("\t %12s: %s", 'files', files)

# -- log the response in logging.debug


def showResponse(response):
    logging.debug('api response:')
    logging.debug('\t%12s: %s', 'status', response.status_code)
    logging.debug('\t%12s: %s', 'reason', response.reason)


def submit_single_file_no_params(file_name):
    # Default data values
    data = {'channels': '1', 'calldirection': '1'}
    return submit_single_file(file_name, data)


def submit_file_list(file_list):
    with open(file_list, 'r') as l:
        for line in l:
            file_name = line.rstrip()
            logging.debug('Submitting {}'.format(file_name))
            r = submit_single_file_no_params(file_name)
            logging.debug(r.url)
            logging.debug(r.text)


def convert_iso_datetime_format(calltime):
    """
    Convert datetime string to ISO datetime string
    """
    service_datetime_fmt = '%m/%d/%Y %H:%M:%S'

    if calltime is None:
        return calltime

    try:
        calltime = parse(calltime)
        calltime = calltime.strftime(service_datetime_fmt)
    except ValueError:
        return None
    else:
        return calltime


def submit_csv_file(csv_file, pid_file, tag=None, nchannels=1):

    data_fields = ['channels', 'calldirection', 'agentId',
                   'agentTeam', 'campaignId', 'calltype', 'calltime', 'timezone',
                   'ANI', 'tag']
    n_failures = 0

    with open(csv_file, 'r') as f:
        with open(pid_file, 'w') as p:
            reader = csv.reader(f)
            for row in reader:
                file_name = row[0]
                data = {}
                n_data_values = len(row)
                if n_data_values > 1:
                    for idx, value in enumerate(row[1:]):
                        if value:
                            if data_fields[idx] == 'channels':
                                value = int(value)
                            elif data_fields[idx] == 'calltime':
                                value = convert_iso_datetime_format(value)

                            data[data_fields[idx]] = value
                            if data_fields[idx] == 'tag':
                                if tag is not None:
                                    data['tag'] += ',{}'.format(tag)

                if 'tag' not in data and tag is not None:
                    data['tag'] = tag
                if 'channels' not in data:
                    data['channels'] = int(nchannels)

                r = submit_single_file(file_name, data)

                if r.status_code != 200:
                    n_failures += 1

                else:
                    j = json.loads(r.text)
                    p.write("{}\n".format(j['pid']))

    return n_failures


def get_user_details():
    headers = {'X-Auth-Token': opts.apitoken, 'Accept': "application/json"}
    r = requests.get(get_user_uri(), headers=headers)
    logging.debug(r.url)
    logging.debug(r.text)


def send_audio(args):
    logging.info('Using csv file: {}'.format(args.csvFile))

    n_failures = submit_csv_file(args.csvFile, args.pidFile,
                                 tag=args.tag, nchannels=args.nchannels)

    if n_failures == 0:
        logging.info("File uploading ran successfully.")


def get_results(args):
    if not os.path.exists(args.resultsDir):
        os.makedirs(args.resultsDir)
    missing_pids = get_json_results_for_pid_list(args.pidFile, args.resultsDir)

    if len(missing_pids) > 0:
        logging.info("No results for PIDs: {}".format(missing_pids))
    else:
        logging.info("Results for all pids have been downloaded.")


def get_results_frames(args):
    if not os.path.exists(args.resultsDir):
        logging.warning("Creating new folder: {}".format(args.resultsDir))
        os.mkdir(args.resultsDir)

    missing_pids = get_json_results_frames_for_pid_list(
        args.pidFile, args.resultsDir)
    if len(missing_pids) > 0:
        logging.info("No results for PIDs: {}".format(missing_pids))
    else:
        logging.info("Results for all pids have been downloaded.")


def get_results_asr(args):
    if not os.path.exists(args.resultsDir):
        logging.warning("Creating new folder: {}".format(args.resultsDir))
        os.mkdir(args.resultsDir)

    missing_pids = get_json_results_asr_for_pid_list(
        args.pidFile, args.resultsDir)
    if len(missing_pids) > 0:
        logging.info("No results for PIDs: {}".format(missing_pids))
    else:
        logging.info("Results for all pids have been downloaded.")

# -- parse text body and return its json attr


def getResponse(body, attr):
    try:
        r = json.loads(body)
        return r[attr]
    except Exception:
        return "?"


def main():
    global opts
    # -- parse the command line args
    opts = cliargs.parse(
        get_results, get_results_frames, get_results_asr, send_audio
    )
    opts = DotMap(opts, _dynamic=False)
    if opts.apiid == None:
        die("BEST_API_ID was specified (env or config file)")
    if opts.apitoken == None:
        die("BEST_API_TOKEN was specified (env or config file)")

    # -- invoke the subcommand
    opts.func(opts)


if __name__ == '__main__':
    main()
