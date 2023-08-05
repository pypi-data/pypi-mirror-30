import sys
import os
import boto3.s3.transfer
import s3transfer.manager
import threading


class ProgressPercentage(object):
    """This is for progress of a transfer.  To impliment your own, ensure the class
    is callable."""
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(f"\r{self._filename}  {self._seen_so_far} / {self._size} ({percentage:.2f}%) ")
            sys.stdout.flush()


class TransferConfig(s3transfer.manager.TransferConfig):
    """Configurations for the transfer mangager
        :param multipart_threshold: The threshold for which multipart
            transfers occur.

        :param max_request_concurrency: The maximum number of S3 API
            transfer-related requests that can happen at a time.

        :param max_submission_concurrency: The maximum number of threads
            processing a call to a TransferManager method. Processing a
            call usually entails determining which S3 API requests that need
            to be enqueued, but does **not** entail making any of the
            S3 API data transfering requests needed to perform the transfer.
            The threads controlled by ``max_request_concurrency`` is
            responsible for that.

        :param multipart_chunksize: The size of each transfer if a request
            becomes a multipart transfer.

        :param max_request_queue_size: The maximum amount of S3 API requests
            that can be queued at a time. A value of zero means that there
            is no maximum.

        :param max_submission_queue_size: The maximum amount of
            TransferManager method calls that can be queued at a time. A value
            of zero means that there is no maximum.

        :param max_io_queue_size: The maximum amount of read parts that
            can be queued to be written to disk per download. A value of zero
            means that there is no maximum. The default size for each element
            in this queue is 8 KB.

        :param io_chunksize: The max size of each chunk in the io queue.
            Currently, this is size used when reading from the downloaded
            stream as well.

        :param num_download_attempts: The number of download attempts that
            will be tried upon errors with downloading an object in S3. Note
            that these retries account for errors that occur when streamming
            down the data from s3 (i.e. socket errors and read timeouts that
            occur after recieving an OK response from s3).
            Other retryable exceptions such as throttling errors and 5xx errors

            are already retried by botocore (this default is 5). The
            ``num_download_attempts`` does not take into account the
            number of exceptions retried by botocore.

        :param max_in_memory_upload_chunks: The number of chunks that can
            be stored in memory at a time for all ongoing upload requests.
            This pertains to chunks of data that need to be stored in memory
            during an upload if the data is sourced from a file-like object.
            The total maximum memory footprint due to a in-memory upload
            chunks is roughly equal to:

                max_in_memory_upload_chunks * multipart_chunksize
                + max_submission_concurrency * multipart_chunksize

            ``max_submission_concurrency`` has an affect on this value because
            for each thread pulling data off of a file-like object, they may
            be waiting with a single read chunk to be submitted for upload
            because the ``max_in_memory_upload_chunks`` value has been reached
            by the threads making the upload request.

        :param max_in_memory_download_chunks: The number of chunks that can
            be buffered in memory and **not** in the io queue at a time for all
            ongoing dowload requests. This pertains specifically to file-like
            objects that cannot be seeked. The total maximum memory footprint
            due to a in-memory download chunks is roughly equal to:

                max_in_memory_download_chunks * multipart_chunksize

        :param max_bandwidth: The maximum bandwidth that will be consumed
            in uploading and downloading file content. The value is in terms of
            bytes per second.
    """

    def __init__(self, **kwargs):
        # super(boto3.s3.transfer.S3TransferConfig, self).__init__(**kwargs)
        s3transfer.manager.TransferConfig.__init__(self, **kwargs)
        self.use_threads = True


class Transfer(boto3.s3.transfer.S3Transfer):
    """There are a number of different implimentations of these methods floating
    around inside boto.  It is extended here to ensure the correct one is used.
    """
    pass
