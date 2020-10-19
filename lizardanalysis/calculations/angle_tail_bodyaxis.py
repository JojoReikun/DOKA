"""
This function calculated the angle between the bodyaxis to the tail vector (tailBase - tailMiddle).
Tail middle is used because it seems that tail base and tail middle follow a sinosoidal trajectory,
while tail tip in some species has chaotic trajectory.
"""

def angle_tail_bodyaxis(**kwargs):

    return