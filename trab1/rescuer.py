##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim

import os
import random
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from abc import ABC, abstractmethod


## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.plan = []              # a list of planned actions
                
        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

        # planning
        self.__planner()

    def sync_explorers(self, explorer_maps):
        """
        Synchronize maps from all explorers and create a unified map.

        Args:
            explorer_maps (list): A list of maps from all explorers.
        """
        print(f"{self.NAME} Synchronizing maps from explorers...")
        self.map = self.merge_maps(explorer_maps)
        print(f"{self.NAME} Unified map created.")

    def merge_maps(self, maps):
        """
        Merge multiple maps into a single unified map.

        Args:
            maps (list): A list of maps from explorers. Each map is a dictionary
                         where keys are coordinates (x, y) and values are cell data.

        Returns:
            dict: A unified map containing all the information from the input maps.
        """
        unified_map = {}

        for map_data in maps:
            for coord, cell_data in map_data.items():
                if coord not in unified_map:
                    unified_map[coord] = cell_data
                else:
                    # Merge logic: prioritize certain data if needed
                    if cell_data['content'] == VS.WALL or cell_data['content'] == VS.END:
                        unified_map[coord]['content'] = cell_data['content']
                    if cell_data['has_victim'] != VS.NO_VICTIM:
                        unified_map[coord]['has_victim'] = cell_data['has_victim']
                        unified_map[coord]['victim_signals'] = cell_data['victim_signals']

        return unified_map
    
    def go_save_victims(self, walls, victims):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""
        self.set_state(VS.ACTIVE)
        
    
    def __planner(self):
        """ A private method that calculates the walk actions to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberata method"""

        # This is a off-line trajectory plan, each element of the list is
        # a pair dx, dy that do the agent walk in the x-axis and/or y-axis
        self.plan = [(1,0),(1,0),(1,0),(1,0),(1,0),(1,0),(1,0),(1,0),
                     (0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(1,0),
                     (0,1),(0,1),(0,1),(-1,-1),(-1,0),(-1,0),(0,-1),
                     (-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),
                     (0,-1),(0,-1)]
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           input(f"{self.NAME} has finished the plan [ENTER]")
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy = self.plan.pop(0)

        # Walk - just one step per deliberation
        result = self.walk(dx, dy)

        # Rescue the victim at the current position
        if result == VS.EXECUTED:
            # check if there is a victim at the current position
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                res = self.first_aid() # True when rescued

        input(f"{self.NAME} remaining time: {self.get_rtime()} Tecle enter")

        return True

