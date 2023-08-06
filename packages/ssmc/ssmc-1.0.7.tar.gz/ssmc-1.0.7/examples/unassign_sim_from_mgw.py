import ssmc
from examples.util import set_env, get_logger, measure

logger = get_logger()
# logger.setLevel(logging.INFO)

# get config
conf = set_env()

# create api client
api = ssmc.APIClient(token=conf.token, secret=conf.secret, zone=conf.zone, debug=conf.debug)

# MGW 1つだけ利用
mgws, _ = api.list_mgws()
mgw = mgws[0]

# activate sim
size, offset = 5000, 0
with measure(f"assign sims - size={size}", logger):
    while True:
        sim_statuses, paging = api.list_sims_of_mgw(mgw_id=mgw.id, size=size, offset=offset)
        total = paging.total
        offset = paging.size + paging.offset

        with measure(f"setup sims: num_of_sims={len(sim_statuses)}", logger):
            for sim_status in sim_statuses:
                # deactivate sim
                if sim_status.activated:
                    with measure(f"deactivate_sim: total={total}, sim_id={sim_status.sim_resource_id}", logger):
                        api.deactivate_sim(sim_id=sim_status.sim_resource_id)
                # delete ip
                if sim_status.ip is not None:
                    with measure(f"delete_ip: total={total}, sim_id={sim_status.sim_resource_id}", logger):
                        api.delete_ip(sim_id=sim_status.sim_resource_id)
                # assign to mgw
                if sim_status.simgroup_id is not None:
                    with measure(
                            f"unassign_sim_from_mgw: total={total}, sim_id={sim_status.sim_resource_id}, mgw_id={mgw.id}",
                            logger):
                        api.unassign_sim_from_mgw(mgw_id=mgw.id, sim_id=sim_status.sim_resource_id)
                # unlock imei
                if sim_status.imei_lock:
                    with measure(f"unlock_imei: total={total}, sim_id={sim_status.sim_resource_id}", logger):
                        api.unlock_imei(sim_id=sim_status.sim_resource_id)
        if offset >= total:
            break
