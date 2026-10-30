# Die Walküre on the roofline

Wagner's opera in 30 shows of 80 seconds, `WK01`..`WK30`, ten to an act, played in order. As with
[Das Rheingold](../das-rheingold/README.md), each quotes the real leitmotifs note for note from
`pixelhome/leitmotifs.py` and composes the rest around them; characters have instruments and the lights follow
their notes. The Commons examples for Hunding and the Death/Fate motif are empty, so Hunding's motif is
composed (a low, heavy, rhythmic tuba figure), and the Annunciation uses `fate` (Donington 84, the power of fate).

## The stage

From the street the porch is the back of the scene.

- **Act I, Hunding's hut.** The whole roof is the room. The hearth glows on Left; the door is the free end of
  Right (the storm, and later spring, come in through it). The great ash tree grows at the middle of Porch Front,
  its branches over the porch, with the sword Nothung buried in the trunk to the hilt (a gold glint).
- **Act II, a wild rocky pass.** Brünnhilde's lookout is the top of the porch; the lovers come in from the free end
  of Right; the fight is on the porch.
- **Act III, the Valkyries' rock.** The porch is the rock, its summit the middle of Porch Front (where Brünnhilde
  will sleep); the wings and Side are the storm clouds the Valkyries ride through. At the end Loge's fire rings
  the porch and then the whole house.

Subjects never begin on Side (enter from the free end of Right, pop up on a front run, rise out of the porch).
Every run stays lit.

## Who is who

| character | colour | voice |
|-----------|--------|-------|
| Siegmund | Wälsung blue `#30a8ff` | horns, cellos (low) |
| Sieglinde | hearth amber `#ffa860` | cellos, oboe |
| Hunding | blood red `#8a0020` in black | tubas, trombones, timpani |
| Wotan | deep blue `#1a3cff`, spear `#c8d8ff` | trombones, tubas |
| Fricka | rose silver `#ff9ad0` | violas, oboe |
| Brünnhilde | silver white `#f4f8ff`, gold glints `#ffd060` | horns, trumpet |
| the Valkyries | Gerhilde `#ff4040`, Ortlinde `#ff9a20`, Waltraute `#f0e040`, Schwertleite `#40e070`, Helmwige `#40d0ff`, Siegrune `#6060ff`, Grimgerde `#c050ff`, Rossweisse `#ff60c0`, over storm cloud `#2a3448` | horns, trumpets, trombones; trilling winds and strings |
| Nothung | white steel `#e8f8ff`, gold hilt `#ffcc40` | trumpet |
| the ash tree | trunk `#5a3010`, leaves `#50b030` | |
| the hearth | `#ff6a10` | |
| the storm | grey blue `#5a6a8a`, lightning white | low strings |
| spring and moonlight | green `#80ff60`, moon `#c8dcff` | violins, harp |
| fate / death | indigo `#2a1a5a`, pale `#a0b0c0` | Wagner tubas (tubas, horns) |
| the magic sleep | soft violet `#7a6aff` | woodwinds |
| Loge's fire | `#ff5000` to `#ffb020`, red `#ff2000` | piccolo, violins, harp, glockenspiel |

## The 30 scenes

