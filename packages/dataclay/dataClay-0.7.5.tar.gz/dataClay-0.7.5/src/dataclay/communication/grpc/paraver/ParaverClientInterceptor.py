"""Interceptor for GRPC client calls."""

from grpc import UnaryUnaryClientInterceptor
from logging import getLogger

from dataclay import PrvManager
from dataclay.communication.grpc.paraver import HEADER_CLIENTPORT
from dataclay.paraver.prv_traces import TraceType

from . import HEADER_MESSAGEID


logger = getLogger(__name__)


class ParaverClientInterceptor(UnaryUnaryClientInterceptor):
    def __init__(self, origin_hostname, remote_hostaddr, remote_port):
        self.request_id = 42
        self.prv_manager = PrvManager.get_manager()
        self.origin_hostname = origin_hostname
        self.remote_hostaddr = remote_hostaddr
        self.remote_port = remote_port

    def intercept_unary_unary(self, continuation, client_call_details, request):
        id = self.request_id
        self.request_id += 1

        metadata = client_call_details.metadata
        if not metadata:
            metadata = list()

        metadata.append((HEADER_MESSAGEID, str(id)))

        # It is known that client_call_details is in fact a namedtuple,
        # (i.e. inmutable) so let's take advantage of the _replace method
        new_call_details = client_call_details._replace(metadata=metadata)

        self.prv_manager.add_network_send(
            TraceType.SEND_REQUEST,
            self.remote_port,
            id,
            self.remote_hostaddr,
            0,  # unknown/unused message size
            0   # unknown/unused method id
        )

        response = continuation(new_call_details, request)

        # FIXME: is the following correct behaviour? Not sure about client_port semantics

        metadata = response.initial_metadata()
        logger.debug("received metadata: %s", metadata)
        client_port = dict(metadata).get(HEADER_CLIENTPORT)
        if not client_port:
            logger.warning("Could not retrieve clientport from metadata, not tracing response")
        else:
            self.prv_manager.add_network_receive(
                self.remote_hostaddr,
                int(client_port),
                id,
                0
            )

        return response
