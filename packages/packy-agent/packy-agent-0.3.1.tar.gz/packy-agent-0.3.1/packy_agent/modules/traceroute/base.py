from __future__ import absolute_import

import logging
import math
import socket
from functools import partial

from packy_agent.modules.traceroute.constants import (
    ICMP_METHOD, UDP_METHOD)
from packy_agent.modules.base.constants import IP_PACKET_HEADER_SIZE_BYTES, \
    ICMP_PACKET_HEADER_SIZE_BYTES, UDP_PACKET_HEADER_SIZE_BYTES
from packy_agent.modules.traceroute.methods.icmp import trace_hop_with_icmp
from packy_agent.modules.traceroute.methods.udp import trace_hop_with_udp
from packy_agent.modules.traceroute.types.gevent_parallel import traceroute_gevent_parallel
from packy_agent.modules.traceroute.types.parallel.base import traceroute_parallel
from packy_agent.modules.traceroute.types.sequential import traceroute_sequential

MIN_ICMP_METHOD_PACKET_SIZE = IP_PACKET_HEADER_SIZE_BYTES + ICMP_PACKET_HEADER_SIZE_BYTES
MIN_UDP_METHOD_PACKET_SIZE = IP_PACKET_HEADER_SIZE_BYTES + UDP_PACKET_HEADER_SIZE_BYTES
RANGE_MIN = {
    ICMP_METHOD: MIN_ICMP_METHOD_PACKET_SIZE,
    UDP_METHOD: MIN_UDP_METHOD_PACKET_SIZE,
}
MAX_PACKET_SIZE = 1500

logger = logging.getLogger(__name__)


def aggregate_results(ping_results):
    agg_results = []
    for pings in ping_results:
        agg = {'loss': pings.count(None)}
        results = filter(None, pings)
        if results:
            # TODO(dmu) HIGH: Hops may differ for different pings. Take care of it
            agg['host'] = results[0][1]
            delays = [x[0] for x in results]
            agg['last'] = delays[-1]
            agg['best'] = min(delays)
            agg['worst'] = max(delays)
            average = sum(delays) / len(delays)
            agg['average'] = average

            variance = sum((x - average) ** 2 for x in delays) / len(delays)
            agg['stdev'] = math.sqrt(variance)
        else:
            agg['host'] = None

        agg_results.append(agg)

    return agg_results


def traceroute(host, timeout=2, probe_count=1, packet_size_bytes=60, max_hops=100,
               method=UDP_METHOD, max_parallelism=10, use_gevent=False):

    if method not in (UDP_METHOD, ICMP_METHOD):
        raise ValueError('Unknown traceroute method: {}'.format(method))

    if max_parallelism < 1:
        raise ValueError('max_parallelism must be greater or equal to 1')

    range_min = RANGE_MIN[method]
    if not (range_min <= packet_size_bytes <= MAX_PACKET_SIZE):
        raise ValueError(
            'packet_size_bytes must be in range from {} to 1500 (inclusive)'.format(range_min))

    try:
        destination_ip_address = socket.gethostbyname(host)
    except socket.gaierror:
        logger.warning('Could not resolve {} to IP address'.format(host))
        return

    kwargs = {
        'destination_ip_address': destination_ip_address,
        'timeout': timeout,
        'packet_size_bytes': packet_size_bytes,
    }

    if max_parallelism == 1 or use_gevent:
        if method == ICMP_METHOD:
            trace_function = trace_hop_with_icmp
        elif method == UDP_METHOD:
            port = [33434]

            def get_port():
                port[0] += 1
                return int(port[0])

            kwargs['port'] = get_port

            trace_function = trace_hop_with_udp
        else:
            assert False, 'Should never get here'
            raise ValueError('Unknown traceroute method: {}'.format(method))

        trace_function_partial = partial(trace_function, **kwargs)
        if max_parallelism == 1:
            results = traceroute_sequential(trace_function_partial, destination_ip_address,
                                            probe_count=probe_count, max_hops=max_hops)
        else:
            results = traceroute_gevent_parallel(trace_function_partial, destination_ip_address,
                                                 probe_count=probe_count, max_hops=max_hops,
                                                 timeout=timeout, max_parallelism=max_parallelism)
    else:
        results = traceroute_parallel(method, kwargs, destination_ip_address,
                                      probe_count=probe_count,
                                      max_hops=max_hops, timeout=timeout,
                                      max_parallelism=max_parallelism)

    return aggregate_results(results)
