# Hardware (`cjimti`)

The gear behind the roofline, as installed. The shape, segments and channel map are in [README.md](README.md); this
file is the controller, power, wiring and what it measures. Keep it current when the hardware changes.

## Controller: Kulp K8-PB at `fpp2.local`

- **Board**: [Kulp K8-PB](https://kulplights.com/manuals/boards/k8-pb/) rev 2.5 on a PocketBeagle 2, running FPP
  10.4. Web UI and API over plain http (`http://fpp2.local`, no https). On Wi-Fi.
- **Ports**: 8 pixel ports (BBB48String), each behind its own eFuse that trips at about 5.2 A. Kulp rates a port at
  800 pixels of data; power, not data, is the limit here. The board has **no reverse-polarity protection**. On rev 2.5
  port 2's enable is always on. Board input V+ 5-18 V.
- **Storage**: FPP boots from the board's built-in storage (`mmcblk0`, about 64 GB, 47 GB free). A 128 GB microSD sits
  in the slot (`mmcblk1`) unused; FPP's storage page calls it "eMMC". FPP 10.4's Flash Copy/Create can't write it
  (its PocketBeagle 2 profile only targets `mmcblk0`).
- **Audio**: no sound card (output "Dummy"). Music reaches the street from the site's Live page and the QR code.
- **Live mode**: pushes to `live.pixelhome.app` from fpp2.
- **Provisioning**: everything on fpp2 comes from this repo (`scripts/fpp_sync.py --apply`); nothing is changed on the
  device by hand. One backup of its settings is kept off-repo.
- **Settings**: brightness 80% on both ports, gamma 1.0. Sequences are rendered for that.

## Pixels and ports

501 12 V WS2811 pixels at 3" spacing in six runs. The controller sits centrally, at the back-left corner of the porch;
two ports carry the house, ports 3-8 are unused.

| port | runs, in data order                     | pixels | channels  | power injection                                |
|-----:|-----------------------------------------|-------:|-----------|------------------------------------------------|
| 1    | Porch Left (82), Left (98), Side (81)   | 261    | 1-783     | far end (back end of Side), 5 A fuse; see Open |
| 2    | Porch Front (71), Porch Right (49), Right (120) | 240 | 784-1503 | far end (free end of Right), 5 A fuse          |

Each port is fed from both ends when its injection is on: the controller end through the port's eFuse, the far end
through its own 5 A fuse.

All 8 ports are wired out, one 16 AWG 3-conductor cable each (V+, data, ground). On the board the port terminals
are two rows of four, numbered down each column: port 1 top left, port 2 below it, port 3 top of the second column,
and so on. The port glands in the box's front wall are two rows of four: ports 1-4 on the row nearer the lid, 5-8 on
the row nearer the ground, left to right.

## Power

- **Supplies**: 2x Mean Well LRS-350-12 (12 V, 29 A, 348 W).
  - **PSU1** feeds the K8-PB and both far-end injections.
  - **PSU2** is mounted with AC in, DC outputs not wired yet (reserved for injection).
- **AC**: a 16 AWG 3-conductor cord comes in through its own gland to PSU2 (on the right), and a jumper of the same
  cord carries L, N and ground across to PSU1.
- **Fuses**: a Faststorm 6-way blade fuse block (85 x 88 mm), used without its cover. It has the negative nut at the
  top, two negative bus bars of three screws under it, three rows of two fuse slots, each slot with its own output
  screw on the outer edge, and the positive nut at the bottom. PSU1's 10 AWG V+ lands on the positive nut and V- on
  the negative nut. The two injection lines use 5 A fuses in the left slots of the first two rows and leave from those
  rows' left screws. Their negatives come off the left bus bar. The other four slots are empty.
- **Wire**: 10 AWG for PSU1's V+/V- to the K8-PB, PSU1's V+/V- to the fuse block, and the V- jumper between PSU1
  and PSU2. Everything else is 16 AWG.- The supply voltage reads 12.1-12.2 V (multimeter and FPP's VIN sensor).

## Enclosure

QILIPSU IP66 PC/ABS box (UL 94 V-0). Everything is on its mounting plate: the K8-PB, the fuse block and both
supplies. The box sits on the ground with the lid on top; every cable enters through glands in one side wall.

From the maker's dimension drawing (mm, ±2):

| | width x height x depth |
|---|---|
| outside, body                      | 415 x 315 x 183 |
| outside, with hinges and latches   | 425 x 340       |
| inside, at the base                | 382 x 282       |
| mounting plate                     | 371 x 271 x 4.5 |

- Inside height is 165 from the floor to the lid, so about 160 above the plate; the base's rim is 101 above the plate.
  Walls 3.5.
- Plate holes (and the matching Φ4.2 bosses inside the box) sit on two patterns: 359 x 259 and 300 x 199.

Keep it closed. The old controller (a Raspberry Pi 4 with a Falcon PiCap V2 at `fpp.local`) died on 2026-11-13
after rain reached it through an open side of its case: USB, Wi-Fi, Ethernet and the PiCap's I2C all failed. It is
retired; its SD card is fine.

## Measured

On fpp2 with brightness 80%, port 1 without injection:

| test                      | port 1  |
|---------------------------|--------:|
| 10% white                 | 1.1 A   |
| 25% white                 | 1.9 A   |
| 50% white                 | 2.8 A   |
| full white (projected)    | ~4 A    |

The curve flattens because the far end of port 1 is starved without injection; a fully powered port 1 should draw
about 5.9 A at full white. The low steps give about **20 mA per pixel at full white** (with the 80% brightness) plus
about 2 mA idle. Re-measure at full white once port 1's injection works.

The heaviest show moments on the first full night (2026-11-14, Das Rheingold's finale): port 1 3.8 A peak and 2.4 A
average over Entry into Valhalla, port 2's controller end 3.0 A peak. No eFuse trips. The catalog does reach full
white on every run (GD03 Dawn holds it for a second).

Temperatures in the closed box: PocketBeagle SoC 57-69 °C, K8-PB board 39-52 °C, CPU under 10%.

## Planned: new metal rail at 2" spacing

The same rooflines at 2" instead of 3" is 1.5x the pixels: about 752.

| run         | now | at 2" |
|-------------|----:|------:|
| Porch Left  |  82 |   123 |
| Left        |  98 |   147 |
| Side        |  81 |   122 |
| Porch Front |  71 |   106 |
| Porch Right |  49 |    74 |
| Right       | 120 |   180 |

On the same two ports with far-end injection on both, at full white:

| port | pixels | total   | controller end (5.2 A eFuse) | far end (5 A fuse) |
|-----:|-------:|--------:|-----------------------------:|-------------------:|
| 1    | 392    | ~8.9 A  | ~4.4 A                        | ~4.4 A             |
| 2    | 361    | ~8.2 A  | ~4.1 A                        | ~4.1 A             |

A run fed at both ends from the same supply splits its load about evenly, so both fuses stay under their ratings.
The whole house at full white is about 17 A (205 W), within one LRS-350-12. Data is well inside the 800-pixel port
rating. When the pixel counts change, `home.json` changes with them; sequences follow from segment names and
distances.

## Open

- **Port 1 injection**: with the far-end injection connected (same PSU1), the far half of port 1 goes dark, with
  either polarity. Points to a rail landing on the wrong conductor at the tail. Check continuity at the controller-end
  plug (injection + to V, - to G, neither to data) and the injection fuse, then connect it while watching port 1's
  current: it should drop when the injection carries its share. Running without it until then; port 1 stays under
  its eFuse.
