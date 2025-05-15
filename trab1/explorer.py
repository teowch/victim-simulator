## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.

import sys
import os
import random
from abc import ABC, abstractmethod
sys.path.append('../')
from vs.abstract_agent import AbstAgent
from vs.constants import VS



class Explorer(AbstAgent):
    def __init__(self, env, map, config_file, resc, direction_tendency):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """
        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)
        self.main_map = map
        self.map = {(0, 0): {'content': VS.BASE, 'visited': True}} # map of the environment
        self.current_position = (0, 0) # current position of the agent in the environment
        self.move_stack = [self.current_position] # stack of moves executed
        self.starterBattery = None # battery of the agent
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent   
        self.direction_tendency = direction_tendency  # tendency to walk in a specific direction
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        if self.starterBattery is None:
            self.starterBattery = self.get_rtime()

        has_victim = self.check_for_victim()
        victim_signals = None
        if has_victim != VS.NO_VICTIM:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            victim_signals = self.read_vital_signals()

        self.map.update({self.current_position: {'content': VS.CLEAR, 'visited': True, 'has_victim': has_victim, 'victim_signals': victim_signals}})

        print(f"\n{self.NAME} deliberate:")
        # No more actions, time almost ended
        if self.get_rtime() <= 1.0:
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            if self.current_position == (0,0):
                self.send_map_to_rescuer()
            else:
                self.send_map_to_rescuer(True)
            print(f"{self.NAME} No more time to explore... invoking the rescuer")
            # self.resc.go_save_victims([],[])
            return False
        return self.direction_decision() # decide the direction and walk


        # elif tecla == "x":
        #     print(f"{self.NAME} exploring phase terminated... invoking the rescuer")
        #     self.resc.go_save_victims([],[])
        #     return False


        # if result == VS.EXECUTED:
        #     # check for victim returns -1 if there is no victim or the sequential
        #     # the sequential number of a found victim
        #     print(f"{self.NAME} walk executed, rtime: {self.get_rtime()}")
        #     seq = self.check_for_victim()
        #     if seq >= 0:
        #         vs = self.read_vital_signals()
        #         print(f"{self.NAME} Vital signals read, rtime: {self.get_rtime()}")
        #         print(f"{self.NAME} Vict: {vs[0]}\n     pSist: {vs[1]:.1f} pDiast: {vs[2]:.1f} qPA: {vs[3]:.1f}")
        #         print(f"     pulse: {vs[4]:.1f} frResp: {vs[5]:.1f}")  
    
    def direction_decision(self):
        neighbors = {direction: content for direction, content in zip(VS.DIRECTION_LIST, self.check_walls_and_lim())}
        for position, content in neighbors.items():
            actual_position = self.calculate_position(position[0], position[1])
            if actual_position not in self.map.keys():
                self.map.update({actual_position: {'content': content, 'visited': False}})

        neighbor_positions = list(neighbors.keys())
        direction_key = neighbor_positions.index(self.direction_tendency)
        actual_neighbor_positions = [self.calculate_position(dx, dy) for dx, dy in neighbor_positions]
        #Return true if at least one of the neighbors is clear and unvisite
        if self.get_rtime() > self.starterBattery / 2 + self.starterBattery * 0.05 and any(neighbors[pos] == VS.CLEAR and not self.map[self.calculate_position(pos[0], pos[1])]['visited'] for pos in neighbor_positions):
            # If there is a clear and unvisited position, walk to it
            while neighbors.get(neighbor_positions[direction_key]) != VS.CLEAR or self.map[actual_neighbor_positions[direction_key]]['visited']:
                direction_key = (direction_key + 1) % len(neighbor_positions)
            dx, dy = neighbor_positions[direction_key]
            self.current_position = self.calculate_position(dx, dy)
            self.move_stack.append(self.current_position)
            self.walk(dx, dy)
        else:
            try:
                back_to = self.move_stack.pop()
                comeback = self.calculate_dx_dy(back_to)
                # If there is no clear and unvisited position, walk to the last position
                print(self.current_position)
                self.current_position = back_to
                print(self.walk(comeback[0], comeback[1]))
            except IndexError:
                print('Returned to base')
                self.send_map_to_rescuer()
                return False
        return True
    
    def send_map_to_rescuer(self, dead=False):
        if dead:
            self.main_map.sync_map({})
            return

        victims = []
        walls = []
        for k, v in self.map.items():
            if v['content'] == VS.WALL or v['content'] == VS.END:
                walls.append(k)
            elif 'has_victim' in v.keys():
                if v['has_victim'] != VS.NO_VICTIM:
                    victims.append(k)

        self.main_map.sync_map(self.map)
        self.resc.go_save_victims(walls,victims)
        print('map sent to rescuer')

    def calculate_position(self, dx, dy):
        """
        Calculates the new position based on the given deltas (dx, dy).

        Args:
            dx (int or float): The change in the x-coordinate.
            dy (int or float): The change in the y-coordinate.

        Returns:
            tuple: A tuple (new_x, new_y) representing the new position after applying the deltas.
        """
        x, y = self.current_position
        new_x = x + dx
        new_y = y + dy
        return (new_x, new_y)
    
    def calculate_dx_dy(self, direction):
        """
        Calculate the change in x and y coordinates (dx, dy) based on the given direction.

        Args:
            direction (tuple): A tuple (dx, dy) representing the target direction.

        Returns:
            tuple: A tuple (new_x, new_y) representing the change in x and y coordinates
                   relative to the current position.
        """
        dx, dy = direction
        x, y = self.current_position
        new_x = dx - x
        new_y = dy - y
        return (new_x, new_y)
