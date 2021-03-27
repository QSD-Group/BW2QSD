#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

Part of this module is based on the BioSTEAM-LCA package:
https://github.com/scyjth/biosteam_lca

This module is under the University of Illinois/NCSA Open Source License. Please refer to
https://github.com/QSD-Group/BW2QSD/blob/master/LICENSE.txt
for license details.
'''

import os, appdirs, tempfile, subprocess, requests
import eidl
from zipfile import ZipFile
from bw2io import importers, strategies

import zipfile
from bw2data.utils import download_file

'''
TODO:
    Add forwast
'''

__all__ = ('DataDownloader',)

class DataDownloader:
    '''
    To download databases from external sources.
    
    Currently support:
        `ecoinvent <https://www.ecoinvent.org/>`_, version 3+, (license and login credentials required)
        `forwarst <https://lca-net.com/projects/show/forwast/>`_ (NOT YET READY)
        `USLCI <>`_ (NOT YET READY)
    
    Parameters
    ----------
    path : str
        Path for database storage, a new directory "database" will be created under the given path,
        default to current working directory.
    
    
    '''
    
    def __init__(self, path=''):
        path = path if path else os.path.abspath(os.path.dirname(__file__))
        self._db_path = os.path.join(path,'database')
        
    def download_ecoinvent(self, path='', store_download=True):
        '''
        Download ecoinvent database using the ``eidl`` package.
        You will be prompted to enter ecoinvent license and login credentials.
        
        The original package ``eidl`` has compatibility issues with some operating systems,
        e.g., :func:`eidl.get_ecoinvent` may not work, this function fixes the bugs.
        
        Parameters
        ----------
        path : str
            Path for for storing the ecoinvent database (if store_download is True).
            Will use the user data storage directory (based on :func:`appdirs.user_data_dir`)
            if not provided.
        store_download : bool
            Whether to store the downloaded file.
        
        Tips
        ----
        The following system models are supported by ecoinvent [1]_:
            
            [1] cutoff: Allocation, cut-off by classification. 
            For users new to LCI databases, ecoinvent recommends using the 
            cut-off system model when starting to work with ecoinvent version 3.
            
            [2] apos: Allocation at the point of substitution.
            
            [3] consequential: Substitution, consequential,


        .. note::
            When selecting system models, you may run into both "cut-off" and "cutoff"
            models, choose "cutoff", "cut-off" is a bug in ecoinvent.

        
        References
        ----------
        .. [1] `System Models in ecoinvent 3 <https://www.ecoinvent.org/database/system-models-in-ecoinvent-3/system-models-in-ecoinvent-3.html>`_
        
        
        '''
        fp = appdirs.user_data_dir(appname='BW2QSD', appauthor='bw2qsd')
        if not os.path.isdir(fp):
            os.makedirs(fp)
            print (f'\nDirectory {fp} created for ecoinvent database.\n')

        with tempfile.TemporaryDirectory() as td:
            if not path:
                if store_download:
                    download_path = fp
                else:
                    download_path = td
            
            print('\nDownloading data...\n')
            downloader = eidl.EcoinventDownloader(outdir=download_path)
            downloader.run()

            print('\nUnzipping data...\n')
            out_path= downloader.out_path
            extract_cmd = ['7za', 'x', out_path, f'-o{download_path}']
            # # do not use downloader.extract, it may not work on Mac app 
            # downloader.extract(target_dir=download_path)
            
            try:
                self.extraction_process = subprocess.Popen(extract_cmd)
                self.extraction_process.wait() 
            except FileNotFoundError as e:
                print (e)
                pass
           
            db_append = downloader.file_name.replace('.7z', '')
            db_name = 'ecoinvent_' + db_append
            datasets_path = os.path.join(download_path, 'datasets')
            ecospold_import = importers.SingleOutputEcospold2Importer(datasets_path, db_name)
            # try:
            #     ecospold_import = importers.SingleOutputEcospold2Importer(datasets_path, db_name)
            # except ImportError as import_err:
            #     print (import_err)
            
            ecospold_import.apply_strategies()
            
            print ('\nInspecting data...\n')
            self.inspect(ecospold_import, db_name)
                    
            print (f'\nSuccessfully imported ecoinvent database version {db_append}.\n')

            return db_name

    def download_forwast(self):
        '''
        NOT  YET READY
        '''
    # def _import_forwast(self):
    #     filepath = download_file("forwast.bw2package.zip", url="http://lca-net.com/wp-content/uploads/")
    #     dirpath = os.path.dirname(filepath)
    #     zipfile.ZipFile(filepath).extractall(dirpath)
    #     bw2.BW2Package.import_file(os.path.join(dirpath, "forwast.bw2package"))



    def download_USLCI(self):
        '''
        NOT  YET READY
        '''



    @staticmethod
    def inspect(sp, db_name):
        '''
        Check for unlinked exchanges in a given database. 
        If found, it will be the user's decision to if or not continue writing to 
        SQLite3 backend.

        Parameters
        ----------
        sp : obj
            The initialized database to be inspected.
        db_name : obj
            Name of the database being inspected.
        
        Returns
        -------
        datasets: int 
            The total number of lci datasets extracted.        
        exchanges : int
            The total number of exchanges.
        unlinked: int
             The total number of unlinked exchanges.
        '''
        
        datasets, exchanges, unlinked = sp.statistics(print_stats=False)
        
        if not unlinked:
            sp.write_database()
        else:
            print(f'There are {unlinked} unlinked exchanges, would you like to show all unlinked exchanges?')
            if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
                 for x in sp.unlinked:
                     print(x)

            print(f'Continue to write database {db_name}?')            
            if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
                print ('Deleting exchanges with zero amount...')
                for ds in sp.data:
                    ds['exchanges'] = [exc for exc in ds['exchanges'] if (exc['amount'] or exc['uncertainty type'] != 0)]
                
                print ('Drop unlinked exchanges?')
                if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
                    try:
                        sp.apply_strategies([strategies.generic.drop_unlinked])  #sp.drop_unlinked(i_am_reckless=True)
                        sp.statistics()
                        sp.write_database()
                    except:
                        print ('Dropping unlinked exchanges failed')
            else:
                raise Warning ('Stopped writing to backend SQLite3 database')      
        return datasets, exchanges















