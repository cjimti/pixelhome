# Siegfried on the roofline

Wagner's opera in 30 shows of 80 seconds, `SF01`..`SF30`, ten to an act, played in order. As with
[Das Rheingold](../das-rheingold/README.md) and [Die Walküre](../die-walkure/README.md), each quotes the real
leitmotifs note for note from `pixelhome/leitmotifs.py` and composes the rest around them; characters have
instruments and the lights follow their notes. The Commons examples for Siegfried's heroic deed (d65), Death
(d62) and Hunding (d60) are empty, and there is none for Brünnhilde's awakening, so "Heil dir, Sonne" is composed
(rising C major brass chords over harp arpeggios) and the deeds use `siegfried_heroism` (d78).

**Bold first.** This is one strand on a roofline seen from across the street: every scene is built from big
moves (whole-run colour changes, fast sweeps end to end, hard hits on the beat, sparks and bursts), saturated
colour on dark, and one clear subject at a time. Nothing that only reads up close.

## The stage

From the street the porch is the back of the scene.

- **Act I, Mime's cave in the forest.** The forge is the porch: Porch Front is the anvil, white-hot where the
  hammer lands, and Porch Left and Right are the chimney walls glowing with the fire. Left and Right are the cave
  mouth and the forest outside. Siegfried comes in from the free end of Right.
- **Act II, the forest outside Fafner's cave.** The porch is the cave mouth, black with two red eyes when the
  dragon wakes. Left, Right and Side are the forest: hard green with gold shafts of light moving through. The
  Woodbird is one hot magenta point that darts anywhere on the roofline.
- **Act III, the foot of Brünnhilde's rock, then the summit.** Erda rises out of the porch; the Wanderer stands
  across the path on Right. The fire is the Walküre's: it rings the porch exactly as `WK30` left it, and
  Siegfried goes through it to the summit (middle of Porch Front) where Brünnhilde sleeps. Her awakening turns
  the whole house from fire to sunrise.

Subjects never begin on Side (enter from the free end of Right, pop up on a front run, rise out of the porch).
Every run stays lit.

## Who is who

| character | colour | voice |
|-----------|--------|-------|
| Siegfried | electric emerald `#00ff40` with a white-hot head `#e8ffe8` | solo horn (his call, d48), horns |
| Nothung | white steel `#e8f8ff`, gold hilt `#ffcc40`; red-hot `#ff3000` while forged | trumpet |
| Mime | sulphur yellow `#e0c800`, cringing dim `#6a5a00` | bassoon, oboe, xylophone |
| the forge | orange `#ff4a08`, white heat `#fff0a0`, sparks `#ffb020` | anvils, timpani |
| the Wanderer (Wotan) | deep blue `#1a3cff`, spear `#c8d8ff` | trombones, tubas |
| Alberich | red `#ff1000` in a muddy halo `#5a1200` | bassoon, trombone, low strings |
| Fafner the dragon | ochre scales `#c88a20` over black, red eyes `#ff0000`, fire breath | tubas, contrabassoon, timpani |
| the forest | green `#18a020`, gold light `#ffd040` | strings (the Forest Murmurs) |
| the Woodbird | hot magenta `#ff30d0` | flute, oboe, piccolo |
| Erda | moss `#4a8a30` and earth `#3a2410` | low winds |
| Brünnhilde | silver white `#f4f8ff`, gold glints `#ffd060` | horns, violins |
| Loge's fire | `#ff5000` to `#ffb020`, red `#ff2000` | piccolo, violins, harp, glockenspiel |
| the sunrise | rose `#ff4080`, gold `#ffc020`, sky `#40a0ff` | full brass, harp |

## The 30 scenes

