"""
DUNGEON ETERNAL v4.0  --  A Text-Based Turn-Based RPG
======================================================
NEW in v4:
  * Move Workshop GATED  -- only accessible after minibosses (story)
      and after every boss kill + level-up (infinite). Never mid-combat.
  * Random 3-Choice Workshop  -- each step (Effect/Delivery/Modifier)
      shows only 3 randomly sampled options. The dungeon decides what's
      available. Infinite mode draws from a far larger pool.
  * Infinite Mode Leveling  -- kill enemies to earn XP. Level up and
      choose a stat boost + get an immediate Workshop visit.
  * Enemy Scaling  -- infinite enemies scale with both cycle number AND
      player level, ensuring fights stay challenging as you grow.
  * Expanded Move Components  -- 20 Effects, 10 Deliveries, 17 Modifiers
      including Shatter, Berserk, Leech, Ignite, Void, Storm, Chaos,
      Soul Rend, Frostbite, Executioner, and more.

STAT SYSTEM
  STR  Strength     -> physical damage scaling
  VIT  Vitality     -> max HP  (base 60 + VIT*8)
  END  Endurance    -> damage reduction (END*0.6 flat)
  DEX  Dexterity    -> dodge% (DEX*1.2), acc% (85+DEX*0.5), crit% (DEX*0.8)
  INT  Intelligence -> magic damage scaling
  WIS  Wisdom       -> max mana (base 40 + WIS*6)
"""

import random
import os
import time

# ═══════════════════════════════════════════════════════════
#  TERMINAL UTILS
# ═══════════════════════════════════════════════════════════

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.022):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def pause(t=0.7):
    time.sleep(t)

def divider(char='=', width=66):
    print(char * width)

