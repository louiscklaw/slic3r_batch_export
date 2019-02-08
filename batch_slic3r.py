#!/usr/bin/env python
# coding:utf-8

import os
import sys
import logging
import traceback
from pprint import pprint
from time import sleep
from datetime import datetime
from subprocess import Popen

from xdo import Xdo

WORKSPACE_DIR = '/home/logic/_workspace'
PROJ_HOME = '/'.join([WORKSPACE_DIR, '3d-printer-tryout/_ref_design/VORON_V2.1/STLs/VORON2.1'])
SLIC3R_ACTIVE_CONFIG='/'.join([WORKSPACE_DIR,'3d-printer-tryout/Slic3r_config_bundle.ini'])

xdo = Xdo()
slic3r_win_id = ''

# debug
file_3mf_list=[
    './Electronics Mounting/batch1.3mf',
    './Electronics Mounting/batch2.3mf',
    './Electronics Mounting/batch4.3mf',
    './Electronics Mounting/batch3.3mf',
    './LCD Module/batch1.3mf',
    './LCD Module/RepRap Full Graphics LCD Module/batch1.3mf',
    './Gantry/AB Drive Units/batch1.3mf',
    './Gantry/AB Drive Units/batch2.3mf',
    './Gantry/AB Drive Units/batch3.3mf',
    './Gantry/batch1.3mf',
    './Gantry/Gantry Cable Management/batch1.3mf',
    './Gantry/X Carriage/Toolhead/batch1.3mf',
    './Gantry/X Carriage/batch1.3mf',
    './Gantry/X Carriage/batch2.3mf',
    './Gantry/Front Idlers/batch1.3mf',
    './Gantry/XY Joints/MZBOT Hall Endstop/batch1.3mf',
    './Gantry/XY Joints/batch1.3mf',
    './Gantry/XY Joints/Mechanical Endstop/batch1.3mf',
    './80T Drivegear VLock/batch1.3mf',
    './FSR Tool Offset Switch/batch1.3mf',
    './Z Drive/batch1.3mf',
    './Z Drive/batch2.3mf',
    './Z Drive/batch3.3mf',
    './Z Drive/Idlers/batch1.3mf',
    './Z Drive/Idlers/batch2.3mf',
]

SLIC3R_BIN_PATH='/home/logic/Appimages/Slic3rPE-1.42.0-alpha5+linux64-full-201902041815.AppImage'

# abs path of 3mf file
batch_3mf_files = [ '/'.join([PROJ_HOME,file_3mf]) for file_3mf in file_3mf_list]
batch_stl_files=[ batch_3mf_file.replace('.3mf','.stl') for batch_3mf_file in batch_3mf_files ]
gcode_files = [batch_stl_file.replace('.stl','.gcode') for batch_stl_file in batch_stl_files]

def launch_slic3r(active_config=''):
    print('start slic3r .. ')

    command = SLIC3R_BIN_PATH
    if active_config!='':
        command = ' '.join([command, '--load %s' % active_config])

    print('-'*120)
    print()
    print(command)
    print()
    print('-'*120)
    input('press a key after start')

    sleep_sec = 5
    print('wait a while for program becomes steady...')
    count_down(5)

    get_win_id()

def get_win_id():
    global slic3r_win_id
    slic3r_win_id = xdo.search_windows(winclass='slic3r'.encode(), only_visible=True)
    slic3r_win_id = slic3r_win_id[0]

    pass

# delete all
# 	- ctrl + del
def delete_existing_model():
    global xdo

    xdo.raise_window(slic3r_win_id)
    # xdo.click_window(slic3r_win_id,1)
    sleep(0.1)

    xdo.send_keysequence_window(slic3r_win_id, 'Alt+e'.encode())
    sleep(0.1)
    xdo.send_keysequence_window(slic3r_win_id, 'a'.encode())
    # sleep(0.5)
    # xdo.send_keysequence_window(slic3r_win_id, 'KP_Delete'.encode())

    # xdo.raise_window(slic3r_win_id)
    # xdo.click_window(slic3r_win_id,1)
    # xdo.focus_window(slic3r_win_id)
    # xdo.send_keysequence_window(slic3r_win_id, 'Ctrl+KP_Delete'.encode())
    sleep(0.1)

# import stl file
# 	- ctrl + i
# 	- insert stl file path (xxx.stl)
# 	- press OK
def import_stl_file(stl_file_path):
    global xdo, slic3r_win_id

    xdo.send_keysequence_window(slic3r_win_id, 'ctrl+i'.encode())
    sleep(0.5)

    open_stl_win_id = xdo.search_windows(winclass='slic3r'.encode(), only_visible=True)[1]
    xdo.send_keysequence_window(slic3r_win_id, 'ctrl+a'.encode())
    sleep(0.5)

    xdo.enter_text_window(open_stl_win_id,stl_file_path.encode())
    xdo.send_keysequence_window(slic3r_win_id, 'KP_Enter'.encode())
    sleep(2)

