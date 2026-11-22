"""A home model: pixel positions, roof segments and the house mesh, read from homes/<id>/home.json.

Node index k is the k-th pixel in controller channel order (channels 3k..3k+2, zero based).
"Path" order runs physically along the roofline in the order given by home.json "path".
"""
import json, os
import numpy as np


class Home:
    def __init__(self, directory):
        self.dir = os.path.abspath(directory)
        with open(os.path.join(self.dir, 'home.json')) as f:
            self.spec = json.load(f)
        self.id = os.path.basename(self.dir)
        self.name = self.spec['name']
        self.seg = {}
        pos = {}
        for s in self.spec['segments']:
            n = s['nodes']
            first = (s['start_channel'] - 1) // 3
            a, b = np.array(s['first']), np.array(s['last'])
            t = np.arange(n) / (n - 1)
            self.seg[s['name']] = np.arange(first, first + n)
            for k, p in zip(range(first, first + n), a + t[:, None] * (b - a)):
                pos[k] = p
        self.N = len(pos)
        assert sorted(pos) == list(range(self.N)), 'segments must cover channels 1..3N without gaps'
        self.channels = self.N * 3
        self.pos = np.array([pos[k] for k in range(self.N)])
        self.path_order = [(p['segment'], p['dir']) for p in self.spec['path']]
        self.path = np.concatenate([self.seg[name][::d] for name, d in self.path_order])
        assert sorted(self.path) == list(range(self.N)), 'path must visit every pixel once'
        steps = np.linalg.norm(np.diff(self.pos[self.path], axis=0), axis=1)
        path_d = np.concatenate([[0], np.cumsum(steps)])
        self.pd = np.empty(self.N)          # distance along the path, by node
        self.pd[self.path] = path_d
        self.pi = np.empty(self.N, int)     # path index, by node
        self.pi[self.path] = np.arange(self.N)
        self.length = path_d[-1]
        self.seg_of = np.empty(self.N, object)
        for name, idx in self.seg.items():
            self.seg_of[idx] = name

    def path_segments(self):
        """[(name, path indices)] in path order."""
        return [(name, self.pi[self.seg[name]]) for name, _ in self.path_order]

    def first(self, name):
        """Path index of a segment's first pixel in path order. Use these instead of literal path indices: the pixel
        counts change when a run is re-strung (Porch Front went from 71 to 107), the distances don't."""
        return int(self.pi[self.seg[name]].min())

    def last(self, name):
        """Path index of a segment's last pixel in path order."""
        return int(self.pi[self.seg[name]].max())

    def mid(self, name):
        """Path index of a segment's middle pixel (the left of the two when there is an even count)."""
        return (self.first(name) + self.last(name)) // 2

    @property
    def corners(self):
        """Path index of the last pixel before each turn: one per segment but the last, in path order."""
        return [self.last(name) for name, _ in self.path_order[:-1]]

    def span_u(self, idx):
        """Position of nodes idx across their own left-right extent, -1..1 (by x)."""
        xs = self.pos[idx, 0]
        return (xs - (xs.max() + xs.min()) / 2) / ((xs.max() - xs.min()) / 2)

    def mesh(self):
        """House mesh as (flat vertex list, flat triangle index list), in layout coordinates."""
        verts, tris = [], []
        with open(os.path.join(self.dir, self.spec['mesh'])) as f:
            for line in f:
                p = line.split()
                if not p:
                    continue
                if p[0] == 'v':
                    verts.append([float(x) for x in p[1:4]])
                elif p[0] == 'f':
                    ids = [int(x.split('/')[0]) - 1 for x in p[1:]]
                    tris += [[ids[0], ids[i], ids[i + 1]] for i in range(1, len(ids) - 1)]
        return np.round(np.array(verts), 1).ravel().tolist(), np.array(tris).ravel().tolist()
