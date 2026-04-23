#!/usr/bin/env python3
"""
Leader-follower demo.

cf1 is the leader and flies a square path. cf3 and cf4 are followers that
maintain a fixed XY offset behind-left and behind-right of the leader.
"""

from crazyflie_py import Crazyswarm
import numpy as np


def main():
    Z = 1.0
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    if len(allcfs.crazyflies) < 2:
        print('Need at least 2 drones (1 leader + >=1 followers)')
        return

    leader = allcfs.crazyflies[0]
    followers = allcfs.crazyflies[1:]
    print(f'Leader: {leader.prefix}   Followers: {[f.prefix for f in followers]}')

    # Follower offsets relative to the leader's position (body-fixed, not rotating)
    follower_offsets = [
        np.array([-0.6, -0.4, 0.0]),   # behind-left
        np.array([-0.6,  0.4, 0.0]),   # behind-right
        np.array([-1.0,  0.0, 0.0]),   # far behind
    ]

    allcfs.takeoff(targetHeight=Z, duration=3.0)
    timeHelper.sleep(3.5)

    # Square path around (0.5, 0.5) at 1 m altitude
    center = np.array([0.5, 0.5, Z])
    half = 0.75
    waypoints = [
        center + np.array([ half,  half, 0]),
        center + np.array([-half,  half, 0]),
        center + np.array([-half, -half, 0]),
        center + np.array([ half, -half, 0]),
        center + np.array([ half,  half, 0]),  # close the loop
    ]

    for wp in waypoints:
        leader.goTo(wp, 0, 3.0)
        for idx, follower in enumerate(followers):
            follower.goTo(wp + follower_offsets[idx], 0, 3.0)
        timeHelper.sleep(3.5)

    # Fly each drone back to its initial XY at hover height before landing
    for cf in allcfs.crazyflies:
        home = np.array(cf.initialPosition) + np.array([0, 0, Z])
        cf.goTo(home, 0, 3.0)
    timeHelper.sleep(3.5)

    allcfs.land(targetHeight=0.04, duration=3.0)
    timeHelper.sleep(3.5)


if __name__ == '__main__':
    main()
