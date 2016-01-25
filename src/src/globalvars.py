#############
##
## globalvars.py is used for communication between modules
##
#############

# player coordinates on map
player_x = 0
player_y = 0

# blocked surroundings of last monster attacked; first outer, then inner ring; order: up, right, down, left (clockwise)
monster_proximity_block = [0, 0, 0, 0]
