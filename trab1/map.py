import matplotlib.pyplot as plt
import numpy as np

class Map:
    def __init__(self):
        self.map = {}
        self.found_victims = 0

    def sync_map(self, map):
        """
        Sync the map with the given map data.
        :param self.map: A dictionary containing the map data.
        """
        for key, value in map.items():
            print('Key: ', key)
            print('Value: ', value)
            if key not in self.map:
                self.map[key] = value
            else:
                if 'has_victim' in value.keys():
                    self.map[key].update(value)
        print('Map synced')
        # print(self.map)
        # self.plot_map()

    def get_map(self):
        """
        Get the current map.
        :return: The current map.
        """
        return self.map
    
    def plot_map(self):
        """
        Plot the map using matplotlib.
        """
        n_victims = 0

        # Encontrar limites
        xs, ys = zip(*self.map.keys())
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Criar matriz de símbolos
        grid = [[' ' for _ in range(width)] for _ in range(height)]

        for (x, y), info in self.map.items():
            gx, gy = x - min_x, y - min_y
            symbol = ' '

            if info['content'] == 2:
                symbol = 'X'
            elif info['content'] == 1:
                symbol = '#'
            elif info.get('has_victim', -1) != -1:
                symbol = f"V{info['has_victim']}"
                n_victims += 1
            elif info.get('visited', False):
                symbol = '.'

            grid[gy][gx] = symbol
        
        print('Víctims Found:', n_victims)

        # Criar uma matriz para imshow (não afeta a visualização dos textos)
        bg = [[0 if cell == ' ' else 1 for cell in row] for row in grid]

        fig, ax = plt.subplots(figsize=(12, 12))
        im = ax.imshow(bg, cmap='Greys', extent=(min_x - 0.5, max_x + 0.5, max_y + 0.5, min_y - 0.5), alpha=0.2)

        # Adicionar textos no centro das células
        for y in range(height):
            for x in range(width):
                symbol = grid[y][x]
                ax.text(x + min_x, y + min_y, symbol, ha='center', va='center', fontsize=8, fontweight='bold')

        # Configurar ticks e grades
        ax.set_xticks(np.arange(min_x, max_x + 1))
        ax.set_yticks(np.arange(min_y, max_y + 1))
        ax.set_xticks(np.arange(min_x - 0.5, max_x + 1), minor=True)
        ax.set_yticks(np.arange(min_y - 0.5, max_y + 1), minor=True)

        ax.grid(which='minor', color='black', linewidth=1)
        ax.tick_params(which='minor', size=0)
        ax.invert_yaxis()

        ax.set_title("Mapa em Grade com Bordas Claras")
        plt.show()
