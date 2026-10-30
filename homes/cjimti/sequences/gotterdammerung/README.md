# Götterdämmerung on the roofline

Wagner's last opera in 30 shows of 80 seconds, `GD01`..`GD30`: the Prologue in six, then eight, seven and nine
for the three acts, played in order. As with [Das Rheingold](../das-rheingold/README.md),
[Die Walküre](../die-walkure/README.md) and [Siegfried](../siegfried/README.md), each quotes the real
leitmotifs note for note from `pixelhome/leitmotifs.py` and composes the rest around them; characters have
instruments and the lights follow their notes. The Commons examples for the call to the wedding (d41), Hagen's
fuller forms (d61), misfortune (d68) and agitation (d69) are empty; Hagen is his falling tritone (d61a), and the
gathering of the vassals is built from their call (d54).

**Very dynamic, always.** One strand on a roofline seen from across the street: every scene moves the whole house.
Big events on the beat (whole runs changing colour at once, sweeps end to end in a second, bursts, shockwaves,
chases), saturated colour against dark, contrast between characters you can read from the far kerb. A scene that
holds still for more than a few seconds is a scene that has stopped.

## The stage

From the street the porch is the back of the scene.

- **Prologue, Brünnhilde's rock.** The porch is the rock, its summit the middle of Porch Front, the magic fire low
  round it. The three Norns stand on Left, Porch Front and Right and throw the golden rope of fate between them,
  a line of gold running back and forth over the whole house, until it snaps. Dawn rises over every run; the
  Rhine Journey sends Siegfried from the summit out of the free end of Right and the river flows the length of
  the house.
- **Act I, the hall of the Gibichungs on the Rhine.** The porch is the hall, torchlit amber and royal purple;
  Left and Side are its far walls, Right is the riverbank, the Rhine flowing past at its free end. In its last
  scenes the act goes back to Brünnhilde's rock (the porch again, the fire round it).
- **Act II, the shore before the hall, at night into a red dawn.** The porch is the hall's doors, the wings the
  shore; the vassals' torches crowd the whole house in points of orange; Hagen's spear stands on Porch Front.
- **Act III, a wooded valley on the Rhine, then the hall.** The river runs along Right and the Side, the forest
  over Left; the hunt comes down out of Left. For the Funeral March the whole house is the procession. For the
  end the porch is the pyre: fire takes every run, Valhalla burns gold-white on the porch, and the Rhine floods
  the house from the free end of Right and puts the fire out.

Subjects never begin on Side (enter from the free end of Right, pop up on a front run, rise out of the porch).
Every run stays lit.

## Who is who

| character | colour | voice |
|-----------|--------|-------|
| Siegfried | electric emerald `#00ff40`, white-hot head `#e8ffe8` | horns (his call, d48) |
| Brünnhilde | silver white `#f4f8ff`, gold glints `#ffd060` | horns, violins |
| Hagen | ultraviolet `#7a00ff` in black, a spear point `#c8d8ff` | tubas, trombones, contrabassoon |
| Gunther | royal gold `#ffb020` | trombone, bassoon |
| Gutrune | rose `#ff4090` | oboe, clarinet, violins |
| Alberich | red `#ff1000` in a muddy halo `#5a1200` | bassoon, low strings |
| Waltraute | Valkyrie orange `#ff9a20` over storm cloud `#2a3448` | horns, trumpets |
| the Norns | grey white `#c8c8d8`; the rope gold `#ffcc40` | low strings, harp |
| the Rhinemaidens | Woglinde `#c0f4ff`, Wellgunde `#20ff90`, Flosshilde `#8c60ff` | flute, oboe, clarinet |
| the Rhine | indigo `#0c1c8c` to teal `#0a7c8a`, green `#14c080` | strings |
| the vassals | torch orange `#ff6a10` points | men's voices as trombones; cowhorns |
| the Ring | gold `#ffaa00` with red `#ff1800` | woodwinds |
| the potion | sickly violet `#a050ff` | clarinets, low strings |
| Loge's fire | `#ff5000` to `#ffb020`, red `#ff2000` | piccolo, violins, harp, glockenspiel |
| Valhalla | gold-white `#fff0a0` on deep blue `#1a3cff` | Wagner tubas (tubas, horns) |
| the ravens | black flecks on white | |

## The 30 scenes

