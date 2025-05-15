import sys
import os
import time

## importa classes
sys.path.append('../')
from vs.constants import VS
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from pathlib import Path
from map import Map

def main(data_folder_name, cfg_ag_folder):
      
    # Instantiate the environment
    env = Env(data_folder)
    map = Map()
    
    # config files for the agents
    rescuer_file = os.path.join(cfg_ag_folder, "rescuer_1_config.txt")
    explorer_file = os.path.join(cfg_ag_folder, "explorer_1_config.txt")
    
    # Instantiate agents rescuer and explorer
    resc1 = Rescuer(env, rescuer_file)
    resc2 = Rescuer(env, rescuer_file)
    resc3 = Rescuer(env, rescuer_file)
    resc4 = Rescuer(env, rescuer_file)

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    exp1 = Explorer(env, map, explorer_file, resc1, VS.DIRECTION_UPRIGHT)
    exp2 = Explorer(env, map, explorer_file, resc2, VS.DIRECTION_DOWNRIGHT)
    exp3 = Explorer(env, map, explorer_file, resc3, VS.DIRECTION_DOWNLEFT)
    exp4 = Explorer(env, map, explorer_file, resc4, VS.DIRECTION_UPLEFT)

    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder = sys.argv[1]
        cfg_ag_folder = sys.argv[2]
    else:
        cur_folder = Path.cwd()
        data_folder = os.path.join(cur_folder.parent, "datasets", "data_10v_12x12")
        # data_folder = os.path.join(cur_folder.parent, "datasets", "data_225v_100x80")
        cfg_ag_folder = os.path.join(cur_folder, "cfg_1")
        
    main(data_folder, cfg_ag_folder)