| code | file | title | what happens | motifs |
|------|------|-------|--------------|--------|
| WK01 | storm.py | Storm | the storm prelude in D minor, rain and lightning over the house | storm (74), spear (73) |
| WK02 | the_stranger.py | The Stranger | Siegmund staggers in from the storm and collapses at the hearth | storm, siegmund (35, 35a) |
| WK03 | a_drink_of_water.py | A Drink of Water | Sieglinde finds him and gives him water; their first looks | sieglinde (36), siegmund, twins_love (37) |
| WK04 | hunding.py | Hunding | Hunding comes home and sees the likeness between them | Hunding (composed), sieglinde |
| WK05 | wehwalt.py | Wehwalt | Siegmund's story: the burned home, the lost sister, the wolf father | volsung_fate (66), siegmund_weary, valhalla (63) |
| WK06 | the_challenge.py | The Challenge | Hunding knows his enemy: a fight at dawn; Sieglinde drugs his drink | Hunding, nothung (43), sword (45) |
| WK07 | walse.py | Wälse! Wälse! | alone by the embers, Siegmund calls for the sword his father promised; the hilt flashes in the tree | sword (45), sieglinde |
| WK08 | the_sword_in_the_tree.py | The Sword in the Tree | Sieglinde tells of the stranger who drove a sword into the ash at her wedding | valhalla, sword, wanderer (17) |
| WK09 | winterstuerme.py | Winterstürme | the door swings open, moonlight and spring flood the room: the love song | spring_song (86), twins_love, bliss (38) |
| WK10 | nothung.py | Nothung! | she names him Siegmund; he draws the sword from the tree; they run into the night | nothung, sword, twins_love_b (37a) |
| WK11 | hojotoho.py | Hojotoho! | Act II prelude; Brünnhilde's war cry from the heights | ride (47), valkyries (22), valkyrie_cry (22a), brunnhilde (88) |
| WK12 | frickas_demand.py | Fricka's Demand | Fricka in her ram-drawn chariot: Siegmund must die | treaties (14), spear, wotan_frustrated (70) |
| WK13 | wotans_confession.py | Wotan's Confession | Wotan tells Brünnhilde everything: the Ring, Erda, the end of the gods | ring (8), curse (13), downfall (4), wotan_grief (82) |
| WK14 | the_order.py | The Order | Siegmund must fall; Brünnhilde must see to it | spear, wotan_grief, valkyries |
| WK15 | in_flight.py | In Flight | the lovers flee; Sieglinde collapses in terror and visions | twins_love, volsung_fate, Hunding's horns |
| WK16 | annunciation.py | The Annunciation of Death | Brünnhilde appears to Siegmund and tells him he must go to Valhalla | fate (84), fate_inevitable (85), valhalla |
| WK17 | brunnhilde_relents.py | Brünnhilde Relents | he would rather kill them both than leave her; moved, Brünnhilde promises victory | fate, twins_love, ride |
| WK18 | the_fight.py | The Fight | storm and horns; Siegmund and Hunding fight on the heights; Wotan's spear shatters Nothung | Hunding, nothung, spear |
| WK19 | siegmund_falls.py | Siegmund Falls | Siegmund dies; at Wotan's gesture Hunding falls; Brünnhilde flees with Sieglinde and the pieces | volsung_fate, spear, ride |
| WK20 | ride_of_the_valkyries.py | Ride of the Valkyries | the sisters arrive one by one through the storm clouds, bearing fallen heroes | ride, valkyrie_cry, valkyries_descent (22b) |
| WK21 | the_eight_sisters.py | The Eight Sisters | all eight together, the Ride at full strength across the whole house | ride, valkyries |
| WK22 | o_hehrstes_wunder.py | O hehrstes Wunder! | Brünnhilde arrives with Sieglinde; told she carries Siegfried, Sieglinde sings out | siegfried (53), redemption (90b), nothung |
| WK23 | wotans_wrath.py | Wotan's Wrath | Wotan arrives in a storm; the sisters hide Brünnhilde | storm, wotan_frustrated, valkyrie_cry |
| WK24 | the_sentence.py | The Sentence | she will lose her godhood and sleep on the rock for the first man who finds her | wotan_grief, sleep (16), valkyries_descent |
| WK25 | was_it_so_shameful.py | Was It So Shameful? | Brünnhilde pleads: she did what he truly wanted | brunnhilde_love (87), volsung_fate, devotion (80) |
| WK26 | a_wall_of_fire.py | A Wall of Fire | let only a hero pass: ring her sleep with fire | siegfried, loge (20), love_fulfilled (90) |
| WK27 | wotans_farewell.py | Wotan's Farewell | Leb wohl: Wotan holds her for the last time | wotan_grief, brunnhilde_love_b (87a), love_fulfilled_c (90c) |
| WK28 | the_kiss_of_sleep.py | The Kiss of Sleep | he kisses her godhood away; she sinks asleep on the summit | sleep, transformation (91), fate |
| WK29 | loge_come.py | Loge, Come! | three strikes of the spear on the rock; fire answers | spear, loge, loge_flicker (20a) |
| WK30 | magic_fire.py | Magic Fire | flames ring the rock and then the whole house; sleep and Siegfried over the fire | loge, sleep, siegfried, fate |

The last frame of each scene sets up the first of the next, so they can run back to back.
