from __future__ import print_function

import boto3
import collections
import datetime
import os
import time


FAKETIME_REALTIME_FILE = os.environ.get('FAKETIME_REALTIME_FILE')

Command = collections.namedtuple('Command', 'ref, time1, time2, rate')

dynamodb = boto3.client('dynamodb')
dynamodb_streams = boto3.client('dynamodbstreams')


def calculate_fake_time(command):
    ref, time1, time2, rate = command

    window_fast = time2 - time1
    window_real = window_fast / float(rate)

    now = get_time()

    elapsed_real = now - ref
    if elapsed_real > window_real:
        elapsed_fast = window_fast
        elapsed_normal = elapsed_real - window_real
    else:
        elapsed_fast = elapsed_real * rate
        elapsed_normal = 0

    return time1 + elapsed_fast + elapsed_normal


def calculate_status(command):
    if calculate_fake_time(command) < command.time2:
        return 'MOVING'
    else:
        return 'IDLE'


def get_time():
    if FAKETIME_REALTIME_FILE:
        with open(FAKETIME_REALTIME_FILE) as open_file:
            return open_file.read()
    else:
        return time.time()


def read_command(table):
    response = dynamodb.get_item(
        TableName=table,
        Key={
            'Id': {
                'S': 'command',
            }
        }
    )
    item = response.get('Item')
    if item:
        value = item['Value']['S']
        return Command(*(int(v) for v in value.split(' ')))


def read_commands(table):
    last_command = None
    while True:
        command = read_command(table)
        if command and command != last_command:
            yield command
            last_command = command
        time.sleep(1)


def log_command(command):
    command_string = '{} {} {} {}'.format(*command)
    print('[{}] {}'.format(datetime.datetime.now(), command_string))


def send_command(command, table):
    log_command(command)
    dynamodb.put_item(
        TableName=table,
        Item={
            'Id': {
                'S': 'command',
            },
            'Value': {
                'S': '{} {} {} {}'.format(*command),
            },
        }
    )


def write_command(command, path):
    log_command(command)
    command_string = '{} {} {} {}'.format(*command)
    with open(path, 'w') as open_file:
        open_file.write(command_string)
