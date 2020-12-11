#!/usr/bin/env python3
#%%
import glob
from torrent_parser import TorrentFileParser
import re
from subprocess import Popen, PIPE
import shlex
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

torrents = sorted_alphanumeric(glob.glob('*.torrent'))
# %%
downloadDir = '/mnt/nas/Downloads'  # Download dir in real disk
downloadDirT = '/downloads'                                # Download dir used in Transmission e.g. docker mounting point

def list(filepath):
    f = []
    d = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            f.append(os.path.join(root, file))
        for dd in dirs:
            d.append(os.path.join(root, dd))

    return f, d

cwd = os.getcwd()
os.chdir(downloadDir)
files, folders = list('./')
os.chdir(cwd)
fileName = [os.path.split(i)[-1] for i in files]
folderName = [os.path.split(i)[-1] for i in folders]

#%%
def findDownload(t):
    try:
        with open(t, 'rb') as f:
            dt = TorrentFileParser(f, encoding='utf-8').parse()
    except:
        return False, None

    tname = dt['info']['name']
    isFolder = False
    if 'files' in dt['info']:
        isFolder = True
    if isFolder:
        for i, fn in enumerate(folderName):
            if fn == tname:
                return True, folders[i]
    else:
        for i, fn in enumerate(fileName):
            if fn == tname:
                return True, files[i]

    return False, None

torrentAdded = []
torrentFailed = []

with ThreadPoolExecutor() as e:
    fs = {e.submit(findDownload, t): t for t in torrents}
    for f in as_completed(fs):
        t = fs[f]
        ifound, fpath = f.result()
        if ifound:
            torrentAdded.append({
                'torrent': t,
                'path': os.path.abspath(os.path.join(downloadDirT, fpath, '../'))
            })
        else:
            torrentFailed.append(t)


# %%
from transmission_rpc import Client
c = Client(host='192.168.1.100', port=9091, path='/transmission/', username='admin', password='admin')


# %%
t = torrentAdded[0]
with open(t['torrent'], 'rb') as f:
    c.add_torrent(f, download_dir=t['path'], paused=True)

#%%
for i in range(1,len(torrentAdded)):
    t = torrentAdded[i]
    with open(t['torrent'], 'rb') as f:
        c.add_torrent(f, download_dir=t['path'], paused=True)

# %%
import json
with open('Failed.json', 'w') as f:
    json.dump(torrentFailed, f, ensure_ascii=False, indent=2)
# %%
