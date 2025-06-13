# Window settings
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
TITLE = "Galactic Conquest"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 50)
GRID_COLOR = (50, 50, 50)

# Galaxy map settings
GALAXY_GRID_SIZE = 64
GALAXY_GRID_WIDTH = 20
GALAXY_GRID_HEIGHT = 15
GALAXY_VIEW_PADDING = 50

# Galaxy settings
GALAXY_SIZE = 1000  # Huge galaxy to fit very distant systems
GRID_SIZE = 40    # Size of each grid cell in pixels
GRID_VIEW_PADDING = 20  # Padding around the grid view

# Planet grid settings
PLANET_GRID_SIZE = 32
PLANET_GRID_WIDTH = 5
PLANET_GRID_HEIGHT = 5

# Resource types
RESOURCE_TYPES = {
    'MINERALS': 'Minerals',
    'FOOD': 'Food',
    'ENERGY': 'Energy',
    'SCIENCE': 'Science'
}

# Building types
BUILDING_TYPES = {
    'POWER_PLANT': 'Power Plant',
    'RESEARCH_LAB': 'Research Lab',
    'FARM': 'Farm',
    'DEFENSE_TURRET': 'Defense Turret',
    'MINING_STATION': 'Mining Station',
    'SOLAR_ARRAY': 'Solar Array',
    'RESEARCH_STATION': 'Research Station',
    'DEFENSE_PLATFORM': 'Defense Platform',
    'SHIPYARD': 'Shipyard'
}

# Building colors
BUILDING_COLORS = {
    'Power Plant': (255, 255, 0),        # Yellow
    'Research Lab': (128, 0, 128),       # Purple
    'Farm': (0, 255, 0),                 # Green
    'Defense Turret': (255, 0, 0),       # Red
    'Mining Station': (139, 69, 19),     # Brown
    'Solar Array': (255, 215, 0),        # Gold
    'Research Station': (0, 191, 255),   # Deep Sky Blue
    'Defense Platform': (220, 20, 60),   # Crimson
    'Shipyard': (100, 149, 237)          # Cornflower Blue - much brighter
}

# Planet types
PLANET_TYPES = {
    'ROCKY': 'Rocky',
    'GAS_GIANT': 'Gas Giant',
    'ICE': 'Ice',
    'DESERT': 'Desert',
    'TERRAN': 'Terran',
    'OCEAN': 'Ocean',
    'VOLCANIC': 'Volcanic',
    'TOXIC': 'Toxic'
}

# Building costs
BUILDING_COSTS = {
    BUILDING_TYPES['POWER_PLANT']: {
        RESOURCE_TYPES['MINERALS']: 75,
        RESOURCE_TYPES['ENERGY']: 25
    },
    BUILDING_TYPES['RESEARCH_LAB']: {
        RESOURCE_TYPES['MINERALS']: 100,
        RESOURCE_TYPES['ENERGY']: 50,
        RESOURCE_TYPES['SCIENCE']: 25
    },
    BUILDING_TYPES['FARM']: {
        RESOURCE_TYPES['MINERALS']: 50,
        RESOURCE_TYPES['ENERGY']: 25
    },
    BUILDING_TYPES['DEFENSE_TURRET']: {
        RESOURCE_TYPES['MINERALS']: 75,
        RESOURCE_TYPES['ENERGY']: 50
    },
    BUILDING_TYPES['MINING_STATION']: {
        RESOURCE_TYPES['MINERALS']: 100,
        RESOURCE_TYPES['ENERGY']: 50
    },
    BUILDING_TYPES['SOLAR_ARRAY']: {
        RESOURCE_TYPES['MINERALS']: 80,
        RESOURCE_TYPES['ENERGY']: 30
    },
    BUILDING_TYPES['RESEARCH_STATION']: {
        RESOURCE_TYPES['MINERALS']: 120,
        RESOURCE_TYPES['ENERGY']: 60,
        RESOURCE_TYPES['SCIENCE']: 40
    },
    BUILDING_TYPES['DEFENSE_PLATFORM']: {
        RESOURCE_TYPES['MINERALS']: 150,
        RESOURCE_TYPES['ENERGY']: 100
    },
    BUILDING_TYPES['SHIPYARD']: {
        RESOURCE_TYPES['MINERALS']: 200,
        RESOURCE_TYPES['ENERGY']: 150,
        RESOURCE_TYPES['SCIENCE']: 75
    },
}

# Building resource generation per turn
BUILDING_PRODUCTION = {
    'Power Plant': {
        'Energy': 8
    },
    'Research Lab': {
        'Science': 5
    },
    'Farm': {
        'Food': 6
    },
    'Defense Turret': {
        # No resource generation, defensive building
    },
    'Mining Station': {
        'Minerals': 5
    },
    'Solar Array': {
        'Energy': 10
    },
    'Research Station': {
        'Science': 8
    },
    'Defense Platform': {
        # No resource generation, defensive building
    },
    'Shipyard': {
        'Minerals': 2,
        'Energy': 2
    },
}

# Planet-specific building restrictions
PLANET_BUILDING_RESTRICTIONS = {
    'ROCKY': ['Power Plant', 'Defense Turret', 'Mining Station', 'Defense Platform'],  # Good for mining and defense
    'GAS_GIANT': ['Research Lab', 'Power Plant', 'Research Station'],  # Energy and research from gas
    'ICE': ['Research Lab', 'Farm', 'Research Station'],  # Water for farms, cold for research
    'DESERT': ['Power Plant', 'Defense Turret', 'Solar Array'],  # Solar power, harsh conditions for defense
    'TERRAN': ['Farm', 'Research Lab', 'Defense Turret', 'Shipyard'],  # Earth-like, most versatile
    'OCEAN': ['Farm', 'Research Lab', 'Research Station'],  # Water-rich, good for farms and research
    'VOLCANIC': ['Power Plant', 'Mining Station', 'Defense Platform', 'Solar Array'],  # High energy and minerals
    'TOXIC': ['Research Lab', 'Defense Platform', 'Research Station'],  # Harsh environment, limited options
}

 