from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os.path import join
import time
import zlib

from XRootD import client
from tqdm import tqdm

from .exceptions import ChecksumMismatchError, ChecksumNotSupportedError


__all__ = [
    'URL',
    'CopyProcess',
]


class URL(object):
    _filesystems = {}

    def __init__(self, path):
        self._path = path
        self._url = client.URL(path)
        assert self._url.is_valid(), path

    def __str__(self):
        return self._path

    def __repr__(self):
        return '{name}({path})'.format(name=self.__class__, path=self._path)

    @property
    def _fs(self):
        host = self._url.protocol + '://' + self._url.hostid
        if host not in self._filesystems:
            self._filesystems[host] = client.FileSystem(host)
        return self._filesystems[host]

    @property
    def exists(self, n_retries=0):
        status, response = self._fs.stat(self._url.path_with_params)
        if status.ok:
            return True
        elif status.errno == 3011:
            return False
        elif status.code == 204:
            print('Received authorisation failure, retrying in 60 seconds ('+str(n_retries)+' total)')
            time.sleep(60)
            return URL.exists.fget(self, n_retries+1)
        else:
            raise ValueError('Unrecognised error status: '+repr(status))

    def checksum(self, checksum_type=None, n_retries=0):
        status, checksum = self._fs.query(client.flags.QueryCode.CHECKSUM, self._url.path_with_params)
        if status.ok:
            reponse_checksum_type, checksum = checksum.strip('\x00').split(' ')
            if checksum_type is not None and reponse_checksum_type != checksum_type:
                raise NotImplementedError(reponse_checksum_type, checksum_type)
            return checksum_type, int(checksum, base=16)
        elif status.code == 204:
            print('Received authorisation failure, retrying in 60 seconds ('+str(n_retries)+' total)')
            time.sleep(60)
            return self.checksum(checksum_type, n_retries+1)
        elif status.errno == 3013:
            print('Checksumming not supported remotely, running locally (might be slow):', self._path)
            assert checksum_type == 'adler32' or checksum_type is None
            with client.File() as f:
                f.open(self._path, client.flags.OpenFlags.READ)
                part_sum = 1
                status, stat_info = f.stat()
                assert status.ok, status
                with tqdm(total=stat_info.size, unit='B', unit_scale=True, leave=False) as pbar:
                    for chunk in f.readchunks(offset=0, chunksize=1024*1024*32):
                        part_sum = zlib.adler32(chunk, part_sum)
                        pbar.update(len(chunk))
            return checksum_type, (part_sum & 0xFFFFFFFF)
        elif status.errno == 3011:
            raise IOError(status.message)
        else:
            raise ValueError('Unrecognised error status: '+repr(status))

    def validate_checksum(self, other):
        if not self.exists:
            raise IOError(str(self) + "doesn't exist")
        if not other.exists:
            raise IOError(str(other) + "doesn't exist")
        checksum_type, self_checksum = self.checksum()
        _, other_checksum = other.checksum(checksum_type)
        if self_checksum != other_checksum:
            raise ChecksumMismatchError(self, hex(self_checksum), other, hex(other_checksum))
            # print('raise ChecksumMismatchError(', self, hex(self_checksum), other, hex(other_checksum))

    def join(self, *args):
        return self.__class__(join(self._path, *args))


class CopyProgressHandler(client.utils.CopyProgressHandler):
    def __init__(self, total_jobs):
        self._jobs_pbar = tqdm(total=total_jobs)
        self._current_id = None
        self._current_pbar = None

    def begin(self, job_id, total, source, target):
        pass

    def end(self, job_id, results):
        self._current_id = None
        if self._current_pbar is not None:
            self._current_pbar.close()
            self._current_pbar = None
        self._jobs_pbar.update()

    def update(self, job_id, processed, total):
        try:
            if self._current_id is None:
                self._current_id = job_id
            elif self._current_id != job_id:
                print('Progress bar logic failure')
            elif self._current_pbar is None:
                # Create this the second loop to workaround for a race in tqdm
                self._current_pbar = tqdm(total=total, unit='B', unit_scale=True, leave=False)
            else:
                self._current_pbar.update(processed - self._current_pbar.n)
        except Exception as e:
            print('Exception in update', e)

    def should_cancel(self, job_id):
        print('Called CopyProgressHandler.should_cancel', job_id)
        return False


class CopyProcess(object):
    def __init__(self):
        self._jobs = {}

    def __bool__(self):
        return bool(self._jobs)

    def __len__(self):
        return len(self._jobs)

    def __contains__(self, lfn):
        return lfn in self._jobs

    def add_job(self, replica, destination):
        from .structures import Replica
        assert isinstance(replica, Replica)
        self._jobs[replica] = destination

    def copy(self):
        print('Copying', len(self._jobs), 'files')
        replicas = sorted(self._jobs, key=lambda replica: replica.lfn)

        process = client.CopyProcess()
        for replica in replicas:
            process.add_job(str(replica.pfn), str(self._jobs[replica]))

        status = process.prepare()
        assert status.ok, status

        status, results = process.run(CopyProgressHandler(len(self._jobs)))
        assert status.ok, (status, results)
        return {replica: result['status'].ok for replica, result in zip(replicas, results)}