| code | file | title | what happens | motifs |
|------|------|-------|--------------|--------|
| SF01 | prelude.py | Prelude | darkness, the brooding over the hoard; the forge flares on the anvil in Mime's rhythm | mime (50), ring (8), forging (52) |
| SF02 | the_bear.py | The Bear | Siegfried storms in from Right driving a bear; Mime flees around the forge | siegfried_horn (48), siegfried_audacity (55) |
| SF03 | the_broken_sword.py | The Broken Sword | Siegfried snaps every sword Mime makes; sparks and shards fly | sword (45), mime_obstinate (51), mime_frustrated (71) |
| SF04 | starling_song.py | The Starling Song | Mime whines how he raised him; Siegfried demands his parents' names | mime_lament (72), siegmund (35), sieglinde (36) |
| SF05 | the_pieces.py | The Pieces of Nothung | Mime shows the shattered sword; Siegfried orders it mended and runs to the forest | nothung (43), siegfried_freedom (56) |
| SF06 | the_wanderer.py | The Wanderer | a stranger in a deep blue cloak comes in, spear in hand | wanderer (17), spear (73) |
| SF07 | three_riddles.py | Three Riddles | wager of heads: Nibelungs, giants, gods; then the question Mime cannot answer | wanderer, ring, giants (58), valhalla (63) |
| SF08 | fear.py | Fear | alone, Mime sees flickering fire everywhere; he tries to teach Siegfried fear | loge_flicker (20a), sleep (16), fafner (57) |
| SF09 | nothung_nothung.py | Nothung! Nothung! | Siegfried files the sword to dust and forges it himself; bellows, flame, red-hot steel | forging, nothung, siegfried_heroism (78) |
| SF10 | the_anvil_splits.py | The Anvil Splits | quenched with a hiss, hammered, and the anvil is cut in two | sword, nothung, siegfried_horn |
| SF11 | neidhohle.py | Neidhöhle | Act II prelude: night at the cave mouth; the dragon's motif crawls up from the bass | fafner, curse (13), ring |
| SF12 | alberichs_watch.py | Alberich's Watch | Alberich waits; a blue storm-light rushes in: the Wanderer again | wanderer, ring, curse |
| SF13 | waking_the_dragon.py | Waking the Dragon | they shout into the cave; the dragon answers and goes back to sleep | fafner, giants, spear |
| SF14 | dawn_in_the_forest.py | Dawn in the Forest | Mime brings Siegfried to the cave and slinks off; daylight breaks through the trees | mime, forest_murmurs (29), siegfried |
| SF15 | forest_murmurs.py | Forest Murmurs | Siegfried lies under the lime tree; the whole house is the forest, alive and moving | forest_murmurs, woodbird (27), innocent_delight (28) |
| SF16 | the_reed_pipe.py | The Reed Pipe | he cuts a reed to answer the bird and fails; he blows his horn instead | woodbird_call (27a), siegfried_horn |
| SF17 | fafner.py | Fafner | the horn wakes the dragon: the cave mouth splits open, red eyes, fire | fafner, giants_authority (59), siegfried_horn |
| SF18 | the_dragon_fight.py | The Dragon Fight | the fight across the whole house; Nothung through the heart | fafner, nothung, siegfried_heroism |
| SF19 | the_dragons_blood.py | The Dragon's Blood | Fafner dies; the hot blood on Siegfried's hand; he tastes it and understands the bird | giants, woodbird, curse |
| SF20 | the_ring_and_the_tarnhelm.py | The Ring and the Tarnhelm | the bird points him into the cave; Alberich and Mime fight over the spoils | ring, tarnhelm (18), mime_frustrated |
| SF21 | mime_poisons.py | The Poisoned Drink | Mime's sweet words, his murderous thoughts heard; Nothung strikes him down | mime, mime_lament, nothung |
| SF22 | the_woodbird_leads.py | The Woodbird Leads | a bride asleep on a rock ringed with fire; the bird flies ahead and he runs after | woodbird, siegfried_freedom, loge (20) |
| SF23 | erda_wakes.py | Erda Wakes | storm; the Wanderer calls Erda up from the earth | erda (3), gotternoth (5a), wanderer |
| SF24 | the_last_question.py | The Last Question | Erda has no answer; Wotan wills the end of the gods and gives the world to the hero | downfall (4), gotternoth, siegfried_heroism |
| SF25 | the_spear_breaks.py | The Spear Breaks | the Wanderer bars the way; Nothung shatters the spear that once broke it | spear, nothung, siegfried_horn |
| SF26 | through_the_fire.py | Through the Fire | Siegfried plunges into the fire; it surges over the house and he comes out on the summit | loge, siegfried_horn, siegfried |
| SF27 | das_ist_kein_mann.py | Das ist kein Mann! | he lifts the shield and helmet and finds a woman: at last he knows fear | sleep, fate (84), innocent_sleep (30) |
| SF28 | heil_dir_sonne.py | Heil dir, Sonne! | the kiss; she wakes and greets the sun: the whole house sunrise | composed awakening, brunnhilde (88), transformation (91) |
| SF29 | ewig_war_ich.py | Ewig war ich | her fear of losing herself; the peaceful theme | siegfried_love (89), brunnhilde_love (87) |
| SF30 | leuchtende_liebe.py | Leuchtende Liebe | the final duet, laughing at death: emerald and silver blaze across the whole house | siegfried, siegfried_love, love_fulfilled (90), siegfried_heroism |

The last frame of each scene sets up the first of the next, so they can run back to back.
