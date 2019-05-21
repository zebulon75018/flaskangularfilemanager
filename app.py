# -*- coding:utf-8 -*-

import json
import datetime

from flask import Flask, request, render_template, jsonify
import os
import sys

app = Flask(__name__)

# From https://github.com/joni2back/angular-filemanager/blob/master/bridges/python/tornado/filemanager.py



def timestamp_to_str(timestamp, format_str='%Y-%m-%d %I:%M:%S'):
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime(format_str)

def filemode(mode):
    is_dir = 'd' if stat.S_ISDIR(mode) else '-'
    dic = {'7': 'rwx', '6': 'rw-', '5': 'r-x', '4': 'r--', '0': '---'}
    perm = str(oct(mode)[-3:])
    return is_dir + ''.join(dic.get(x, x) for x in perm)


def get_file_information(path):
    if sys.platform == 'win32':
    if os.path.isdir(path):
            ftype = 'dir'
            fmode = "drwxrwxrwx"
    else:
            ftype ='file'
            fmode = "-rwxrwxrwx"
    fsize = 0 
    ftime = timestamp_to_str(os.path.getatime(path))
    """
    else:
        fstat = os.stat(path)
        if stat.S_ISDIR(fstat.st_mode):
            ftype = 'dir'
        else:
            ftype = 'file'
        
        fsize = fstat.st_size
        ftime = timestamp_to_str(fstat.st_mtime)
        fmode = filemode(fstat.st_mode)
    """
    return ftype, fsize, ftime, fmode



class FileManager:
    def __init__(self, root='/', show_dotfiles=True):
        self.root = os.path.abspath(root)
        self.show_dotfiles = show_dotfiles

    def list(self, request):
        path = os.path.abspath(self.root + request['path'])
        if not os.path.exists(path) or not path.startswith(self.root):
            return {'result': ''}

        files = []
        for fname in sorted(os.listdir(path)):
            if fname.startswith('.') and not self.show_dotfiles:
                continue

            fpath = os.path.join(path, fname)

            try:
                ftype, fsize, ftime, fmode = get_file_information(fpath)
            except Exception as e:
                print(" Exception %s " % e)
                continue

            files.append({
                'name': fname,
                'rights': fmode,
                'size': fsize,
                'date': ftime,
                'type': ftype,
            })

        return {'result': files}


fm = FileManager("YOURPATH",False)

@app.route('/bridges/php/handler.php', methods=["POST"])
def handler():
    jsondata = request.json
    if jsondata["action"] == "list":
        return jsonify(fm.list(jsondata))
    else:
        return jsonify([])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
