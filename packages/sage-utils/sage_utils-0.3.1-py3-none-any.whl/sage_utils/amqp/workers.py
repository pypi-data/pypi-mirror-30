from sage_utils.amqp.base import AmqpWorker
from sage_utils.amqp.clients import RpcAmqpClient


class BaseRegisterWorker(AmqpWorker):
    """
    Base class for implementing worker which is registering a new
    microservice in Open Matchmaking platform.
    """
    REQUEST_QUEUE_NAME = "auth.microservices.register"
    REQUEST_EXCHANGE_NAME = "open-matchmaking.direct"
    RESPONSE_EXCHANGE_NAME = "open-matchmaking.responses.direct"
    CONTENT_TYPE = 'application/json'

    def get_microservice_data(self, app):
        raise NotImplementedError("The `get_microservice_data(data)` method "
                                  "must be implemented.")

    async def run(self, *args, **kwargs):
        client = RpcAmqpClient(
            self.app,
            routing_key=self.REQUEST_QUEUE_NAME,
            request_exchange=self.REQUEST_EXCHANGE_NAME,
            response_queue='',
            response_exchange=self.RESPONSE_EXCHANGE_NAME
        )
        response = await client.send(self.get_microservice_data(self.app))

        assert 'error' not in response.keys(), response['error']
        assert 'content' in response.keys()
        assert response['content'] == 'OK'
