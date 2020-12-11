# Transmission-migrate

Dirty python 3 script used to migrate the download folder of Transmission between different machines. What the script does is

1. Find all the torrent files
2. Look for the seemingly correct downloder folder by parsing the torrent file and check the name of downloaded content
3. Add the torrent back to Transmission via RPC protcol and queue for verification

## Requirements
- python3
- transmission-rpc: https://transmission-rpc.readthedocs.io/en/v3.2.1/index.html
- torrent_parser: https://github.com/7sDream/torrent_parser