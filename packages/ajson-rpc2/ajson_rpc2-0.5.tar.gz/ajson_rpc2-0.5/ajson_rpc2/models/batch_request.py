''' To send several Request objects at the same time,
the Client MAY send an Array filled with Request objects.
This module defines the class for batch request'''
from ..typedef import List, Dict
from .request import Request, Notification
from .fixed_list import FixedList


class BatchRequest:
    '''
    BatchRequest represent several rpc-call at the same time
    Use batch request should improve client or server performance
    Due to it can save the transfer time
    '''
    def __init__(self, requests: FixedList=None, notifications: FixedList=None):
        if requests is None:
            requests = FixedList(Request)
        if notifications is None:
            notifications = FixedList(Notification)
        self.requests = requests
        self.notifications = notifications

    @classmethod
    def from_json(cls, json: List[Dict]):
        ''' convert from dict to the new BatchRequest object

        :param json: the batch request json object which use to convert '''
        if isinstance(json, list) is False:
            raise TypeError(f"json object should be a type of list, not {str(type(json))}")
        batch_request = cls()
        for req in json:
            if 'id' in req:
                batch_request.requests.append(Request.from_json(req))
            else:
                batch_request.notifications.append(Notification.from_json(req))

        return batch_request
