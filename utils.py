from __future__ import division
import pygame

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def rect_overlaps_solid(rect, solid_rects):
    for r in solid_rects:
        if rect.colliderect(r):
            return True
    return False

class Timer(object):
    def __init__(self, frames=0):
        self.t = 0
        self.max = frames
    def start(self, frames=None):
        if frames is not None:
            self.max = frames
        self.t = self.max
    def tick(self):
        if self.t > 0:
            self.t -= 1
    def active(self):
        return self.t > 0
