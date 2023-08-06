from awstools._aws import AwsManager


class EventManager(AwsManager):

    def __init__(self, queue_name, region='us-east-1', **kwargs):
        super(EventManager, self).__init__(**kwargs)
        self.name = queue_name
        self.region = region

    def consume(self):
        while 1:
            messages = queue_in.get_messages(wait_time_seconds=20, num_messages=10)
            for message in messages:
                queue_in.delete_message(message)


def start_consumer():
    pass


if __name__ == '__main__':
    start_consumer()
