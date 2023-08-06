

class Response(object):
    """
    The response object that is used by default for microservices.
    """
    CONTENT_FIELD_NAME = 'content'
    ERROR_FIELD_NAME = 'error'
    EVENT_FIELD_NAME = 'event-name'

    def append_extra_fields(self, event_name, *args, **kwargs):
        return {self.EVENT_FIELD_NAME: event_name}

    def from_error(self, error_type, message, event_name=None):
        if isinstance(message, str) and not message.endswith('.'):
            message = message + '.'

        response = {
            self.ERROR_FIELD_NAME: {
                "type": error_type,
                "message": message
            }
        }
        response.update(self.append_extra_fields(event_name))
        return response

    def wrap_content(self, data, event_name=None):
        response = {self.CONTENT_FIELD_NAME: data}
        response.update(self.append_extra_fields(event_name))
        return response
