from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from .structures import DiracFile
# from .utils import grouper


def from_bkquery(bk_paths):
    if not isinstance(bk_paths, list):
        bk_paths = [bk_paths]

    from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery
    # from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    files = []
    for bk_path in bk_paths:
        bkQuery = BKQuery(bkQuery=bk_path, visible='Yes')
        # bkClient = BookkeepingClient()

        # useFilesWithMetadata = False
        # if useFilesWithMetadata:
        #     res = bkClient.getFilesWithMetadata(bkQuery.getQueryDict())
        #     if not res['OK']:
        #         print('ERROR getting the files', res['Message'], file=sys.stderr)
        #         sys.exit(1)
        #     parameters = res['Value']['ParameterNames']
        #     for record in res['Value']['Records']:
        #         dd = dict(zip(parameters, record))
        #         lfn = dd.pop('FileName')
        #         files.append(DiracFile(lfn))

        lfns = bkQuery.getLFNs(printSEUsage=False, printOutput=False)
        files.extend([DiracFile(lfn) for lfn in lfns])

        if not files:
            raise ValueError('No files found for BK query:', bk_path)

    print(len(files), 'files found')

    return files


def from_prod_id(prod_ids, file_type):
    if not isinstance(prod_ids, list):
        prod_ids = [prod_ids]

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    files = []
    for prod_id in prod_ids:
        bk_client = BookkeepingClient()
        result = bk_client.getProductionFiles(prod_id, file_type)
        if not result['OK']:
            print('ERROR getting the files', result['Message'], file=sys.stderr)
            sys.exit(1)
        files.extend([DiracFile(lfn) for lfn in result['Value']])

        if not files:
            raise ValueError('No files found for BK query:', prod_id)

    print(len(files), 'files found')

    return files
