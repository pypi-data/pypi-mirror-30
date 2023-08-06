

class Response(object):
    """
    The response object that is used by default for microservices.
    """
    CONTENT_FIELD_NAME = 'content'
    ERROR_FIELD_NAME = 'error'
    EVENT_FIELD_NAME = 'event-name'

    def __init__(self, data=None, *args, **kwargs):
        super(Response, self).__init__()
        self.data = data

    @classmethod
    def from_error(cls, error_type, message, event_name=None):
        if isinstance(message, str) and not message.endswith('.'):
            message = message + '.'

        response = {
            cls.ERROR_FIELD_NAME: {
                "type": error_type,
                "message": message
            },
            cls.EVENT_FIELD_NAME: event_name
        }
        return cls(data=response)

    @classmethod
    def with_content(cls, data, event_name=None):
        response = {
            cls.CONTENT_FIELD_NAME: data,
            cls.EVENT_FIELD_NAME: event_name
        }
        return cls(data=response)
