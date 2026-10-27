# Roofline House (`cjimti`)

501 RGB pixels along the roofline in six straight runs, FPP on a Falcon PiCap V2, DDP, rendered for
80% brightness and gamma 1.0.

## Shape

Every pixel sits at the same height (y ≈ 150), so the roofline is a flat outline. Seen from above,
street at the bottom (`+z` is toward the street):

```
 z=-637  ●  (free end, back of the house)
         │
         │ Side (81)            ┌──── Porch Front (71) ────┐   z=-569
         │                      │                          │
         │                      │ Porch                    │ Porch
         │                      │ Left                     │ Right
         │                      │ (82)                     │ (49)
         │                      │                          │
 z=-147  └──── Left (98) ───────┘                          └──── Right (120) ────●  z=-191
        x=-596              x=-196                     x=152                 x=629 (free end)
```

Two wings come forward toward the street; between them the porch is set back about 420 units.
From the street the **Left** and **Right** wing fronts and the **Porch Front** read as three
horizontal lines (the porch one farther away and higher in the view); **Porch Left**, **Porch
Right** and **Side** run away from the viewer, so they look short and steep. The 3D player's default
camera is the street view.

| segment     | nodes | runs from → to (path direction)        | length | spacing | channels   |
|-------------|------:|----------------------------------------|-------:|--------:|------------|
| Side        |  81   | (-596, -637) back → (-596, -146) front  | 490    | 6.1     | 541–783    |
| Left        |  98   | (-595, -148) → (-195, -148)             | 400    | 4.1     | 247–540    |
| Porch Left  |  82   | (-196, -151) front → (-196, -565) back  | 414    | 5.1     | 1–246      |
| Porch Front |  71   | (-194, -569) → (150, -569)              | 344    | 4.9     | 784–996    |
| Porch Right |  49   | (152, -565) back → (152, -196) front    | 368    | 7.5     | 997–1143   |
| Right       | 120   | (153, -191) → (629, -191)               | 476    | 4.0     | 1144–1503  |

- **Path** (`G.path`, `G.pd`, `G.pi`): one continuous line, 2512 units, starting at the free back
  end of Side and ending at the free right end of Right. Path index ranges: Side 0–80, Left 81–178,
  Porch Left 179–260, Porch Front 261–331, Porch Right 332–380, Right 381–500.
- **Corners** (90° turns), by path index: 80|81 Side→Left (front-left corner of the house),
  178|179 Left→Porch Left, 260|261 Porch Left→Porch Front (back-left of the porch), 331|332
  Porch Front→Porch Right (back-right of the porch), 380|381 Porch Right→Right.
- **Two free ends**: path index 0 (back of Side, the farthest pixel from the street) and 500 (right
  end of Right). Things can enter or leave the house there.
- **Channel order is not path order**: Porch Left is wired first. Always address pixels through
  `G.seg`, `G.path` or positions, never by raw index arithmetic.
- **Spacing differs by run** (4.0 to 7.5 units). Effects defined in distance (`G.pd`, `G.pos`) look
  even across runs; effects defined per pixel index squash or stretch on Porch Right and Side.
- **Symmetry**: the facade is roughly mirror-symmetric about x ≈ 16: Left ↔ Right, Porch Left ↔
  Porch Right. Side has no partner (it is the house's left flank).

## Power and comfort

- Full white on all 501 pixels for long stretches is hard on the supply and on the neighbours. Keep
  full-house white to moments.
- Avoid sustained strobing (more than about 3 full-house flashes per second for more than a couple
  of seconds).