| code | file | title | what happens | motifs |
|------|------|-------|--------------|--------|
| GD01 | the_norns.py | The Norns | night on the rock; the three Norns throw the golden rope between them and sing of the world ash and Valhalla | norns (23), norns_rope (10), valhalla (63), loge (20) |
| GD02 | the_rope_breaks.py | The Rope Breaks | they sing of the Ring and the curse; the rope frays and snaps; the Norns sink away | norns_rope, ring (8), curse (13), downfall (4) |
| GD03 | dawn.py | Dawn | daybreak rolls over the whole house, red to gold to white | dawn (49), brunnhilde (88) |
| GD04 | zu_neuen_taten.py | Zu neuen Taten | Siegfried and Brünnhilde; he gives her the Ring, she gives him her horse Grane | siegfried_heroism (78), brunnhilde_love (87), ring |
| GD05 | heil_brunnhilde.py | Heil, Brünnhilde! | their ecstatic farewell, the two colours blazing end to end | love_fulfilled (90), siegfried (53), siegfried_horn |
| GD06 | rhine_journey.py | Siegfried's Rhine Journey | the horn call carries him down from the rock and along the river, the whole house the Rhine | siegfried_horn, rhine (2), rheingold (31), renunciation (76), ring |
| GD07 | the_gibichungs.py | The Gibichungs | the hall: Gunther in gold, Gutrune in rose, and Hagen in the shadows | hagen (61a), gutrune (40) |
| GD08 | hagens_plan.py | Hagen's Plan | a bride for Gunther, a husband for Gutrune: the potion | potion (19), hagen, ring |
| GD09 | siegfried_arrives.py | Siegfried Arrives | a horn on the river; his boat lands; "Heil, Siegfried!" and the curse beneath | siegfried_horn, curse, hagen |
| GD10 | the_potion.py | The Potion | he drinks to Brünnhilde, forgets her, and burns for Gutrune | potion, gutrune, love_potion (39) |
| GD11 | blood_brotherhood.py | Blood Brotherhood | Siegfried and Gunther swear on their mingled blood | oath (42), oath_b (42a), plot (75) |
| GD12 | hagens_watch.py | Hagen's Watch | Hagen alone at the door, waiting for the Ring | hagen, ring, vassals (54) |
| GD13 | waltraute.py | Waltraute | back on the rock: a Valkyrie storms in begging Brünnhilde to give the Ring back to the Rhine | valkyries (22), ride (47), valhalla, wotan_grief (82) |
| GD14 | the_false_gunther.py | The False Gunther | through the fire comes Siegfried in Gunther's shape and tears the Ring from her | tarnhelm (18), loge, ring, curse |
| GD15 | alberich.py | Alberich | night on the shore: Alberich comes to the sleeping Hagen; swear to win the Ring | ring, curse, hagen |
| GD16 | hoiho.py | Hoiho! | dawn; Hagen blows the cowhorn and calls the vassals to arms | vassals, hagen |
| GD17 | the_vassals.py | The Vassals | the men come running with torches from every side and the shore fills with fire | vassals, gutrune |
| GD18 | the_ring_on_his_hand.py | The Ring on His Hand | Brünnhilde, led in, sees the Ring on Siegfried's hand: betrayed | ring, curse, brunnhilde |
| GD19 | the_oath_on_the_spear.py | The Oath on the Spear | he swears on Hagen's spear he is innocent; she swears he lies | oath, spear (73), brunnhilde |
| GD20 | vengeance.py | Vengeance | Brünnhilde, Gunther and Hagen swear Siegfried's death | plot, hagen, curse |
| GD21 | the_wedding_procession.py | The Wedding Procession | the double wedding sweeps out in rose and gold over a house full of torches | gutrune, vassals, plot |
| GD22 | rhinemaidens.py | The Rhinemaidens | in the river the three maidens ask Siegfried for the Ring; he laughs | rhinemaidens (26), rheingold, rhine |
| GD23 | the_hunt.py | The Hunt | horns in the forest; he tells his story: Mime, the sword, the dragon, the bird | siegfried_horn, forging (52), woodbird (27) |
| GD24 | the_ravens.py | The Ravens | two ravens fly up; Hagen's spear in his back | hagen, curse, plot |
| GD25 | heilige_braut.py | Heilige Braut | dying, he greets Brünnhilde one last time | brunnhilde (88), sleep (16), siegfried_love (89) |
| GD26 | funeral_march.py | Siegfried's Funeral March | the vassals carry him through the night; the whole house the procession | volsung_fate (66), siegmund (35), sword, siegfried, siegfried_horn |
| GD27 | the_dead_hand.py | The Dead Hand | Hagen kills Gunther for the Ring; the dead hand rises against him | ring, curse, hagen |
| GD28 | immolation.py | Brünnhilde's Immolation | she orders the pyre and sends the ravens to Valhalla | love_fulfilled, valhalla, transformation (91) |
| GD29 | valhalla_burns.py | Valhalla Burns | she rides into the fire; flames take every run; Valhalla burns on the porch | loge, valhalla, downfall_b (5), ride |
| GD30 | redemption.py | Redemption | the Rhine floods the house, Hagen drowns, the maidens take the Ring, and love redeems the world | rhine, rhinemaidens, downfall, redemption (90b) |

The last frame of each scene sets up the first of the next, so they can run back to back.
