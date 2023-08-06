import ipaddress

import ssmc
from examples.util import set_env, get_logger, measure

logger = get_logger()
# logger.setLevel(logging.INFO)

# get config
conf = set_env()

# create api client
api = ssmc.APIClient(token=conf.token, secret=conf.secret, zone=conf.zone, debug=conf.debug)

# const
# L2_MODE_START_IP = ipaddress.IPv4Address('10.0.1.1')
L3_MODE_START_IP = ipaddress.IPv4Address('10.16.1.1')

mgws, pagging = api.list_mgws()
mgw = mgws[0]

# activate sim
size, offset = 5000, 0
iter_num = 0
with measure(f"assign sims - size={size}", logger):
    while True:
        sims, paging = api.list_sims(size=size, offset=offset)
        total = paging.total
        offset = paging.size + paging.offset

        with measure(f"setup sims: num_of_sims={len(sims)}", logger):
            for sim in sims:
                iter_num += 1

                # get sim status for check PUT request
                sim_status = api.get_sim_status(sim.id)
                # activate sim
                if not sim_status.activated:
                    with measure(f"activate_sim: total={total}, sim_id={sim.id}", logger):
                        api.activate_sim(sim.id)
                # assign to mgw
                if sim_status.simgroup_id is None:
                    with measure(f"assign_sim_to_mgw: total={total}, sim_id={sim.id}, mgw_id={mgw.id}", logger):
                        api.assign_sim_to_mgw(mgw.id, sim.id)
                # set ip
                if sim_status.ip is None:
                    with measure(f"set_ip: total={total}, sim_id={sim.id}", logger):
                        api.set_ip(sim_id=sim.id, ip=str(L3_MODE_START_IP + iter_num))
                # imei lock
                dummy_imei = "123456789012345"
                if not sim_status.imei_lock:
                    with measure(f"lock_imei: total={total}, sim_id={sim.id}", logger):
                        api.lock_imei(sim_id=sim.id, imei=dummy_imei)

        if offset >= total:
            break