# export gcode
# 	- ctrl + G
# 	- insert output path (xxx.gcode)
# 	- press OK
def export_gcode(gcode_path):
    global xdo, slic3r_win_id
    xdo.send_keysequence_window(slic3r_win_id, 'ctrl+g'.encode())
    sleep(0.5)

    open_stl_win_id = xdo.search_windows(winclass='slic3r'.encode(), only_visible=True)[1]
    xdo.send_keysequence_window(slic3r_win_id, 'ctrl+a'.encode())
    sleep(0.5)

    delete_file_if_exist(gcode_path)
    xdo.enter_text_window(open_stl_win_id,gcode_path.encode())
    xdo.send_keysequence_window(slic3r_win_id, 'KP_Enter'.encode())
    sleep(0.5)

def export_batch_stl(batch_stl_path):
    global xdo, slic3r_win_id
    print('export batch stl')
    xdo.raise_window(slic3r_win_id)

    sleep(0.1)
    # xdo.send_keysequence_window_down(slic3r_win_id, 'alt+f'.encode())
    # sys.exit()
    for key_seq in ['alt+f','e','s']:
        print('press %s' % key_seq )
        xdo.send_keysequence_window_down(slic3r_win_id, key_seq.encode())
        sleep(0.2)

    open_stl_win_id = xdo.search_windows(winclass='slic3r'.encode(), only_visible=True)[1]

    delete_file_if_exist(batch_stl_path)
    xdo.send_keysequence_window(slic3r_win_id, 'ctrl+a'.encode())
    xdo.enter_text_window(open_stl_win_id,batch_stl_path.encode())
    xdo.send_keysequence_window(slic3r_win_id, 'KP_Enter'.encode())
    sleep(0.5)


# done

def get_slic3r_window():
    # xprop |grep ^_NET
    global xdo
    print('get_slic3r_window')
    slic3r_win_id = xdo.search_windows(winclass='slic3r'.encode(), only_visible=True)
    pprint(slic3r_win_id)
    return slic3r_win_id

def check_if_file_exist(file_to_check):
    return os.path.exists(file_to_check)

def delete_file_if_exist(file_to_delete):
    if check_if_file_exist(file_to_delete):
        print('delete file')
        os.remove(file_to_delete)

def getEpochTime(offset=0):
    return int(datetime.now().strftime('%s')) + offset

def check_time_out_already(time_start, timeout):
    # return true if within timeout
    check = getEpochTime()
    return ((check - time_start) < timeout)

def wait_until_file_exist(file_to_wait, timeout=180):
    start = getEpochTime()
    keep_going = True

    FILE_READY_COOLDOWN_s = 0.1

    while (keep_going):
        sleep(1)
        file_found = check_if_file_exist(file_to_wait)
        keep_going = check_time_out_already(start,timeout) and not(file_found)
        print('wait for file %s ' % file_to_wait)

    if not(keep_going) and not(file_found):
        print('error get file %s timeout !!' % file_to_wait)
    elif (file_found):
        print('file %s found' % file_to_wait)
        # sleep a while for cooldown
        sleep(FILE_READY_COOLDOWN_s)

def count_down(time_to_count_s, message=''):
    for i in range(time_to_count_s,0,-1):
        print('counting down... %d' % i)
        if message != '':
            print(message)
        sleep(1)


if __name__ == '__main__':
    launch_slic3r(SLIC3R_ACTIVE_CONFIG)
    count_down(3, 'hands off keyboard and mouse')

    slic3r_win_id = get_slic3r_window()[-1]
    for (batch_3mf_file, batch_stl_file) in zip(batch_3mf_files, batch_stl_files):
        get_slic3r_window()
        import_stl_file(batch_3mf_file)

        export_batch_stl(batch_stl_file)
        wait_until_file_exist(batch_stl_file)
        delete_existing_model()


    for (stl_file, gcode_file) in zip(batch_stl_files, gcode_files):
        print('\r'*3)
        print('processing STL file : %s '% stl_file)
        print('-'*120)
        get_slic3r_window()
        import_stl_file(stl_file)

        export_gcode(gcode_file)
        wait_until_file_exist(gcode_file)
        delete_existing_model()
        # # delete_file_if_exist(gcode_file)

    print('-'*120)
    print()
    print('done')
