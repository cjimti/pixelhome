"""Import a home from an xLights show directory: Single Line models become segments, the Mesh
view object becomes house.obj (baked into layout coordinates), the first controller becomes the
controller block.

usage: python -m pixelhome.xlights SHOW_DIR HOME_DIR --name NAME [--path Side:-1,Left:-1,...]

Without --path the roofline path runs through the segments in channel order; edit home.json
"path" so it follows the roof physically, since sequences sweep along it.
"""
import argparse, json, os, re
import numpy as np


def _attrs(tag):
    return dict(re.findall(r'(\w+)="([^"]*)"', tag))


def segments(rgbeffects):
    out = []
    for m in re.finditer(r'<model ([^>]*)>', rgbeffects):
        a = _attrs(m.group(1))
        if a.get('DisplayAs') != 'Single Line':
            continue
        n = int(a.get('NodesPerString') or a['parm2'])
        p0 = np.array([float(a['WorldPosX']), float(a['WorldPosY']), float(a['WorldPosZ'])])
        p1 = p0 + np.array([float(a['X2']), float(a['Y2']), float(a['Z2'])])
        if a.get('Dir', 'L') == 'R':
            p0, p1 = p1, p0
        out.append(dict(name=a['name'], start_channel=int(a['StartChannel'].split(':')[-1]), nodes=n,
                        first=np.round(p0, 6).tolist(), last=np.round(p1, 6).tolist()))
    return sorted(out, key=lambda s: s['start_channel'])


def mesh(show_dir, rgbeffects, out_path):
    m = re.search(r'<view_object [^>]*DisplayAs="Mesh"[^>]*>', rgbeffects)
    if not m:
        return None
    a = _attrs(m.group(0))
    rot = (float(a['RotateX']), float(a['RotateY']), float(a['RotateZ']))
    if rot != (180, 0, 180):
        raise SystemExit(f'mesh rotation {rot} not supported yet (only 180,0,180)')
    scale = np.array([float(a['ScaleX']), float(a['ScaleY']), float(a['ScaleZ'])])
    pos = np.array([float(a['WorldPosX']), float(a['WorldPosY']), float(a['WorldPosZ'])])
    lines = []
    for line in open(os.path.join(show_dir, a['ObjFile'])):
        p = line.split()
        if p and p[0] == 'v':
            v = np.array([float(x) for x in p[1:4]]) * scale
            v[[0, 2]] *= -1                    # RotateX 180 then RotateZ 180 == RotateY 180
            v += pos
            lines.append('v {:.3f} {:.3f} {:.3f}\n'.format(*v))
        elif p and p[0] == 'f':
            lines.append(line)
    with open(out_path, 'w') as f:
        f.write('# house mesh in layout coordinates (imported from xLights)\n')
        f.writelines(lines)
    return os.path.basename(out_path)


def controller(show_dir):
    path = os.path.join(show_dir, 'xlights_networks.xml')
    if not os.path.exists(path):
        return None
    m = re.search(r'<Controller ([^>]*)>', open(path).read())
    if not m:
        return None
    a = _attrs(m.group(1))
    return dict(name=a.get('Name'), hardware=f"{a.get('Vendor', '')} {a.get('Model', '')}".strip(),
                host=a.get('IP'), protocol=a.get('Protocol'),
                brightness=int(a.get('DefaultBrightnessUnderFullControl', 100)) / 100,
                gamma=float(a.get('DefaultGammaUnderFullControl', 1)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('show_dir')
    ap.add_argument('home_dir')
    ap.add_argument('--name', required=True)
    ap.add_argument('--description', default='')
    ap.add_argument('--path', help='comma separated segment:dir, dir 1 or -1')
    a = ap.parse_args()
    rgb = open(os.path.join(a.show_dir, 'xlights_rgbeffects.xml')).read()
    segs = segments(rgb)
    if a.path:
        path = [dict(segment=p.split(':')[0], dir=int(p.split(':')[1])) for p in a.path.split(',')]
    else:
        path = [dict(segment=s['name'], dir=1) for s in segs]
    os.makedirs(a.home_dir, exist_ok=True)
    spec = dict(name=a.name, description=a.description, units='xLights layout units',
                controller=controller(a.show_dir), segments=segs, path=path,
                mesh=mesh(a.show_dir, rgb, os.path.join(a.home_dir, 'house.obj')))
    with open(os.path.join(a.home_dir, 'home.json'), 'w') as f:
        text = json.dumps(spec, indent=2)
        f.write(re.sub(r'\[\s+([-\d.]+),\s+([-\d.]+),\s+([-\d.]+)\s+\]', r'[\1, \2, \3]', text) + '\n')
    print(f"{a.home_dir}: {sum(s['nodes'] for s in segs)} pixels in {len(segs)} segments")


if __name__ == '__main__':
    main()