def header(title, width=66):
    divider('=', width)
    pad = max(0, (width - len(title) - 2) // 2)
    inner = ' ' * pad + title + ' ' * (width - 2 - pad - len(title))
    print('=' + inner + '=')
    divider('=', width)

def pick(prompt, options, allow_cancel=False):
    while True:
        print(f"\n  {prompt}")
        if allow_cancel:
            print("  [0] Cancel / Go back")
        for i, opt in enumerate(options, 1):
            print(f"  [{i}] {opt}")
        raw = input("  > ").strip()
        if allow_cancel and raw == '0':
            return -1
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        print("  !! Invalid choice.")

def hp_bar(cur, mx, w=18):
    f = int(w * max(cur, 0) / mx)
    return '#' * f + '.' * (w - f)

def mana_bar(cur, mx, w=18):
    f = int(w * max(cur, 0) / mx)
    return '*' * f + '.' * (w - f)

# ═══════════════════════════════════════════════════════════
#  STAT FORMULAS
# ═══════════════════════════════════════════════════════════

def calc_max_hp(vit):       return 60 + vit * 8
def calc_max_mana(wis):     return 40 + wis * 6
def calc_phys_dmg(s, lo=4, hi=10):  return s * 2 + random.randint(lo, hi)
def calc_magic_dmg(i, lo=5, hi=12): return int(i * 2.2) + random.randint(lo, hi)
def calc_dmg_red(end):      return end * 0.6
def calc_dodge(dex):        return min(dex * 1.2, 40.0)
def calc_acc(dex):          return min(85 + dex * 0.5, 99.0)
def calc_crit(dex):         return min(dex * 0.8, 35.0)
def roll_hit(acc):          return random.uniform(0, 100) <= acc
def roll_dodge(dex):        return random.uniform(0, 100) <= calc_dodge(dex)
def roll_crit(dex):         return random.uniform(0, 100) <= calc_crit(dex)
def apply_crit(d):          return int(d * 1.75)

# ═══════════════════════════════════════════════════════════
#  LOOT TABLES
# ═══════════════════════════════════════════════════════════

STAT_LOOT = [
    dict(name="Iron Longsword",        desc="+3 STR",   type="stat", stat="str", value=3),
    dict(name="War Axe",               desc="+5 STR",   type="stat", stat="str", value=5),
    dict(name="Berserker's Cleaver",   desc="+7 STR",   type="stat", stat="str", value=7),
    dict(name="Titan's Maul",          desc="+10 STR",  type="stat", stat="str", value=10),
    dict(name="Blood-Iron Gauntlets",  desc="+4 STR",   type="stat", stat="str", value=4),
    dict(name="Adventurer's Cloak",    desc="+3 VIT",   type="stat", stat="vit", value=3),
    dict(name="Life Amulet",           desc="+5 VIT",   type="stat", stat="vit", value=5),
    dict(name="Heartstone Pendant",    desc="+7 VIT",   type="stat", stat="vit", value=7),
    dict(name="Giant's Belt",          desc="+10 VIT",  type="stat", stat="vit", value=10),
    dict(name="Leather Vest",          desc="+3 END",   type="stat", stat="end", value=3),
    dict(name="Chain Mail",            desc="+5 END",   type="stat", stat="end", value=5),
    dict(name="Dragon Scale Plate",    desc="+7 END",   type="stat", stat="end", value=7),
    dict(name="Fortress Shield",       desc="+4 END",   type="stat", stat="end", value=4),
    dict(name="Stone Guard Helm",      desc="+6 END",   type="stat", stat="end", value=6),
    dict(name="Swift Boots",           desc="+3 DEX",   type="stat", stat="dex", value=3),
    dict(name="Shadowstep Gloves",     desc="+5 DEX",   type="stat", stat="dex", value=5),
    dict(name="Assassin's Band",       desc="+4 DEX",   type="stat", stat="dex", value=4),
    dict(name="Falcon Ring",           desc="+7 DEX",   type="stat", stat="dex", value=7),
    dict(name="Apprentice Tome",       desc="+3 INT",   type="stat", stat="int", value=3),
    dict(name="Spellweave Robe",       desc="+5 INT",   type="stat", stat="int", value=5),
    dict(name="Arcane Orb",            desc="+7 INT",   type="stat", stat="int", value=7),
    dict(name="Staff of Power",        desc="+6 INT",   type="stat", stat="int", value=6),
    dict(name="Eldritch Codex",        desc="+9 INT",   type="stat", stat="int", value=9),
    dict(name="Sage's Hood",           desc="+3 WIS",   type="stat", stat="wis", value=3),
    dict(name="Mana Crystal",          desc="+5 WIS",   type="stat", stat="wis", value=5),
    dict(name="Oracle's Mantle",       desc="+7 WIS",   type="stat", stat="wis", value=7),
    dict(name="Wellspring Talisman",   desc="+4 WIS",   type="stat", stat="wis", value=4),
]

CONSUMABLE_LOOT = [
    dict(name="Health Potion",         desc="Restore 40-60 HP",           type="consumable", cid="hp_potion",   qty=2),
    dict(name="Greater Health Flask",  desc="Restore 80-120 HP",          type="consumable", cid="hp_flask",    qty=1),
    dict(name="Mana Vial",             desc="Restore 30-50 Mana",         type="consumable", cid="mana_vial",   qty=2),
    dict(name="Elixir of Clarity",     desc="Restore 70-100 Mana",        type="consumable", cid="mana_elixir", qty=1),
    dict(name="Rage Brew",             desc="Next attack guaranteed crit", type="consumable", cid="rage_brew",   qty=1),
    dict(name="Iron Skin Salve",       desc="+8 END for 3 turns",         type="consumable", cid="iron_skin",   qty=1),
    dict(name="Ghost Pepper Extract",  desc="Hurl for 25-40 magic dmg",   type="consumable", cid="pepper",      qty=1),
    dict(name="Resurrection Shard",    desc="Auto-revive once at 1 HP",   type="consumable", cid="revive",      qty=1),
    dict(name="Scroll of Swiftness",   desc="+5 DEX for 1 fight",         type="consumable", cid="swift_scroll",qty=1),
    dict(name="Titan's Draft",         desc="+6 STR for 1 fight",         type="consumable", cid="titan_draft", qty=1),
]

ALL_LOOT = STAT_LOOT + CONSUMABLE_LOOT

def gen_loot(count=3, force_consumable=True):
    pool = []
    if force_consumable:
        pool.append(random.choice(CONSUMABLE_LOOT))
        pool += random.sample(STAT_LOOT, count - 1)
    else:
        pool = random.sample(ALL_LOOT, count)
    random.shuffle(pool)
    return pool[:count]

def treasure_cache(count=4):
    """Bigger loot pool for treasure rooms: more consumables possible."""
    n_cons = random.randint(1, 2)
    n_stat = count - n_cons
    pool = random.sample(CONSUMABLE_LOOT, min(n_cons, len(CONSUMABLE_LOOT)))
    pool += random.sample(STAT_LOOT, min(n_stat, len(STAT_LOOT)))
    random.shuffle(pool)
    return pool[:count]

# ═══════════════════════════════════════════════════════════
#  MOVE WORKSHOP  --  Component-Based Move Crafting
# ═══════════════════════════════════════════════════════════
#
#  A crafted move = Effect + Delivery + Modifier
#  The combination determines: damage formula, mana cost,
#  side effects (stun, heal, poison, shield, etc.)
#
#  EFFECTS  (what it does)
#  DELIVERIES (how it's delivered -- physical, magic, hybrid, drain...)
#  MODIFIERS  (extra twist -- crit focus, armor pierce, self-heal, AoE echo...)

EFFECTS = [
    # id, label, desc, mana_base
    ("strike",    "Strike",      "A focused damage hit",                        6),
    ("blast",     "Blast",       "Wide destructive burst",                      9),
    ("drain",     "Drain",       "Siphon damage into healing",                  10),
    ("venom",     "Venom",       "Apply poison (5 dmg/turn, 3 turns)",          8),
    ("ward",      "Ward",        "Raise a protective barrier",                  8),
    ("surge",     "Surge",       "Overcharge for massive damage; costs HP",     14),
    ("slow",      "Slow",        "Debuff enemy (-3 STR for 3 turns)",           9),
    ("mend",      "Mend",        "Heal yourself instead of attacking",          10),
    ("echo",      "Echo",        "Strike twice in succession",                  12),
    ("execute",   "Execute",     "Bonus damage below 30% enemy HP",             10),
    # Infinite-mode expanded effects
    ("shatter",   "Shatter",     "Break armor (enemy END -5, permanent)",       11),
    ("berserk",   "Berserk",     "Triple hit at 60% power each; risks 10 HP",  16),
    ("leech",     "Leech",       "Steal 30% enemy current HP as healing",       13),
    ("curse",     "Curse",       "Reduce all enemy stats by 2 for 4 turns",    12),
    ("barrier",   "Barrier",     "Shield equal to WIS*2+15; absorbs next hit", 9),
    ("ignite",    "Ignite",      "Heavy magic hit + burn 4/turn, 4 turns",     13),
    ("rend",      "Rend",        "Bleeding: enemy loses 8% max HP each turn",  11),
    ("overload",  "Overload",    "1.5x INT blast; halve your mana pool",       15),
    ("riposte",   "Riposte",     "Counter-stance: next enemy hit reflects 50%",10),
    ("devastate", "Devastate",   "Single massive blow: STR*4 flat bonus dmg",  17),
]

DELIVERIES = [
    # id, label, desc, dmg_type, mana_mod
    ("physical",  "Physical",   "Pure STR-based hit; reduced by armor",        "phys",   0),
    ("arcane",    "Arcane",     "Pure INT-based; ignores armor",               "magic",  2),
    ("hybrid",    "Hybrid",     "50% STR + 50% INT; halved armor reduction",   "hybrid", 1),
    ("shadow",    "Shadow",     "DEX-based; ignores ALL armor",                "dex",    1),
    ("holy",      "Holy",       "STR+INT blended; bonus vs debuffed enemies",  "holy",   2),
    ("wild",      "Wild",       "Random damage 0.5x to 2.5x; chaotic",        "wild",   -1),
    # Infinite-mode expanded deliveries
    ("void",      "Void",       "WIS-based; ignores armor; drains enemy mana", "void",   3),
    ("storm",     "Storm",      "DEX+INT combined; hits twice at 70% each",   "storm",  3),
    ("runic",     "Runic",      "STR+WIS blended; bonus per status on enemy", "runic",  2),
    ("chaos",     "Chaos",      "Random type each use: phys/magic/dex/holy",  "chaos",  -1),
]

MODIFIERS = [
    # id, label, desc, mana_mod, effect_key
    ("none",        "None",          "No modifier",                             0,  None),
    ("piercing",    "Piercing",      "Ignore 75% of enemy armor",              2,  "pierce"),
    ("vampiric",    "Vampiric",      "Heal 40% of damage dealt",               3,  "vamp"),
    ("stunning",    "Stunning",      "25% chance to stun enemy for 1 turn",    2,  "stun"),
    ("critstrike",  "Crit Strike",   "+15% extra crit chance",                 2,  "crit_up"),
    ("empowered",   "Empowered",     "Deal +30% damage; no extra cost",        3,  "empower"),
    ("volatile",    "Volatile",      "If it crits, also hit yourself for 8",   -1, "volatile"),
    ("echo_mod",    "Echo",          "If it kills, immediately recast free",   3,  "echo"),
    ("weakening",   "Weakening",     "On hit, reduce enemy END by 3",          2,  "weaken"),
    ("mana_burn",   "Mana Burn",     "Restore 8 mana on successful hit",       1,  "mana_burn"),
    # Infinite-mode expanded modifiers
    ("soulrend",    "Soul Rend",     "On hit, enemy loses 2 of all stats",     4,  "soulrend"),
    ("overcharge",  "Overcharge",    "Deal +50% dmg; cost +8 HP on use",       1,  "overcharge"),
    ("doubledown",  "Double Down",   "50% chance to deal double damage",        2,  "doubledown"),
    ("lifeline",    "Lifeline",      "Heal 20 HP flat after attack resolves",  3,  "lifeline"),
    ("executioner", "Executioner",   "Kills restore 40% of max HP",            4,  "executioner"),
    ("frostbite",   "Frostbite",     "Freeze enemy: -5 STR and -3 DEX, 2t",   3,  "frostbite"),
    ("relentless",  "Relentless",    "If enemy dodges, auto-recast at 70%",    2,  "relentless"),
]


def craft_move_fn(effect_id, delivery_id, modifier_id):
    """Return a function(player, enemy) -> str implementing the crafted move."""

    def fn(player, enemy):
        p, e = player, enemy
        msgs = []

        # ── Compute base damage ──────────────────────────────
        eff      = next(x for x in EFFECTS    if x[0] == effect_id)
        deliv    = next(x for x in DELIVERIES if x[0] == delivery_id)
        mod      = next(x for x in MODIFIERS  if x[0] == modifier_id)
        dmg_type = deliv[3]   # phys / magic / hybrid / dex / holy / wild

        # Effect multipliers
        eff_mults = {
            "strike":  1.0,
            "blast":   1.2,
            "drain":   0.85,
            "venom":   0.7,
            "ward":    0.0,
            "surge":   1.8,
            "slow":    0.8,
            "mend":    0.0,
            "echo":    0.75,
            "execute": 1.0,
        }
        emult = eff_mults.get(effect_id, 1.0)

        # Modifier multiplier
        mod_key = mod[4]
        extra_mult = 1.3 if mod_key == "empower" else 1.0
        if mod_key == "overcharge":
            extra_mult = 1.5

        raw = 0
        armor_red = calc_dmg_red(e.end)

        if dmg_type == "phys":
            raw = calc_phys_dmg(p.str, 4, 12)
            dmg = max(1, int(raw * emult * extra_mult - armor_red))
        elif dmg_type == "magic":
            raw = calc_magic_dmg(p.int, 5, 14)
            dmg = max(1, int(raw * emult * extra_mult))   # no armor
        elif dmg_type == "hybrid":
            raw = (calc_phys_dmg(p.str, 3, 9) + calc_magic_dmg(p.int, 3, 9)) // 2
            dmg = max(1, int(raw * emult * extra_mult - armor_red * 0.5))
        elif dmg_type == "dex":
            raw = p.dex * 2 + random.randint(4, 12)
            dmg = max(1, int(raw * emult * extra_mult))   # ignores armor
        elif dmg_type == "holy":
            raw = int((calc_phys_dmg(p.str, 2, 8) + calc_magic_dmg(p.int, 2, 8)) * 0.6)
            bonus = 1.2 if (e.atk_debuff > 0 or getattr(e, "_frost_turns", 0) > 0
                            or getattr(e, "_poison_turns", 0) > 0) else 1.0
            dmg = max(1, int(raw * emult * extra_mult * bonus - armor_red * 0.4))
        elif dmg_type == "wild":
            mult = random.uniform(0.5, 2.5)
            raw  = calc_phys_dmg(p.str, 2, 10)
            dmg  = max(1, int(raw * mult * emult))
        elif dmg_type == "void":
            raw = p.wis * 2 + random.randint(5, 14)
            dmg = max(1, int(raw * emult * extra_mult))   # ignores armor
        elif dmg_type == "storm":
            raw = p.dex + p.int + random.randint(4, 12)
            d1  = max(1, int(raw * 0.7 * emult * extra_mult))
            d2  = max(1, int(raw * 0.7 * emult * extra_mult))
            e.hp -= d1
            msgs.append(f"Storm hit 1: {d1}")
            dmg = d2
        elif dmg_type == "runic":
            raw = (calc_phys_dmg(p.str, 2, 8) + p.wis * 2 + random.randint(2, 8)) // 2
            status_count = sum([
                e.atk_debuff > 0,
                getattr(e, "_frost_turns", 0) > 0,
                getattr(e, "_poison_turns", 0) > 0,
                getattr(e, "_stunned", False),
            ])
            bonus = 1.0 + status_count * 0.15
            dmg = max(1, int(raw * emult * extra_mult * bonus - armor_red * 0.5))
        elif dmg_type == "chaos":
            rtype = random.choice(["phys", "magic", "dex", "holy"])
            if rtype == "phys":
                raw = calc_phys_dmg(p.str, 4, 12)
                dmg = max(1, int(raw * emult * extra_mult - armor_red))
            elif rtype == "magic":
                raw = calc_magic_dmg(p.int, 5, 14)
                dmg = max(1, int(raw * emult * extra_mult))
            elif rtype == "dex":
                raw = p.dex * 2 + random.randint(4, 12)
                dmg = max(1, int(raw * emult * extra_mult))
            else:
                raw = int((calc_phys_dmg(p.str, 2, 8) + calc_magic_dmg(p.int, 2, 8)) * 0.6)
                dmg = max(1, int(raw * emult * extra_mult - armor_red * 0.3))
            msgs.append(f"[Chaos:{rtype}]")
        else:
            raw = calc_phys_dmg(p.str); dmg = max(1, int(raw * emult))

        # Piercing modifier
        if mod_key == "pierce":
            dmg = max(1, int(raw * emult * extra_mult - armor_red * 0.25))

        # Crit check
        crit_bonus = 15 if mod_key == "crit_up" else 0
        did_crit = roll_crit(p.dex + crit_bonus // 2) or p.guaranteed_crit
        if did_crit:
            dmg = apply_crit(dmg)
            p.guaranteed_crit = False
            msgs.append("CRIT!")

        # ── Special effect overrides for Ward / Mend / Barrier / Riposte ──
        if effect_id == "ward":
            p._arcane_shield = True
            return "You erect a ward -- the next hit will be blocked entirely!"

        if effect_id == "barrier":
            shield_val = p.wis * 2 + 15
            p._arcane_shield = True
            p._barrier_val   = shield_val
            return f"Barrier raised! Absorbs up to {shield_val} damage from the next hit!"

        if effect_id == "riposte":
            p._riposte_ready = True
            return "Riposte stance! The next enemy attack will be reflected 50% back!"

        if effect_id == "mend":
            heal = p.wis * 2 + p.str + random.randint(10, 25)
            p.hp = min(p.max_hp, p.hp + heal)
            return f"You mend your wounds, restoring {heal} HP!"

        # ── Shatter: permanent armor break ────────────────────
        if effect_id == "shatter":
            e.end = max(0, e.end - 5)
            # also deal light phys hit
            red  = calc_dmg_red(e.end)
            dmg2 = max(1, int(calc_phys_dmg(p.str, 2, 8) * emult * extra_mult - red))
            e.hp -= dmg2
            return f"Shatter! {e.name}'s armor breaks (-5 END permanently)! {dmg2} damage."

        # ── Leech: steal % of current enemy HP ───────────────
        if effect_id == "leech":
            stolen = max(5, int(e.hp * 0.30))
            e.hp -= stolen
            p.hp  = min(p.max_hp, p.hp + stolen)
            return f"Leech! Steal {stolen} HP from {e.name}! (You now have {p.hp}/{p.max_hp})"

        # ── Curse: multi-stat debuff ──────────────────────────
        if effect_id == "curse":
            e.str = max(1, e.str - 2); e.dex = max(1, e.dex - 2)
            e.end = max(0, e.end - 2); e.int = max(0, e.int - 2)
            e.atk_debuff += 2; e._frost_turns = max(e._frost_turns, 4)
            return f"Curse! {e.name} loses 2 to all stats for 4 turns!"

        # ── Ignite: big magic + burn DoT ─────────────────────
        if effect_id == "ignite":
            fire_dmg = max(1, int(calc_magic_dmg(p.int, 8, 16) * emult * extra_mult))
            e.hp -= fire_dmg
            e._poison_stacks = getattr(e, "_poison_stacks", 0) + 4
            e._poison_turns  = max(getattr(e, "_poison_turns", 0), 4)
            return f"Ignite! {fire_dmg} magic damage + {e.name} BURNS (4/turn, 4 turns)!"

        # ── Rend: percentage bleed ────────────────────────────
        if effect_id == "rend":
            rend_dmg = max(1, int(calc_phys_dmg(p.str, 3, 9) * emult * extra_mult
                                   - calc_dmg_red(e.end)))
            e.hp -= rend_dmg
            bleed = max(3, int(e.max_hp * 0.08))
            e._poison_stacks = getattr(e, "_poison_stacks", 0) + bleed
            e._poison_turns  = max(getattr(e, "_poison_turns", 0), 3)
            return f"Rend! {rend_dmg} damage + {e.name} bleeds ({bleed}/turn, 3 turns)!"

        # ── Overload: massive INT dump ────────────────────────
        if effect_id == "overload":
            blast = max(1, int(calc_magic_dmg(p.int, 10, 20) * 1.5 * emult * extra_mult))
            e.hp -= blast
            p.mana = p.mana // 2
            return f"OVERLOAD! {blast} void damage! Your mana pool halves (now {p.mana})."

        # ── Devastate: massive flat STR bonus ────────────────
        if effect_id == "devastate":
            base = calc_phys_dmg(p.str, 6, 14) + p.str * 4
            dmg  = max(1, int(base * emult * extra_mult - calc_dmg_red(e.end)))
            if roll_crit(p.dex) or p.guaranteed_crit:
                dmg = apply_crit(dmg); p.guaranteed_crit = False
                msgs.append("CRIT!")
            e.hp -= dmg
            return f"DEVASTATE! {' '.join(msgs)}{dmg} crushing damage!"

        # ── Berserk: triple hit, self-cost ────────────────────
        if effect_id == "berserk":
            p.hp = max(1, p.hp - 10)
            red  = calc_dmg_red(e.end)
            total = 0; parts = []
            for _ in range(3):
                d = max(1, int(calc_phys_dmg(p.str, 2, 8) * 0.6 * emult * extra_mult - red))
                if roll_crit(p.dex): d = apply_crit(d); parts.append(f"{d}!")
                else: parts.append(str(d))
                e.hp -= d; total += d
            p.guaranteed_crit = False
            return f"BERSERK! {' + '.join(parts)} = {total} total! (cost 10 HP)"

        # ── Surge: pay HP ─────────────────────────────────────
        if effect_id == "surge":
            cost_hp = max(5, int(p.max_hp * 0.20))
            p.hp = max(1, p.hp - cost_hp)
            msgs.append(f"(cost {cost_hp} HP)")

        # ── Echo: double hit ──────────────────────────────────
        if effect_id == "echo":
            d2 = max(1, int(dmg * 0.75))
            e.hp -= d2
            msgs.append(f"Echo hit: {d2}")

        # ── Execute bonus ─────────────────────────────────────
        if effect_id == "execute" and e.hp <= e.max_hp * 0.30:
            exe_bonus = int(dmg * 0.6)
            dmg += exe_bonus
            msgs.append(f"EXECUTE! +{exe_bonus}")

        # ── Apply main damage ─────────────────────────────────
        e.hp -= dmg
        msgs.insert(0 if not msgs else len(msgs) - len([m for m in msgs if 'cost' in m or 'Echo' in m]),
                    f"{dmg} damage")

        # ── Post-hit modifiers ────────────────────────────────
        if mod_key == "vamp":
            heal = int(dmg * 0.40)
            p.hp = min(p.max_hp, p.hp + heal)
            msgs.append(f"healed {heal} HP (vampiric)")

        if mod_key == "stun" and random.random() < 0.25:
            e._stunned = True
            msgs.append(f"{e.name} is STUNNED!")

        if mod_key == "volatile" and did_crit:
            p.hp -= 8
            msgs.append("volatile backlash: -8 HP to you")

        if mod_key == "echo" and not e.is_alive():
            msgs.append("(kill echo -- free recast would trigger in combat)")

        if mod_key == "weaken":
            e.end = max(0, e.end - 3)
            msgs.append(f"{e.name}'s END reduced by 3")

        if mod_key == "mana_burn":
            p.mana = min(p.max_mana, p.mana + 8)
            msgs.append("+8 Mana returned")

        # ── New infinite-mode modifiers ───────────────────────
        if mod_key == "soulrend":
            e.str = max(1, e.str - 2); e.dex = max(1, e.dex - 2)
            e.end = max(0, e.end - 2); e.int = max(0, e.int - 2)
            msgs.append(f"{e.name} loses 2 to all stats (Soul Rend)!")

        if mod_key == "overcharge":
            p.hp = max(1, p.hp - 8)
            msgs.append("(Overcharge: -8 HP to you)")

        if mod_key == "doubledown" and random.random() < 0.50:
            e.hp -= dmg
            msgs.append(f"Double Down! Extra {dmg} dmg!")

        if mod_key == "lifeline":
            p.hp = min(p.max_hp, p.hp + 20)
            msgs.append("+20 HP (Lifeline)")

        if mod_key == "executioner" and not e.is_alive():
            heal = int(p.max_hp * 0.40)
            p.hp = min(p.max_hp, p.hp + heal)
            msgs.append(f"Executioner: kill! +{heal} HP!")

        if mod_key == "frostbite":
            e.atk_debuff = getattr(e, "atk_debuff", 0) + 5
            e.dex        = max(1, e.dex - 3)
            e._frost_turns = max(getattr(e, "_frost_turns", 0), 2)
            msgs.append(f"{e.name} FROSTBITTEN (-5 STR, -3 DEX, 2 turns)!")

        # ── Venom effect ─────────────────────────────────────
        if effect_id == "venom":
            e._poison_stacks = getattr(e, "_poison_stacks", 0) + 5
            e._poison_turns  = max(getattr(e, "_poison_turns", 0), 3)
            msgs.append(f"{e.name} poisoned (5/turn, 3 turns)")

        # ── Slow effect ───────────────────────────────────────
        if effect_id == "slow":
            e.atk_debuff = getattr(e, "atk_debuff", 0) + 3
            e._frost_turns = max(getattr(e, "_frost_turns", 0), 3)
            msgs.append(f"{e.name} slowed (-3 STR, 3 turns)")

        return "  ".join(msgs)

    return fn


def build_crafted_move(name, effect_id, delivery_id, modifier_id):
    eff   = next(x for x in EFFECTS    if x[0] == effect_id)
    deliv = next(x for x in DELIVERIES if x[0] == delivery_id)
    mod   = next(x for x in MODIFIERS  if x[0] == modifier_id)

    base_cost = eff[3] + deliv[4] + mod[3]
    mana_cost = max(4, base_cost)

    desc = f"{eff[1]} / {deliv[1]}"
    if mod[0] != "none":
        desc += f" / {mod[1]}"
    desc += f"  [{mana_cost} MP]"

    fn = craft_move_fn(effect_id, delivery_id, modifier_id)
    return Move(name, mana_cost, desc, fn, crafted=True)


def move_workshop_screen(player, infinite_mode=False):
    """Full interactive move workshop with random 3 choices per step."""
    clear()
    header("MOVE WORKSHOP")
    if infinite_mode:
        slow_print("\n  The Workshop trembles with deep-dungeon power.")
        slow_print("  Three random options appear at each step -- the dungeon decides what's possible.")
    else:
        slow_print("\n  Craft a custom ability. Three choices appear at each step -- choose wisely.")
    slow_print("  Effect + Delivery + Modifier = your new move. Name it anything.\n")

    # Determine pools based on mode
    eff_pool = EFFECTS if infinite_mode else EFFECTS[:10]   # story: base 10; infinite: all 20
    del_pool = DELIVERIES if infinite_mode else DELIVERIES[:6]
    mod_pool = MODIFIERS if infinite_mode else MODIFIERS[:10]

    # Step 1: Effect -- random 3
    sampled_effs = random.sample(eff_pool, min(3, len(eff_pool)))
    eff_opts = [f"{e[1]:<14} -- {e[2]}" for e in sampled_effs]
    eff_idx  = pick("Step 1 -- Choose an EFFECT (3 random options):", eff_opts, allow_cancel=True)
    if eff_idx == -1:
        slow_print("  Cancelled."); pause(0.8); return

    # Step 2: Delivery -- random 3
    sampled_dels = random.sample(del_pool, min(3, len(del_pool)))
    del_opts = [f"{d[1]:<14} -- {d[2]}" for d in sampled_dels]
    del_idx  = pick("Step 2 -- Choose a DELIVERY (3 random options):", del_opts, allow_cancel=True)
    if del_idx == -1:
        slow_print("  Cancelled."); pause(0.8); return

    # Step 3: Modifier -- random 3
    sampled_mods = random.sample(mod_pool, min(3, len(mod_pool)))
    mod_opts = [f"{m[1]:<16} -- {m[2]}" for m in sampled_mods]
    mod_idx  = pick("Step 3 -- Choose a MODIFIER (3 random options):", mod_opts, allow_cancel=True)
    if mod_idx == -1:
        slow_print("  Cancelled."); pause(0.8); return

    eff_id = sampled_effs[eff_idx][0]
    del_id = sampled_dels[del_idx][0]
    mod_id = sampled_mods[mod_idx][0]

    # Preview
    eff   = sampled_effs[eff_idx]
    deliv = sampled_dels[del_idx]
    mod   = sampled_mods[mod_idx]
    base_cost = eff[3] + deliv[4] + mod[3]
    mana_cost = max(4, base_cost)

    clear()
    header("MOVE WORKSHOP -- PREVIEW")
    print(f"\n  Effect   : {eff[1]:<14}  -- {eff[2]}")
    print(f"  Delivery : {deliv[1]:<14}  -- {deliv[2]}")
    print(f"  Modifier : {mod[1]:<14}  -- {mod[2]}")
    print(f"\n  Mana Cost: {mana_cost}")
    print()

    name = input("  Name this move (or press Enter for auto-name): ").strip()
    if not name:
        name = f"{eff[1]} {deliv[1]}"
        if mod_id != "none":
            name += f" [{mod[1]}]"

    new_move = build_crafted_move(name, eff_id, del_id, mod_id)

    # Step 4: Choose slot to replace
    print(f"\n  '{name}' is ready. Choose which slot to replace (or cancel):\n")
    slot_opts = []
    for i, mv in enumerate(player.moves):
        tag = " [crafted]" if getattr(mv, "crafted", False) else ""
        slot_opts.append(f"Slot {i+1}: {mv.name}  [{mv.mana_cost} MP]{tag}  -- {mv.desc}")
    slot_idx = pick("Replace slot:", slot_opts, allow_cancel=True)
    if slot_idx == -1:
        slow_print("  Cancelled -- move not equipped."); pause(0.8); return

    old_name = player.moves[slot_idx].name
    player.moves[slot_idx] = new_move
    slow_print(f"\n  '{old_name}' replaced with '{name}'!")
    pause(1.0)


# ═══════════════════════════════════════════════════════════
#  MOVE CLASS
# ═══════════════════════════════════════════════════════════

class Move:
    def __init__(self, name, mana_cost, desc, fn, crafted=False):
        self.name      = name
        self.mana_cost = mana_cost
        self.desc      = desc
        self.fn        = fn
        self.crafted   = crafted

    def execute(self, player, enemy):
        if player.mana < self.mana_cost:
            return None
        player.mana = max(0, player.mana - self.mana_cost)
        return self.fn(player, enemy)

# ═══════════════════════════════════════════════════════════
#  PLAYER
# ═══════════════════════════════════════════════════════════

class Player:
    def __init__(self, name, cls):
        self.name = name
        self.cls  = cls

        base = {
            "Barbarian": (12, 10,  8,  5,  2,  3),
            "Wizard":    ( 3,  6,  4,  7, 14,  9),
            "Paladin":   ( 7, 10,  9,  5,  5,  7),
            "Rogue":     ( 8,  7,  5, 13,  4,  5),
        }[cls]
        self.str, self.vit, self.end, self.dex, self.int, self.wis = base

        self._refresh_derived()
        self.hp   = self.max_hp
        self.mana = self.max_mana

        # Status effects
        self.iron_skin_turns  = 0
        self.iron_skin_bonus  = 0
        self.guaranteed_crit  = False
        self.revive_shard     = False
        self._arcane_shield   = False
        self._smoke_dodge     = False
        self._poison_stacks   = 0
        self._poison_turns    = 0
        self._swift_turns     = 0   # temp DEX buff
        self._swift_bonus     = 0
        self._titan_turns     = 0   # temp STR buff
        self._titan_bonus     = 0

        self.inventory   = {}
        self.total_kills = 0
        self.cycle       = 1
        self.rooms_done  = 0

        # Infinite-mode leveling
        self.level       = 1
        self.xp          = 0
        self.xp_to_next  = 100   # base XP needed to level up

        self.moves = self._build_moves()  # always exactly 4 slots

    def _refresh_derived(self):
        self.max_hp   = calc_max_hp(self.vit)
        self.max_mana = calc_max_mana(self.wis)

    def gain_xp(self, amount):
        """Add XP and return True if level-up occurred."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            return True
        return False

    def level_up(self):
        """Perform a level-up: increment level, reset XP, grow thresholds."""
        self.xp        -= self.xp_to_next
        self.level      += 1
        self.xp_to_next  = int(self.xp_to_next * 1.35)  # escalating XP curve

    @property
    def effective_end(self):
        bonus = self.iron_skin_bonus if self.iron_skin_turns > 0 else 0
        return self.end + bonus

    @property
    def effective_dex(self):
        bonus = self._swift_bonus if self._swift_turns > 0 else 0
        return self.dex + bonus

    @property
    def effective_str(self):
        bonus = self._titan_bonus if self._titan_turns > 0 else 0
        return self.str + bonus

    # ── Inventory ────────────────────────────────────────

    def add_consumable(self, cid, qty):
        self.inventory[cid] = self.inventory.get(cid, 0) + qty

    def has_consumable(self, cid):
        return self.inventory.get(cid, 0) > 0

    def use_consumable(self, cid, enemy=None):
        if not self.has_consumable(cid):
            return "You don't have that."
        self.inventory[cid] -= 1
        if self.inventory[cid] <= 0:
            del self.inventory[cid]

        if cid == "hp_potion":
            h = random.randint(40, 60); self.hp = min(self.max_hp, self.hp + h)
            return f"Health Potion: restored {h} HP!"
        if cid == "hp_flask":
            h = random.randint(80, 120); self.hp = min(self.max_hp, self.hp + h)
            return f"Greater Flask: restored {h} HP!"
        if cid == "mana_vial":
            r = random.randint(30, 50); self.mana = min(self.max_mana, self.mana + r)
            return f"Mana Vial: restored {r} Mana!"
        if cid == "mana_elixir":
            r = random.randint(70, 100); self.mana = min(self.max_mana, self.mana + r)
            return f"Elixir of Clarity: restored {r} Mana!"
        if cid == "rage_brew":
            self.guaranteed_crit = True
            return "Rage Brew: next attack GUARANTEED to crit!"
        if cid == "iron_skin":
            self.iron_skin_turns = 3; self.iron_skin_bonus = 8
            return "Iron Skin Salve: +8 END for 3 turns!"
        if cid == "pepper":
            if enemy:
                d = random.randint(25, 40); enemy.hp -= d
                return f"Ghost Pepper Extract: {d} magic damage to {enemy.name}!"
            return "Nothing to throw it at."
        if cid == "revive":
            self.revive_shard = True
            return "Resurrection Shard: you will revive once at 1 HP!"
        if cid == "swift_scroll":
            self._swift_turns = 99; self._swift_bonus = 5   # lasts whole fight
            return "Scroll of Swiftness: +5 DEX for this fight!"
        if cid == "titan_draft":
            self._titan_turns = 99; self._titan_bonus = 6
            return "Titan's Draft: +6 STR for this fight!"
        return "Item used."

    def apply_loot(self, loot):
        if loot["type"] == "stat":
            s, v = loot["stat"], loot["value"]
            if s == "str": self.str += v
            elif s == "vit":
                old = self.max_hp; self.vit += v; self._refresh_derived()
                self.hp = min(self.hp + (self.max_hp - old), self.max_hp)
            elif s == "end": self.end += v
            elif s == "dex": self.dex += v
            elif s == "int": self.int += v
            elif s == "wis":
                old = self.max_mana; self.wis += v; self._refresh_derived()
                self.mana = min(self.mana + (self.max_mana - old), self.max_mana)
        elif loot["type"] == "consumable":
            self.add_consumable(loot["cid"], loot["qty"])

    # ── Status tick ──────────────────────────────────────

    def tick_status(self):
        if self.iron_skin_turns > 0:
            self.iron_skin_turns -= 1
            if self.iron_skin_turns == 0: self.iron_skin_bonus = 0
        if self._swift_turns > 0:
            self._swift_turns -= 1
            if self._swift_turns == 0: self._swift_bonus = 0
        if self._titan_turns > 0:
            self._titan_turns -= 1
            if self._titan_turns == 0: self._titan_bonus = 0
        if self._poison_turns > 0:
            dmg = self._poison_stacks; self.hp -= dmg
            self._poison_turns -= 1
            print(f"  Venom eats at you: {dmg} poison damage! ({self._poison_turns} turns left)")
            if self._poison_turns == 0: self._poison_stacks = 0

    def end_fight_cleanup(self):
        """Reset per-fight temp buffs."""
        self._swift_turns = 0; self._swift_bonus = 0
        self._titan_turns = 0; self._titan_bonus = 0

    # ── Class move builders ──────────────────────────────

    def _build_moves(self):
        c = self.cls
        if c == "Barbarian":
            return [
                Move("Cleave",        8,  "STR heavy hit; 10% double-swing",            self._barb_cleave),
                Move("War Cry",       12, "Gain +4 STR perm; enemy loses turn",          self._barb_warcry),
                Move("Reckless Slam", 14, "Massive STR hit (half armor); 5 self-dmg",    self._barb_slam),
                Move("Blood Frenzy",  20, "3 rapid STR hits; heal 50% of dmg dealt",     self._barb_frenzy),
            ]
        if c == "Wizard":
            return [
                Move("Arcane Bolt",   8,  "INT magic; ignores armor",                    self._wiz_bolt),
                Move("Frost Nova",    14, "INT dmg + freeze (-4 STR, 2 turns)",          self._wiz_frost),
                Move("Mana Surge",    18, "2x INT dmg; costs 30% max HP",               self._wiz_surge),
                Move("Arcane Shield", 10, "Block next hit; +20 Mana on block",           self._wiz_shield),
            ]
        if c == "Paladin":
            return [
                Move("Holy Strike",   8,  "STR+INT blended; heal 8-14 HP",              self._pal_holy),
                Move("Shield Bash",   10, "STR dmg; stun enemy 1 turn",                 self._pal_bash),
                Move("Divine Light",  16, "No dmg; heal WIS*3+20 HP",                   self._pal_heal),
                Move("Consecrate",    22, "(STR+INT)*1.6 holy blast; costs 8 HP",        self._pal_consecrate),
            ]
        if c == "Rogue":
            return [
                Move("Shadowstrike",  8,  "DEX-scaled; ignores all armor; high crit",    self._rog_shadow),
                Move("Poison Blade",  10, "DEX hit + 6 poison/turn, 3 turns",            self._rog_poison),
                Move("Smoke Bomb",    12, "Guarantee next dodge; light DEX hit",          self._rog_smoke),
                Move("Death Mark",    24, "3 DEX hits; instant kill if <25% HP",          self._rog_deathmark),
            ]
        return []

    # ── Barbarian ────────────────────────────────────────

    def _barb_cleave(self, p, e):
        red = calc_dmg_red(e.end)
        dmg = max(1, int(calc_phys_dmg(p.effective_str, 6, 14) - red))
        if roll_crit(p.effective_dex) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            msg = f"CRIT! Cleave tears {e.name} for {dmg} damage!"
        else:
            msg = f"Cleave strikes {e.name} for {dmg} damage!"
        e.hp -= dmg
        if random.random() < 0.10:
            d2 = max(1, int(calc_phys_dmg(p.effective_str, 3, 8) - red))
            e.hp -= d2; msg += f"  Double swing! +{d2} more!"
        return msg

    def _barb_warcry(self, p, e):
        p.str += 4; e._stunned = True
        return f"WAR CRY! +4 STR permanently. {e.name} recoils -- loses its turn!"

    def _barb_slam(self, p, e):
        half_red = calc_dmg_red(e.end) * 0.5
        dmg = max(1, int(calc_phys_dmg(p.effective_str, 10, 20) - half_red))
        if roll_crit(p.effective_dex) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            msg = f"CRIT! Reckless Slam CRUSHES {e.name} for {dmg}!"
        else:
            msg = f"Reckless Slam CRUSHES {e.name} for {dmg}!"
        e.hp -= dmg; p.hp -= 5
        return msg + "  Recoil: -5 HP to you."

    def _barb_frenzy(self, p, e):
        red = calc_dmg_red(e.end); total = 0; hits = []
        for _ in range(3):
            d = max(1, int(calc_phys_dmg(p.effective_str, 2, 8) - red))
            if roll_crit(p.effective_dex): d = apply_crit(d); hits.append(f"{d}!")
            else: hits.append(str(d))
            e.hp -= d; total += d
        heal = total // 2; p.hp = min(p.max_hp, p.hp + heal)
        p.guaranteed_crit = False
        return f"Blood Frenzy! {' + '.join(hits)} = {total} dmg. Healed {heal} HP!"

    # ── Wizard ───────────────────────────────────────────

    def _wiz_bolt(self, p, e):
        dmg = calc_magic_dmg(p.int, 6, 14)
        if roll_crit(p.effective_dex) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            return f"CRIT! Arcane Bolt DETONATES on {e.name} for {dmg} magic dmg!"
        e.hp -= dmg
        return f"Arcane Bolt slams {e.name} for {dmg} magic dmg (armor ignored)!"

    def _wiz_frost(self, p, e):
        dmg = calc_magic_dmg(p.int, 4, 10); e.hp -= dmg
        e.atk_debuff = getattr(e, "atk_debuff", 0) + 4; e._frost_turns = 2
        return f"Frost Nova! {dmg} magic dmg. {e.name} slowed (-4 STR, 2 turns)!"

    def _wiz_surge(self, p, e):
        cost = max(5, int(p.max_hp * 0.30)); p.hp = max(1, p.hp - cost)
        dmg = calc_magic_dmg(p.int, 8, 16) * 2
        if roll_crit(p.effective_dex) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            msg = f"CRIT! Mana Surge OBLITERATES {e.name} for {dmg} magic dmg!"
        else:
            msg = f"Mana Surge! {dmg} magic dmg. (Cost {cost} HP)"
        e.hp -= dmg; return msg

    def _wiz_shield(self, p, e):
        p._arcane_shield = True
        return "Arcane Shield raised! Next hit absorbed. +20 Mana on block."

    # ── Paladin ──────────────────────────────────────────

    def _pal_holy(self, p, e):
        red = calc_dmg_red(e.end) * 0.5
        dmg = max(1, int((calc_phys_dmg(p.effective_str, 3, 8)
                          + calc_magic_dmg(p.int, 2, 6)) * 0.6 - red))
        if roll_crit(p.effective_dex) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            msg = f"CRIT! Holy Strike burns {e.name} for {dmg} divine dmg!"
        else:
            msg = f"Holy Strike smites {e.name} for {dmg} divine dmg!"
        e.hp -= dmg; heal = random.randint(8, 14)
        p.hp = min(p.max_hp, p.hp + heal)
        return msg + f"  You heal {heal} HP."

    def _pal_bash(self, p, e):
        dmg = max(1, int(calc_phys_dmg(p.effective_str, 4, 10) - calc_dmg_red(e.end)))
        e.hp -= dmg; e._stunned = True
        return f"Shield Bash! {dmg} dmg. {e.name} STUNNED (loses next turn)!"

    def _pal_heal(self, p, e):
        heal = p.wis * 3 + 20 + random.randint(0, 15)
        p.hp = min(p.max_hp, p.hp + heal)
        return f"Divine Light! You restore {heal} HP!"

    def _pal_consecrate(self, p, e):
        p.hp = max(1, p.hp - 8)
        raw = calc_phys_dmg(p.effective_str, 5, 12) + calc_magic_dmg(p.int, 5, 12)
        dmg = max(1, int(raw * 1.6 - calc_dmg_red(e.end) * 0.4))
        if roll_crit(p.effective_dex) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            msg = f"CRIT! Consecrate ANNIHILATES {e.name} for {dmg} holy dmg!"
        else:
            msg = f"Consecrate BLASTS {e.name} for {dmg} holy dmg! (cost 8 HP)"
        e.hp -= dmg; return msg

    # ── Rogue ────────────────────────────────────────────

    def _rog_shadow(self, p, e):
        dmg = p.effective_dex * 2 + random.randint(5, 14)
        if roll_crit(p.effective_dex + 5) or p.guaranteed_crit:
            dmg = apply_crit(dmg); p.guaranteed_crit = False
            msg = f"CRIT! Shadowstrike finds the gap: {dmg} (armor ignored)!"
        else:
            msg = f"Shadowstrike slips through for {dmg} (armor ignored)!"
        e.hp -= dmg; return msg

    def _rog_poison(self, p, e):
        instant = max(1, p.effective_dex + random.randint(2, 8)); e.hp -= instant
        e._poison_stacks = getattr(e, "_poison_stacks", 0) + 6
        e._poison_turns  = 3
        return f"Poison Blade! {instant} instant + {e.name} poisoned (6/turn, 3 turns)!"

    def _rog_smoke(self, p, e):
        p._smoke_dodge = True
        light = max(1, p.effective_dex // 2 + random.randint(1, 6)); e.hp -= light
        return f"Smoke Bomb! {light} light hit. You WILL dodge the next attack!"

    def _rog_deathmark(self, p, e):
        total = 0; hits = []
        for _ in range(3):
            d = p.effective_dex * 2 + random.randint(2, 10)
            if roll_crit(p.effective_dex): d = apply_crit(d); hits.append(f"{d}!")
            else: hits.append(str(d))
            e.hp -= d; total += d
        p.guaranteed_crit = False
        msg = f"Death Mark! {' + '.join(hits)} = {total} dmg!"
        if e.hp <= e.max_hp * 0.25 and e.is_alive():
            e.hp = 0; msg += f"  {e.name} marked for death -- INSTANTLY SLAIN!"
        return msg

    # ── Display ──────────────────────────────────────────

    def status(self):
        hb = hp_bar(self.hp, self.max_hp)
        mb = mana_bar(self.mana, self.max_mana)
        print(f"  {self.name} [{self.cls}]  Lv.{self.level}")
        print(f"  HP:   [{hb}] {max(self.hp,0):>4}/{self.max_hp}")
        print(f"  Mana: [{mb}] {self.mana:>4}/{self.max_mana}")
        print(f"  STR:{self.effective_str:>2}  VIT:{self.vit:>2}  END:{self.effective_end:>2}"
              f"  DEX:{self.effective_dex:>2}  INT:{self.int:>2}  WIS:{self.wis:>2}")
        if self.level > 1 or self.xp > 0:
            xb = hp_bar(self.xp, self.xp_to_next, 14)
            print(f"  XP:   [{xb}] {self.xp:>3}/{self.xp_to_next}")
        fx = []
        if self.iron_skin_turns > 0:  fx.append(f"IronSkin({self.iron_skin_turns}t)")
        if self._swift_turns    > 0:  fx.append(f"Swift+{self._swift_bonus}DEX")
        if self._titan_turns    > 0:  fx.append(f"Titan+{self._titan_bonus}STR")
        if self.guaranteed_crit:      fx.append("NextCrit!")
        if self._arcane_shield:       fx.append("ArcaneShield")
        if self._smoke_dodge:         fx.append("Evasion!")
        if self.revive_shard:         fx.append("Revive")
        if fx: print(f"  FX: {', '.join(fx)}")
        if self.inventory:
            inv = "  Bag: " + "  ".join(
                f"{k.replace('_',' ').title()}x{v}" for k, v in self.inventory.items())
            print(inv)

    def stat_sheet(self):
        print(f"\n  +-- {self.name} the {self.cls}  [Level {self.level}] " + "-" * 26)
        print(f"  |  HP {self.hp}/{self.max_hp}    Mana {self.mana}/{self.max_mana}")
        print(f"  |  XP {self.xp}/{self.xp_to_next}  (next level)")
        print(f"  |  STR {self.str:>2}  VIT {self.vit:>2}  END {self.end:>2}")
        print(f"  |  DEX {self.dex:>2}  INT {self.int:>2}  WIS {self.wis:>2}")
        print(f"  |  Dodge {calc_dodge(self.dex):.1f}%  "
              f"Acc {calc_acc(self.dex):.1f}%  "
              f"Crit {calc_crit(self.dex):.1f}%")
        print(f"  |  Dmg Reduction: {calc_dmg_red(self.effective_end):.1f}")
        print(f"  |  Abilities:")
        for i, mv in enumerate(self.moves):
            tag = " [crafted]" if getattr(mv, "crafted", False) else ""
            print(f"  |    [{i+1}] {mv.name}  [{mv.mana_cost} MP]{tag}")
        if self.inventory:
            print(f"  |  Inventory:")
            for cid, qty in self.inventory.items():
                print(f"  |    {cid.replace('_',' ').title()} x{qty}")
        print(f"  +" + "-" * 45)


# ═══════════════════════════════════════════════════════════
#  ENEMY
# ═══════════════════════════════════════════════════════════

class Enemy:
    def __init__(self, name, str_, vit, end_, dex, int_, flavor, abilities=None, scale=1.0):
        self.name    = name
        self.flavor  = flavor
        self.str     = max(1, int(str_  * scale))
        self.vit     = max(1, int(vit   * scale))
        self.end     = max(0, int(end_  * scale))
        self.dex     = max(1, int(dex   * scale))
        self.int     = max(0, int(int_  * scale))
        self.max_hp  = calc_max_hp(self.vit)
        self.hp      = self.max_hp
        self.abilities = abilities or []

        self.atk_debuff    = 0
        self._frost_turns  = 0
        self._stunned      = False
        self._poison_stacks= 0
        self._poison_turns = 0

    @property
    def effective_str(self):
        return max(1, self.str - self.atk_debuff)

    def is_alive(self): return self.hp > 0

    def tick_effects(self):
        msgs = []
        if self._frost_turns > 0:
            self._frost_turns -= 1
            if self._frost_turns == 0:
                self.atk_debuff = max(0, self.atk_debuff - 4)
                msgs.append(f"  {self.name}'s slow wears off.")
        if self._poison_turns > 0:
            dmg = self._poison_stacks; self.hp -= dmg; self._poison_turns -= 1
            msgs.append(f"  Poison burns {self.name} for {dmg}! ({self._poison_turns} ticks left)")
            if self._poison_turns == 0: self._poison_stacks = 0
        return msgs

    def act(self, player):
        if self._stunned:
            self._stunned = False
            return 0, f"{self.name} is stunned -- loses its turn!"

        if self.abilities and random.random() < 0.35:
            ab = random.choice(self.abilities)
            return ab(self, player)

        if not roll_hit(calc_acc(self.dex)):
            return 0, f"{self.name} swings wildly and misses!"

        if getattr(player, "_smoke_dodge", False):
            player._smoke_dodge = False
            return 0, f"{self.name} attacks but you vanish in smoke -- DODGED!"

        if roll_dodge(player.effective_dex):
            return 0, f"{self.name} attacks but you dodge out of the way!"

        if getattr(player, "_arcane_shield", False):
            player._arcane_shield = False
            player.mana = min(player.max_mana, player.mana + 20)
            return 0, f"{self.name} attacks but Arcane Shield absorbs it! (+20 Mana)"

        dmg = max(1, int(calc_phys_dmg(self.effective_str, 2, 8)
                         - calc_dmg_red(player.effective_end)))

        if roll_crit(self.dex):
            dmg = apply_crit(dmg)
            msg = f"CRIT! {self.name} lands a vicious blow for {dmg} damage!"
        else:
            msg = f"{self.name} strikes for {dmg} damage!"

        player.hp -= dmg
        return dmg, msg

    def status(self):
        hb = hp_bar(self.hp, self.max_hp)
        fx = []
        if self.atk_debuff > 0:    fx.append(f"Slow(-{self.atk_debuff}STR)")
        if self._poison_turns > 0: fx.append(f"Poison({self._poison_turns}t)")
        if self._stunned:          fx.append("Stunned!")
        suf = f"  [{', '.join(fx)}]" if fx else ""
        print(f"  {self.name}  HP: [{hb}] {max(self.hp,0):>4}/{self.max_hp}{suf}")


# ═══════════════════════════════════════════════════════════
#  ENEMY ABILITIES
# ═══════════════════════════════════════════════════════════

def _check_block(p, e, block_msg):
    if getattr(p, "_arcane_shield", False):
        p._arcane_shield = False; p.mana = min(p.max_mana, p.mana + 20)
        return True, block_msg + " (+20 Mana)"
    if getattr(p, "_smoke_dodge", False):
        p._smoke_dodge = False
        return True, "You dodge in the smoke -- DODGED!"
    return False, ""

def eab_double_strike(e, p):
    blocked, bm = _check_block(p, e, f"{e.name} double-strikes but blocked")
    if blocked: return 0, bm
    red = calc_dmg_red(p.effective_end)
    d1 = max(1, int(calc_phys_dmg(e.effective_str, 1, 6) - red))
    d2 = max(1, int(calc_phys_dmg(e.effective_str, 1, 6) - red))
    p.hp -= d1 + d2
    return d1+d2, f"{e.name} strikes TWICE -- {d1} + {d2} = {d1+d2} damage!"

def eab_poison_fang(e, p):
    dmg = max(1, int(calc_phys_dmg(e.effective_str, 1, 5)
                     - calc_dmg_red(p.effective_end)))
    p.hp -= dmg
    p._poison_stacks = getattr(p, "_poison_stacks", 0) + 5
    p._poison_turns  = max(getattr(p, "_poison_turns", 0), 3)
    return dmg, f"{e.name} bites for {dmg} and POISONS you (5/turn, 3 turns)!"

def eab_shield_bash(e, p):
    blocked, bm = _check_block(p, e, f"{e.name} bashes but blocked")
    if blocked: return 0, bm
    dmg = max(1, int(calc_phys_dmg(e.effective_str, 4, 10)
                     - calc_dmg_red(p.effective_end) * 0.5))
    p.hp -= dmg
    return dmg, f"{e.name} SHIELD BASHES through your guard for {dmg} damage!"

def eab_arcane_bolt(e, p):
    blocked, bm = _check_block(p, e, "Arcane Bolt hits Arcane Shield")
    if blocked: return 0, bm
    dmg = calc_magic_dmg(e.int, 6, 16); p.hp -= dmg
    return dmg, f"{e.name} fires Arcane Bolt for {dmg} magic damage (ignores armor)!"

def eab_lifedrain(e, p):
    dmg = max(1, int(calc_phys_dmg(e.effective_str, 2, 8)
                     - calc_dmg_red(p.effective_end)))
    p.hp -= dmg; e.hp = min(e.max_hp, e.hp + dmg // 2)
    return dmg, f"{e.name} drains {dmg} HP from you (healed {dmg//2})!"

def eab_enrage(e, p):
    e.str += 3
    dmg = max(1, int(calc_phys_dmg(e.effective_str, 2, 8)
                     - calc_dmg_red(p.effective_end)))
    p.hp -= dmg
    return dmg, f"{e.name} ENRAGES! (+3 STR) then strikes for {dmg}!"

def eab_meteor(e, p):
    blocked, bm = _check_block(p, e, "Meteor hits Arcane Shield")
    if blocked: return 0, bm
    dmg = calc_magic_dmg(e.int, 14, 28); p.hp -= dmg
    return dmg, f"{e.name} calls down a METEOR for {dmg} magic damage!"

def eab_dark_curse(e, p):
    dmg = calc_magic_dmg(e.int, 6, 14); p.hp -= dmg
    p.dex = max(1, p.dex - 2)
    return dmg, f"{e.name} casts Dark Curse! {dmg} dmg and your DEX drops by 2!"

def eab_regen(e, p):
    heal = random.randint(12, 22); e.hp = min(e.max_hp, e.hp + heal)
    return 0, f"{e.name} regenerates {heal} HP!"

def eab_warcry(e, p):
    e.str += 4
    return 0, f"{e.name} WAR CRY! (+4 STR permanently)"


# ═══════════════════════════════════════════════════════════
#  ENEMY FACTORIES
# ═══════════════════════════════════════════════════════════

def make_goblin(s=1.0):
    return Enemy("Goblin", 6, 4, 3, 7, 1,
        "A wiry goblin with a chipped blade and a cruel grin.",
        [eab_double_strike], s)

def make_skeleton(s=1.0):
    return Enemy("Skeleton", 7, 5, 5, 5, 2,
        "Bones rattle as this undead warrior charges forward.",
        [eab_shield_bash], s)

def make_dire_wolf(s=1.0):
    return Enemy("Dire Wolf", 8, 5, 4, 9, 1,
        "A massive wolf with glowing crimson eyes and razor fangs.",
        [eab_double_strike, eab_poison_fang], s)

def make_dark_elf(s=1.0):
    return Enemy("Dark Elf Ranger", 8, 5, 4, 10, 3,
        "A swift dark elf with twin blades coated in venom.",
        [eab_poison_fang, eab_double_strike], s)

def make_stone_golem(s=1.0):
    return Enemy("Stone Golem", 9, 9, 10, 2, 1,
        "A lumbering construct of enchanted stone.",
        [eab_shield_bash, eab_enrage], s)

def make_vampire(s=1.0):
    return Enemy("Vampire", 9, 7, 5, 8, 4,
        "A pale vampire who has lived centuries on stolen life.",
        [eab_lifedrain, eab_regen], s)

def make_orc_warchief(s=1.0):
    return Enemy("Orc Warchief", 13, 12, 9, 6, 2,
        "A mountain of muscle and fury, wielding a blood-soaked greataxe.",
        [eab_enrage, eab_double_strike, eab_warcry, eab_shield_bash], s)

def make_lich(s=1.0):
    return Enemy("The Lich", 5, 10, 4, 7, 13,
        "A skeletal sorcerer draped in a cloak of dark runes.",
        [eab_arcane_bolt, eab_dark_curse, eab_lifedrain, eab_regen], s)

def make_chimera(s=1.0):
    return Enemy("Chimera", 12, 12, 8, 8, 5,
        "Lion's head, goat's body, serpent's tail -- a nightmare beast.",
        [eab_double_strike, eab_poison_fang, eab_enrage, eab_shield_bash], s)

def make_shadow_dragon(s=1.0):
    return Enemy("Shadow Dragon", 16, 18, 12, 10, 10,
        "An ancient dragon cloaked in living darkness. The air freezes when it breathes.",
        [eab_meteor, eab_lifedrain, eab_enrage, eab_dark_curse, eab_warcry], s)

def make_demon_king(s=1.0):
    return Enemy("Demon King Malachar", 18, 20, 14, 12, 14,
        "The Demon King himself. Reality warps around his presence.",
        [eab_meteor, eab_dark_curse, eab_arcane_bolt, eab_lifedrain, eab_enrage, eab_warcry], s)

NORMAL_ENEMIES   = [make_goblin, make_skeleton, make_dire_wolf,
                    make_dark_elf, make_stone_golem, make_vampire]
MINIBOSS_ENEMIES = [make_orc_warchief, make_lich, make_chimera]
FINAL_BOSSES     = [make_shadow_dragon, make_demon_king]


# ═══════════════════════════════════════════════════════════
#  DUNGEON BUILDERS
# ═══════════════════════════════════════════════════════════

def build_story_dungeon():
    normals    = random.sample(NORMAL_ENEMIES, 6)
    minibosses = MINIBOSS_ENEMIES[:]; random.shuffle(minibosses)
    return (normals[0:2] + [minibosses[0]]
          + normals[2:4] + [minibosses[1]]
          + normals[4:6] + [minibosses[2]]
          + FINAL_BOSSES)

def build_infinite_cycle(cycle_num, player_level=1):
    # Base scale from cycles + extra scaling from player level to keep it challenging
    cycle_scale  = 1.0 + (cycle_num - 1) * 0.18
    level_bonus  = (player_level - 1) * 0.08   # +8% per player level above 1
    scale        = cycle_scale + level_bonus
    normals    = random.sample(NORMAL_ENEMIES, 3)
    minibosses = random.sample(MINIBOSS_ENEMIES, 2)
    final      = [random.choice(FINAL_BOSSES)]
    return [(fn, scale) for fn in (normals + minibosses + final)]


# ═══════════════════════════════════════════════════════════
#  COMBAT ENGINE
# ═══════════════════════════════════════════════════════════

def combat(player, enemy, fight_label, is_boss=False, is_final=False, infinite_mode=False):
    clear()
    divider('=')
    tag = ("  [!! FINAL BOSS !!]" if is_final
           else "  [-- MINI-BOSS --]" if is_boss else "")
    print(f"  {fight_label}{tag}")
    divider('=')
    slow_print(f"\n  {enemy.flavor}\n")
    pause(0.4)

    turn = 1
    while player.hp > 0 and enemy.is_alive():
        player.tick_status()
        if player.hp <= 0:
            if player.revive_shard:
                player.revive_shard = False; player.hp = 1
                print("  Resurrection Shard shatters -- cling to life with 1 HP!")
            else:
                return "dead"

        divider('-')
        print(f"  -- TURN {turn} --")
        player.status(); print(); enemy.status()
        divider('-')

        # Build menu
        move_opts = []
        for mv in player.moves:
            ok = "OK" if player.mana >= mv.mana_cost else "!!"
            tag2 = " [C]" if getattr(mv, "crafted", False) else ""
            move_opts.append(f"[{ok}] {mv.name:<20} [{mv.mana_cost:>2} MP]{tag2}  {mv.desc}")

        inv_opts = []; inv_keys = []
        for cid, qty in list(player.inventory.items()):
            inv_opts.append(f"    Use {cid.replace('_',' ').title()} x{qty}")
            inv_keys.append(cid)

        extra_opts = ["    View Stats", "    Flee (50% chance)"]
        all_opts   = move_opts + inv_opts + extra_opts
        n_mv, n_iv = len(move_opts), len(inv_opts)

        choice    = pick("Your action:", all_opts)
        used_turn = True

        if choice < n_mv:
            mv = player.moves[choice]
            if player.mana < mv.mana_cost:
                print(f"\n  Not enough Mana! (need {mv.mana_cost}, have {player.mana})")
                pause(1.0); used_turn = False
            else:
                msg = mv.execute(player, enemy)
                print(f"\n  {msg}")

        elif choice < n_mv + n_iv:
            cid = inv_keys[choice - n_mv]
            print(f"\n  {player.use_consumable(cid, enemy)}")

        else:
            label = extra_opts[choice - n_mv - n_iv].strip()
            if label == "View Stats":
                player.stat_sheet()
                input("\n  Press Enter to return..."); used_turn = False
            else:  # Flee
                if is_boss or is_final:
                    print("\n  You cannot flee from this battle!"); pause(1.0); used_turn = False
                elif random.random() < 0.5:
                    slow_print("\n  You flee from battle!"); pause(0.8); return "fled"
                else:
                    print("\n  You tried to flee but failed!")

        if not used_turn:
            continue

        pause(0.5)
        if not enemy.is_alive(): break

        # Enemy phase
        tick_msgs = enemy.tick_effects()
        for tm in tick_msgs: print(tm)
        if tick_msgs: pause(0.3)
        if not enemy.is_alive(): break

        _, msg = enemy.act(player)
        print(f"\n  {msg}")

        if player.hp <= 0:
            if player.revive_shard:
                player.revive_shard = False; player.hp = 1
                print("\n  Resurrection Shard shatters -- you survive at 1 HP!")
            else:
                pause(0.6); return "dead"

        pause(0.6)
        turn += 1

    player.end_fight_cleanup()
    if not enemy.is_alive():
        player.total_kills += 1
        # Award XP in infinite mode
        if infinite_mode:
            xp_gain = 30 + int(enemy.max_hp * 0.15)
            if is_boss:   xp_gain = int(xp_gain * 2.0)
            if is_final:  xp_gain = int(xp_gain * 3.0)
            leveled = player.gain_xp(xp_gain)
            print(f"\n  +{xp_gain} XP ({player.xp}/{player.xp_to_next} to next level)")
            pause(0.6)
            if leveled:
                player.level_up()
                level_up_screen(player)
        return "victory"
    return "dead"


# ═══════════════════════════════════════════════════════════
#  LOOT SCREEN
# ═══════════════════════════════════════════════════════════

def loot_screen(player, source_name, count=3, is_boss=False, treasure=False):
    clear()
    divider('=')
    if treasure:
        print(f"  TREASURE ROOM -- {source_name}")
    else:
        print(f"  VICTORY!  {source_name} has been vanquished!")
    divider('=')

    c = 5 if treasure else (4 if is_boss else 3)
    slow_print(f"\n  {c} items available. Choose ONE:\n")

    opts    = treasure_cache(c) if treasure else gen_loot(c)
    display = [f"{item['name']:<32} {item['desc']}" for item in opts]
    choice  = pick("Select your reward:", display)

    chosen = opts[choice]
    player.apply_loot(chosen)

    if chosen["type"] == "consumable":
        slow_print(f"\n  You pocket {chosen['name']} x{chosen['qty']}! ({chosen['desc']})")
    else:
        slow_print(f"\n  You equip the {chosen['name']}! ({chosen['desc']})")

    if not treasure:
        rh = random.randint(18, 35); rm = random.randint(12, 25)
        player.hp   = min(player.max_hp,   player.hp   + rh)
        player.mana = min(player.max_mana, player.mana + rm)
        print(f"  You rest briefly: +{rh} HP, +{rm} Mana.")

    input("\n  Press Enter to continue...")


# ═══════════════════════════════════════════════════════════
#  ROOM SYSTEM
# ═══════════════════════════════════════════════════════════
#
#  Each "step" in the dungeon presents 3 doors. Behind each is one of:
#    COMBAT   -- a guaranteed fight (normal, miniboss, or boss depending on depth)
#    TREASURE -- free loot cache, no fighting
#    TRAP     -- risk/reward event: big reward OR punishing penalty
#
#  Boss rooms are never offered as choices -- they're mandatory gates.

TRAP_EVENTS = [
    # (name, flavor, good_msg, bad_msg, good_fn, bad_fn, good_chance)
    {
        "name": "Mimic Chest",
        "flavor": "A large ornate chest sits in the center of the room. It looks... too perfect.",
        "good": "The chest is genuine! You loot it freely.",
        "bad":  "IT'S A MIMIC! It lunges and bites you for 30 damage!",
        "good_fn": lambda p: [p.apply_loot(random.choice(ALL_LOOT)),
                               p.apply_loot(random.choice(CONSUMABLE_LOOT))],
        "bad_fn":  lambda p: setattr(p, "hp", max(1, p.hp - 30)),
        "chance": 0.45,
    },
    {
        "name": "Ancient Altar",
        "flavor": "A blood-stained altar pulses with dark energy. A voice whispers: 'Sacrifice...'",
        "good": "The altar accepts your blood! It grants you a vision of power. (+2 to all stats)",
        "bad":  "The altar rejects you! Dark energy tears through you. (-20 max HP, -8 Mana)",
        "good_fn": lambda p: [setattr(p, "str", p.str + 2),
                               setattr(p, "vit", p.vit + 2),
                               setattr(p, "end", p.end + 2),
                               setattr(p, "dex", p.dex + 2),
                               setattr(p, "int", p.int + 2),
                               setattr(p, "wis", p.wis + 2),
                               p._refresh_derived()],
        "bad_fn":  lambda p: [setattr(p, "vit", max(1, p.vit - 2)),
                               setattr(p, "wis", max(1, p.wis - 1)),
                               p._refresh_derived(),
                               setattr(p, "hp", min(p.hp, p.max_hp))],
        "chance": 0.35,
    },
    {
        "name": "Strange Potion",
        "flavor": "A glowing vial sits on a pedestal. The label reads: 'Drink Me (maybe)'.",
        "good": "Delicious! Your body tingles with power. (+8 to a random stat)",
        "bad":  "Ugh, it tastes awful. You feel weaker. (-4 to a random stat)",
        "good_fn": lambda p: p.apply_loot(random.choice(
                       [l for l in STAT_LOOT if l["value"] in (7, 9, 10)])),
        "bad_fn":  lambda p: p.apply_loot({
                       "type": "stat", "stat": random.choice(["str","vit","end","dex","int","wis"]),
                       "value": -4}),
        "chance": 0.50,
    },
    {
        "name": "Pit of Shadows",
        "flavor": "A dark chasm rumbles beneath a narrow bridge. Mist swirls below.",
        "good": "You cross safely and find a cache of supplies on the other side!",
        "bad":  "You slip! Falling damage and a rough landing. (-25% current HP)",
        "good_fn": lambda p: [p.apply_loot(random.choice(CONSUMABLE_LOOT)),
                               p.apply_loot(random.choice(CONSUMABLE_LOOT))],
        "bad_fn":  lambda p: setattr(p, "hp", max(1, int(p.hp * 0.75))),
        "chance": 0.55,
    },
    {
        "name": "The Gambler's Shrine",
        "flavor": "A robed skeleton sits at a table with three cards face-down. 'Choose one,' it rasps.",
        "good": "THE HIGH CARD! The shrine erupts with golden light. (+3 consumables!)",
        "bad":  "The Death Card. Dark energy drains your mana to zero and deals 20 damage.",
        "good_fn": lambda p: [p.add_consumable(random.choice(CONSUMABLE_LOOT)["cid"], 1)
                               for _ in range(3)],
        "bad_fn":  lambda p: [setattr(p, "mana", 0),
                               setattr(p, "hp", max(1, p.hp - 20))],
        "chance": 0.40,
    },
    {
        "name": "Whispering Runes",
        "flavor": "Runes cover the walls, glowing faintly. A disembodied voice offers knowledge.",
        "good": "The runes teach you. You unlock a free move workshop session!",
        "bad":  "The runes curse you! Your mind reels. (-3 INT, -3 WIS)",
        "good_fn": lambda p: setattr(p, "_workshop_free", True),
        "bad_fn":  lambda p: [setattr(p, "int", max(1, p.int - 3)),
                               setattr(p, "wis", max(1, p.wis - 3)),
                               p._refresh_derived()],
        "chance": 0.50,
    },
]


def run_trap(player, infinite_mode=False):
    """Execute a trap room. Returns 'dead' if player dies, else None."""
    event = random.choice(TRAP_EVENTS)
    clear()
    header(f"TRAP ROOM -- {event['name']}")
    slow_print(f"\n  {event['flavor']}\n")
    pause(0.5)

    input("  Press Enter to proceed (there's no turning back)...")
    print()

    success = random.random() < event["chance"]
    if success:
        slow_print(f"\n  SUCCESS! {event['good']}")
        event["good_fn"](player)
        # If rune event granted free workshop, trigger it now
        if getattr(player, "_workshop_free", False):
            player._workshop_free = False
            pause(1.0)
            move_workshop_screen(player, infinite_mode=infinite_mode)
    else:
        slow_print(f"\n  FAILURE! {event['bad']}")
        event["bad_fn"](player)
        if player.hp <= 0:
            if player.revive_shard:
                player.revive_shard = False; player.hp = 1
                slow_print("  Resurrection Shard activates -- you survive at 1 HP!")
            else:
                pause(1.0)
                return "dead"

    pause(0.5)
    print()
    player.status()
    input("\n  Press Enter to continue...")
    return None


ROOM_ICONS = {
    "combat":   "[COMBAT]",
    "treasure": "[TREASURE]",
    "trap":     "[TRAP]",
}

ROOM_DESCS = {
    "combat":   "The door thrums with violent energy. A fight awaits.",
    "treasure": "Golden light seeps under the door. Riches may lie within.",
    "trap":     "Strange runes glow around the frame. Risk and reward mingle here.",
}

def choose_room(step_label, can_flee=True):
    """Present 3 room doors. Returns one of: 'combat', 'treasure', 'trap'."""
    clear()
    header(f"THE CROSSROADS  --  {step_label}")
    slow_print("\n  Three doors stand before you. Each leads somewhere different.")
    slow_print("  Choose wisely -- you cannot go back.\n")

    # Guarantee at least one of each type isn't always offered;
    # pool is weighted so combat is more common
    pool = ["combat", "combat", "treasure", "trap", "trap"]
    chosen_types = random.sample(pool, 3)
    # Ensure no two consecutive same types looks boring -- shuffle until varied
    for _ in range(20):
        if chosen_types[0] != chosen_types[1] or chosen_types[1] != chosen_types[2]:
            break
        random.shuffle(chosen_types)

    labels = []
    for i, rt in enumerate(chosen_types, 1):
        labels.append(f"Door {i}: {ROOM_ICONS[rt]}  -- {ROOM_DESCS[rt]}")

    choice = pick("Which door do you enter?", labels)
    return chosen_types[choice]


# ═══════════════════════════════════════════════════════════
#  END SCREENS
# ═══════════════════════════════════════════════════════════

TITLE = """
  +==============================================================+
  |                                                              |
  |           D U N G E O N   E T E R N A L   v 4              |
  |              A Text-Based Turn-Based RPG                     |
  |                                                              |
  |   Room Choices  |  Move Crafting  |  Six Stats               |
  |   Combat  *  Treasure  *  Traps                              |
  |   Infinite Leveling  *  Scaling Enemies  *  Abyss Forge      |
  |                                                              |
  +==============================================================+
"""

CLASS_DESCRIPTIONS = {
    "Barbarian": (
        "Barbarian  -- Brawler / Tank\n"
        "    STR 12  VIT 10  END 8   DEX 5   INT 2   WIS 3\n"
        "    HP ~140  Mana ~58\n"
        "    Moves: Cleave | War Cry (+4 STR) | Reckless Slam | Blood Frenzy\n"
        "    High physical damage, durable, heals through Blood Frenzy."
    ),
    "Wizard": (
        "Wizard     -- Glass Cannon / Controller\n"
        "    STR 3   VIT 6   END 4   DEX 7   INT 14  WIS 9\n"
        "    HP ~108  Mana ~94\n"
        "    Moves: Arcane Bolt | Frost Nova (slow) | Mana Surge | Arcane Shield\n"
        "    Devastating magic, ignores armor, fragile -- dodge and obliterate."
    ),
    "Paladin": (
        "Paladin    -- Sustainer / Support\n"
        "    STR 7   VIT 10  END 9   DEX 5   INT 5   WIS 7\n"
        "    HP ~140  Mana ~82\n"
        "    Moves: Holy Strike (self-heal) | Shield Bash (stun) | Divine Light | Consecrate\n"
        "    Resilient, self-sustaining, stuns enemies to outlast any fight."
    ),
    "Rogue": (
        "Rogue      -- Precision / Assassin\n"
        "    STR 8   VIT 7   END 5   DEX 13  INT 4   WIS 5\n"
        "    HP ~116  Mana ~70\n"
        "    Moves: Shadowstrike (ignore armor) | Poison Blade | Smoke Bomb | Death Mark\n"
        "    High crit, armor-ignoring, poison, guaranteed dodge. Fragile but deadly."
    ),
}

def intro():
    clear(); print(TITLE)
    slow_print("  Choose your path. Craft your power. Survive the eternal darkness.\n")
    input("  Press Enter to begin your legend...")

def character_creation():
    clear(); header("CREATE YOUR CHARACTER")
    name = input("\n  Enter your hero's name: ").strip() or "Hero"
    cls_names = ["Barbarian", "Wizard", "Paladin", "Rogue"]
    cls_descs = [CLASS_DESCRIPTIONS[c] for c in cls_names]
    print()
    choice = pick("Choose your class:", cls_descs)
    cls    = cls_names[choice]
    player = Player(name, cls)
    clear(); header(f"{player.name} the {player.cls}  --  ARISE!")
    player.stat_sheet()
    slow_print("\n  Three doors wait at every crossroads. The dungeon hungers.\n")
    input("  Press Enter to enter the dungeon...")
    return player

def choose_mode():
    clear(); header("SELECT MODE")
    print()
    slow_print("  Story Mode    -- Navigate rooms toward 3 minibosses and 2 final bosses.")
    slow_print("                   Move Workshop unlocks after each miniboss (3 random choices).")
    slow_print("  Infinite Mode -- Endless cycles scaling forever. How deep can you go?")
    slow_print("                   Level up, grow stronger, and forge moves from the abyss.\n")
    choice = pick("Choose your mode:", ["Story Mode", "Infinite Mode"])
    return "story" if choice == 0 else "infinite"

def game_over_screen(player, mode, cycle=1):
    clear(); divider('X')
    slow_print(f"\n  {player.name} has fallen to the darkness...")
    if mode == "infinite":
        slow_print(f"  Survived {cycle-1} full cycle(s). Total kills: {player.total_kills}.")
        slow_print(f"  Reached Level {player.level}.")
    else:
        slow_print("  The dungeon claims another soul.")
    player.stat_sheet(); divider('X')
    input("\n  Press Enter to exit.")

def victory_screen(player):
    clear(); divider('*')
    slow_print(f"\n  * * *  VICTORY!  * * *")
    slow_print(f"\n  {player.name} the {player.cls} has conquered the dungeon!")
    slow_print(f"  Final Level: {player.level}")
    slow_print("  Songs will be sung of your legend for ages to come.")
    player.stat_sheet(); divider('*')
    input("\n  Press Enter to exit.")

def cycle_clear_screen(player, cycle_num):
    clear(); divider('o')
    slow_print(f"\n  CYCLE {cycle_num} COMPLETE  [Level {player.level}]")
    slow_print(f"  Total kills: {player.total_kills}")
    slow_print(f"  The dungeon deepens... Cycle {cycle_num+1} will be harder.\n")
    rh = int(player.max_hp * 0.4); rm = int(player.max_mana * 0.4)
    player.hp   = min(player.max_hp,   player.hp   + rh)
    player.mana = min(player.max_mana, player.mana + rm)
    print(f"  Deep rest: +{rh} HP, +{rm} Mana.")
    print("\n  The abyss offers a boon. Choose one stat upgrade:\n")
    bonus_opts = random.sample(STAT_LOOT, 3)
    display    = [f"{i['name']:<32} {i['desc']}" for i in bonus_opts]
    choice     = pick("Cycle bonus -- choose one:", display)
    player.apply_loot(bonus_opts[choice])
    slow_print(f"\n  {bonus_opts[choice]['name']} equipped! ({bonus_opts[choice]['desc']})")
    print("\n  The forge pulses with abyssal energy before you descend.")
    if pick("", ["Visit Move Workshop (infinite pool)", "Skip and descend"]) == 0:
        move_workshop_screen(player, infinite_mode=True)
    divider('o')
    input("\n  Press Enter to descend deeper...")


def level_up_screen(player):
    """Interactive level-up screen for infinite mode."""
    clear(); header(f"LEVEL UP!  -->  Level {player.level}")
    slow_print(f"\n  {player.name} grows stronger from the depths!")
    slow_print(f"  You are now Level {player.level}.\n")

    # Choose a stat to raise
    print("  Choose a primary stat to increase:\n")
    stat_choices = [
        ("str", "+3 STR  (Strength  -- physical damage)"),
        ("vit", "+3 VIT  (Vitality  -- max HP +24)"),
        ("end", "+3 END  (Endurance -- damage reduction +1.8)"),
        ("dex", "+3 DEX  (Dexterity -- dodge, crit, acc)"),
        ("int", "+3 INT  (Intelligence -- magic damage)"),
        ("wis", "+3 WIS  (Wisdom    -- max Mana +18)"),
    ]
    sampled = random.sample(stat_choices, 3)   # random 3 stat options
    display  = [s[1] for s in sampled]
    choice   = pick("Pick your stat gain:", display)
    stat_id, desc = sampled[choice]
    player.apply_loot({"type": "stat", "stat": stat_id, "value": 3})
    player.hp   = min(player.max_hp,   player.hp   + 20)   # level-up bonus heal
    player.mana = min(player.max_mana, player.mana + 10)
    slow_print(f"\n  {desc.split('--')[0].strip()} gained! (+20 HP, +10 Mana restored)")

    # Offer workshop on level-up (every level)
    print()
    if pick("The dungeon's power surges. Forge a new move?",
            ["Visit Move Workshop (infinite pool)", "Skip"]) == 0:
        move_workshop_screen(player, infinite_mode=True)

    divider('-')
    input("\n  Press Enter to continue...")


# ═══════════════════════════════════════════════════════════
#  STORY GAME LOOP
# ═══════════════════════════════════════════════════════════
#
#  Story structure (with rooms):
#    Phase 1: 2 normal room-steps -> mandatory miniboss gate
#    Phase 2: 2 normal room-steps -> mandatory miniboss gate
#    Phase 3: 2 normal room-steps -> mandatory miniboss gate
#    Final:   2 mandatory final boss rooms
#
#  Each "room-step" lets the player pick a door (combat/treasure/trap).
#  Miniboss and final boss rooms are mandatory (no door choice).

def run_story(player):
    normals    = random.sample(NORMAL_ENEMIES, 6)
    minibosses = MINIBOSS_ENEMIES[:]; random.shuffle(minibosses)
    norm_idx   = 0

    def get_normal_enemy():
        nonlocal norm_idx
        fn = normals[norm_idx % 6]; norm_idx += 1
        return fn

    phases = [
        ("Phase 1", [get_normal_enemy(), get_normal_enemy()], minibosses[0]),
        ("Phase 2", [get_normal_enemy(), get_normal_enemy()], minibosses[1]),
        ("Phase 3", [get_normal_enemy(), get_normal_enemy()], minibosses[2]),
    ]

    step = 0
    total_steps = 6 + 3 + 2  # normals room-steps + miniboss fights + final boss fights

    for phase_name, phase_normals, boss_fn in phases:
        for norm_fn in phase_normals:
            step += 1
            room_type = choose_room(f"{phase_name}  Step {step}/{total_steps}")

            if room_type == "combat":
                enemy  = norm_fn()
                result = combat(player, enemy, f"FIGHT  {phase_name}", False, False, False)
                if result == "dead":
                    game_over_screen(player, "story"); return
                if result == "fled":
                    slow_print("\n  You flee into the corridor..."); pause(0.8)
                    input("  Press Enter to continue..."); continue
                loot_screen(player, enemy.name, count=3)

            elif room_type == "treasure":
                loot_screen(player, "Ancient Cache", treasure=True)

            elif room_type == "trap":
                result = run_trap(player, infinite_mode=False)
                if result == "dead":
                    game_over_screen(player, "story"); return

        # Mandatory miniboss
        step += 1
        clear(); header(f"GATE -- {phase_name} -- MINI-BOSS AHEAD")
        slow_print("\n  The path narrows. A massive door sealed with runes blocks the way.")
        slow_print("  There is no choice here. You must fight.\n")
        input("  Press Enter to face the guardian...")
        enemy  = boss_fn()
        result = combat(player, enemy, f"MINI-BOSS  {phase_name}", True, False, False)
        if result == "dead":
            game_over_screen(player, "story"); return
        loot_screen(player, enemy.name, count=4, is_boss=True)

        # Workshop ONLY after miniboss (3 random choices, story pool)
        slow_print("\n  Victory! The runes on the wall glow -- the Workshop beckons.")
        if pick("A forge shimmers before you:", ["Visit Move Workshop", "Press forward"]) == 0:
            move_workshop_screen(player, infinite_mode=False)

    # Final bosses (mandatory)
    for i, boss_fn in enumerate(FINAL_BOSSES):
        step += 1
        clear(); header("THE FINAL GATES")
        slow_print("\n  The air crackles with dread power. This is it.\n")
        input("  Press Enter to face your destiny...")
        enemy  = boss_fn()
        result = combat(player, enemy, f"FINAL BOSS {i+1}/2", False, True, False)
        if result == "dead":
            game_over_screen(player, "story"); return
        if i < len(FINAL_BOSSES) - 1:
            loot_screen(player, enemy.name, count=5, is_boss=True)

    victory_screen(player)


# ═══════════════════════════════════════════════════════════
#  INFINITE GAME LOOP
# ═══════════════════════════════════════════════════════════

def run_infinite(player):
    cycle = 1
    while True:
        player.cycle = cycle
        encounters   = build_infinite_cycle(cycle, player.level)
        # First 3 are normals (room choice), last 3 are boss/miniboss (forced)
        normals_enc  = encounters[:3]
        bosses_enc   = encounters[3:]

        for i, (enemy_fn, scale) in enumerate(normals_enc):
            step_lbl = f"CYCLE {cycle}  FIGHT {i+1}/6  [Lv.{player.level}]"
            room_type = choose_room(step_lbl)

            if room_type == "combat":
                enemy  = enemy_fn(scale)
                result = combat(player, enemy, step_lbl, False, False, infinite_mode=True)
                if result == "dead":
                    game_over_screen(player, "infinite", cycle); return
                if result == "fled":
                    slow_print("\n  You flee..."); pause(0.8)
                    input("  Press Enter..."); continue
                loot_screen(player, enemy.name, count=3)

            elif room_type == "treasure":
                loot_screen(player, f"Hidden Cache (Cycle {cycle})", treasure=True)

            elif room_type == "trap":
                result = run_trap(player, infinite_mode=True)
                if result == "dead":
                    game_over_screen(player, "infinite", cycle); return

        for i, (enemy_fn, scale) in enumerate(bosses_enc):
            is_final = (i == 2)
            lbl = f"CYCLE {cycle}  BOSS {i+1}/3  [Lv.{player.level}]"
            enemy  = enemy_fn(scale)
            result = combat(player, enemy, lbl, not is_final, is_final, infinite_mode=True)
            if result == "dead":
                game_over_screen(player, "infinite", cycle); return
            loot_screen(player, enemy.name, count=4 if not is_final else 5, is_boss=True)

            # Workshop after every boss kill in infinite mode (infinite pool)
            slow_print("\n  Power flows through you. The Workshop manifests...")
            if pick("Forge a move from the abyss?",
                    ["Visit Move Workshop (infinite pool)", "Skip"]) == 0:
                move_workshop_screen(player, infinite_mode=True)

        cycle_clear_screen(player, cycle)
        cycle += 1


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    intro()
    mode   = choose_mode()
    player = character_creation()
    if mode == "story":
        run_story(player)
    else:
        run_infinite(player)

if __name__ == "__main__":
    main()
