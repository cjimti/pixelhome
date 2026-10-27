"""Read/write FSEQ v2 files, uncompressed or zstd (the format FPP plays)."""
import hashlib, math, struct
import numpy as np
import zstandard

PRODUCER = 'pixelhome'


def read(path):
    """-> (uint8 array (frames, channels), step_ms)"""
    d = open(path, 'rb').read()
    assert d[:4] == b'PSEQ', 'not an FSEQ file'
    off, minor, major, hlen, chans, frames, step, flags, comp, nblk, nsparse = struct.unpack('<HBBHIIBBBBB', d[4:23])
    assert major == 2, f'FSEQ v{major} not supported'
    nb = nblk | ((comp >> 4) << 8); ctype = comp & 15
    if ctype == 0:
        raw = d[off:off + chans * frames]
    else:
        assert ctype == 1, f'compression type {ctype} not supported'
        dz = zstandard.ZstdDecompressor()
        pos, parts = off, []
        for i in range(nb):
            fnum, size = struct.unpack('<II', d[32 + i * 8:40 + i * 8])
            if size == 0: continue
            parts.append(dz.decompressobj().decompress(d[pos:pos + size]))
            pos += size
        raw = b''.join(parts)
    return np.frombuffer(raw[:chans * frames], np.uint8).reshape(frames, chans), step


def write(path, data, step_ms, compress=True):
    """data: uint8 array (frames, channels). Writes FSEQ v2.0, zstd-compressed in blocks unless
    compress=False. The unique id is derived from the data, so identical input gives identical files."""
    data = np.ascontiguousarray(data, np.uint8)
    frames, chans = data.shape
    blocks = []
    if compress:
        per = max(math.ceil(frames / 250), math.ceil(65536 / chans))      # <= 250 blocks, >= 64 KB each
        cz = zstandard.ZstdCompressor(level=10)
        for f0 in range(0, frames, per):
            blocks.append((f0, cz.compress(data[f0:f0 + per].tobytes())))
    sp = PRODUCER.encode() + b'\0'
    vh = struct.pack('<H', len(sp) + 4) + b'sp' + sp
    vh_off = 32 + len(blocks) * 8
    off = (vh_off + len(vh) + 3) & ~3
    uid = int.from_bytes(hashlib.sha256(data.tobytes()).digest()[:8], 'little')
    comp = 1 if compress else 0
    head = b'PSEQ' + struct.pack('<HBBHIIBBBBBBQ', off, 0, 2, vh_off, chans, frames, step_ms, 0,
                                 comp | ((len(blocks) >> 8) << 4), len(blocks) & 0xff, 0, 0, uid)
    index = b''.join(struct.pack('<II', f0, len(b)) for f0, b in blocks)
    with open(path, 'wb') as f:
        f.write(head + index + vh + b'\0' * (off - vh_off - len(vh)))
        if compress:
            for _, b in blocks:
                f.write(b)
        else:
            f.write(data.tobytes())
