import ssmc
from examples.util import set_env, get_logger

logger = get_logger()
# logger.setLevel(logging.INFO)
conf = set_env(debug=True)

api = ssmc.APIClient(token=conf.token, secret=conf.secret, zone=conf.zone, debug=conf.debug)

# name
SIM_NAME='8981049999999000010'
# search sims by name
sims, paging = api.search_sims_by_name(name=SIM_NAME)
logger.debug(sims)
# get sim by name
sim = api.get_sim_by_name(name=SIM_NAME)
logger.debug(sim)
