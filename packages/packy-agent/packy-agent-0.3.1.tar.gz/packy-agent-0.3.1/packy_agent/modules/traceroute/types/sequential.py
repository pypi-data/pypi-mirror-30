from collections import defaultdict


def traceroute_sequential(trace_function_partial, destination_ip_address,
                          probe_count, max_hops):
    destination_hop = max_hops
    should_exit = False
    results = defaultdict(dict)
    for ttl in xrange(1, destination_hop + 1):
        for ping_number in xrange(probe_count):
            trace_result = trace_function_partial(ttl=ttl)
            results[ttl][ping_number] = trace_result
            if trace_result:
                _, ip_address, is_destination_reached = trace_result
                if is_destination_reached or ip_address == destination_ip_address:
                    should_exit = should_exit or is_destination_reached
                    destination_hop = min(ttl, destination_hop)

        if should_exit:
            break

    return [[results[ttl].get(ping_number) for ping_number in xrange(probe_count)]
            for ttl in xrange(1, destination_hop + 1)]
