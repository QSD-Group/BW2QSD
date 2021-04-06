#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

Part of this module is based on the BioSTEAM-LCA package:
https://github.com/scyjth/biosteam_lca

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
for license details.
'''

import os, appdirs, subprocess, shutil, requests, functools
import brightway2 as bw2
import eidl
from zipfile import ZipFile
from bw2io import importers, strategies

'''
TODO:
    JSON conversion, then add USLCI, etc.
'''


__all__ = ('DataDownloader',)


def _check_db(name, force_skipping=False):
    dbs = []
    for k in bw2.databases.keys():
        if name.lower() in k:
            dbs.append(k)
    
    if dbs:
        print(f'\nThe following {name} database(s) {dbs} exist(s).')

        if force_skipping:
            return False
        else:
            print(f'\nWould you like to download a different version of {name}?')
            if input('[y]/[n]: ') in ('n', 'N', 'no', 'No', 'NO'):
                return False
    
    return True


def _make_dir(path, end_dir=''):
    if not path:
        path = fp = appdirs.user_data_dir(appname='BW2QSD', appauthor='bw2qsd')
        if not os.path.isdir(fp):
            os.makedirs(fp)
            print (f'\nDirectory {fp} created for storing database.')

    full_path = os.path.join(path, end_dir) if end_dir else path
    if not os.path.isdir(full_path):
        os.makedirs(full_path)
        print (f'\nDirectory {full_path} created for storing database.')

    return full_path



class DataDownloader:
    '''
    To download databases from external sources.
    
    Currently support:
        - `ecoinvent <https://www.ecoinvent.org/>`_, version 3+, (license and login credentials required)
        - `FORWAST <https://lca-net.com/projects/show/forwast/>`_
        - `USLCI <>`_ (NOT YET READY)
    
    '''
        
    def download_ecoinvent(self, path='', remove_download=False,
                           remove_cache_data=False):
        '''
        Download ecoinvent database using the ``eidl`` package.
        You will be prompted to enter ecoinvent license and login credentials.
        
        The original package ``eidl`` has compatibility issues with some operating systems,
        e.g., :func:`eidl.get_ecoinvent` may not work, this function fixes the bugs.
        
        .. note::
            
            The entire process may take 10-20 min.
        
        
        Parameters
        ----------
        path : str
            Path for for storing the extracted raw database file.
            Will use the user data storage directory (based on :func:`appdirs.user_data_dir`)
            if not provided.
            
            .. note::
            
                Downloaded files are stored under the "EcoInventDownLoader" directory
                in the user data storage directory.


        remove_download : bool
            Whether to remove the downloaded zipfile after extracting.
        remove_cache_data : bool
            Whether to remove the raw database files (i.e., unzipped zipfile)
            after importing.
        
        Tip
        ---
        The following system models are supported by ecoinvent [1]_:
            
            [1] cutoff: Allocation, cut-off by classification. \
            For users new to LCI databases, ecoinvent recommends using the \
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
        if not _check_db('ecoinvent'):
            return

        path = _make_dir(path, 'ecoinvent')
        downloader = eidl.EcoinventDownloader()
        downloader.run()

        print('\nUnzipping data...')
        
        db_append = downloader.file_name.replace('.7z', '')
        
        extracted_path = os.path.join(path, db_append)
        try: # remove previous extracted cache
            os.rmdir(extracted_path)
        except FileNotFoundError:
            pass
        
        extract_cmd = ['7za', 'x', downloader.out_path, f'-o{extracted_path}']
        # # do not use downloader.extract, it may not work on Mac app 
        # downloader.extract(target_dir=path)
        
        self.extraction_process = subprocess.Popen(extract_cmd)
        self.extraction_process.wait()

        db_name = 'ecoinvent_' + db_append
        datasets_path = os.path.join(extracted_path, 'datasets') 
                
        ecospold_import = importers.SingleOutputEcospold2Importer(datasets_path, db_name)
        ecospold_import.apply_strategies()
        
        print('\nInspecting data...')
        self.inspect(ecospold_import, db_name)
        
        if remove_download:
            os.remove(downloader.out_path)

        if remove_cache_data:
            shutil.rmtree(extracted_path)
            try:
                os.rmdir(path)
            except OSError:
                pass
                
        print(f'\nSuccessfully imported ecoinvent database as "ecoinvent_{db_append}".')


    def download_forwast(self, path='',
                         url='http://lca-net.com/wp-content/uploads/forwast.bw2package.zip',
                         remove_download=False, remove_cache_data=False):
        '''
        Download the FORWAST database.
        
        Parameters
        ----------
        path : str
            Path for for storing the downloaded and extracted raw database file.
            Will use the user data storage directory (based on :func:`appdirs.user_data_dir`)
            if not provided.
        url : str
            FORWAST database downloading url.
            You may need to update the url according to the FORWAST website
            if the default one is not working.       
        remove_download : bool
            Whether to remove the downloaded zipfile after extracting.
        remove_cache_data : bool
            Whether to remove the raw database files (i.e., unzipped zipfile)
            after importing.
        
        See Also
        --------
        The `FORWARST project <https://lca-net.com/projects/show/forwast/>`_.
        
        '''
        if not _check_db('FORWAST', True):
            return
        
        path = _make_dir(path, 'forwast')
        fp = os.path.join(path, 'forwast.package.zip')
        fp_extracted = os.path.join(path, 'forwast.bw2package')
        if os.path.exists(fp_extracted):
            print('\nUsing previously extracted FORWAST package in directory ' \
                  f'"{path}".')
        
        else:            
            if os.path.exists(fp):
                print('\nUsing previously downloaded FORWAST package in directory ' \
                      f'"{path}".')
    
            else:
                print('\nDownloading data...\n')
                r = requests.get(url, stream=True)
                if r.status_code != 200:
                    raise (f'URL "{url}" returns status code "{r.status_code}".')
               
                # From BioSTEAM-LCA:
                # use the following code instead of ``r.raw.read`` to save what is being streamed to a file.
                # with open(filename, 'wb') as fd:
                with open(fp, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128): # chunk = 128 * 1024
                        fd.write(chunk)
            
            print('\nExtracting data...')
            ZipFile(fp).extractall(path)         
        bw2.BW2Package.import_file(os.path.join(path, 'forwast.bw2package'))
        
        if remove_download:
            os.remove(fp)

        if remove_cache_data:
            shutil.rmtree(path)
    
        print('\nSuccessfully imported FORWAST database as "forwast".')



    def download_USLCI(self, db_path):
        '''
        NOT READY YET
        
        
        Import the pre-downloaded and pre-converted (from JSON to ecoSpold1 or ecoSpold2)
        U.S. Life Cycle Inventory (USLCI) database from
        `Federal LCA Commons repository <https://www.lcacommons.gov/lca-collaboration/>`.
        
        .. note::
            
            The files in the `Federal LCA Commons repository <https://www.lcacommons.gov/lca-collaboration/>`
            are in JSON file, and need to be converted to ecoSpold1 (`outdated <https://www.ecoinvent.org/data-provider/data-provider-toolkit/ecospold2/changes-from-ecospold1-to-ecospold2/changes-from-ecospold1-to-ecospold2.html>`_)
            or ecoSpold2 before using.
            
        Parameters
        ----------
        db_path : str
            Directory to the sown
        
        
        '''
        db_name = 'us_lci'
        
        
        from warnings import warn
        warn('This function is not ready yet.')
        return
    
        #!!! Look into brightway2 for direct importing from JSON
    
        lci_import = importers.SingleOutputEcospold2Importer(
            os.path.join(self.dirpath, 'US_LCI'), db_name)
        lci_import.apply_strategies()
        
        lci_import.migrate('unusual-units')
        lci_import.migrate('default-units')
        
        # Link the biosphere flows by their names, units, and categories
        link_iter = functools.partial(strategies.link_iterable_by_fields, 
                                      other= bw2.Database(bw2.config.biosphere),
                                      kind='biosphere')
        lci_import.apply_strategy(link_iter)
        
        print('\nInspecting data...\n')        
        self.inspect(lci_import, db_name)

        print('\nSuccessfully imported U.S. Life Cycle Inventory database as "us_lci".')


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
            print(f'\nThere are {unlinked} unlinked exchanges, would you like to show all unlinked exchanges?')
            if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
                 for x in sp.unlinked:
                     print(x)

            print(f'\nContinue to write database {db_name}?')            
            if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
                print ('Deleting exchanges with zero amount...')
                for ds in sp.data:
                    ds['exchanges'] = [exc for exc in ds['exchanges'] if (exc['amount'] or exc['uncertainty type'] != 0)]
                
                print ('\nDrop unlinked exchanges?')
                if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
                    try:
                        sp.apply_strategies([strategies.generic.drop_unlinked])  #sp.drop_unlinked(i_am_reckless=True)
                        sp.statistics()
                        sp.write_database()
                    except:
                        print ('\nDropping unlinked exchanges failed')
            else:
                raise Warning ('\nStopped writing to backend SQLite3 database')      
        return datasets, exchanges


    @property
    def available_databases(self):
        '''All databases that have been loaded into ``Brightway2``.'''
        return bw2.databases














