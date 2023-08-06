import boto3
import logging
import json
import datetime
import dateutil.parser

class KinesisFirehoseHandler(logging.Handler):
    """
    Amazon Kinesis Firehose logging handler
    """

    def __init__(self, *args, **kwargs):

        super(KinesisFirehoseHandler, self).__init__(
            level=kwargs.pop('level', logging.NOTSET))
        self.stream_name = kwargs.pop('stream_name', None)
        self.client = boto3.client('firehose')
        
    def with_backpack(self, backpack):
        self.backpack = backpack
        return self

    def emit(self, record):
        try:
            if self.backpack:
                record.__dict__.update(self.backpack.perm_items)
                record.__dict__.update(self.backpack.metrics)
                record.__dict__.update(self.backpack.one_time_items)
                if(self.backpack.timers):
                    for m in self.backpack.timers:
                        
                        delta = datetime.datetime.now() - dateutil.parser.parse(self.backpack.timers[m])
                        record.__dict__['{}InMs'.format(m)] = int(delta.total_seconds() * 1000)
            self.client.put_record(
                DeliveryStreamName=self.stream_name,
                Record={ 'Data': self.format(record) })
            if (self.backpack.one_time_items):
                self.backpack.one_time_items = {}
        except:
            raise
            self.handleError(record)

