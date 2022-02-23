#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is copied from the EcoInventDownLoader (eidl) repository at
https://github.com/haasad/EcoInventDownLoader
with only minor bug fix and modification to be compatible with BW2QSD.

The reason for including this module in BW2QSD rather than adding EcoInventDownLoader
as a dependent package is because EcoInventDownLoader does not have a PyPI release,
and installing it via conda requires the installation of the entire Brightway2 framework
via conda, which has some unfixed bugs, and the use of both pip and conda in installation
could be overwhelming for users.

This module is under dual licenses:

    EcoInventDownLoader (MIT)
    Please refer to https://github.com/haasad/EcoInventDownLoader/blob/master/LICENSE
    for license details.

    BW2QSD (University of Illinois/NCSA)
    Please refer to https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
'''

import os
import string
import tempfile
import getpass
import subprocess

import requests
from bs4 import BeautifulSoup
import brightway2 as bw

from .storage import eidlstorage


class EcoinventDownloader:
    def __init__(self, username=None, password=None, version=None,
                 system_model=None, outdir=None, **kwargs):
        self.username = username
        self.password = password
        self.version = version
        self.system_model = system_model
        self.outdir = outdir

    def run(self):
        if self.check_stored():
            return
        if self.username is None or self.password is None:
            self.username, self.password = self.get_credentials()
        print('logging in to ecoinvent homepage...')
        self.login()
        self.db_dict = self.get_available_files()
        print('login successful!')
        if (self.version, self.system_model) not in self.db_dict.keys():
            self.version, self.system_model = self.choose_db()
        if self.check_stored():
            return

        print('downloading {} {} ...'.format(self.system_model, self.version))
        self.download()
        print('download finished!: {}\n'.format(self.out_path))

    @property
    def file_name(self):
        fn = '{}{}.7z'.format(self.system_model, str(self.version).replace('.', ''))
        return fn

    def check_stored(self):
        if self.file_name in eidlstorage.stored_dbs:
            self.out_path = eidlstorage.stored_dbs[self.file_name]
            print('database already downloaded')
            return True
        else:
            return False

    def get_credentials(self):
        un = input('ecoinvent username: ')
        pw = getpass.getpass('ecoinvent password: ')
        return un, pw

    def login(self):
        self.session = requests.Session()
        logon_url = 'https://v33.ecoquery.ecoinvent.org/Account/LogOn'
        post_data = {'UserName': self.username,
                     'Password': self.password,
                     'IsEncrypted': 'false',
                     'ReturnUrl': '/'}
        try:
            self.session.post(logon_url, post_data, timeout=20)
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError) as e:
            self.handle_connection_timeout()
            raise e

        success = bool(self.session.cookies)
        self.login_success(success)

    def login_success(self, success):
        if not success:
            print('Login failed')
            self.username, self.password = self.get_credentials()
            self.login()

    def handle_connection_timeout(self):
        print('The request timed out, please check your internet connection!')
        if eidlstorage.stored_dbs:
            print(
                'You have the following databases stored:\n\t{}\n'.format(
                    '\n\t'.join(eidlstorage.stored_dbs.keys())) +
                'You can use these offline by adding the corresponding `version` and `system_model` keywords\n' +
                "Example: eidl.get_ecoinvent(version='3.5', system_model='cutoff')"
            )

    def get_available_files(self):
        files_url = 'https://v33.ecoquery.ecoinvent.org/File/Files'
        try:
            files_res = self.session.get(files_url, timeout=20)
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError) as e:
            self.handle_connection_timeout()
            raise e
        soup = BeautifulSoup(files_res.text, 'html.parser')
        file_list = [l for l in soup.find_all('a', href=True) if
                     l['href'].startswith('/File/File?')]
        link_dict = {f.contents[0]: f['href'] for f in file_list}
        link_dict = {
            k.replace('-', ''):v for k, v in link_dict.items() if k.startswith('ecoinvent ') and
            k.endswith('ecoSpold02.7z') and not 'lc' in k.lower()
        }
        db_dict = {
            tuple(k.replace('ecoinvent ', '').split('_')[:2:]): v for k, v in link_dict.items()
        }
        return db_dict

    def choose_db(self):
        versions = {k[0] for k in self.db_dict.keys()}
        version_dict = dict(zip(string.ascii_lowercase,
                                sorted(versions, reverse=True)))
        print('\n', 'available versions:')
        for k, version in version_dict.items():
            print(k, version)
        while True:
            version = input('version: ')
            if version in versions or version in version_dict.keys():
                break
            else:
                print('Enter version number or letter')
        system_models = {k[1] for k in self.db_dict.keys() if k[0] == version_dict.get(version, version)}
        sm_dict = dict(zip(string.ascii_lowercase, sorted(system_models)))
        print('\n', 'system models:')
        for k, sm in sm_dict.items():
            print(k, sm)
        while True:
            sm = input('system model: ')
            if sm in system_models or sm in sm_dict.keys():
                break
            else:
                print('Enter system model or letter')
        dbkey = (version_dict.get(version, version),
                 sm_dict.get(sm, sm))
        return dbkey

    def download(self):
        url = 'https://v33.ecoquery.ecoinvent.org'
        db_key = (self.version, self.system_model)
        try:
            file_content = self.session.get(url + self.db_dict[db_key], timeout=60).content
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError) as e:
            self.handle_connection_timeout()
            raise e

        if self.outdir:
            self.out_path = os.path.join(self.outdir, self.file_name)
        else:
            self.out_path = os.path.join(os.path.abspath('.'), self.file_name)

        with open(self.out_path, 'wb') as out_file:
            out_file.write(file_content)

    def extract(self, target_dir):
        extract_cmd = ['py7zr', 'x', self.out_path, target_dir]
        try:
            self.extraction_process = subprocess.Popen(extract_cmd)
            self.extraction_process.wait()
        except FileNotFoundError as e:
            if "PYCHARM_HOSTED" in os.environ:
                print('It appears the EcoInventDownLoader is run from PyCharm. ' +
                      'Please make sure you select the the correct conda environment ' +
                      'as your project interperter or run your script/command in a ' +
                      'Python console outside of PyCharm.')
            raise e


def get_ecoinvent(db_name=None, auto_write=False, download_path=None, store_download=True, **kwargs):

    """
    Download and import ecoinvent to current brightway2 project
    Optional kwargs:
        db_name: name to give imported database (string) default is downloaded filename
        auto_write: automatically write database if no unlinked processes (boolean) default is False (i.e. prompt yes or no)
        download_path: path to download .7z file to (string) default is download to temporary directory (.7z file is deleted after import)
        store_download: store the .7z file for later reuse, default is True, only takes effect if no download_path is provided
        username: ecoinvent username (string)
        password: ecoivnent password (string)
        version: ecoinvent version (string), eg '3.5'
        system_model: ecoinvent system model (string), one of {'cutoff', 'apos', 'consequential'}
    """
    with tempfile.TemporaryDirectory() as td:
        if download_path is None:
            if store_download:
                download_path = eidlstorage.eidl_dir
            else:
                download_path = td

        downloader = EcoinventDownloader(outdir=download_path, **kwargs)
        downloader.run()
        downloader.extract(target_dir=td)

        if not db_name:
            db_name = downloader.file_name.replace('.7z', '')
        datasets_path = os.path.join(td, 'datasets')
        importer = bw.SingleOutputEcospold2Importer(datasets_path, db_name)

    if 'biosphere3' not in bw.databases:
        if auto_write:
            bw.bw2setup()
        else:
            print('No biosphere database present in your current ' +
                  'project: {}'.format(bw.projects.current))
            print('You can run "bw2setup()" if this is a new project. Run it now?')
            if input('[y]/n ') in {'y', ''}:
                bw.bw2setup()
            else:
                return

    importer.apply_strategies()
    datasets, exchanges, unlinked = importer.statistics()

    if auto_write and not unlinked:
        print('\nWriting database {} in project {}'.format(
            db_name, bw.projects.current))
        importer.write_database()
    else:
        print('\nWrite database {} in project {}?'.format(
            db_name, bw.projects.current))
        if input('[y]/n ') in {'y', ''}:
            importer.write_database()


def get_ecoinvent_cli():
    downloader = EcoinventDownloader()
    downloader.run()