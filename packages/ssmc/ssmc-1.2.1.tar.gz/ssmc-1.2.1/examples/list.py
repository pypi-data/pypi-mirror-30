import ssmc
from examples.util import set_env, get_logger, measure

logger = get_logger()
# logger.setLevel(logging.INFO)

# get config
conf = set_env(debug=True)

# create api client
api = ssmc.APIClient(token=conf.token, secret=conf.secret, zone=conf.zone, debug=conf.debug)
with measure("list mgw", logger):
    mgws, paging = api.list_mgws()
logger.info(f"Total: {paging.total}")
logger.info(f"Count {len(mgws)}: {mgws}")

size = 1
with measure(f"list sims - size={size}", logger):
    sims, paging = api.list_sims(size=size)
logger.info(f"Total: {paging.total}")
logger.info(f"Count {len(sims)}: {sims}")

# SIM一覧
with measure(f"list all sims - total={paging.total}", logger):
    size, offset = 3000, 0
    while True:
        with measure(f"list all sims - size={size}, offset={offset}, total={paging.total}", logger):
            _, paging = api.list_sims(size=size, offset=offset)
        total = paging.total
        offset = paging.size + paging.offset
        if offset >= total:
            break

# MGW配下のSIM
for mgw in mgws:
    _, paging = api.list_sim_statuses_of_mgw(mgw_id=mgw.id, size=1)
    total = paging.total
    with measure(f"list sims of mgw - {total}: mgw_id={mgw.id}", logger):
        size, offset = 3000, 0
        while True:
            with measure(f"list sims of mgw id={mgw.id} - size={size}, offset={offset}, total={paging.total}", logger):
                sims, paging = api.list_sims_of_mgw(mgw_id=mgw.id, size=size, offset=offset)
            logger.info(f"Total: {paging.total}")
            logger.info(f"Count {len(sims)}: {sims}")
            total = paging.total
            offset = paging.size + paging.offset
            if offset >= total:
                break
