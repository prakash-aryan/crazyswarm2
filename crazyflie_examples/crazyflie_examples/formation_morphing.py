#!/usr/bin/env python3
"""
Formation morphing demo.

All drones take off together and transition through a sequence of
geometric formations (line, triangle, V, circle) while remaining
at 1 m altitude. Works with any number of drones; the formation
generators scale automatically.
"""

from crazyflie_py import Crazyswarm
import numpy as np


def line_formation(n: int, spacing: float = 0.4):
    """Horizontal line along the y axis."""
    y0 = -(n - 1) * spacing / 2
    return [np.array([0.0, y0 + i * spacing, 0.0]) for i in range(n)]


def triangle_formation(n: int, radius: float = 0.5):
    """Equilateral-ish arrangement, collapses to 1 or 2 points for n<3."""
    if n == 1:
        return [np.zeros(3)]
    if n == 2:
        return [np.array([0.0, -radius, 0.0]), np.array([0.0, radius, 0.0])]
    return [
        np.array([radius * np.cos(2 * np.pi * i / n),
                  radius * np.sin(2 * np.pi * i / n),
                  0.0])
        for i in range(n)
    ]


def v_formation(n: int, spacing: float = 0.4):
    """Classic V pointing along +x, apex leading."""
    positions = [np.array([0.0, 0.0, 0.0])]  # apex
    for i in range(1, n):
        side = -1 if i % 2 == 1 else 1
        rank = (i + 1) // 2
        positions.append(np.array([-rank * spacing, side * rank * spacing * 0.7, 0.0]))
    return positions


def circle_formation(n: int, radius: float = 0.55):
    """Regular n-gon on a circle."""
    return [
        np.array([radius * np.cos(2 * np.pi * i / n),
                  radius * np.sin(2 * np.pi * i / n),
                  0.0])
        for i in range(n)
    ]


def main():
    Z = 1.0
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs
    n = len(allcfs.crazyflies)
    print(f'Formation morphing with {n} drones')

    center = np.array([0.5, 0.5, Z])

    formations = [
        ('line', line_formation(n)),
        ('triangle', triangle_formation(n)),
        ('V-shape', v_formation(n)),
        ('circle', circle_formation(n)),
        ('line', line_formation(n)),  # morph back at the end
    ]

    move_duration = 5.0
    settle = 5.5

    # Stagger each drone at a different height so formation transitions
    # (where XY paths can cross near the center) cannot produce collisions.
    z_stagger = [i * 0.35 for i in range(n)]

    allcfs.takeoff(targetHeight=Z, duration=3.0)
    timeHelper.sleep(3.5)

    # Lift each drone to its stagger height before any formation moves
    for cf, dz in zip(allcfs.crazyflies, z_stagger):
        pos = np.array(cf.initialPosition) + np.array([0, 0, Z + dz])
        cf.goTo(pos, 0, 2.5)
    timeHelper.sleep(3.0)

    for name, offsets in formations:
        print(f'Moving to {name}')
        for i, (cf, off, dz) in enumerate(zip(allcfs.crazyflies, offsets, z_stagger)):
            target = center + off + np.array([0, 0, dz])
            cf.goTo(target, 0, move_duration)
            # Stagger start times so drones don't all cross the center at once
            if i < n - 1:
                timeHelper.sleep(0.3)
        timeHelper.sleep(settle)

    # Return to initial XY at hover height before landing
    for cf in allcfs.crazyflies:
        home = np.array(cf.initialPosition) + np.array([0, 0, Z])
        cf.goTo(home, 0, move_duration)
    timeHelper.sleep(settle)

    allcfs.land(targetHeight=0.04, duration=3.0)
    timeHelper.sleep(3.5)


if __name__ == '__main__':
    main()
