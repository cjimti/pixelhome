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
  device by hand. One backup of its settings is kept off-repo. The exception is the pixel ports' virtual strings
  (name, pixel count, start channel, 80%, gamma 1.0 per run, as in the table below and `home.json`, and 1 null node
on each port's first string): `fpp_sync` doesn't
  write them. They're set over the API (`GET`, edit, `POST /api/channel/output/co-bbbStrings`, then
  `/api/system/fppd/restart`) when a run's count changes, after the sync has put FSEQs with the new channel count on
  the player.
- **Settings**: brightness 80% on both ports, gamma 1.0. Sequences are rendered for that.

## Pixels and ports

537 12 V WS2811 pixels in six runs: Porch Front at 2" spacing on the new rail, the others still at 3" (see
[Planned](#planned-new-metal-rail-at-2-spacing)). The controller sits centrally, at the back-left corner of the porch;
two ports carry the house, ports 3-8 are unused.

| port | runs, in data order                              | pixels | channels | power injection                                |
|-----:|--------------------------------------------------|-------:|----------|------------------------------------------------|
| 1    | Porch Left (82), Left (98), Side (81)            | 261    | 1-783    | far end (back end of Side), 5 A fuse; see Open |
| 2    | Porch Front (107), Porch Right (49), Right (120) | 276    | 784-1611 | far end (free end of Right), 5 A fuse; see Open |

Each port is fed from both ends when its injection is on: the controller end through the port's eFuse, the far end
through its own 5 A fuse.

Each port starts with one null pixel (an F-Amp) between the controller and its first run, added with the K8-PB: set
as 1 null node on the port's first virtual string (Porch Left on port 1, Porch Front on port 2). Without it the null
takes the first pixel's data and every pixel on the port shows its neighbour's colour, one place along. The nulls
use no channels, so `home.json` and the sequences don't know about them.

All 8 ports are wired out, one 18 AWG 3-conductor cable each (V+, data, ground). On the board the port terminals
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
  and PSU2. The AC cord and its jumper are 16 AWG. The port cables and the injection lines are 18 AWG; see
  [Wire and connectors](#wire-and-connectors).
- **Voltage**: the supply reads 12.1-12.2 V (multimeter and FPP's VIN sensor).

## Wire and connectors

What the runs are made of, so repairs and extensions match.

| use | product |
|---|---|
| port cables (V+, data, ground) and most runs so far | NAOEVO 18 AWG 3-conductor, stranded tinned copper, PVC jacket |
| power runs, including both injection lines | CONEPY 18 AWG 2-conductor (18/2), stranded tinned copper, PVC jacket |
| long leads from here on (first: the right-side lights' 25-30 ft lead) | 16 AWG |
| 3-pin plugs (V+, data, ground) | [Nilight 3-pin](https://www.amazon.com/dp/B0B615GJJ4) waterproof pigtails: PA66 housing, rubber seals, pre-crimped 16 AWG tinned copper leads, 10 A, -10 to +80 °C, rain-proof but not for submersion |
| 2-pin plugs (power) | [BFXM 2-pin](https://www.amazon.com/dp/B0DCJS59LF) waterproof pigtails: IP65, H62 brass terminals, 16 AWG leads, -40 to +105 °C |
| splices | haisstronica solder-seal connectors, 18-16 AWG (green) |

The pixel strings come with JST connectors that aren't waterproof, and every run is a custom length, so each end is
cut and spliced onto one of these pigtails. The F-Amp null pixels are bare wire. The flat plugs tuck behind the rail
more easily than round pixel plugs, and they're sturdier.

Mixing gauges is fine. The thinnest wire on a port (18 AWG) carries the port's 5.2 A eFuse limit, and voltage drop
adds up per foot of each gauge, so a short 18 AWG tail on a long 16 AWG lead drops about as little as 16 AWG all the
way.

- Colours: red is V+, black is V- (ground), blue is data, on the 3-pin pigtails, and red and black on the 2-pin ones.
  Keep it that way at every splice: the K8-PB has no reverse-polarity protection.
- Other vendors sell connectors that look the same with the colours in a different pin order. They can't mix with
  these without colour exceptions, so reorder from the same listings and check a new batch's pin order against a
  known-good plug before using it.
- Keep plugs off the ground and out of standing water, with a drip loop before each one: they are rated for rain,
  not for sitting in a puddle.

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

On fpp2 with brightness 80%, no injection on either port, 2026-11-21 (FPP test mode, RGB fill of the whole house at
each channel level; currents from the K8-PB's port sensors, `GET /api/fppd/ports`):

| channel level | port 1 (261) | port 2 (276) | both   | at the pixels |
|--------------:|-------------:|-------------:|-------:|--------------:|
| 0 (dark)      | 0.03 A       | 0.04 A       | 0.07 A | 1 W           |
| 10%           | 1.13 A       | 1.13 A       | 2.26 A | 27 W          |
| 20%           | 1.73 A       | 1.75 A       | 3.48 A | 42 W          |
| 30%           | 2.18 A       | 2.18 A       | 4.36 A | 53 W          |
| 40%           | 2.55 A       | 2.54 A       | 5.10 A | 62 W          |
| 50%           | 2.85 A       | 2.82 A       | 5.68 A | 69 W          |
| 60%           | 3.11 A       | 3.09 A       | 6.20 A | 75 W          |
| 70%           | 3.34 A       | 3.32 A       | 6.65 A | 80 W          |
| 80%           | 3.55 A       | 3.54 A       | 7.09 A | 86 W          |

VIN stayed at 11.9-12.3 V. Idle is about 0.13 mA a pixel. The whole-house curve flattens (10% already draws a third
of 80%) because the runs starve without injection, not because the pixels do: the first 20 pixels of port 1 alone,
with no drop to speak of, draw in a straight line.

| channel level | 10% | 20% | 40% | 60% | 80% | 100% |
|--------------:|----:|----:|----:|----:|----:|-----:|
| per pixel     | 5.1 mA | 8.9 mA | 18.0 mA | 26.7 mA | 36.6 mA | 45.3 mA |

So a pixel draws about **45 mA at full white** with the 80% brightness (15 mA a channel), linear in the channel value,
plus 0.13 mA idle. Low loads follow that exactly: the night loops measured 0.18 A (Candlelight), 0.22 A (Food Coma)
and 0.57 A (Amber Waves), and Daylight 0.24 A, each within 0.01 A of `0.07 A + 15 mA x the sum of channel values`.
Fully fed, the house at full white would draw about 24 A (290 W), about 12 A a port: the starving is what keeps the
ports under their limits today. See [Planned](#planned-new-metal-rail-at-2-spacing) for what that means.

The heaviest show moments on the first full night (2026-11-14, Das Rheingold's finale): port 1 3.8 A peak and 2.4 A
average over Entry into Valhalla, port 2's controller end 3.0 A peak. No eFuse trips. The catalog does reach full
white on every run (GD03 Dawn holds it for a second).

Temperatures in the closed box: PocketBeagle SoC 57-69 °C, K8-PB board 39-52 °C, CPU under 10%. In direct afternoon
sun on a mild day (2026-11-21, about 21 °C / 70 °F outside, Daytime Loops playing, CPU 3%): SoC 71.5 °C, board
53.6 °C. Nearly all of that is the sun. The PocketBeagle 2 Industrial is rated to a 105 °C junction; shade or vent
the box if the SoC passes about 80 °C.

## Planned: new metal rail at 2" spacing

The same rooflines at 2" instead of 3" is 1.5x the pixels: about 752. It goes up a run at a time; Porch Front is
done (107, 2026-11-21).

| run         | at 3" | at 2"      |
|-------------|------:|-----------:|
| Porch Left  |    82 |        123 |
| Left        |    98 |        147 |
| Side        |    81 |        122 |
| Porch Front |    71 | 107 (done) |
| Porch Right |    49 |         74 |
| Right       |   120 |        180 |

At the measured 45 mA a pixel at full white (see [Measured](#measured)), fully fed from both ends, each end carrying
about half:

| port | pixels | full white | each end | at 80% channel, each end |
|-----:|-------:|-----------:|---------:|-------------------------:|
| 1 today (3", 261)       | 261 | ~11.8 A | ~5.9 A | ~4.8 A |
| 2 today (276)           | 276 | ~12.5 A | ~6.3 A | ~5.1 A |
| 1 at 2" on two ports    | 392 | ~17.7 A | ~8.9 A | ~7.2 A |
| 2 at 2" on two ports    | 361 | ~16.3 A | ~8.2 A | ~6.6 A |

The ends are a 5.2 A eFuse and a 5 A fuse, so **once injection works, full white is already over both on today's
ports**; the starving is what hides it now (and the catalog does reach full white: GD03 Dawn holds it a second). At
2" the whole house is about 34 A (410 W) at full white: more than one LRS-350-12 (29 A), within the two. Before
injection goes back in, cap the draw: FPP brightness (60% keeps today's ports at 4.4-4.7 A an end), or a cap on each
port's frame draw in the build. For 2", spread the runs over more ports (3-8 are wired and unused, each with its own
eFuse; PSU2 is there for injection): one run a port, e.g. Right's 180 at about 8.1 A, is about 4 A an end. Data is
well inside the 800-pixel port rating. When a run is re-strung, its count changes in `home.json`, the start channels of the runs after it on its
port move with it, and so do that port's virtual strings on fpp2; sequences follow from segment names, distances
and `G.first/last/mid/corners`, never literal path indices.

## Open

- **Far-end injection, both ports**: connecting either port's far-end injection (PSU1, through the fuse block) makes
  the far half of that port go dark, with either polarity. Both are unplugged; the house runs from the controller end
  only. On 2026-11-21 over Götterdämmerung that peaked at 2.9 A on port 1 and 3.4 A on port 2 (averages 1.0 A and
  1.2 A), well under the eFuses, and the far ends looked fine. The same result in both polarities means the two
  injection conductors are at the same potential, which shorts the run's V+ to ground at the far end: the + landing on
  a negative bus-bar screw instead of its fuse's output screw, or a blown 5 A fuse with the conductors touching. It's
  the same on both lines, so look at what they share (how they leave the fuse block). Checks:
  1. Injection unplugged at the run: its far-end plug should read about 12.1 V, red to black.
  2. If not: the fuse's output screw should read 12 V to the negative nut, red should leave from that screw and black
     from the bus bar, and the 5 A fuse should have continuity.
  3. PSU1 off, line unplugged at both ends: the two conductors should be open to each other.
  4. Port lit, both sides unplugged: across each pair about to be joined (line red to the run's V+ pin, line black to
     its ground pin) should read under about 1 V.
  Then connect it while watching the port's current (`GET /api/fppd/ports`, `ma`): it should drop as the far end takes
  a share. A jump of amps is a short; unplug at once.
  Once it works, a fully fed port at full white is over its fuses (see Planned): cap the draw before leaving it
  connected.
