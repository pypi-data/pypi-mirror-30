from __future__ import absolute_import

import logging
from collections import defaultdict

import gevent.pool

from packy_agent.utils.gevent import async_patched_socket

logger = logging.getLogger(__name__)


def generate_ping_arguments(ping_count, max_hops):
    for ttl in xrange(1, max_hops + 1):
        for ping_number in xrange(ping_count):
            yield {'ttl': ttl, 'ping_number': ping_number}


def trace_once(trace_function_partial, ttl, ping_number):
    try:
        return ttl, ping_number, trace_function_partial(ttl=ttl)
    except Exception:
        logger.exception('Error while pinging')
        return ttl, ping_number, None


def traceroute_gevent_parallel(trace_function_partial, destination_ip_address,
                               probe_count, max_hops, timeout, max_parallelism=10):
    def trace_function_partial_local(kwargs):
        return trace_once(trace_function_partial, **kwargs)

    destination_hop = max_hops

    results = defaultdict(dict)
    with async_patched_socket():
        pool = gevent.pool.Pool(size=max_parallelism)
        ping_arguments = generate_ping_arguments(probe_count, max_hops)
        for ttl, ping_number, trace_result in pool.imap_unordered(trace_function_partial_local,
                                                                  ping_arguments):
            results[ttl][ping_number] = trace_result
            if trace_result:
                _, ip_address, is_destination_reached = trace_result
                if is_destination_reached or ip_address == destination_ip_address:
                    destination_hop = min(ttl, destination_hop)
                    for ttl_local in xrange(destination_hop, 0, -1):
                        if len(results[ttl_local]) < probe_count:
                            break
                    else:
                        pool.kill(timeout=timeout)
                        break

    return [[results[ttl].get(ping_number) for ping_number in xrange(probe_count)]
            for ttl in xrange(1, destination_hop + 1)]
