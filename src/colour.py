import numpy as np


def compute_intensity(pos, pos_list, radius):
    return (norm(np.array(pos_list) - np.array(pos), axis=1) < radius).sum()


def compute_colours(all_pos):
    colours = [compute_intensity(pos, all_pos, 1e-4) for pos in all_pos]
    colours /= max(colours)
    return colours
