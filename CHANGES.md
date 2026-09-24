# 190 Expanded: Changes from Vanilla

This page lists what **190 Expanded** changes from vanilla Total War: THREE KINGDOMS. It then covers what the two optional overhauls change on top of 190 Expanded: the **Campaign Overhaul** and the **Battle Overhaul**.

The page is built from the mod's own data files. Every table row, script and string is compared against the base game. The written sections explain what each change means in play. The stat-table appendices list every exact number.

## How the layers fit together

| Layer | What it is | Compared against |
|---|---|---|
| **Vanilla** | Total War: THREE KINGDOMS with all DLC | none (this is the baseline) |
| **190 Expanded** | The main mod: Extra Regions + Factions & Characters | Vanilla |
| **Campaign Overhaul** | Optional rebalance of economy, court, characters, recruitment and campaign AI | 190 Expanded |
| **Battle Overhaul** | Optional rebalance of units, weapons, abilities, morale and battle rules | 190 Expanded |

**Install order:** 190 Expanded's Extra Regions, then 190 Expanded [Factions & Characters], then the Overhaul, then any other mods. The All-in-One builds replace the first two packs with a single pack.

## How to read this page

- **Part 1** covers everything 190 Expanded adds to or changes from vanilla.
- **Parts 2 and 3** only describe what each overhaul changes relative to 190 Expanded. If a value isn't mentioned there, it is the same as in 190 Expanded.
- Numbers are written **old → new**.
- Names come from the in-game text. Internal keys are shown in `code` where they help modders find a row.
- The **stat tables** are in separate tabs at the top of this page. Use the search box to filter any table by unit or building name:
  - [190 Expanded stat tables](#appendix-190e)
  - [Campaign Overhaul stat tables](#appendix-campaign)
  - [Battle Overhaul stat tables](#appendix-battle)
- Generated on 24 September 2026 from the current mod files.
- The vanilla baseline is the game database from before CA's September 2026 crossplay patch.

---

## Part 1: Vanilla → 190 Expanded

This part lists everything 190 Expanded changes compared with an unmodded copy of Total War: THREE KINGDOMS. It covers the three live packs: Extra Regions (map, start positions and character equipment data), Factions & Characters (factions, characters, units, buildings, scripts, interface) and Flags. The optional Campaign and Battle Overhauls are separate layers, covered in Parts 2 and 3.

The mod is built around the 190 AD campaign. Unless a line says otherwise, it refers to that start.

| Area | What 190 Expanded adds or changes |
|---|---|
| Land regions | 39 new land regions and 19 new sea regions |
| Provinces | 16 new provinces, 7 vanilla regions moved to a different province |
| Factions | 100 new faction records (51 new factions plus their separatist versions) |
| Playable in 190 | 84 more faction-select entries: 32 new factions and 52 existing ones made playable |
| Characters | 623 new historical character templates, 96 Korean generic templates |
| Units | 251 new land units; 489 vanilla units changed |
| Buildings | 97 new building chains with 305 levels |
| Technology | 120 new technologies |
| Character skills | 193 new skill trees with 3,417 skill nodes |
| Effect bundles | 4,009 new effect bundles |
| Text | 22,890 new localised strings |
| Scripts | 261 campaign and frontend scripts added or modified |

---

### Map & regions

The campaign map is extended to the north-west and to the Korean peninsula. The map camera's bounds are widened from 455 × 495 to 600 × 550 in every start date so the new land can be reached.

#### The north-west and the northern frontier

Ten new land regions across five provinces:

| Province | Regions |
|---|---|
| Dunhuang | Dunhuang, Jiuquan |
| Zhangye | Lude, Xihai |
| Xiping | Xidu, Nan'an, Huandao |
| Wuyuan | Wuyuan, Yuan |
| Wuwei (vanilla province) | Rile |

#### The north-east and Korea

Twenty-nine new land regions across eleven provinces:

| Province | Regions |
|---|---|
| Hyunto | Hyunto, Liaodui, Changli |
| Lelang | Pyongyang, Xi'anping |
| Daifang | Daifang, Liekou, Changcen |
| Dongokjeo | Gaema, Guda, Gungnae-seong |
| Dongye | Dongye, Loufang |
| Ye | Siljik-guk, Haslla |
| Hanseong | Wirye-seong, Michuhol, Uhyumotak-guk |
| Mahan | Mokji-guk, Gori-guk, Geonma-guk |
| Chimmi Darye | Shinmi-guk, Tamna, Nakno-guk, Anya-guk |
| Jinhan | Seorabeol, Dabeol-guk |
| Byeonhan | Guya-guk, Geochilsan-guk |

Nineteen new sea regions cover the Bohai Sea, the Sea of Japan, the Korean seas and the coastal waters between the new provinces.

#### Reorganised vanilla provinces

- A new province, **Pei**, is formed from Peixian (taken from Chen, and now Pei's capital) and Fuli (taken from Huainan).
- Zhixian moves from Shangdang to Henei.
- Hanchang moves from Baxi to Hanzhong.
- Meixian moves from Hanzhong to Jingzhao.
- Shanglian moves from Shangyong to Ba.
- Gushi moves from Huainan to Runan.

#### Start dates

- **190 AD** is the main campaign and the one the mod is designed and tested around.
- Start positions for **194, 198, 207 and 217** are also rebuilt on the expanded map. The 207 start reuses vanilla's Mandate of Heaven start slot and the 217 start reuses the Eight Princes slot, so those two vanilla start dates are replaced. The later dates get less testing than 190.
- The Mandate of Heaven start script no longer runs its vanilla systems (the mandate war, imperial court, Yellow Turban fervour, emergent factions and the Liang Rebellion triggers), because that slot now holds the 207 start.

---

### Factions

#### New factions in the 190 start

Thirty-two new factions, all playable:

| Group | Factions |
|---|---|
| Han warlords (15) | Bian Rang, Chen Wen, Handan Shang, Hu Mao, Huang Clan, Liu Pan, Ma Ai, Su Dai, Tong Zhi, Wang Sheng, Zhang Jin, Zhang Xian, Zhao Wei, Zhu Hao, Zhuge Xuan |
| Korean kingdoms (7) | Goguryeo (led by Gogukcheon), Baekje (Chogo), Silla (Beolhyu), Gaya (Kim Suro), Buyeo, Dongye (Yeonbul), Tamna |
| Northern tribes (5) | Wuhuan Tribes (Qiulijiu), Xiongnu Tribes (Yufuluo), Tuyuhun (Kuitou), Northern Wei (Tuoba Jiefan), Di Tribes |
| Outlaws and rebels (4) | Gan Ning, You Tu, Zu Lang, Fei Zhan |
| Yellow Turbans (1) | Yellow Turban Wu Huan |

#### Existing factions made playable in 190

Fifty-two factions that were unplayable or absent from the 190 faction-select screen now have a playable entry:

- **Han warlords:** Cai Mao, Chen Gui, Gao Gan, Gongsun Du, Han Fu, Hua Xin, Huang Zu, Jia Long, Kong Zhou, Lai Gong (Gaoliang), Liu Dai, Liu Xun, Liu Yao, Liu Yu, Lu Kang, Ni Xiaode (Nanhai), Sheng Xian, Shi Huang, Wang Kuang, Wang Lang, Wu Jing, Wu Ju (Yulin), Ying Shao, Zhai Rong, Zhang Chao, Zhang Lu, Zhang Yang, Zhu Fu.
- **Lü Bu** and **Sun Ce** as their own factions in 190. Sun Ce's faction-select entry now opens in 190 instead of 194.
- **The Han Empire**, with a "Loyalty to the Han" path to victory: it cannot declare itself emperor by creating a seat, but can take the title by capturing an existing emperor's capital.
- **Rebels:** Han Sui, Song Jian's Liang Rebels, Yang Feng, the Shanyue Rebels (Pan Lin) and the generic Yellow Turban Rebellion.
- **Nanman:** Ahuinan, Dongtuna, Jinhuansanjie, King Duosi, King Wutugu, Mangyachang, Tu'An, Xi'Ni, Yang Feng of the Nanman, and the Jiangyang, Jianning, Jiaozhi, Yongchang, Yunnan and Zangke tribes. Each starts with its own Fealty card and must gather the others to unite the tribes.
- **Qu Pan's Jiuzhen.**

#### Factions in later start dates

The 207 and 217 starts add nineteen more new factions: Cao Ren, Chen Lan, Du Ji, Guan Yu, Han Xuan, Lei Xu, Liu Du, Liu Shan, Ma Chao, Sun Ben, Sun Quan, Xiahou Yuan, Zhang Liao, Zhao Fan, Zhong Yao, Zhou Yu, Zhu Jun, Zhuge Liang and the Yellow Turbans of Xu He.

#### Faction presentation

- **Flags:** 56 new flag sets, and new unit banners for the Di, Wuhuan, Xianbei, Tuoba and Xiongnu.
- **Kingdom names:** new rank-based kingdom and duchy names for the added factions. Four vanilla names change: Zhai Rong's Chao becomes Zeng, Ying Shao's Xiapi becomes Pi, Chen Gui's Qing becomes Lai, and Zhu Fu's Kui becomes Mou.
- **Faction select:** new leader descriptions, difficulty and playstyle ratings, and mechanic cards for every added faction. Prince Liu Chong's starting situation is re-rated from Easy to Very Hard.
- **Loading screens:** 324 new campaign intro loading-screen entries.
- **Voice-over:** Liu Yu and Chen Wen get full voice-over.
- **Faction types:** Han Sui, Liu Yu, Gao Gan, Zhang Lu, Jia Long, Liu Dai and King Wutugu change from unplayable to playable; the vanilla Looters (`3k_dlc04_faction_rebels`) move from the Han subculture to the bandit subculture; Yang Feng becomes an outlaw faction.
- **Faction groups:** Tao Qian moves from the Coalition group to the Regional Warlords group in 190.

---

### Characters

#### Unique characters

- **623 new historical character templates** across the start dates, whether they begin on the map, spawn later, are born, or wait in recruitment pools.
- **1,027 new unique careers** and **549 new unique armours** give added characters their own career bonuses and signature armour.
- **Existing historical characters** who used generic art and data in vanilla now have their own: 481 templates get a unique art set, 280 get a bespoke skill tree, 760 get their own starting equipment and traits, and 184 get a unique bodyguard retinue. Examples include Wang Kuang and Cai He.
- 24 vanilla birth-year and spawn windows are adjusted. Cao Chun is now born in 170 instead of 178, and Gan Ning can appear from 189 instead of 200.
- Wei Yan's scripted spawn window now opens in 200 instead of 195.

#### Korea

- Around 59 named historical figures across the Go clan of Goguryeo (Gogukcheon, Chogo, Go Balgi, Go Yeonu, Go Gyesu and others), the Seok and Kim clans of Silla (Beolhyu, Seok Naehae, Kim Suro's Gaya line, Heo Hwangok), Dongye (Yeonbul, Tam Hari, Hae Mayeo) and retainers such as Lady Woo, Eul Paso, Myeongrim Eosu, Mil U and Yu Yu.
- Baekje has sixteen named characters of the Onjo line, including Buyeo Gusu, Buyeo Goi, Buyeo Saban, Jin Gwa and Jin Chung, with their own name pool.
- **96 Korean generic character templates** cover every office and element, so Korean factions no longer recruit from the Han Chinese pool. The Korean name pools add 134 clone names and 34 unique names.
- Eul Paso can join Goguryeo through an event, for 500 gold.

#### Historical births

Historical children are born into their families on their real birth years:

- **31 births**, among them Cao Zhi, Cao Rui, Cao Biao, Cao Shuang, Liu Feng, Guan Suo, Zhuge Ke, Sima Shi, Sima Zhao, Wang Yuanji, Zhong Hui, Sun Deng and Xin Xianying, and Korean children such as Go Uwigeo, Go Yeonbul, Buyeo Saban, Seok Uro and Kim Michu.
- **11 Goguryeo characters** arrive on their birth years with a birth event, including Myeongrim Eosu, Mil U, Deuk Rae, Yu Okgu and Yu Yu.

#### Historical joins

Twenty-eight historical generals can join their historical lords during a year window, with a dilemma when they arrive: Cao Cao (13, including Xu Chu, Dian Wei, Man Chong, Yue Jin, Zhong Yao, Deng Ai and Hua Tuo), Sun Jian (9) and Sun Ce (8), who share Zhou Yu, Zhang Zhao, Lu Meng and the Qiao sisters, and Liu Bei (5, including Xu Shu and Jiang Wei). Zuo Ci, Zhou Cang and Bao Sanniang are Romance-mode only. Generals also join AI factions, so their status can change on its own.

#### Generic characters and pools

- Faction recruitment pools hold more characters: up to 5 instead of 2, with a median of 3 instead of 1.
- Pools refresh more often: a full refresh every 3 turns instead of 5, and a partial refresh every turn instead of every 2.
- 333 historical templates stay in the pools for up to 40 rounds before disappearing, instead of 20.
- More southern character templates and new portrait art for a range of minor characters.

#### Spouses

About 90 historical spouses now give their partner a bonus while married. For example, Lady Yan gives Lü Bu a melee damage bonus, Dong Bai adds family-estate income, and Lady Lu Ji gives a combat bonus. The bonus follows whoever the spouse is married to.

#### Character skill trees

- **193 new skill trees** with 3,417 skill nodes. They include 27 Korean trees (486 nodes) covering every generic archetype plus bespoke trees for Go Yeonu, Seok Naehae, Buyeo Gusu, Go Balgi, Lady Woo, Eul Paso, Chogo, Kim Suro, Gogukcheon and Beolhyu, a bespoke tree for Cai Mao, and a generic barbarian tree.
- 237 new character skills and 237 new unit abilities, such as Sima Hui's Water Mirror, Ma Su's Hilltop Sermon, Ma Zhong's Yoke of the South and the Xiongnu Mark of Scorn.
- Yellow Turban skill trees (378 nodes in 12 trees) are no longer locked to the Yellow Turban subculture, so a Yellow Turban character keeps his tree after joining another faction.

---

### Faction mechanics

Each faction below has a mechanic that vanilla does not have, or a vanilla mechanic that 190 Expanded rebuilds.

#### Nomadic Hordes: Wuhuan, Xiongnu, Tuyuhun, Northern Wei and Di

- Armies become wandering settlements. Each army has building slots that grow as its general does, and you build and upgrade structures in them over five tiers, paying gold and turns.
- Army buildings include the Nomadic Host camp, Mobile Forge, Herders, Gatherers and Foragers, Shaman's Yurt, Fletchers, Traders and Salvagers, Traveling Artisans, Saddlemaker and the Grand Equine Entourage. Each tribe also has its own: The Chanyu's Tents (Xiongnu), Confederation Muster (Tuyuhun), Ordo Forges (Northern Wei), Di Pathfinders and the Nomadic Host of the Wuhuan.
- Downgrading or demolishing refunds 50% of the tier's cost. Cancelling refunds 100%. Rushing finishes a job at once for three times the remaining share of its cost.
- Each army carries its own population, starting at 2,000. Herders and Gatherers add 50 to 150 people per turn by tier, up to the camp's capacity.
- Gatherers and Foragers give a flat +1 to +5 food per army, faction-wide, counted as foraging.
- When an army is recalled, you choose which surviving general inherits its slots and buildings.
- The five tribes also use **Barbaric Fervour**, which rises while at war and through certain settlement actions and falls in peace and with faction rank.
- Their tax levels work differently. Minimal tax gives +50% post-battle loot and +50% food, and extortionate tax gives −50% of each. Public order falls by 2 at normal tax and by up to 10 at either extreme.

#### Ma Teng's Stables

- Stable foals in training stalls and give each a focus: Hill Gallops, Formation Drills, Long Rides, Night Runs, Parade Grounds, or rest. Fatigue and stable events have to be managed.
- A horse's training sets its bloodline and quality: Common, Refined, Exceptional or Elite.
- Six bloodlines (Common, Qiang, Wuhuan, Xianbei, Xiongnu and Han Pasture) unlock as your realm reaches their homelands.
- Broken-in horses move to the paddock. From there you can assign them as mounts, sell them, dedicate them for a faction-wide bloodline blessing, breed a sire and dam, or release them.
- Stall capacity grows to 36 with faction rank, owned horse pastures and horse-district buildings.

#### Governor Edicts: Gongsun Zan

- Gongsun Zan's five inspectors (Agricultural, Government, Industrial, Economic and Military) can each enact one edict over the commandery they govern and the owned commanderies next to it.
- The edicts on offer depend on the officeholder's personality. Darker traits open riskier edicts with real downsides.
- Effects scale over five tiers with the holder's rank. An edict lasts until you revoke it or the holder loses the post or trait behind it.

#### Trial by Combat: Lü Bu

- Lü Bu's Greatest Warriors are won in a turn-based duel rather than granted when the warrior joins. The duel choices are Attack, Guard, Special or Yield, with a Momentum bar that powers Special.
- Winning claims the warrior's trophy. A loss or a flight locks that warrior away for 3 turns.
- Over forty named warriors can be challenged, including Sun Jian, Pang De, Yan Liang, Wen Chou, Lu Meng, Han Dang, Ling Tong, Kuitou, Tadun, Meng Huo and Zhurong. Each trophy already collected adds to Lü Bu's attack in the duel.
- A separate debate minigame lets Lü Bu argue his father's legacy: Change the Subject, Invoke My Halberd, or Punch the Nerd.
- AI Lü Bu and trophies won on the battlefield work as in vanilla.

#### Path to Unity: Liu Bei (rebuilt)

- Liu Bei's Path to Unity is rebuilt around **seven patron warlords**: Gongsun Zan, Kong Rong, Tao Qian, Liu Biao, Liu Yan, Ma Teng and the Sun clan. Each patron has a five-stage track.
- Tracks advance on **Esteem**. Each turn you gain +1, +2 or +3 at the Friendly, Very Friendly and Best Friends attitude bands, +1 for a trade agreement and +1 for an alliance or coalition, and lose 3 while at war with the patron. A battle won against the patron's enemy adds 4, or 6 if the patron fought beside you. The stage thresholds are 15, 35, 60, 90 and 130.
- Stages give militia bonuses and the 38 officers who historically joined Liu Bei, such as Zhao Yun, Mi Zhu, Huang Zhong, Zhuge Liang, Pang Tong, Fa Zheng, Ma Chao and Lady Sun. Earned stages are never taken back, but **conquering a patron voids its track for good**.
- Liu Bei's new Five Tiger Generals court category starts with 1 post. Completing the Gongsun Zan, Tao Qian, Ma Teng and Sun tracks opens one more post each, up to five. Liu Biao's and Liu Yan's final stages confederate Jing and Yi, and Kong Rong's pays +25 Han Empire progression.
- Kong Rong's track unlocks Fury of Beihai (rank 3) and Thunder of Jian'an (rank 6), and Tao Qian's unlocks Territorial Archers and Territorial Spearmen (rank 3). Units unlocked by the mechanic are rank-locked only, with no unit cap.
- The faction panel shows each patron's progress, and a readout shows your live Esteem.

#### Tribal Management: Liu Yu (reworked)

- 22 tribal region cards each unlock one tribal unit with no unit cap. The other 8 region cards give a tribe-wide bonus instead, such as −10% upkeep for Wuhuan units, +10% replenishment for Xianbei units, or −15% recruitment cost for Xiongnu units.
- 26 chieftain cards each give a combat bonus to their own tribe's units, for example Tadun +10% melee and +8 morale for Wuhuan units, or Ma Chao +15% charge for Qiang units.
- **Pacifism** grows with high public order and alliances. At levels 2, 3 and 4 it gives +5/+10/+15% replenishment and −5/−10/−15% recruitment cost for tribal units.
- Liu Yu also earns Pacifism for every faction allied with him, and has the Artisan Labour building and access to Integrate on Han Empire settlements.

#### Legacy of Wu: Sun Ce in 190

Sun Ce's vanilla Legacy of Wu collection now runs in the 190 campaign, where Sun Ce and Sun Jian exist as two separate factions. A frontend option decides whether Sun Ce stays on the field or folds into Sun Jian.

#### The Needle Path: Zhang Jin

- **Qi** comes from winning battles against non-Han factions and from piercing forbidden points. It is spent on blessings, decays over time, and is lost when battles are lost.
- A chart of 32 acupuncture points: 20 blessings that cost Qi, and 12 forbidden points that are free but drain Qi every turn until refunded.
- Points belong to sets (Crown, Hand, Guard, Root, Stride and others) that pay a bonus once complete.
- Taoist Rites assignments give steady Qi or spend it to mend garrisons, and Captive Rituals after battle turn prisoners into Qi.
- Zhang Jin also gains 24 equipment sets.

#### Father's Legacy: Zhu Hao

- **Father's Legacy** is earned one point per trial as Zhu Hao steps out of Zhu Jun's shadow, from Unproven through Acknowledged, Respected and Honoured to His Equal. Some trials are hidden.
- Points buy permanent doctrines at a unit-upgrade shop. There are 20 doctrines in five element sets of four, such as Earth Doctrine: Crushing Blows, Fire Doctrine: Furious Charge and Water Doctrine: Deep Quivers.
- Completing a set grants its capstone: Rapid Deploy (Earth), Mighty Knockback (Fire), Fire While Moving and Parthian Shot (Water), Fatigue Immune (Wood) or Stalk (Metal).
- Zhu Hao also uses captain retinues instead of heroic generals.

#### The Black Market: You Tu

- **Enforcement** rises with battles and duels won and falls with losses and purchases. It runs from Scattered through Regrouping, Organising and Coordinated to Ironclad. Higher Enforcement raises spying and post-battle income but cuts military supplies.
- Spend Enforcement or gold on twelve kinds of equipment case (weapons, armour, mounts, followers, accessories and mixed lots), each in a standard and a Fine tier, with an Open ×10 option.
- You Tu can confederate bandit factions.

#### Sanity: Qu Pan

- **Sanity** (0 to 10) sets which kind of episode fires every Harvest. At high Sanity almost every episode is a gift that erodes a little more sanity. At the bottom almost everything is a disaster, but surviving one claws sanity back.
- Around sixty episodes, from "This Is Fine" to "The horror... the horror..". Every dilemma offers the same second option: trust Commander Lu.
- The Commander Lu assignment gives +1 Sanity per turn.
- Jiuzhen now holds Faction Council meetings.

#### Ferocity and Liu Biao's Favour: Liu Pan

- **Ferocity** (starts at 15) rises with victories (+8 decisive, +5 close, +3 defending), sacking (+12), looting (+8) and executing captives (+3), and with +2 per army in the Raiding stance. It falls by 6 per defeat and decays by 2 to 6 per turn.
- Ferocity tiers run from Dormant to Terror of the South. They add up to +25% movement, +25% loot, +25% replenishment on foreign soil and +15% ambush chance, and at the top tier −15% upkeep for Changsha Raiders and Stalkers, at the cost of public order.
- **Liu Biao's Favour** (starts at 50) grows by 2 per turn while Liu Pan is Liu Biao's vassal and by 5 per victory over Liu Biao's enemies. It falls by 5 per sack and at high Ferocity.
- Favour tiers run from Estranged to Heir of Jing. They give up to +15% income, −15% recruitment cost and +2 satisfaction, and at tiers 3 and 4 a stipend from Xiangyang of 3% or 6% of Liu Biao's regular income (capped at 500 or 1,000 per turn).
- Liu Pan gains the Raiding stance and Integrate.

#### Embers and Hill Stalkers: Wu Huan

- Wu Huan's Yellow Turbans generate **Embers** from the Ember Shrine building chain: Hidden Shrine, Ember Shrine, Sanctuary of the Southern Spark, Great Sanctuary of the Ember, then Inferno of the Yellow Sky.
- **Hill Stalkers** lets his armies ambush while attacking, with a chance based on the ground.
- Wu Huan has a 26-mission starting chain.

#### Languor: Wang Sheng

- **Languor** rises steadily on its own, from killing members of the Sun clan and from marrying Lady Wu, and falls with almost any action, battle or war.
- The **Hall of Repose** building chain raises public order and Languor, but increases corruption and reduces income from every source.

#### Web of Diplomacy: Chen Wen

- **Web of Diplomacy** grows with every member of Chen Wen's alliances (+10 per ally per turn) and with his Meeting Halls. It is spent on character actions such as Focused Tutoring and Call to Arms.
- Chen Wen has his own alliance, coalition and empire treaties, and his alliances unlock allied factions' signature units.
- His career gives +10 morale to his unique units and militia and +3 relations with Han Empire factions.

#### Depredation: Ze Rong

- Ze Rong's armies can take the Depredation stance to raid enemy territory for income, depending on the buildings in the region.
- A panel breaks down what each raiding army earns. When several armies raid the same region, only the highest earner pays.
- Ze Rong also has the Raiding Hubs building.

#### Contest of the Northern Captains

- Seven northern warlords race up a seven-level mission ladder: Gao Gan, Gongsun Du, Han Fu, Liu Dai, Liu Yu, Wang Kuang and Zhang Yang.
- A dedicated panel shows progress pips, current standings and who has been knocked out. The winner gains the Northern Captains' service.

#### Conquest and the Korean victory: Goguryeo

- Goguryeo gains **Conquest** by winning battles and inflicting casualties, and loses it through defeats and decay.
- Goguryeo gets three Korean campaign-victory missions.

#### Domestic and Foreign Affairs: Gongsun Du

- Two balancing resources. Battles against non-Han factions raise Domestic Affairs and lower Foreign Affairs, and battles against Han factions do the reverse.
- The Office of Affairs building raises both and can produce unique followers.

#### Path to Succession and Ancestral Legacy: Tuyuhun

- **Path to Succession** grows with victories and casualties on both sides.
- **Ancestral Legacy** is earned through the faction leader, heir posts and certain characters, and is spent to recruit, banish and release court members.

#### Keenness: Northern Wei

- **Keenness** is gained by winning battles and taking larger cities, and lost through defeats and decay.
- Northern Wei can use Coercion on Han and bandit factions.

#### Trailblazing: Di Tribes

**Trailblazing** grows with victories, enemy casualties and population, and falls with defeats, friendly casualties and decay.

#### Chaos and Undying Resolve: Wuhuan Tribes

- **Chaos** fuels invasion and pillage.
- **Undying Resolve** restores all movement when you take prisoners into your army.

#### Tributaries: Xiongnu Tribes

**Tributaries** is built through tribute. The Take Tribute diplomatic option pays into it, and the Xiongnu Staging Encampment adds tribute income, charge speed and cavalry replenishment.

#### Subservience and ambushes: Huang Zu

- **Subservience** is raised through new court positions that also improve ambush chance.
- Huang Zu's armies can ambush while attacking.

#### Insurgency and the Spymaster: Han Sui

- **Insurgency** is Han Sui's resource.
- Han Sui gets the Wu Hu Warband unit.
- A Spymaster court post raises cover gain, maximum cover and spy numbers.
- His espionage building chain runs Eavesdropper's Shack, Informant's Safehouse, then Espionage Ring.

#### Lord of the Sources: Song Jian (Liang Rebels)

- **Lord of the Sources** replaces the vanilla Liang Rebellion economy bundle.
- Song Jian has his own units, Hoarder of Sources (rank 6) and Defender of Ways (rank 3).

#### Celestial Masters: Zhang Lu

- **Celestial Masters** grows from Non-Believer through Follower to Devout Follower and beyond.
- Zhang Lu has a Taoist roster of sixteen units: the Tianshi and Wudou lines, Tao Penitents and Zhenren Defenders.

#### Integrate: the Liu clan warlords

Liu Yu, Liu Dai, Liu Yao and Liu Pan can **Integrate**, which annexes and absorbs Han Empire settlements.

#### Resource mechanics for the remaining Han factions

Each of these factions gets a unique resource with its own tiers, gained and lost as described, usually with a unique building or assignments:

| Faction | Resource | How it moves |
|---|---|---|
| Bian Rang | Rectitude | Raised by assignments; spent to buy officers and run assignments |
| Handan Shang | Firmness | Up with armies in the field, assignments and victories; down with defeats, governors, military access and non-aggression pacts |
| Huang Clan | Supervision | Up with assignments, non-aggression pacts and military access; down with armies in the field and court posts |
| Jia Long | Gentry Support | Up with Gentry assignments, Country Estates and wins against non-Han factions |
| Kong Zhou | Harmony | Up with assignments, high satisfaction and Poetry Halls; down with low satisfaction and armies in the field |
| Liu Dai | Siegecraft | Up with battles, enemy casualties and assignments; Guard Granary building |
| Liu Yao | War Fatigue | Up with battles, casualties and war; eased by assignments and the Labour House |
| Lu Kang | Jurisdiction | Up with governors and while a vassal; down with armies that are not garrisoned |
| Ma Ai | Mercantilism | Up with assignments and trade agreements; down with armies and governors |
| Gao Gan | Impenetrable | Up with defensive victories; down with defeats; Conscription Office building |
| Sheng Xian | Inner Circle | Up with good relationships and buildings; down with each character in the faction |
| Wang Lang | Erudition | Up with low-level characters and assignments; University of Cultivation building |
| Wu Jing | Fraternity | Up with victories, enemy casualties and family members in the faction |
| Yang Feng | Rebellion | Up with aggressive and raiding stances and offensive victories; down with defensive stances |
| Zhang Chao | Method and Flow | Up with assignments, satisfaction and rank; Calligraphy Schools building |
| Zhang Yang | Capability | Tiers from Incompetent Fools to Soaring Hawks; Specialised Forge building |
| Zhuge Xuan | Heavenly Balance | Up with offensive battles and assignments; down with defensive battles |
| Cai Mao | Preparation | Military assignments improve generals, units and relations with Liu Biao |
| Gan Ning | Youxia | Up with offensive victories, sharing the spoils and certain settlement actions |
| Zu Lang | Independence | Up with defensive victories and assignments; down with defensive defeats and decay |

#### Eight Princes systems given to 190 factions

Five 190 factions reuse mechanics from the Eight Princes campaign:

- Han Fu gets Sima Yue's Influence, the Military Emissary and Provincial Advisor posts, and Attitude Manipulation.
- Wu Ju (Yulin) gets Sima Jiong's Control, captain retinues and his court.
- Chen Gui gets Sima Lun's Subterfuge, the Judiciary building, Coercion and Instigate Proxy War.
- Su Dai gets Sima Ai's Reformation, with a reworded description focused on income rather than research.
- Wang Kuang gets Sima Wei's Fury, plus the Reward the Nobility and Rally Conscripts assignments.

#### Yellow Turban Embers

He Yi, Gong Du and Huang Shao lose their vanilla Dominion faction traits and use **Embers**, a resource that decays over time and brings penalties at low levels. It is fed by population (He Yi), battle loot and raiding (Gong Du) and research (Huang Shao). Huang Shao gets his own copy of the Yellow Turban technology tree. Yellow Turban factions can now have children and adopt.

#### Vassal Contracts (all factions)

- Every vassal pair carries four tribute dials: Family Estate (background income), War Loot, Taxes and Trade. Each can be set to 0, 10, 20, 35 or 50%. Yuan Shu and Dong Zhuo may also set 75% or 100%.
- The dials are set from a new Vassal panel on the faction header. Changes are staged and applied together, and then lock for 5 turns. Every pair is locked for the first 3 turns of a campaign.
- Heavier tribute lowers the vassal's attitude toward its master. The breakdown shows it as one "Vassal Contract" line, from +5 per dial at 0% to −12 at 50% (and −30 at 100%).
- The 190 vassals start with set terms. For example, Liu Pan pays 50% estate, 35% loot and 10% taxes and trade to Liu Biao, and the Han Empire pays Dong Zhuo 100% estate, 75% taxes and 50% trade. Liu Xun now starts as Yuan Shu's vassal. Any other vassal starts at 20% on every dial.
- Vassals have a **Liege Bond** (0 to 100) that follows the master's attitude and the tribute paid. From tier 4 the vassal is Liege Bound: the master can neither annex nor release it, and must join any war declared on it.
- A player vassal can ask its master for a task once a year, and masters also send tasks unasked. Tasks lower a dial when completed and cost attitude when failed.
- Masters can annex a vassal after 10 turns if both share a subculture and attitude is Best Friends (150+). They can merge two vassals, and can gift 1,000 to 25,000 gold.
- A player vassal can win the campaign through its master: the master needs 3 emperor seats and the master's whole realm needs 95 counties.
- Vanilla's fixed 20% vassal tribute is removed from the vassalage treaty, because the dials replace it.

#### Offspring Raising (all factions)

- A new Offspring tab in the court panel lists every child in your court.
- Children pass through Infancy (0–5), Schooling (6–10), Youth (11–14) and Coming of Age (15).
- In each trait stage you pick one of six activities: Hunting, Study, Court, Farm & Craft, Temple or Drill. The activity sets the personality trait in that stage's slot. A stage left undecided has a 35% chance of a negative trait.
- At 15 the child takes an item (weapon, armour, mount, follower or accessory) or a career. Forty famous children are offered a historical heirloom instead.
- A badge on the Court button and an event with the child's portrait tell you when a decision is waiting. AI factions raise their children the same way.

#### Orphans of fallen houses

When a faction dies and its children come into your care, you are asked about each one in turn: raise the child yourself, or send them to another house of their own subculture. Your place in the queue survives a save and reload.

#### Reworked historical mission chains (Path of Glory)

- Thirteen vanilla factions get reworked historical mission chains with new "Path of Glory" reward bundles (49 in total) and targets adjusted for the 190 Expanded map: Cao Cao, Dong Zhuo, Gongsun Zan, Kong Rong, Liu Biao, Liu Chong, Ma Teng, Sun Jian, Tao Qian, Yuan Shao, Yuan Shu, Zhang Yan and Zheng Jiang.
- Examples: Ma Teng's first target becomes the Di Tribes, Yuan Shu's second becomes Chen Wen, and Liu Biao's third asks for an alliance with Liu Bei instead of confederation.
- Liu Chong's "Unite Chen" step now asks for the Chen capital and his home county.
- The 15 modified tutorial scripts give reward bundles that last 6 or 10 turns instead of 3.
- Every new playable faction has its own start and tutorial scripts.

#### Unique buildings and assignments for other factions

| Faction | Unique feature |
|---|---|
| Hua Xin | Offices of Merit: a Prime Minister slot, income, less corruption |
| Wu Jing | Forward Encampment: income in adjacent commanderies, higher starting rank for units |
| Ying Shao | Teaching Assignment: experience for characters in the local and adjacent provinces |
| Ni Xiaode (Nanhai) | Military Supervision assignment and Military Security buildings |
| Zhao Wei | Government Support: peasant income and farm food |
| Liu Chong | Chen Kingdom Garrison: Chen Militia Patrols up to the Fortress of the Chen Kingdom or Pride of Chen, granting Prestige and Fortitude |
| Shanyue factions | Shanyue Camp settlement option: food from banditry, bandit-network research rate |

---

### Governance

#### Faction Council

- Around ninety new suggestions join the seasonal council meeting.
- **Economy and court:** Mint New Coinage, Patronage of the Arts, Tax Amnesty, Open the Granaries, Retrench the Court, Grant Land to the Gentry, Levy the Corvée, Promote Industry, Commerce, Peasantry or Culture, Court Examination and Reassess the Rolls.
- **Military:** Reward Heroism (6,000 experience for a recent victor), Grand Review of Troops, Quarter the Army, Contract Free Companies, Winter Provisioning and Post Riders.
- **Intrigue against rivals:** Spread Sedition, Blight Their Harvest, Buy Out Their Merchants, Denounce Them Abroad, Suborn Their Commander and Bribe Their Quartermasters.
- **Equipment searches** for a weapon, armour, mount, follower or accessory.
- **Faction-flavoured options** for about forty-five leaders, from The Longzhong Plan and King of Hexi to The Bandit Queen's Word, The White Horse Fellows and The Peace of Jing.
- The council now runs for all 62 playable Han factions in 190, not just vanilla's list.

#### The Bandit Council

- Bandit-subculture factions get a council of their own.
- Each Winter your seven seated ministers each offer two rival policies, and whichever you pick holds for 5 turns.
- The fourteen policies are Cheap or Expensive Incense Burning, Increase or Decrease Troop Share, Black Market or Traditional Channels Focus, Renowned Mercenaries or Extort Tributaries, Strict Discipline or Loose Ambitions, Offensive Maneuvers or Defensive Tactics, and Loot Requisition or Press Gang.

#### The Grand Tournament

- Chosen from the council, the tournament runs for a full year in five stages.
- Pick a martial discipline in spring. Your highest-ranked undeployed general of that class becomes your champion.
- Four seasonal bouts then ask whether each victory serves the dynasty, the champion or the crowd, and each answer has its own consequences. A champion can come away injured.

#### Governor Edicts

Gongsun Zan's inspectors enact regional edicts. See Governor Edicts under Faction mechanics.

#### Court

- New court categories: the **Five Tiger Generals** for Liu Bei (tied to Path to Unity), the **Five Wei Elites** for Cao Cao and the **Four Hebei Elite** for Yuan Shao.
- A **Korean court screen** with 15 offices, such as Grand General of the Armies, Minister of Inspections, Prime Chancellor of the Realm and Minister of Horse Management, and a matching faction progression panel.
- The cap on total assignments per faction rank is raised from 10 to 999 at every rank.
- Relationship caps are raised: acquaintances from 11 to 300, and friends and rivals from 7 to 200.

---

### Units & rosters

#### New units by group

| Group | Units | Count |
|---|---|---|
| Korean shared roster | Peasant Spears, Peasant Clubs, Hunters, Long Spear Militia and Warriors, Axe Militia and Warriors, Trained, Veteran and Noble Bowmen, Imported Crossbows, Mounted Bows, Scout Cavalry, Pillager and Noble Pillager Cavalry, Hwandudaedo Guard Cavalry, Spear Defenders, Arrow Storm and others | 21 |
| Korean polity units | Gaya, Baekje, Silla, Dongye, Tamna, Buyeo and Goguryeo (Highland Tribesmen, Highland Lancers, Highland Noble Lancers, Highland Noble Cataphracts, Goguryeo Kingsguards) | 17 |
| Faction-leader units | Two per southern warlord, Liu vassal and Yellow Turban splinter, plus Liu Bei's pair | 40 |
| Han provincial units | Two per Han province, recruited through the provincial hubs | 28 |
| Frontier regional units | Wuhuan, Xianbei, Xiongnu and Korean frontier troops | 13 |
| Other faction units | Units for the other added and newly playable factions, including crossbow units such as Silent Mists, Yan Crossbow and White Dragon Crossbowmen | 66 |
| Zhang Lu's Taoist roster | Tianshi and Wudou lines, Tao Penitents, Zhenren Defenders | 16 |
| Nomad garrisons | Untried, Hardened and Sworn Blades, Warriors, Spears, Shields, Brutes, Archers, Skirmishers, Riders and Nobles | 25 |
| Di Tribes | Di Cataphracts, Di Horse Archers, Di Marauders, Di Raiders | 4 |
| Levies and militia | Zealot militia (6) and Farmland militia (4) | 10 |
| Siege engines | Rapid Dragon Crossbow and Whirlwind Trebuchet, each with a bastion version | 4 |
| Others | Tiger Riders, Xiliang Commander, Song Jian's Hoarder of Sources and Defender of Ways, Han Sui's Wu Hu Warband, and two Xiahou Yuan units for the later starts | 7 |

#### Faction-leader units

Most faction-leader units unlock at character rank 3 and rank 6:

- **Gaya:** Ingot Breakers, Iron-Plate Guard
- **Baekje:** Border Raiders, Yocha Stormers
- **Silla:** Cloud-Readers, Fortress Wardens
- **Dongye:** Dan-gung Archers, Three-Zhang Spears
- **Tamna:** Samseong Ponies, Strait Raiders
- **Buyeo:** Household Levy, Ma-ga Lancers
- **All Korean factions:** Arrow Storm, unlocked by the Crown of War technology rather than by rank
- **Shi Xie:** Jiaozhi Javelineers, Jiaozhi Longbows
- **Qu Pan:** Jiuzhen Tigers, Jiuzhen Elephants
- **Shi Huang:** Cangwu Shieldwall, Cangwu Breachers
- **Fei Zhan:** Yue Archers, Forest Axes
- **Zhang Xian:** Lingling Spears, Lingling Swordguard
- **Pan Lin:** Shanyue Hunters, Dread Spears
- **Liu Pan:** Changsha Raiders, Changsha Stalkers
- **Liu Xun:** Lujiang Archers, Lujiang Shieldguard
- **Ni Xiaode:** Nanhai Marines, Pearl Halberdiers
- **Zhu Fu:** Wuling Improvisers, Inconstant Guard
- **Bian Rang:** Scholar Crossbows, Retainer Spearguards
- **Su Dai:** Hired Marksmen, Caravan Wardens
- **Lai Gong:** Gaoliang Levies, Watch Archers
- **Wu Ju:** Storm Axes, Tempest Glaives
- **Zhang Jin:** Vermilion Archers, Meridian Halberdiers
- **Wu Huan:** Jiangdong Zealots, Faithful Archers
- **Huang Zu:** Jingzhou Ambushers (with a unique Devastating Ambush), Veteran Ambuscader
- **Cai Mao:** Jingzhou Marines, Elite Naval Vanguard (with a unique Naval Support bombardment)
- **Hu Mao:** Prefect's Watch, Vigil Repeaters
- **You Tu:** Jiangdong Stormbreakers, Yue Enforcers

Liu Bei no longer recruits Yi Archers and Yi Marksmen. He gets **Crossbow Militia** (no rank requirement) and **White Feathered Riders** (rank 5) instead.

Among the stronger new units, Highland Noble Cataphracts cost 2,025, Jiuzhen Elephants 1,900, Di Cataphracts 1,800 and Ma-ga Lancers 1,750. The Lujiang Archers and Inconstant Guard carry standard infantry health (86,400 for the body), the same as Azure Dragons.

#### Regional recruitment

- **34 provincial recruitment hubs** sit in each commandery's side slot. There are Han hubs for Bing, Ji, Jiao, Jing, Liang, Qing, Sili, Xu, Yan, Yang, Yi, Yong, You and Yu, with tribal variants such as Bing-Xiongnu, Liang-Qiang, Yang-Yue, Yi-Nanman and Jiao-Vietnam. The Korean Frontier Works hubs are Samhan, Samhan-Yemaek, Yemaek, Yemaek-Xianbei and Yemaek-Han.
- Each Han province offers two regional units, such as Youzhou Brutes and Wusun Auxiliaries (You), Chu Blademasters and Jingzhou Noble Guards (Jing), or Storms of Lu and Sages of the Analects (Qing).
- A regional set is not tied to any faction leader: Yemaek Valley Warriors, Yemaek Scouts, Samhan Raiders, Samhan Assault Infantry, Lelang Guards and Daifang Defenders.
- **Tribal recruitment buildings** (Qiang Conscription, Xiongnu Hordes, Xiliang Horse Breeding, Yue Hunting Grounds, Xianbei and Wuhuan Horse Grounds, Chu Recruitment and Qi Ranged Recruitment) are open to the Han, Korean, Yellow Turban and Nanman cultures.
- For human players, some units can only be recruited in their home regions.
- Qiang Hunters and Qiang Raiders stay exclusive to Ma Teng (and to Han Sui at rank 6). The hubs and the Qiang Conscription building offer only the Qiang infantry and Qiang Marauders.

#### Changes to vanilla units

The full list is in the appendix. The main pattern is that every hero and general unit is standardised by class:

| Class | Charge | Missile block | Morale | Shield defence |
|---|---|---|---|---|
| Vanguard (fire) | 334 | 20% | 50 | 15 |
| Champion (wood) | 154 | 20% | 50 | 15 |
| Sentinel (metal) | 190 | 50% | 50 | 15 |
| Commander (earth) | 215 | 50% | 50 | 15 |
| Strategist (water) | 134 | 35% | 50 | 15 |

- 211 hero and general units gain the shield defence and missile block above, 187 have morale set to 50, and 176 have charge set to their class value.
- Strategists benefit most: charge rises from 34 to 134, morale from 23 to 50, and missile block from 0 to 35%. Guo Jia, Jia Xu, Pang Tong, Xun Yu, Lu Zhi and Diaochan are examples.
- Some heroes lose on these changes: Prince Liu Chong's morale falls from 65 to 50, and the generic Champion general's charge falls from 215 to 154 and morale from 60 to 50.
- 107 hero units carry 30 ammunition instead of 10 to 13.
- Every vanilla unit gains one or more abilities that character skills can enable. For example, the Steel Bastion passive is attached to all 489 units, and hero units gain the new hero-skill abilities such as Downpour, Guard, Blade Dance and Paired Resonance.
- Prince Liu Chong's unique crossbow swaps its numbers: 720 base damage and 1,350 armour-piercing damage, instead of 1,350 and 720.
- The hero version of the burning mace uses the hero burning-weapon effect instead of the unit one.
- The White Tiger's Claws now display their own weapon models.
- Tiger mounts are registered as mounts, which is what the new Tiger Riders unit uses.

---

### Buildings

#### Nomadic settlements

A complete building set for the steppe tribes, in five districts:

- **Settlement Administration:** eleven tiers, from Deserted Camp through Nomadic Camp and Nomadic Host to the Royal Encampment.
- **Nomadic Crafts:** Yurt Maker (up to the House of White Felt), Cart Wheeler (up to the Rolling City, with a War Cart branch), Spinner's Yurt (up to Silk of the Steppe), Blacksmith's Workplace and Carpenter Yurt. The Blacksmith and Carpenter produce equipment.
- **Herds:** Goat Herders (up to Sea of Herds, with a hides branch), Shepherds Camp (up to Golden Flocks).
- **Trade:** Bartering Grounds (up to the Gate of the Silk Road, with a Horse Fair branch), Wine Trader (up to the Feast Hall of the Khan), Treasurer.
- **War camp and culture:** Warriors Yurts, Campfires, Storyteller Yurt, Lightning Shrine, Noblemen's Camp.
- **Side buildings:** Cavalry Training Grounds, Herding Pastures, Raiding Hub.
- Captured Han buildings convert to their nomad equivalents where one exists, and nomad settlements have their own garrisons.

#### Faction buildings

| Faction | Building chain |
|---|---|
| Gao Gan | Conscription Office (Military Conscription): replenishment, less population |
| Gongsun Du | Office of Affairs |
| Liu Yu | Drifter Workforce Camp (Artisan Labour): population capacity |
| Liu Yao | Refugee Shacks (Labour House): population, less War Fatigue |
| Jia Long | Country Estates: family estates, income, Gentry Support |
| Kong Zhou | Local Tutor (Poetry Halls): Harmony, culture income |
| Wang Lang | Village Tutor (University of Cultivation): income, lower salaries |
| Zhang Chao | Calligraphy Schools |
| Zhuge Xuan | Tutor's Shack (Specialised School): culture, industry and commerce, experience, garrison |
| Chen Wen | Rest Stop (Meeting Halls): Web of Diplomacy, unit capacity |
| Sheng Xian | Officer Lounge |
| Liu Dai | Supply Sheds (Guard Granary): siege defence, replenishment |
| Wu Jing | Meeting Lodge (Forward Encampment) |
| Hua Xin | District Court (Offices of Merit) |
| Zhang Yang | Local Smithy (Specialised Forge): ancillary chance, replenishment, industry |
| Ze Rong | Raiding Hubs |
| Han Sui | Eavesdropper's Shack, Informant's Safehouse, Espionage Ring |
| Xiongnu Tribes | Xiongnu Staging Encampment |
| Liu Chong | Chen Kingdom Garrison (8 levels) |
| Wang Sheng | Hall of Repose |
| Wu Huan | Ember Shrine |

#### Shared buildings

- Han factions get three new side-slot chains: Forager's Camp, Mustering Field and Merchant's Camp.
- Korean side buildings: Hunter's Den, Roads, Watch Tower.
- The 34 provincial recruitment hubs described under Units & rosters.

#### Building availability

- Bandit and rebel factions (28 faction entries, counting separatists) use the bandit building set instead of the default one, among them Zhang Yan, Zheng Jiang, Gan Ning, Zu Lang, Yang Feng and the Shanyue Rebels.
- Faction-unique chains replace the matching standard chain for their faction only.
- 97 levels of vanilla resource buildings now count toward unlocking a settlement's secondary slots (4 points each instead of 0).
- Pass (gate) settlements can be damaged.
- Some garrisons from resource buildings, Tao Qian's resource garrisons and Yellow Turban temples are removed (16 links), and 459 vanilla retinue slots start with different units. Resource-building garrisons now field the mod's veteran units, such as Armoured Archers, Veteran Sabre Infantry, Veteran Sabre Cavalry and Veteran Lance Cavalry.

---

### Technology

- **A Korean technology tree** replaces the borrowed one. It has three branches of 20 technologies each: Court, from Those Beneath the Crown to Crown of Sidansu; Military, from First Muster to Crown of War; and Economy, from Economic Foundations to Riches from Distant Shores. Crown of War, the last Military technology, unlocks the Arrow Storm.
- In the 217 start, Korean factions use technology trees adapted from the Eight Princes civic, military and espionage trees.
- **Huang Shao** gets his own copy of the three Yellow Turban trees (60 technologies), so his missions point to his own techs.
- The 217 start gets full Han and Yellow Turban tree sets.
- 144 new building-to-technology requirements gate the new buildings, and 345 new technology effect rows back the new trees.

---

### Items, traits & careers

#### New items

| Category | New items |
|---|---|
| Unique armour | 549, one per added character |
| Careers | 1,027 unique careers |
| Weapons | 16, including Warlord's Bane, Dragon's Defiance, Tiger Cleaver, Zhanmadao, Avengers, Bloodfest, Zhanlu and Yuchang, and the Tiger Hooks and Lion of Yangping Hooks |
| Accessories | 10, including Commander Lu, The Manual of Concealing Method, Xiang'er, the Eight Immortal Gourd, a crossbow line (Common to Exceptional) and a Tribal Recurve Bow |
| Mounts | Wuhuan Stallion, Xianbei Warhorse, Xiongnu Galloper (all Exceptional) and General Hu |
| Followers | 22, such as the Pirate Captain, Shanyue Assassin, Defected Chanyu, Wuhuan Headsman, Xianbei Clan Head, Goguryeo Blade Master, Silla Bow Commander, Beastmaster and Wandering Craftsmen |
| Faction collections | 69 Liu Yu tribal cards, 42 new Lü Bu warrior trophies, 35 Liu Bei patron stages |

- Each faction starts with 2 to 4 ancillaries by default. The range can be set in the mod options.
- Characters start with more ancillaries by wealth. The default maximum drops from 3 to 2, but every wealth tier now allows up to 2 (up to 3 at the top two tiers), and tiers 4 to 9 guarantee at least one.
- Han strategists can no longer equip the Yellow Turban faction-pool two-handed maces. Yellow Turban healers keep them, including those serving a Han faction and in every start date. Strategists written with their own mace (Lu Kang, Wei Huang and Huang Ang, among others) keep theirs.

#### Changes to existing items and careers

- **Unique armours:** 19 unique armours that repeated an attribute from the wearer's own skill tree now carry a different one. For example, Liu Bei's armour changes from Encourage to Immune to morale penalties, Huang Gai's from Scare to Fatigue Immunity, Yan Baihu's from Stalk to Snipe, and Xu Sheng's from Disciplined to Immune to Fear & Terror.
- **Morale careers:** 88 careers that gave flat morale now give a larger bonus to a matching group of units, chosen by the character's element and record. For example, Zhu Jun changes from +8 morale to +12 morale for elite units, Han Dang from +2 to +7 for shock cavalry, and Diaochan from +4 to +8 for militia ranged units. Zhang Jue gives +5 morale to Yellow Turban units.
- **Satisfaction careers:** 58 careers that gave flat satisfaction now give it to one class. For example, Sima Ying gives +10 satisfaction for strategists, and Mangyachang gives satisfaction for Nanman.
- **Renamed career:** Ying Yang Delian's career changes from Chess Grandmaster to Master of Harmonies.

#### Traits

- The veteran traits come sooner. The high-kills threshold drops from 250 to 150 kills, "many battles fought" from 10 battles to 5, and old age is reached at 75 instead of 65.
- Captive and battle outcomes award more trait points in several cases. For example, executing captives now gives 2 points instead of 1 to earth and water characters.
- Cruel and Kind personalities push half as hard on sparing or killing a defeated duel opponent (±50 instead of ±100).
- Yellow Turban armour upgrades and learning traits follow the character's origin rather than the faction. Yellow Turban characters keep them in any faction, and non-Yellow Turban characters in Yellow Turban factions do not get them.

---

### Interface & quality of life

- **Ironic Menu:** a new hub on the top menu bar. It opens the Character Joins list (every general who can join Cao Cao, Sun Jian, Sun Ce or Liu Bei, with their join window and status), the Character Births list and the Mod Guide.
- **Character Compendium:** an info menu showing a selected character's birth year, spouse and active effects, and a table of notable historical birth years.
- **Faction panels:** new panels for Nomadic Hordes, Ma Teng's Stables, Governor Edicts (with a map of edict coverage), Lü Bu's duels, You Tu's Black Market, Zhang Jin's Needle Path, Zhu Hao's doctrines, the Northern Captains, Vassal Contracts, Ze Rong's raid income and the Bandit Council. Most open from a faction-header button.
- **Spy status badges:** each character shows a counter-espionage read: confirmed spy, suspect, willing or unwilling to be turned, cannot be turned, or unknown.
- **Mute a commandery:** a checkbox on the province panel silences a commandery's notification badges and upgrade markers. Up to eight can be muted at a time.
- **Dismissal confirmation:** releasing a character from service asks you first.
- **Tooltips:** horde building costs and Ze Rong's raid income appear in the standard hover breakdowns.
- **Mod conflict warning:** the game checks for known incompatible mods (TUP, TROM, WU Kingdassance, NGC, Radious, AFP, Nanman Chief, UAD, Gathering Heroes, Koihime and the Year mod) and shows a warning listing any it finds.
- **Mod options in the campaign:** the options panel is available from the in-campaign menu as well as the main menu, and many settings apply the moment you press Apply.
- **New-campaign screen:** the map is shown by default and the character list can be toggled. Frontend entries with unlocalised names are hidden.
- **Idle experience:** characters with no court post and no real assignment earn 100 experience per turn, alongside the vanilla 250 for a post and 500 for an assignment.
- **Recruitment from turn 1:** unit recruitment is available on the first turn instead of the second.
- **End-turn warnings:** the "projected negative income from diplomatic payments" warning no longer blocks ending the turn and can be suppressed.
- **Save protection:** the mod keeps its large saved data out of the game's 64 KB saved-value limit, so crossing the limit no longer silently wipes every mod's saved state. Each save also writes a recovery snapshot of that data next to the game executable.
- **Debug log:** an optional per-faction, per-session log file that is never overwritten, controlled from the mod options.
- **Developer console:** a Lua console button on the menu bar for testing and troubleshooting.
- **Multiplayer:** every mechanic's script runs identically on both machines in multiplayer, so the Nomadic Hordes, Stables, Edicts, Needle Path, Black Market, duels and the other panels no longer desync co-op games. Mod options in multiplayer apply once at campaign load, so both players need matching settings.

---

### Mod options (MCT)

The Mod Configuration Tool is strongly recommended; without it you cannot change these settings. Options in **190E Frontend** take effect on the next new campaign. The other sections apply during a campaign.

| Option | Section | Default | What it does |
|---|---|---|---|
| Historic mode | 190E Frontend | On | Wu Anguo and Hua Xiong die at the start, as in history |
| Looters take empty land | 190E Frontend | Off | Seeds Looter armies onto unowned land |
| Nanman choice | 190E Frontend | Off | Destroy the Nanman, have one faction control all, or split them into three (work in progress) |
| Lü Bu on the field | 190E Frontend | Off | Starts an AI Lü Bu as his own faction, with Gao Shun's army, instead of under Dong Zhuo |
| Sun Ce on the field | 190E Frontend | Off | Keeps Sun Ce as his own faction instead of folding into Sun Jian |
| Total War mode | 190E Frontend | Off | The player goes to war with every faction they meet |
| Multiplayer mode | 190E Frontend | Off | Skips the turn-1 setup changes |
| Spawn all characters, turn 1 | 190E Frontend | Off | Spawns every character on turn 1 |
| Min starting ancillaries | 190E Frontend | 2 | Minimum ancillaries each faction starts with (0–100) |
| Max starting ancillaries | 190E Frontend | 4 | Maximum ancillaries each faction starts with (0–100) |
| Scripted lord confederations | 190E Options | On | Master switch for the four scripted confederations below |
| Yuan Shao confederates Han Fu | 190E Options | On | Happens on turns 3–6 |
| Yuan Shu takes Kong Zhou | 190E Options | On | 191–195; required for the next two |
| Cao Cao confederates Liu Dai | 190E Options | On | 192–195 |
| Yuan Shu takes Chen Wen | 190E Options | On | 193–199 |
| Take gold from destroyed factions | 190E Options | Off | Take 25%, 50%, 75% or 100% of a destroyed faction's gold |
| Take equipped items | 190E Options | Off | Also take items that were equipped |
| Items to take | 190E Options | None | None, or up to Common, Uncommon, Exceptional or Legendary items |
| Absorb characters | 190E Options | Off | Absorb all non-generic characters from a destroyed faction |
| Prevent AI forced march | 190E Options | Off | Stops AI armies using forced march |
| Allow Wooden Stakes | 190E Options | Off | Leave off to remove the stakes deployable from every faction, since it can crash battles |
| Debug log | Debug | Off | Keeps a separate log per faction and session |
| Verbose log | Debug | Off | Also captures engine output and script errors |
| Write log marker | Debug | Button | Writes a marker line into the log |
| Player boosts | 190E Boosts | 0 (off) | Character experience, research, income and movement in +25% steps up to +200%; replenishment +5% steps to +50%; public order +2 steps to +20; character costs −5% steps to −100% |
| AI boosts | 190E Boosts | 0 (off) | The same seven boosts for every AI faction, set separately |
| Cheat toggles | 190E Cheats | Off | +999 prestige per turn, army slots, spy slots, trade agreements, governor posts or assignment slots (the game still caps assignments at 10) |
| Treasury | 190E Cheats | Button | +100,000 gold now |
| Rank ups | 190E Cheats | Button | Unlocks rank-ups without the prestige requirement |

- Boosts and cheats take effect at the start of the affected faction's next turn.
- Lowering a boost or unticking a cheat removes it again.
- The cheat buttons are disabled in multiplayer.
- If MCT already has a settings file from an earlier version, options that default to On may appear unticked until you tick them and press Apply.

---

### Balance changes to vanilla content

#### Economy and campaign values

- Base faction income (the flat "other" income) rises from 2,000 to 2,500 for major factions and from 1,000 to 2,000 for minor factions.
- Base land replenishment rises from 4% to 6%.
- Provinces start with 10 military supply instead of 5.
- Random spouses are aged 17 to 30 instead of 25 to 35.
- Bandit factions no longer lose 5 military supply per turn in their own territory.
- The Liang Rebellion economy bundle no longer halves character salaries or removes building and retinue upkeep, corruption and food distribution costs. Song Jian's Lord of the Sources resource replaces it.
- Yuan Shu's character-recruitment conversion rate rises from 20 to 50, and his Emperorship payload now lasts 10 turns instead of 0.
- Sima Jiong's character-recruitment conversion rate rises from 10 to 20.

#### Diplomacy

- Han and Nanman factions start with −10 attitude toward each other instead of +10.
- Vassals no longer pay a fixed 20% of their income; Vassal Contracts set tribute instead.
- The Liu Biao vassal treaty's tribute is removed for the same reason.
- The AI's non-aggression, military access and trade-monopoly goals now propose the mod's variants of those treaties.
- You Tu can confederate bandits; the Huang Clan and Zhang Jin can sign non-aggression and military access pacts with bandits.
- Chen Wen's alliance, coalition and empire treaties behave like Yuan Shu's and Yuan Shao's special versions.

#### Campaign behaviour

- Non-Nanman armies no longer receive the jungle penalty in Nanman regions (Yunnan, Jianning and Yongchang). Nanman armies keep their jungle bonuses.
- Characters form relationships with up to 500 others when they spawn, instead of 20.
- A child coming of age no longer gains the automatic family-member relationship trigger.
- Cao Cao's schemes and the extended progression script run in the 217 start.

#### Units and heroes

See Changes to vanilla units under Units & rosters for the hero standardisation, Liu Chong's crossbow and Liu Bei's roster swap.

---

### Fixes to vanilla

- **Kong Rong's "01a" mission** named a faction that does not exist (`3k_main_yellow_turban_taishan` instead of `3k_main_faction_yellow_turban_taishan`), so the chain died if that branch was reached. It now points at the right faction.
- **Han strategists and two-handed maces:** the strategist equipment list included the Yellow Turban faction-pool mace group with no permission check, so any Han strategist could equip those maces. They no longer can; Yellow Turban healers keep access in every start date.
- **Liu Yan's Private Tutelage** worked out its experience reward from a fixed vanilla experience curve, which could hand out a negative amount when a different curve was loaded. It now reads the curve in use, never grants a negative amount, and refunds the ambition at the top rank.
- **Tooltip colours:** ability recharge and the Northern Army unit-cap effects now show reductions in green instead of red.
- **The burning mace hero weapon** now uses the hero burning-weapon contact effect.

---

See the [190 Expanded stat tables](#appendix-190e) appendix for every changed and new unit.


---

## Part 2: Campaign Overhaul

The Campaign Overhaul is the optional campaign half of the 190 Expanded Overhaul. It loads on top of 190 Expanded, so everything below is described relative to a normal 190E game. It slows the early game down and makes it more expensive: buildings take about twice as long to finish, characters need far more experience to rank up, the best units are gated behind the rank of the general recruiting them, and flat bonuses such as settlement commerce, trade influence from markets and free satisfaction from faction rank are removed. In return, what a character is and does counts for more. Attributes and personality traits now drive governor and minister output, governors scale with rank, and most economic bonuses are attached to a specific person, building or policy. Faction support, reserves and military supplies all now have real costs, and the AI gets a new set of personalities and difficulty handicaps so that it can keep up.

The pack changes 137 database tables and 9 campaign scripts. This page covers the patterns and gives representative numbers. The full value-by-value lists are in the appendix linked at the end.

---

### Economy & buildings

#### Settlements (the Settlement Administration chain)

- **Commerce bonus removed.** Settlement levels no longer give "+% income from commerce". In 190E this ran from +25% at a Large Town to +150% at the Imperial City. Across all culture variants, 95 settlement and market rows lose their commerce percentage.
- **Population capacity flattened.** Every level of the Han settlement chain now gives a flat **+7,500** population capacity. In 190E it grew from 200 (Small Town) to 4,000 (Large Regional City). Upgrading a settlement no longer raises its population cap. Damage no longer reduces it either, because the damaged and ruined values are also 7,500.
- **Reserves doubled.** Reserve capacity per settlement level is doubled: 10→20 (tiers 1-3), 20→40 (tiers 4-6), 30→60 (tiers 7-9) and 50→100 at the Imperial City. Damaged settlements keep their full reserve capacity.
- **More building slots at the top.** The Imperial City now gives 8 building slots (was 6). Its secondary-slot unlock value rises from 12 to 16.
- **Settlements now cost upkeep.** Settlement levels 3-10 now cost upkeep, from 15 at level 3 to 120 at level 10 (was 0 for all levels).
- **Walls now carry artillery.** The settlement itself now provides wall artillery (bolt throwers and trebuchets): 2+2 at Small City, 3+3 at Small Regional City and 4+4 at the Imperial City. This artillery has been taken off the Security buildings (Patrols, Guard Posts, the capital and province security chains, and Ma Teng's security chain), which lose all of their wall artillery. Pass forts shift from bolt throwers to trebuchets.

#### Where income comes from now

**Trade.**

- Markets no longer give trade influence. The Marketplace, the Bureau of Trading Associations, the trade ports, jade trade, artisan tools and tea gardens all lose theirs (79 rows).
- Trade influence now comes from settlement size instead. Towns give +4-6%, cities +10-14% and metropolises +20%.
- A new effect, **"+% income from trade agreements"**, appears on 89 building rows (for example Marketplace +2%, Bureau of Trading Associations +5%), on assignments and on several faction bonuses.
- Every faction now carries a base **-25% income from trade agreements**.

**Markets and inns.**

- The Marketplace now gives +40% commerce (was +75%) and the Bureau of Trading Associations +100% (was +150%).
- The Lodge gives +180 flat commerce (was 140) but loses its +50% commerce. The Grand Guest House gives +300 (was 200) and loses its +100%.

**Agriculture and industry.**

- Farms now add a percentage to peasantry income: Communal Grain Farms +60% and Grand Grain Estates +100%.
- Labour chains add industry income. Labourer Conscription Housing gives +60% industry, and the Office of Works gives +80% industry, +40% peasantry and -20% building upkeep.
- Labour buildings lose their big population-growth numbers. For example Office of Works growth is now +5 (was +100).

**Government.**

- The Magistrate gives +20% all income (was 15%). The Secretariat gives +40% (was 20%) and -20% character salary. The Directorate gives +60% (was 25%) and -40% salary.
- The Imperial Palace gives +120% income from all sources, +100 prestige (was 30) and -60% character salary. It loses +500 peasantry income and its palace-guard garrison upgrade.
- Prestige from administration buildings roughly doubles (for example County Office 5→10, Directorate 20→40).

- **Culture.** The Grand Academy gains +225 income (culture). Many schools and faction-unique schools gain culture income.
- **Cross-chain construction discounts halved.** Every "X buildings construction cost reduction" effect is halved: -10%→-5% and -15%→-10%. The Imperial Palace's economic discount drops from -50% to -10%.
- **Nanman-style Han chains** (the DLC06 variants, now renamed "Traditional Settlement Administration", "Traditional Marketplaces" and so on) lose their +% all income and research rate. They gain corruption reduction, building-upkeep reduction and character experience instead.

#### Construction time, instant-build cost and upkeep

- **Build times roughly double.** Most district buildings go from 1/2/3 turns to 2/4/6 turns per tier. Some high tiers are shortened instead (for example 6→4). The most common changes are 1→2 (70 levels), 2→4 (69 levels) and 3→6 (62 levels).
- **Instant construction costs double.** 501 building levels cost exactly twice as much to build instantly.

**Upkeep is rebalanced.** 136 building levels get more upkeep and 63 get less. For example:

- Government administration now costs 20/40/60/80 upkeep (was 0/10/10/10).
- The Yuan and decadence palace chains cost 40/80/120/160/500.
- Markets cost 15-75 upkeep (was 10-60).
- Craftsmen and high farm tiers get cheaper (for example Grand Grain Estates 110→100).

**Settlement level needed for each building tier has changed.**

- Tier 1 now needs settlement level 1 (was 4). Tier 2 needs level 3 (was 4).
- Tier 3 needs level 4-5, tier 4 needs level 6-7, and tier 5 needs level 9-10 (was 7).
- Early buildings open sooner and the top tier opens later.

#### Tech gates for buildings

**Han building tiers are now unlocked through the Reform technologies**, not individual tree technologies:

- **Centralised Storage** gates 11 building levels.
- **Division of Labour** gates 16.
- **Streamlined Governance** gates 18.
- **Centralised Labour** gates 45, including most tier 4-5 artisan, mint and workshop buildings.

- 102 building levels lose their tech requirement entirely. Most are faction-unique chains (Black Mountain, Gongsun Zan, Kong Rong, Liu Biao, Ma Teng, Cao Cao and Dong Zhuo conscription) and the whole Yellow Turban building set.
- 44 levels that had no tech gate now have one, including low tiers of markets, inns, schools, logistics and labour.
- Some technologies now need a building first. For example Mastery of Ceremonies needs a County Office, Garrison Conscripts needs a conscription building and Shock Warfare needs a horse ranch.

#### Resource buildings and provincial resources

Tier 4-5 resource buildings now need a provincial resource (23 new requirements):

- Grain, rice and tea farms need Tools.
- Livestock needs Farms.
- Fisheries need Lumber.
- Silk, spice, trading ports, horses and pine lumber need Entrepreneurs.
- Copper and bamboo need Industrialists.

- The Grand Silk Market (`3k_district_market_silk_trade_5`) now supplies Entrepreneurs.
- The resource-building changes follow the same patterns as above: flat and percentage peasantry and commerce income added, trade influence replaced by trade-agreement income, and cross-chain construction discounts halved.

#### Bandit buildings

- The Black Market add-on gives +200% income from banditry (was +50%).
- Bandit camps give a visible +500 population capacity. They lose their hidden population capacity and their food from banditry.
- Camp banditry income is 100/150 (was 75/125).
- Mountain, temple, jade and port-trade hideouts now give 50/100/150 banditry income (was 100/150/200).
- Bandit residential buildings (tiers 3-5) unlock **poison arrow towers**.
- Zhang Yan's Black Mountain administration can no longer be demolished (except by Yellow Turbans) and gains post-battle loot income.
- **Bandits can no longer build the Han market, inn, trade-port, artisan-labour, private-workshop or land-development chains.** They get the Yellow Turban versions of those chains instead.

#### Faction-unique buildings

The pattern-wide rebalance also covers the 190E faction buildings:

- Chen Wen's inns and Kong Zhou's and Zhuge Xuan's schools get more commerce and culture income.
- Gongsun Du's Office of Affairs becomes a corruption-reduction chain (-5% to -25%). Its income is trimmed: for example tier 5 gives +100% (was 120%).
- Liu Dai's granaries trade peasantry income for public order, faction support and ranged ammunition.
- Zhang Yang's equipment workshops lose industry income. They gain military supplies, and their final tiers become faction-unique.
- Zhang Lu's Taoist religion chain is reworked (more peasantry income, less food).
- Jie Fan's settlements gain wall artillery and population income.
- Wang Kuang's judiciary gains income but costs more public order.
- Gao Gan's conscription and Jia Long's estates get buffs.
- Liu Yu's labour buildings gain population capacity.

#### Regional (province) units

The province bonuses from 190E now also reduce upkeep and recruitment cost of that province's two regional units. The reduction applies per owned region and ranges from -1% (Yang, Yi) to -10% (Qing, Yan). Examples:

- Ji: Jizhou Noble Bodyguards and Cangting Rearguards.
- Liang: Xiliang Hammer Guard and Western Border Guards.

---

### Taxes & public order

Tax effects now depend on difficulty. Rows marked "Normal" and "Easy" apply only to a human player on those difficulties. The unmarked "base" row is the value otherwise.

| Tax level | Tax take | Public order (base / Normal / Easy) | Faction support per region (base / Normal / Easy) |
|---|---|---|---|
| Exempt | unchanged | 0 (was +25) | none |
| Minimal | unchanged | -1 (was +15) / 0 / 0 | +10 / +15 / +20 |
| Low | unchanged | -3 (was +6) / -2 / 0 | +5 / +8 / +10 |
| Normal | unchanged | -6 (was 0) / -4 / -2 | 0 |
| High | 115% (was 110%) | -10 (was -6) / -8 / -6 | -20 / -15 / -10 |
| Extortionate | 130% (was 120%) | -15 / -15 / -15 | -40 / -30 / -20 |

- Taxes no longer buy public order. Every level below Extortionate now costs public order. Low taxes help through **faction support**, and high taxes damage faction support heavily.
- The food-from-farming modifiers (+50% Extortionate down to -50% Minimal) are unchanged in value. They are now also listed again for Easy and Normal.
- The tax-rate display rows for Low and Minimal on Easy and Normal now read -15% and -30%.

**Outlaw (bandit) taxes** are rebuilt. Their old salary, satisfaction, retinue-upkeep and army-morale effects are removed and replaced by:

| Bandit tax | Public order | Corruption | Character XP | Morale (characters only) | Banditry income | Supplies (own territory) |
|---|---|---|---|---|---|---|
| Extortionate | +10 | +40% | -50% | +15 | - | - |
| High | +5 | +20% | -25% | +8 | - | - |
| Low | -8 | - | +50% | - | +200% | +5 |
| Minimal | -15 | - | +100% | - | +400% | +10 |

**Public order now affects faction support.** For Han, outlaw and Liu Yu public-order bands:

| Public order band | Faction support |
|---|---|
| Outraged | -20 |
| Unhappy | -10 |
| Troubled | -5 |
| Content | +1 |
| Happy | +3 |
| Jubilant | +5 |

Outlaw replenishment from public order is inverted: happy bandit regions now replenish +1% to +5%, and angry ones -1% to -5% (it used to be the reverse).

---

### Population & food

- **Settlement size gives trade, not food.** The population-size bands no longer change food production. They now give trade influence: 0-2% for villages, 4-6% for towns, 10-14% for cities and 20% for metropolises.
- Kong Rong's population bands, which already gave trade influence, are roughly halved (Metropolis 35-45% → 20%).
- **The "Scattered (0)" band is now a dead zone.** It covers populations of 0-6 only (was 0-50), but a region in this band **produces no income from any source**. The next band starts at 7 (was 51).
- **Food shortages hit income.** Food-shortage tiers 1-5 now cut peasantry income by -25%, -50%, -75%, -100% and -200%. They also drain reserves faster: -5/-10/-20/-40/-60 per turn (was -4/-8/-12/-16/-20).

**Reserves matter for the Emperor.** Food surpluses and shortages no longer change Imperial Favour directly. Your reserve level does instead:

- An Empty stockpile costs -1 favour.
- Full or Abundant reserves give +2.
- The favour factor is renamed from "Food Surplus/Shortage" to "Filled/Empty Reserves".
- Empty reserves also cut population growth by -40 (was -20).

- **Reserves supply armies less.** Military supplies from reserves are lower at every level: Limited +1 (was 6), Stable +5 (was 8), Full +10 (was 15), Abundant +15 (was 20).
- **Winter fertility.** Three new display bundles are added: High, Average and Low fertility (Winter). This pack gives them no effects of their own.

**Assignments.**

- Develop Farmland now gives +4 food and +25% food production (was +100% farming food and -2 agriculture build time).
- Re-settlement Programme now gives +100% peasantry income and +25% recruitment cost (was +4 food and +50% food).
- Surplus Distribution gives +4 food and +10 growth.

---

### Faction progression, legitimacy & faction support

#### Faction support

Low faction support now hurts much more. On Normal difficulty, for a standard human faction:

| Support band | Income (all sources) | Food production | Recruitment cost | Replenishment | Migration growth | Militia morale |
|---|---|---|---|---|---|---|
| None (0-20) | -80% (was -50%) | -80% | +80% | -8% | -12 | -6 |
| Low (20-40) | -50% (was -25%) | -50% | +50% | -6% | -6 | -3 |
| Medium (40-60) | -25% (was -12%) | -25% | +25% | -4% | -3 | -2 |
| High (60-80) | -10% (was -5%) | -10% | +10% | -2% | -1 | -1 |

- Easy halves most of these: for example -40% income, -40% food and +40% recruitment cost at None.
- Bandit, Liu Bei and Yuan Shu support bundles get the same treatment.
- Liu Bei's public-order penalty from low support is halved (for example -10 → -5 at None).
- The AI gets the same kinds of penalties, but softer, and they shrink as difficulty rises. At None support the AI gets -50% food and +50% recruitment cost. Its replenishment penalty falls from -8% on Easy to -2% on Legendary.
- **Regional support gain is fixed at 10 per round** for every faction on every difficulty. In 190E it ranged from 5 to 30, depending on faction and difficulty. Liu Bei also now spreads +5 support to emergent factions.
- A garrisoned army (Situation: Garrisoned or bandit Stance: Garrisoned) now gives +10 faction support to its region.

#### Faction rank and extended progression

- **Assignment slots are doubled** at every faction rank. This applies to Han (DLC07 extended progression), Yellow Turbans, bandits, Nanman, Eight Princes, Yan Baihu and Zheng Jiang ranks, for example 1→2 at rank 1 and 8→16 at rank 8.
- Character-experience bonuses from the assignment track rise (for example rank 8: +50% → +100%).

**Faction ranks no longer hand out free satisfaction.** Satisfaction is removed from:

- The Han warlord and emperor-contender ranks.
- The Han and Yellow Turban world-leader bundles.
- Cao Cao, Dong Zhuo, Gongsun Zan, Liu Bei, Liu Biao, Yuan Shao, Yuan Shu, Shi Xie, Nanman and Eight Princes ranks.
- The extended-progression Armies track (+5 to +15).

Other extended-progression swaps:

- **Armies track:** +1 to +15 seasonal retinue deployments replace satisfaction. At rank 8 it also gives +15% charge bonus, replacing -15% unit upkeep.
- **Governors track:** +2 to +18 food (prestige) replaces the salary reduction. Rank 8 adds +4 public order.
- **Trade track:** +2 to +18 diplomatic relations replace trade influence. Rank 8 adds +30% income from all sources.
- **Spies track:** more maximum cover (up to 25 at rank 8). Rank 8 adds +10 faction support.
- **Assignments track:** rank 8 gives -5% corruption.

#### Faction mechanics

- **Legitimacy (Yuan Shu) is re-themed.** The ranks are renamed Loyal Yuan / Yuan Clansmen / Dangerous Upstart / Usurper. The higher you climb, the more the Han distrust you:

| Level | Name | Key effects |
|---|---|---|
| 1 | Loyal Yuan | +20 relations with Han factions, +5 satisfaction, +5% salary, no public-order penalty (was -2) |
| 2 | Yuan Clansmen | -3% recruitment, -2% unit upkeep, +3% income, +5 Han relations, +10 satisfaction, +20 prestige (was 50) |
| 3 | Dangerous Upstart | -5% recruitment and upkeep, +20% income (was 10%), -25 Han relations, -3 Imperial Favour |
| 4 | Usurper | -30% recruitment and upkeep, +100% income (was 20%), +20 public order (was 9), -200 Han relations, -100 Imperial Favour |

The legitimacy cap rises from 400 to 600, and the level thresholds move (level 2 now starts at 16 instead of 26, and level 4 at 86 instead of 76).

**Heroism (Sun Jian):**

- The cap is 1,000 (was 200). The heroism decay and satisfaction effects are removed.
- Levels now give public order (up to +12), construction cost reduction (up to -20%) and recruitment cost reduction.
- The level thresholds shift up (level 3 is 56-90, level 4 is 91+).

**Unity (Liu Bei):**

- Levels no longer give prestige or administrator positions.
- They give corruption reduction (up to -15%), less desire for higher office (up to -50%) and more income (Harmonious +20%, One Mind +30%).
- Characters drain more unity (-5 and -2, was -2 and -1).

**Credibility (Cao Cao):**

- Low credibility levels now regenerate credibility (+2 and +1) instead of decaying.
- Imperial Favour from credibility is lower (Paragon +2, was +4).

**Cao Cao's schemes** are mostly toned down. They now target the scheming army directly and include new drawbacks:

- Hawk and Tiger Manoeuvres gives +100% movement (was +50%) but locks fatigue at Exhausted.
- Gift of Honour costs +1,000% salary (was +50%).
- A Cow for a Wolf now raises construction cost by +150% (was +15%).

**Infamy (Dong Zhuo):**

- Levels now worsen relations with Han factions (-10 to -30). This replaces the general diplomacy penalty.
- Levels give morale when attacking (+5 to +40) and charge bonus (+10 to +100). Legendary grants Terror.
- Infamy decays much more slowly (Legendary -4, was -16).

**Imperial Favour:**

- At low favour (10-50) you lose the satisfaction and corruption penalties. Han relations are worse (-40 at 10). Favour regenerates (+2/+2/+1/+1), and looting pays more (+100% settlement loot at 10).
- At high favour (70-100) favour slowly decays (-1 to -2), and satisfaction bonuses are larger (+20 at 100).
- Favour payloads are bigger: small gain +10 (was +3), large gain +20 (was +10), small loss -5 (was -3).

**Imperial decrees and aid:**

- Diplomatic Sanctions now give -50 Han relations and -5 satisfaction, replacing the tributary, trade and recruitable-character penalties.
- Economic Sanctions add -15% trade-agreement income.
- Food Aid adds +15% peasantry income.
- Military Aid no longer speeds mustering or replenishment.

**Restoring the Han vs A New Dynasty:**

- Restoring the Han now gives +25 faction support, but -10 satisfaction, +25% corruption and +25% desire for office.
- A New Dynasty gives -20% retinue upkeep, +15 satisfaction and +15% replenishment, and only -6 public order (was -15).

- **Dynasty Support (Empress He's government):** imperial units now start with -34% to +14% replenishment, depending on the support level. Each level gives +2 starting rank for imperial recruits, up to +10. The flat imperial-unit base bonus (+10 rank, +10% speed, -21% replenishment) is removed.
- **Yan Baihu's White Tiger confederation:** it loses its bandit-network cost reductions. It gains morale, charge, melee damage, evasion and diplomacy, and recruitment discounts rise (for example Empire -50%, was -20%).
- **Kong Rong's Trade Monopoly:** adds +5% to +50% trade-agreement income. Market forces drain faster (Dominating -52, was -20).
- **Liu Biao:** Governance domain extent is raised at every level (for example Supreme 32→38), and the Kingdom rank sets domain extent to 999.
- **Gan Ning's resource:** its charge bonus is converted from percentage to flat (+2 to +10%, plus +5 to +25 flat when attacking). It adds research rate (up to +100%).
- **Lu Bu (Chaotic Rule):** +1 army, -30% recruitment cost and -20% retinue upkeep.
- **Sun Ce (Men of Merit):** post-battle capture chance +5% (was +30%), salary -5% (was -20%).
- **Seat of an Emperor (the capital of a world leader):** +100% income from all sources (was 50%), +15 growth (was 5), +6 public order (was 4) and +25% trade-agreement income. It loses +100% commerce.
- **Prime Minister of the Han:** +30% tributary income, and peasantry income +25% (was 10%).
- **NPC economies:** the Han Empire faction, Yellow Turban remnants and rebels no longer get 100% free building and retinue upkeep (now -50% and -20%). The Han Empire faction gets -35 satisfaction and +200% desire for office. Liang rebels get a full set of upkeep and corruption reductions.

---

### Court positions & governors

#### Salaries

| Post | Human salary | AI salary |
|---|---|---|
| Minister | 225 (was 350) | 150 (was 50) |
| Minister (family member) | 200 (new) | 100 (new) |
| Governor | 125 (was 250) | 100 (was 50) |
| Governor (family member) | 100 (new) | 75 (new) |
| Court noble | 50 (was 150) | unchanged |
| Family member (no post) | 25 (was 0) | 25 (was 0) |

Players pay less for officials and the AI pays more. Family members are now a little cheaper in office than outsiders.

#### Governors

- **Governors no longer give a flat -30% corruption.** Their base corruption row is set to 0.
- **Governors scale with rank.** A new tooltip line says "The effects of your governors depends on their rank. At rank 4 and 7, the effects are improved." At the higher tiers they give +15% and then +20% income from all sources (bandit underlings +10%).
- **The army slot moves to the top tier.** Governors no longer give +1 available army at the lowest tier. They give it only at the highest governor tier.
- This applies to the default, Nanman, Shi Xie, Yellow Turban and Eight Princes governors, and to 190E's Jin Xuan jurisdiction and Chen Lan rebellion posts.
- Attributes now feed governor income directly (see Attributes below).

#### Ministers: personality traits matter

- **7,700+ new rows tie ministers' personality traits to effects in office.**
- 84 personality traits are covered. They apply across 39 minister posts: the five standard Han ministers (including the Dong Zhuo and Korean variants), Sun Ce's officials and commanders, Shi Xie's ministers, the bandit court and the Yellow Turban generals.
- **Unique courts added by 190E are covered too:** Hua Xin (10 posts), Huang Zu (5 posts), and Zhao Wei's prime minister and heir.

Typical effects:

- Ambitious ministers want independence and lose satisfaction.
- Greedy ministers add +5% corruption and +10% desire for higher office.
- Loyal ministers reduce independence ambition and desire for office.
- Brave ministers add morale.

- The most common effects across the set are satisfaction, public order, independence ambition, experience, desire for office, ambush defence, faction support, morale and charge speed.

#### Faction-specific court changes

- **Imperial and dynastic courts no longer spread their effects faction-wide.** This covers the Grand Commandant, Grand Excellencies of Works and over the Masses, General-in-Chief, and Grand Tutor for the Han Empire court, the bandit court, Sun Ce and Nanman/Shi Xie.
- The Nanman tribal council now applies its effects faction-wide.
- **Bandit court:** positional bonuses are replaced. Faction-wide posts now carry "no desire for higher office until rank 4/6/8/10". The Prime Minister and Right Hand can trigger a civil war if they defect. Small faction bonuses (+5% income, +5 morale, -5% recruitment and so on) are attached to specific posts.

**Gongsun Zan's Military Inspectors:** they lose -30% corruption. Each inspector now boosts a sector at levels 0/5/8:

- Earth: +25% / +25% / +50% peasantry income.
- Metal: industry income, same scale as Earth.
- Water: commerce income, same scale as Earth.
- Fire: -10% / -10% / -20% recruitment cost.
- Wood: +50% / +50% / +100% food.
- At levels 5 and 8 each inspector also slows construction of their building type by +1 turn.

- **Zhao Wei:** the five ministers become **Federation Leaders**, the prime minister becomes a **Key Advisor** and the heir becomes the **Confederation Inheritor**, who no longer has to be family. The Federation Leaders lose their faction-wide bonuses. The Key Advisor gets +20% income and +30% food (was 15% and 50%). The Inheritor gets -15% recruitment cost, +20% experience and +25% trade influence.
- **Liu Bei's Tiger Generals, Cao Cao's Five Wei Elite and Yuan Shao's Four Hebei:** these posts now give +10% melee damage, +10% speed and +10% armour respectively. Their melee evasion drops from 15 to 5 (Yuan Shao 3).

---

### Characters

#### Experience (scripted, `3k_campaign_experience.lua`)

| Setting | Before | After |
|---|---|---|
| XP per battle kill | 1.5 | 1 |
| Share of retinue kills counted | 0.75 | 2 |
| Winner multiplier | 2 | 1.5 |
| Loser multiplier | 1 | 2 |
| Duel: proposer wins | 2,500 | 1,000 |
| Duel: proposer loses | 100 | 500 |
| Duel: target wins | 100 | 1,500 |
| Duel: target loses | 100 | 1,000 |
| Duel: no winner | 10 | 500 |
| Faction leader's passive share of others' XP | 5% | 1% |
| Minister XP at level 3 / 7 | x0.8 / x0.4 | x1.15 / x1.3 |
| Court noble XP at level 3 / 5 / 7 | x0.8 / x0.5 / x0.2 | x1.1 / x1.2 / x1.3 |

- Kills made by a general's retinue now count for much more, and losing a battle is no longer wasted experience.
- Accepting a duel pays better than issuing one.
- Ministers and court nobles now gain experience faster as they rank up instead of slowing down.

#### Rank thresholds

Generals need far more experience per rank, but the late ranks give extra skill points:

| Rank-up | XP before | XP after | Skill points |
|---|---|---|---|
| 1 | 3,000 | 12,000 | - |
| 2 | 8,000 | 24,000 | - |
| 3 | 16,000 | 44,000 | - |
| 4 | 30,000 | 68,000 | - |
| 5 | 53,000 | 108,000 | - |
| 6 | 88,000 | 152,000 | - |
| 7 | 138,000 | 224,000 | 2 (was 1) |
| 8 | 206,000 | 296,000 | 2 (was 1) |
| 9 | 295,000 | 416,000 | 3 (was 2) |

Other experience sources:

- Satisfaction: the High band gives +25% experience.
- Faction rank: see the assignments track above.
- Technologies.
- AI handicaps.

Character templates for human factions now spawn at rank 0 (was up to rank 3).

#### Rank effects

- **Every character class gains melee attack rate with rank:** +3% per rank from rank 2, up to +30% at rank 10.
- **Hidden AI hints are added per rank.** Low-rank characters are steered towards governor posts, mid ranks towards command, and high ranks towards minister posts.

**Formations now apply to the whole force**, not only when the character commands the army.

- Sentinels (Earth) now get Loose at rank 1, Shield Wall at 2, Diamond from 3 and Circle from 4. They lose several Spear Wall, Pike Wall, Wedge and Hollow Square grants at ranks 3-6.
- Strategists (Water) lose their rank 2-6 Shield Wall, Hollow Square, Testudo, Circle and Diamond grants.

#### Attributes

- **Low attributes now carry penalties.** For example Instinct at 10 gives -20% melee damage, Expertise at 10 gives -10 melee evasion, and Authority at 10 gives -4 morale.
- The top-end values are smaller than in 190E. Cunning at 200 gives +25% ammunition (was +100%) and Resolve gives +91% health (was +99%).

**Attributes now drive the income of the province a character governs:**

- Authority: -15% to +25% income from all sources.
- Cunning: -30% to +75% commerce.
- Expertise: -30% to +75% industry.
- Resolve: -30% to +75% peasantry.
- Instinct: -6 to +10 public order.

**Attributes now also have minister effects:**

- Authority: satisfaction.
- Cunning: experience.
- Expertise: construction cost (+10% to -14%).
- Instinct: recruitment cost.
- Resolve: food (-15% to +25%).

- Removed attribute effects: Cunning's military supplies, Resolve's population growth, and Expertise's governor construction cost (moved to the minister scope).
- All attributes add hidden AI hints that push high-attribute characters into generalships.

#### Skills (representative)

Most mastery and DLC skills are trimmed and many swap their effects:

- **Zeal:** +10% melee attack rate (was 40%).
- **Evasiveness:** +15% capture evasion (was 25%).
- **Villainy:** +15% ambush chance (was 25%), gains +10% officer capture chance.
- **Craft:** caltrops, +1 stakes, oil and towers.
- **Nobility:** loses Encourage, gains -10% retinue upkeep and +15% melee damage for melee cavalry.
- **Meditation:** Immune to Fear and Terror instead of Unbreakable.
- **Intensity:** +5 hit chance and +25 charge bonus, replacing Mighty Knockback.
- **Passion:** gains Mighty Knockback.
- **Bravery:** +10% melee damage instead of fear immunity.
- **Reach:** +50% reinforcement range instead of +25% movement.
- **Night battles:** Composure and Obfuscation now enable night battles only for the army the character commands.
- **Emperor Xian's skills** are cut (for example Imperious +10 Han relations and +10% peasantry, was +25 and +25%).
- **Yellow Turban skills** are cut hard (for example Integrity +2 satisfaction and -1% corruption, was +20 and -20%).
- The custom-battle attribute loadouts gain +6% melee attack rate per tier.

#### Assignments

- **Seven new foreign assignments** are available against a province you do not own:

| Assignment | Effect |
|---|---|
| Supply Runs | Your armies there: +10% ammunition, +15 military supplies |
| Promote Offensive Tactics | Your armies there: +20% charge bonus, +20% damage and AP damage when attacking |
| Promote Defensive Tactics | Your armies there: +8 melee defence, +10% armour, +15% missile range |
| Target Enemy Ammo Stores | Owner's armies there: -10% ammunition, -15% missile AP damage |
| Night Raids | Owner's armies there: -5 morale, +25 fatigue modifier |
| Skirmishing & Harassment | Owner's armies there: -4% replenishment, -15% movement |
| Whispers of Disloyalty | Owner's characters there: -20 satisfaction, higher turncoat chance |

**Existing assignments are rebalanced** (full list in the appendix):

- Tax Collector: +25% all income (was +50% peasantry).
- Market Stimulation: +100% commerce, silk and spice, with -25% peasantry.
- Industrial Exploitation: +100% industry (was 30%), with -25% commerce.
- Root Out Corruption: -25% corruption (was -50%) and -10 satisfaction.
- Supervise Construction: -5% cost (was -10%) and loses its -25% upkeep.
- Find the Filial and Incorrupt: loses its -50% corruption and now raises desire for office.
- Black Market Investigation: +15% trade influence (was 50%), +5% trade income and a 5% chance of an ancillary.

- **Assignment running costs drop** (for example Develop Farmland 250→50, Find the Filial and Incorrupt 500→100 per turn, Market Investigation start 1,000→100). Several 190E unlock assignments now have upkeep.
- Counter-spy actions cost 50 network points (was 30).

#### Satisfaction and relationships

- Low satisfaction makes characters easier to turn and makes your faction easier to spy on. High satisfaction does the reverse and adds +25% experience.
- Low satisfaction no longer changes corruption or military supplies.
- Guanxi weights are roughly doubled (for example "like" 2→4 and "agreement" 1→2), so relationships form and sour faster.
- Releasing a captive is always remembered (100%, was 25%). Employing one is remembered only 25% of the time (was 100%).
- Characters live longer: the death chance at age 70 is 5-10% (was 15-20%).
- Retiring characters return after 2 turns (was 1).
- When a faction dies, characters of any rank can survive (was rank 5+).

---

### Technology

- **Technologies now give prestige.** 80 technologies gain +10 to +20 prestige, and Mandate of Heaven gives +100. Yellow Turban enlightenment and Han prestige values on 92 existing technology rows are retuned.
- **Army slots move to conscription technologies.** Available armies are removed from Supply Canals, Green Dragon Supply Ships and Hierarchical Enfeoffments. They are added to Garrison Conscripts, Regional Levy, Convict Drafts and Extended Conscription Period. Two Yellow Turban army techs and the Call for Warriors and Embolden the People techs (including Huang Shao's versions) also grant army slots.
- **Assignment slots from technology** are added to 12 technologies, mostly the Yellow Turban character techs (+2 each).

**Bandit network techs:**

- They cost 50% more research: 400→600, 600→900 and 800→1,200.
- They lose their unit-cap unlocks (Ji Infantry, Raider Cavalry, Sabre Cavalry and others). Those units now come through unit permissions instead.

- **Eight Princes techs are cheaper:** tier 1 500→300, tier 2 600→500, tier 3 800→700.
- The Korean tree gets prestige bonuses.
- The 190E Yellow Turban resource techs (Huang Shao variants) get their own unlocks.

---

### Recruitment & unit unlocks

#### Rank-based unlocks

**Unit requirements are rewritten around the recruiting general's rank.** In the main rewrite alone:

- 108 requirements now need rank 3.
- 78 need rank 6.
- 50 need rank 5.
- 30 need rank 2.
- 28 need rank 7.
- 14 need rank 8.
- 12 need rank 4.

- **Rank 7:** the five elite Han requirements (`3k_main_unit_requirement_*_elite`), Jiazi Raiders and Yellow Turban Archery Masters.
- **Rank 8:** all Imperial guard units (Household Cavalry, Lancer Cavalry, Sword Guard, Palace Cavalry, Palace Crossbowmen, Gate Guards), the world-leader units and the Juggernaut.
- **Rank 6:** most Yellow Turban elites (Exemplars of the Tao, the Land's Chosen, Stalwart Shields), Yellow Turban trebuchets and many bandit-network units.
- **Class restrictions are removed.** 139 requirements no longer need a particular general class, so any general of the right rank can recruit them.
- **Many technology and building prerequisites are dropped.** Rank is now the gate instead. Examples: Yellow Turban unit techs, Private Tutors, Silk Road Expeditions and Ma Teng's security buildings.
- Six Eight Princes imperial-guard units now also require world-leader status.
- Liu Bei's **Path to Unity** unit unlocks (41 requirements) now need a rank as well (2-5).
- Chen Wen's allied-unit unlocks, Liu Yu's tribal units, the Korean rosters, the tribe units and Zhang Lu's Wudou and Tianshi lines get rank requirements, adjusted from their 190E values.

#### What got easier

- **Regional (province) units no longer need rank.** 88 provincial side-building units drop from rank 3 or 6 to rank 1. Their effect text no longer shows "(Rank N)".
- A set of basic line units, militia and the Dragon units become available with no requirement. The Dragons need world-leader status plus a level 6 general.
- Zhang Yan gains 41 extra units split across a "Han" and a "Yellow Turban" roster.
- Han Sui, Ma Teng and Zhang Lu gain north-western units.

#### Who can recruit what

**Bandits lose the Han roster:**

- Imperial guards.
- The Dragons.
- Standard Han line infantry, cavalry and archers.
- Heavy crossbows.
- Cataphracts.
- Defenders of Earth and Protectors of Heaven.

They gain a wide southern, northern and Nanman mix instead, for example Jiangdong Zealots, the Jiaozhi and Cangwu units, elephants, Northern Sabre and Lancer cavalry, Qingzhou infantry and Dongzhoubing.

- **Nanman and Yellow Turbans** gain the Northern cavalry and infantry lines. The Nanman also gain the Black Mountain units.
- Han factions gain Dao Swordguards and Dao Swordguard Cavalry, and lose Defenders of Earth and Protectors of Heaven to the Yellow Turbans.
- Liu Yan's Dongzhoubing Defenders and Marksmen: the inheritance bundles no longer grant them, and Liu Yan's faction bundle now sets their recruitment cap row to -999 (was +2). The source file is named as if this makes them unlimited, but in-game testing should confirm whether they are uncapped or blocked.
- Northern Cavalry, Heavy Crossbows and territorial archers and spearmen drop to rank 1.

---

### Costs & upkeep of units

The Campaign pack barely changes recruitment prices:

| Unit | Recruitment | Upkeep |
|---|---|---|
| Veteran Lance Cavalry | 1,350 → 1,550 | 320 → 380 |
| Veteran Sabre Infantry | 625 → 850 | 180 → 225 |
| Veteran Sabre Cavalry | 1,300 → 1,625 | 315 → 400 |
| Veteran Jianguard Infantry | unchanged | 205 → 250 |
| Veteran Jianguard Cavalry | 1,325 → 1,700 | 335 → 425 |
| Armoured Archers | 450 → 500 | 165 → 135 |
| Wuhuan Noble Riders | 950 → 1,450 | 205 → 405 |
| Jiazi Raiders | 900 → 1,800 | 240 → 480 |
| Virtuous Noblemen | 1,200 → 1,800 | 320 → 480 |

Everything else about army cost moves through effects:

- **Faction support** changes recruitment cost from +80% to +10%.
- **Legitimacy** gives up to -30% recruitment and upkeep.
- **Heroism** gives up to -10% recruitment.
- **Governors, Gongsun Zan's inspectors and the bandit court** give small discounts.

**Assignments:**

- Conscription Campaign: -15% recruitment.
- Military Requisition: -15% recruitment and +10% replenishment.

- **Yuan Shu:** hiring characters costs 200 treasury per resource point (was 50).
- **The AI** gets -40% to -80% recruitment cost by faction potential (was -5% to -60%), plus extra artillery-upkeep effects. See Campaign AI.
- **Retinue upkeep:** Heroism, bandit loot levels and Lu Bu's bundle all add reductions.

Autoresolve strength (`melee_cp`) is retuned for 401 units. Most rise, typically 1.3x to 2.8x. This makes autoresolve reflect elite units better.

---

### Campaign AI

The AI data is rebuilt around making the AI **fight, occupy and spend like a player**, with difficulty handled by handicaps rather than faction potential.

**Personalities (608 rows, 1,712 group weights):**

- Many AI personalities move to militarist or uber-militarist budgets and high or very high aggression.
- Many switch from "destroyer" to "aggressive" occupation, so they are less inclined to raze.
- Previously unused personality groups get weight.

- **Occupation priorities (1,722 rows):** the AI stops prioritising hordes, migrating and regionless targets. It focuses on settled targets.

**Budgets:**

- The caps on army, construction, character and spy spending are raised: armies from 2,000 to 50,000, the others to 10,000.
- Army share is trimmed, and construction and character shares rise.
- The Han Empire and rebel budgets are rebuilt from scratch.

- **Construction:** new building-synergy sets for Han, Yellow Turban, Nanman and 190E faction buildings (+204 rows, -85 rows).
- **Character skills:** 1,086 new skill-synergy rows, so the AI picks coherent skill lines for administrators, commanders, ministers, retinues and Records/Romance characters.
- **Army composition:** the military generator templates, qualities and ratios are rewritten (full `data__.tsv` replacements) so AI armies field 190E's regional, Korean, northern-tribe, southern and Liu Bei unique units.

**Diplomacy:**

- AIs are far less willing to request vassalage (-50 to -200 depending on relations, was -10).
- Strategic distance is now scored the opposite way for seven peace-deal types.
- Breaking vassal or alliance treaties costs less trust.
- The AI is more willing to trespass on friendly territory and less on hostile.
- Recurring payment demands are no longer repeated if one already exists.
- Vassalising now needs rank 4 (was 3).

- **Captives:** the AI now prefers to enslave or release captives and almost never executes them.
- **Stances:** the AI marches and attacks in the default stance (Han, Nanman, bandits, Yellow Turbans) instead of forced march.
- **Task system:** shorter planning horizon (5 rounds, was 10), and it tries to match recommended force size on aggressive tasks. About 415 task-generator priorities are retuned.
- **Capital relocation** strongly favours walled major settlements far from enemies.
- **The AI accepts night battles** (100%, was 5%).

**Difficulty now comes from handicaps, not potential:**

- All difficulty-based faction-potential bonuses (322 rows) are set to 0.
- Base potentials are raised instead. Cao Cao, Sun Jian and Yuan Shao go to 120; Dong Zhuo, Gongsun Zan, Liu Bei, Liu Biao, Ma Teng and Yuan Shu to 60; minors from -50 to 0.
- The Han Empire and Yellow Turbans get -100 potential when the player is Chinese.
- The Hard, Very Hard and Legendary potential modifiers rise to 15/30/30 (was 10/20/20).

**AI-only handicaps by potential:**

- -40% to -80% recruitment cost.
- -5% to -25% salary.
- -40% to -90% building upkeep.
- Free spies.
- -33% desire for office.
- -50% food distribution cost.
- +15 military supplies at home.
- Up to +200% character experience.
- More artillery upkeep.

- **AI finance bias on Very Hard and Legendary** is reduced (level 2→1, turns 3→0).
- **Governors:** the AI's governor-independence threshold is 100 (was 20). When independence triggers, the AI always grants it (was 50%).
- **Faction council:** several suggestions are disabled or de-weighted for the AI, including pirate and barbarian raids, New Character, Vassal Heir and Target Enemy Character.

---

### Council, invasions, Yuan Shao's armoury and imperial intrigue

#### Faction council (`council_fix.lua` and the council queries script)

- **Suggestion costs scale with the campaign turn.** `council_fix.lua` overrides how suggestions are added:

| Turn | Cost multiplier |
|---|---|
| 1-50 | x1 |
| 51-100 | x1.25 |
| 101-150 | x1.5 |
| 151-200 | x1.75 |
| 201+ | x2 |

- **Base costs are rebalanced**, before the turn multiplier:

| Suggestion | Before | After |
|---|---|---|
| Long Range Logistics, Imported Foodstuffs, Foreign Trade Contracts, the three Economy Booms | 0 | 100 |
| Commandery Garrison Reinforcement | 0 | 300 |
| Veteran Recruitment Officers | 200 | 450 |
| Medicinal Horse Feed, Tailored Footwear, Artisan Fletchers | 200 | 500 |
| Character Celebrated | 200 | 500 |
| Rapid Deployment Measures | 500 | 750 |
| Civil Engineers Assigned | 200 | 750 |
| Paid Informants | 200 | 1,000 |
| Guerrilla Action, Charter Siege Merchants, Supply Stockpile Contaminated | 500 | 1,000 |
| Peace Keeping Troops Present | 500 | 1,000 (lasts 15 turns, was 5) |
| Civic Propaganda | 200 | 1,000 |
| Pirate and Xianbei raids | 500 | 1,000 |
| Crop Failure | 500 | 1,500 |
| Rebellion Raised in Neighbouring Commandery | 1,000 | 2,000 |
| Senior Mentor Assignment | 500 | 200 |
| Character Skill Tree Reset | 1,000 | 500 |
| Vassal Faction Heir Moved to Your Court | 1,000 | 750 |

- **Durations:** Logistics Impeded lasts 5 turns (was 11), Subject of Scandal 5 (was 21) and Supply Stockpile Contaminated 2 (was 6).

**Effects:**

- Economy Booms: -75% to the other two sectors (was -50%). Commerce Boom adds +10% trade income.
- Senior Mentor: +50% experience (was +200%).
- Civil Engineers: +1 extra building per turn (was +2).
- Peace Keeping Troops: +10 public order (was 5).
- Medicinal Horse Feed: +100 cavalry charge bonus and -15% cavalry upkeep.
- Veteran Recruitment Officers: -35% cost, -2 mustering turns and +3 starting rank.

**Triggers are stricter or looser:**

- "Low public order" now means -40 (was -20).
- "High satisfaction" means 70 (was 50).
- "Poor relations" means below 10 (was 50).
- "Large faction" means 10 regions (was 5).
- "Low food" means below 1 food (was 6).
- Army-presence checks need 1 army (was 2).
- The three raid suggestions (Gulf of Tonkin, Bohai Bay, Xianbei) now look at factions you are **at war** with rather than all non-allied factions.

- **Rewards:** the "few unassigned ancillaries" suggestion can now award exceptional weapons, followers, accessories and named stallions. A trait re-roll bug fix (`ceo_matched` reset) is included.

#### Invasions (`3k_campaign_invasions.lua`)

- Invasion armies reach the middle tier at turn 60 (was 25) and the late tier at turn 120 (was 75).
- Invasion armies are larger: early average/strong/very strong 4/8/12 units (was 3/6/9), and late up to 6/10/14.
- The generic unit pools are replaced by the five DLC05 bandit units (Marauders, Raiders, Warriors, Hunters, Gang). Captain weights rise from 1 to 5.

#### Yuan Shao's captain armoury (`dlc07_faction_yuan_shao_captain_armoury.lua`)

The armoury is re-priced:

| Upgrade | Before | After |
|---|---|---|
| Melee Charge Bonus | 30 | 300 |
| Melee Damage | 30 | 150 |
| Melee Attack Rate | 30 | 150 |
| Attack Range | 60 | 300 |
| Armour | 60 | 100 |
| Guerrilla Deployment | 30 | 60 |
| Stalk | 150 | 300 |
| Ranged Attack Rate | 100 | 150 |
| Unit Training (elite) | 60 | 120 |
| Replenish / Resupply in Enemy Territory (elite) | 100 | 200 |
| Whitewater (elite) | 150 | 300 |
| Ambush Battles (elite) | 300 | 600 |
| Unbreakable (elite) | 150 | 600 |
| Caltrops | 60 | 30 |
| Smoke Screen | 150 | 30 |
| Morale | 100 | 60 |
| Poison Arrows | 100 | 60 |
| Missile Block Chance | 300 | 100 |

Effect values also change:

- Charge +25% (was 15%).
- Morale +8 (was 5).
- Unit training +75 XP per season (was 25).
- Ammunition +10% (was 50%).
- Speed +15% (was 25%).
- Range +10% (was 7%).

#### Imperial intrigue (`dlc07_imperial_intrigue.lua`)

- A protectorate leader must be rank 6 (was 5) to generate Imperial Favour.
- The cooldown between applying favour changes is 5 turns (was 10), and a target can be hit again after 2 turns (was 8).
- The protectorate list drops Liu Yan and Yuan Shao and adds Lu Bu, Liu Chong, Tao Qian and Lu Zhi.
- Emperor missions fire more often: high-favour supply events weight 55 (was 25), low-favour sanctions and demands 35 (was 15), and supply missions 25 (was 15).

#### Ancillaries

- Buildings that spawn ancillaries now roll a **random ancillary** rather than one tied to the building's category.
- Master craftsmen produce faster: tier intervals are 10-15 / 5-15 / 5-8 turns (was 15-20 / 10-15 / 5-10).

---

### Other campaign rules

**Military supplies:**

- A season on foreign soil drains -20 (was -40, or -30 on Normal). The movement penalty is removed.
- Low supplies now start at 1 (was 11). Low gives -4 morale, -25% ammunition and -6% foreign replenishment. Empty gives -50% ammunition and locks fatigue at Exhausted.
- Normal and Abundant supplies give +5% and +10% ammunition.

**Stances:**

- Forced March blocks replenishment and removes line of sight.
- Encamp gives +2% replenishment (+6% abroad) and +50% reinforcement range.
- Ambush needs 50% movement left (was 25%) and gives -50% reinforcement range.
- Ma Teng's foraging gives +20 supplies (was 10) and replenishment, but the army cannot start battles.

- **Ambush success by terrain:** open ground drops sharply (plains, desert and tundra 40%→5%; grassland and wetland 45%→10%). Hilly dense forest rises to 95% (was 50%).
- **Rivers** cost 200 movement to cross (was 2,000).
- **Jungle:** Han armies are no longer locked at Tired, lose -5 supplies (was -10) and -25% ambush avoidance. Nanman armies get +10% movement (was +50%), +40% ambush avoidance, +10 supplies and ambush chance.
- **Night battles:** attacker visibility x0.75 (was x1). Defender visibility x0.75 (was x0.5). The defender's morale penalty is -7 (was -15).

**Sieges:**

- Maximum siege effort is 18 (was 8).
- Sapping costs 8 effort (was 2) and can be built twice (was 5 times).
- Siege-tower and ram autoresolve effectiveness rises slightly.

- **Loot:** the commander's share of loot is x0.3 (was x1).
- **Economy constants:** minor-faction background income is 3,000 (was 2,000–2,500).

**Diplomacy and culture:**

- Chinese-to-Chinese base attitude is -5 (was +10), with faster swings (x1.1).
- Yellow Turbans like each other (+40) and hate Han less (-20, was -40).
- Korean attitudes are reworked.

- **Vassal income:** Liu Biao's special vassal treaty now transfers 0% of income (was 20%). Yuan Shu's vassal treaty transfers 35% (was 20%).
- **Captives:** employ priority rules favour high-loyalty recruits. Yellow Turban captive employment is de-prioritised.
- **Characters:** random character ages are 15-30 (was 18-51). Template characters are distributed to human factions.
- **Events:** Sun Jian's historical death event and the Zhurong marriage event are rarer or re-weighted. Cao Cao's father's death now triggers the right war declaration.
- **Liu Xie's flag:** the Han Empire uses Empress He's flag when renamed.

---

### Battle-side values in the Campaign pack

The Campaign pack also contains battle data. If you run the Campaign pack **without** the Battle pack, these values apply. If you run both, the Battle pack usually overrides them (see Compatibility notes).

**Rules:**

- Hero-vs-unit matched combat is 5% (was 80%). This stops AI generals being dismounted.
- The ward-save maximum is 75 (was 100).

**Cavalry speed (`rew_190e_cavalry_faster_speed`, `@rew_ironic_patchup`):**

- Heavy cavalry run 8.0 (was 6.2).
- Medium cavalry 8.6 (was 7.5).
- Light cavalry 9.7 (was 9.5).
- Cataphracts 7.5-7.8 (was 5.8).
- The veteran ("expert") variants are faster too, and deceleration rises slightly.

**Heroic weapons (`rew_heroic_weapon_rebalance`, 127 rows):**

- Hero and general weapons get higher damage and AP. For example Zhang Jue's weapon goes 1,970 → 3,570, and the Records strategists' weapons 21 → 30.
- Splash attacks are limited to 1 target (was unlimited).
- Building damage is cut to 2-15 (was 25-100).
- Many weapons gain +3 to +7 bonus vs cavalry and large.

- **Other weapons:** bonus vs cavalry now also applies vs large on bows and crossbows (+52 vs large). Korean and tribe weapons are adjusted, as are the two Jian-mastery and mace fixes.

**Unit stats (`land_units`, 42 units):**

- The ji and spear lines gain charge (+50 typical) and melee defence (+20 typical).
- The sabre and jian cavalry lines gain +10-30 melee defence.
- Nanman slingers have 22-28 ammunition (was 62-64).
- The Juggernaut is now direct-fire artillery with 8 shots (was 12).

- **Unit sizes (`land_units_templates`):** Jiazi Raiders go to 36 men (was 18), Virtuous Noblemen to 36 (was 24), and 190E tribe units get new sizes (76 rows).

**Projectiles:**

- Multiple bolt throwers become single heavy bolts with more AP and range.
- The Juggernaut becomes an explosive fire bomb (4,000 damage).
- Nanman axes, darts and slings are nerfed.
- Composite and horn bows gain a little damage and AP.
- Bandit poison towers are new.

**Armour and shields:**

- Partial iron armour is 38 (was 32) and heavy leather 32 (was 26).
- Character sword-and-shield ancillaries block 50-65% of missiles (was 10-30%).

- **Unit experience:** accuracy growth is 3 (was 0.8), reload growth 1.7 (was 5.2), and melee attack gains 1.

**Abilities:**

- 19 duel and hero abilities are flagged so the AI uses them in duels.
- Dense Jungle gives Nanman a big autoresolve bonus.
- Tribal Fear hits harder (-50 morale).
- Inner Fire trades attack speed for +10 melee attack.
- Brother and friend presence give +10 and +5 melee defence.

- **Battle AI:** new personality overrides and property junctions, and better role usage for champion, commander and sentinel generals.
- **UI:** bonus vs infantry and bonus vs cavalry are shown on unit cards. There is a new "Role: Field Canons" bullet (sic).

---

### Removed vanilla/190E content

Several tables ship as full `data__.tsv` replacements. Rows that are missing from those files are removed from the game:

**Building effects (900 rows removed; 1,053 re-added in new form):**

- Commerce % on settlements and markets (95).
- Mandate of Heaven fervour from buildings (108).
- Trade influence on markets and resource buildings (79).
- Hidden population capacity on bandit camps (61, replaced by a visible +500).
- Wall artillery on Security buildings (55, moved to settlements).
- Prestige on bandit and Nanman buildings (38).
- Migration growth on labour and school buildings (35).
- Flat peasantry income on administration buildings (34).
- Bandit camp food (30).
- Assorted corruption, food %, research, public order, redeployment-cost and spy-network rows.
- Unit caps for elephants, Tiger Slingers and Tiger Warriors on Nanman buildings.
- The Imperial Palace's palace-guard garrison upgrade.
- Army, underling and spy position limits on a few buildings.

**Effect bundle contents (240 rows):**

- Food % from settlement size (all 48 size bands for Han, He Yi and Kong Rong).
- The foreign-soil movement penalty.
- Free satisfaction on faction ranks and world-leader bundles.
- The satisfaction, salary and trade rows of the extended-progression tracks.
- Imperial Favour from food surplus and shortage.
- White Tiger bandit-network discounts.
- Unity's prestige and administrator slots.
- Infamy's Scare and Unbreakable.
- Several Cao Cao scheme side effects.
- Liu Yan's inheritance Dongzhoubing unlocks.
- Ma Teng's "Recruitment and replenishment: enabled" while foraging.
- The No Loot! Unbreakable.
- The Seat of an Emperor's +100% commerce.

- **Technology effects (214 rows):** unit caps on bandit-network techs, army slots on the supply techs, and a set of Yellow Turban and bandit tech bonuses.
- **Building tech gates (350 rows):** replaced by the Reform gates described above. 102 building levels no longer need any tech.
- **Attribute effects (393 rows):** the whole old attribute ladder, replaced by the new penalty-to-bonus curves.
- **AI army generator (189 unit-quality, 98 ratio and 16 priority rows):** replaced by 190E-aware templates.
- **Unit permissions:** 121 bandit-network permission rows and 41 bandit military-grouping rows (the Han roster).
- **Outlaw tax effects (20 rows):** salary, satisfaction, retinue upkeep and morale by tax level.
- **Rank formations (42 rows)**, 20 skill-effect rows, 16 assignment-effect rows and 7 tech-requires-building rows.
- **Other replacements:** 85 AI construction-synergy rows, 82 AI region-group rows, 28 wall-artillery rows, 6 bandit building-chain availabilities, 2 vassal treaty-requirement options, battle-AI personality rows, 3 unit card bullet overrides, and the flat AI salary handicap.

---

### Compatibility notes

**Cavalry speed conflict.**

- The Campaign pack ships `battle_entities\rew_190e_cavalry_faster_speed.tsv`, which speeds up cavalry.
- The Battle pack ships `!!_rew_190e_cavalry_faster_speed_reverted.tsv` and its own `!!_rew_ironic_patchup.tsv`.
- With both halves installed, the Battle pack's `!!`-prefixed rows should take priority, so the Campaign speeds above will not apply. Light cavalry deceleration, for example, ends at 3.55, not 3.75.

**Other shared rows.** The same applies to other rows that both halves edit with different values:

- 35 `land_units` stat rows.
- 370 `main_units` autoresolve values.
- 108 melee-weapon rows.
- 23 projectiles.
- 18 unit sizes.
- Two armour types.
- Two unit-experience growth rates.
- Siege-vehicle autoresolve.
- The Juggernaut explosion.
- The two game rules: matched combat 5% vs 0%, and ward save 75 vs 70.
- One Dynasty Support bundle row: level 2 imperial replenishment is -14% in Campaign and -12% in Battle.

Treat the Campaign-pack battle values as the "Campaign only" configuration.

**Faction council script.**

- The Overhaul's `script\campaign\_shared\3k_campaign_faction_council.lua` replaces 190E's own copy at the same path.
- The difference is small: the Overhaul copy drops **Jiuzhen** (`3k_dlc06_faction_jiuzhen`) from the council's playable-faction list, so a Jiuzhen player loses council suggestions.
- It also removes 190E's `vfs.exists` check that switches the Prime Minister seat between Overhaul and non-Overhaul court layouts. That check is harmless while the Overhaul is loaded, because it takes the same branch.
- Any future edits to 190E's council script will be hidden while the Overhaul is installed, unless they are repeated in the Overhaul copy.

**Imperial intrigue script.**

- The Overhaul ships its own `dlc07_imperial_intrigue.lua`, which takes precedence over any 190E copy.
- The staged Imperial Favour v2 feature already includes a matching Overhaul-pack copy (`Beta\Output\ImperialFavour2\overhaul_pack`). It must replace the Overhaul's version when that feature ships.

- **Other shared scripts.** `3k_campaign_experience.lua`, the council queries, invasions, Yuan Shao's armoury and the ancillary-spawning scripts are full copies of vanilla files. Any other mod that edits the same vanilla scripts will conflict with the Campaign pack.

See the [Campaign Overhaul stat tables](#appendix-campaign) appendix for every changed value.


---

## Part 3: Battle Overhaul

The Battle Overhaul is an optional pack that loads on top of 190 Expanded. Every change below is measured against 190E, which is vanilla plus the 190E changes. The pack has no scripts. It changes 50 database tables and touches 704 existing units.

The data points to one goal: slower, heavier line battles in which the rank-and-file matter more than the characters. Heroes lose roughly a quarter of their weapon damage and most of their one-shot splash strikes. Generals' bodyguards are made the same size everywhere. Soldiers get more armour, more hit points and clearer counters (spears against cavalry, cavalry against infantry). Casualties now drain morale much harder. Missile units are tougher and more accurate but fire more slowly, and fatigue hurts far more.

---

### Heroes & generals

Characters appear in battle in two forms. The **hero** is the single-model duellist. The **general** is the character leading a bodyguard unit, the form used in Records mode and by some characters. Both forms change.

#### General bodyguard units (95 changed)

- **Same size for every class.** Bodyguard units are now **31 men with 52,080 HP**: 26 guards, 4 standard bearers and the general. Before this, combat classes had **41 men / 73,200 HP** (70,200 for some) and strategists had **21 men / 36,600 HP**. Warrior generals lose about 29% of their HP; strategist generals gain about 42%.
- **Upkeep 0 → 200** on all 95 general unit records.
- **Muster time.** Bodyguards now spawn at **20% strength** (`spawning_health_fraction` 1.0 → 0.2) and take **8 turns** to reach full strength (was 1). This matches how regular units recruit in 190E. The campaign effect is inferred from the column names.
- **Flagged as high threat** (`is_high_threat` false → true) for 94 generals and 38 heroes. The battle AI should now prioritise them as targets.
- **Capture power** drops for all characters: heroes 25 → 5, generals 10 → 5.
- **Bodyguard weapons now hit one target per swing.** 63 general weapon profiles go from unlimited splash (-1) to 1. Most one-handed swords, axes and maces gain **+40 bonus vs infantry** (swords with shields +35, axes +50). Building damage drops from 25–2,500 to 2–250. Two-handed axes, the Cleaver of Mountains and the giant maces attack more slowly (3.0 → 4.0 s).
- **Melee defence 0 → 10** (warriors) or **0 → 20** (strategists) for most characters.

#### Heroes (118 changed)

- **Strategist HP doubled.** Water-class heroes go from **12,000 → 24,000 HP**, bringing them up to the 24,000 other heroes already had. This covers Zhuge Liang, Sima Yi, Guo Jia, Jia Xu, Pang Tong, Xun Yu, Lu Zhi, Diaochan, Chen Gong, Xiao Qiao, Zhang Hong, Zhang Zhao, Kong Rong, Tao Qian, Lady Zhen, Fa Zheng, Liu Yan, Sima Ying and the generic Water hero. Xu Shu goes from 20,000 → 24,000.
- **Weapon damage cut about 25% overall.** Summed damage plus AP across the 74 changed hero weapons falls from 137,208 to 103,315.
- **The phantom shield is gone.** All four 190E "no shield" hero profiles (`rew_main_hero_none_*`, used by about 210 character units) go from **15 → 0 shield defence** and **10 → 0 shield armour**. Missile block stays at 35%.
- **Armour changes.** Many heroes gain armour: common strategists 15/20 → 25, Huang Gai 45 → 80, Gao Shun and Zhou Tai → 80. A few lose some: Lady Bian 55 → 25, Wang Lang 50 → 25, Zhang He 55 → 38.
- **Heavier heroes no longer bowl through lines.** Hero battle entities lose most of their mass: heavy infantry hero 1,500 → 150, medium 1,000 → 110, light 750 → 75. Hero horses are slower and lighter, for example:

| Hero mount | Run speed | Acceleration | Mass |
|---|---|---|---|
| Red Hare | 10.0 → 7.5 | 6.0 → 2.8 | 2,500 → 1,500 |
| Dilu | 10.5 → 9.5 | 8.0 → 3.35 | 1,500 → 800 |
| Shadow Runner | 10.5 → 9.5 | 6.0 → 3.35 | 2,000 → 800 |
| Heavenly Fire | 8.0 → 7.5 | 4.2 → 3.35 | 2,500 → 1,750 |
| Heavy hero horse | 8.0 → 6.2 | 4.2 → 2.8 | 2,500 → 1,500 |
| Medium hero horse | 8.6 → 7.5 | 6.0 → 3.05 | 2,000 → 1,200 |
| Light hero horse | 9.7 → 9.5 | 8.0 → 3.35 | 1,500 → 800 |

Deceleration goes up on all of them, so they stop and turn faster. The hero elephant's acceleration drops from 2.8 to 2.2. The Tribal Horse ancillary mount goes from 9.5 → 8.5 run speed and 2,250 → 800 mass.

#### Representative hero weapons (damage / AP)

| Weapon | Before | After |
|---|---|---|
| Generic sword and shield (unique) | 1,178 / 871 | 750 / 400 |
| Twin swords (unique) | 1,832 / 1,354 | 1,050 / 650 |
| Two-handed spear (unique) | 472 / 1,886 | 200 / 950 |
| Halberd (unique) | 1,512 / 1,512 | 1,100 / 1,100 |
| Yellow Turban staff (unique) | 1,820 / 96 | 1,700 / 50 |
| Yellow Turban twin maces (unique) | 1,682 / 561 | 100 / 980 |
| Lü Bu (Sky Piercer) | 1,079 / 2,161 | 1,100 / 1,100, +35 vs cavalry/large |
| Guan Yu (Green Dragon Sabre) | 2,564 / 1,324 | 1,720 / 410 |
| Zhang Jue (unique staff) | 1,970 / 219 | 1,700 / 50 |
| Huangfu Song (halberd) | 1,134 / 1,134 | 565 / 565 |
| Zhanmadao (unique, 190E) | 1,150 / 875 | 2,550 / 1,425, now unlimited splash |
| Burning mace (Nanman unique) | 0 / 3,000 | 2,600 / 0 |
| Elephant trunk (unique) | 2,000 / 2,000 | 1,800 / 1,800 |

Most hero weapons also gain small bonuses: +5 to +20 vs infantry for swords, maces and axes, and +20 to +35 vs cavalry and large for polearms. Axes and maces gain the **Shield Breaker** contact effect.

#### Hero missile weapons

Hero and general bows are rebuilt around a single profile of **480 damage / 226 AP** with a **+200 bonus vs cavalry**. They fire much more slowly:

- Composite bow (unique), Huang Zhong's bow and Taishi Ci's bow: **1,500 / 800 → 480 / 226**, reload **2 s → 10–12 s**.
- Huangfu Song's bow: 1,350 / 720 → 480 / 226.
- Liu Chong's crossbow: 720 / 1,350 → 275 / 585, reload 2 s → 24 s, range 250 → 300.
- Shamoke's bow: 1,500 / 800 (1 arrow) → 240 / 113 (5 arrows).
- Ancillary crossbows: reload 3–5 s → 24 s, +200 vs cavalry.
- Yue Jin's bow and the Tribal Bow: 1,350–1,450 damage → 430–480.

#### Duels

Every strategist hero gains the four duel abilities: **Duellist's Challenge, Accept Duel, Reject Duel and Retreat from Duel**. This covers 24 heroes, among them Guo Jia, Jia Xu, Pang Tong, Diaochan, Lu Zhi, Xun Yu, Chen Gong, Xiao Qiao, Xu Shu, Zhang Hong, Zhang Zhao and Li Ru. The duel rules change too; see the rules table under Morale, fatigue & battle rules.

#### Equipment in Records mode

- The pack adds **169 Records-mode equipment rows**. Armour ancillaries worn in Records now use separate **bodyguard-level armour profiles**. For example, Lü Bu's, Dong Zhuo's and Ma Chao's armour give **62** on a general (80 on the hero). Guan Yu's and Cao Cao's give 47. Common light tunics give 7–10.
- In Records mode, the unique armours of **Guan Yu, Liu Bei, Lü Bu, Xiahou Dun and Zhou Yu** now point at these general versions instead of the hero ones.
- Another 169 rows spell out the Romance-mode (hero) armour for each armour ancillary: 159 map to hero armour profiles and 10 to other armour keys.
- **Defence of Levity** is now a glaive instead of a halberd: hero 1,720 / 410, general 69 / 14.
- **Imperial Gold Inlaid Blade** (Emperor Xian) gets its own visible sword model and a unique-grade sword instead of an exceptional one.
- **Fear & Discipline** is upgraded from exceptional to unique twin swords.
- **Sequencer** now uses Taishi Ci's unique bow.

---

### Infantry

Changes cover 138 melee infantry, 85 spear and 35 pike/polearm units. For every value, see the [Battle Overhaul stat tables](#appendix-battle).

#### Across all infantry

- **Better base armour.** The shared armour types are raised: leather partial 20 → 23, leather reinforced 25 → 29, leather heavy 26 → 37, iron partial 32 → 46, iron lamellar 45 → 54, iron full 53 → 64. Almost every unit gains armour: 108 of 110 melee units with an armour change, averaging 32.9 → 41.7.
- **Missile resistance.** 112 melee infantry units go from **0 → 25% missile damage resistance**, and 10 go to 50%.
- **Faster attacks.** Most units gain a melee attack-speed bonus (`melee_attack_interval_reduction_percentage`) of **0 → 10%, 20% or 30%**. The size tracks training.
- **Unit sizes.** Standard infantry goes from **160 → 200 men** (HP 96,000 → 120,000), and some elites from 160 → 120. The standard of 600 HP per man is kept.
- **Deeper formations.** 30 units go from 5 → 8 ranks deep by default.
- **Campaign movement.** 153 units go from 1,900 → 1,950 action points and 18 go to 2,450.
- **Costs.** 420 recruitment costs and 448 upkeeps change. Melee infantry averages **694 → 848 gold**. Standard lines settle on steps of 400 / 580 / 640 / 860 / 960.
- **AI roles.** 437 units move to 24 new AI usage groups, such as `rew_main_infantry_spear_n_shield`, `rew_main_infantry_melee_shock` and `rew_main_infantry_ranged_harassers`. These tell the battle AI whether a unit is a blocker, flanker, cavalry-blocker, harasser and so on.

#### Swords, axes and maces

- One-handed sabres hit harder: **25 → 33** (elite 30 → 42, militia 20 → 25). Double-edged swords swing faster (2.5 s → 2.0 s).
- Axes and maces gain **+10 vs infantry** and swing more slowly (2.0 s → 2.5 s). Yellow Turban clubs and maces gain **Shield Breaker**.
- Nanman flint axes and mixed maces trade base damage for AP. For example, flint axe 24 / 3 → 7 / 16.
- Representative units:

| Unit | Changes |
|---|---|
| Sabre Infantry | Cost 600 → 640, armour 32 → 46, weapon 25 → 33, missile block 60% → 50% |
| Jian Sword Guards | Cost 700 → 640, MD 38 → 44, armour 26 → 37, shield def 20 → 25 |
| Yellow Turban Warriors | Cost 400 → 640, 160 → 200 men, MD 29 → 35, morale 24 → 38 |
| Sabre Militia | Cost 450 → 400, weapon 20 → 25 |
| Pearl Dragons | Armour 7 → 54, charge 125 → 225, shield added (def 20), new zhanmadao animation |

#### Spears

- **Anti-cavalry is much stronger.** The basic spear goes from **7 → 50 bonus vs cavalry** and gains **+25 vs large**. The long spear (2h250) goes from 10 → 40 vs cavalry and gains +80 vs large. Across 83 spear units, the average bonus vs cavalry rises from 6.5 to 45.7.
- **Shields.** Spearmen lose some shield defence (20 → 15, or 15 → 5 for tower shields) but block more missiles (55% → 65%, or up to 80% for tower shields).
- Spear Guards: shield def 20 → 15, missile block 55% → 65%, spear 7 → 50 vs cavalry.
- Heavy Spear Guards: MD 14 → 24, armour 32 → 46, missile block 60% → 80%.
- Peasant Band: cost 380 → 300, now 40 vs cavalry and 80 vs large.

#### Pikes and halberds

- The ji polearm goes from **5 → 30 vs cavalry** and gains **+60 vs large**.
- Melee defence rises sharply: the average goes 21.7 → 45.1. Ji Infantry go **6 → 40** and Heavy Ji Infantry **8 → 48**.
- Several units swap between the spear and pike classes: 190E's tribal "Untried/Hardened/Sworn Spears" become pikes, and Defenders of the Empire become spears.

---

### Missile units & projectiles

Changes cover 98 missile infantry and 23 missile cavalry units.

#### Tougher, more accurate, slower

- **Hit points.** Archers now have the standard 600 HP per man instead of about 340–370. For example, Archers go **54,000 → 96,000 HP** at 160 men. 75 of 78 missile infantry HP changes are increases.
- **Accuracy.** 67 missile infantry and 19 missile cavalry units gain **+10 / +20 / +30 accuracy** (was 0).
- **Reload time roughly doubles.** Bows go **7 s → 13 s**, flaming arrows 12 s → 19 s, crossbows **15 s → 24 s** and elite crossbows 11 s → 24 s. Many units get a 10–30% reload bonus back from their unit stats (`reload_time_reduction_percentage`).
- **Range is standardised:** bows 200/250 → **225**, laminated bows 225 → 250, poison bows → 225–250.
- **Better armour piercing and bonuses.** Arrows go from 8–10 → 16–20 AP, and bows gain **+52 vs large**.
- **Longer calibration distance** (50 → 150–225 m), so shots stay accurate to longer range. The effect is inferred from the column name.
- Archers and crossbowmen get a weaker sidearm: 9 → 13 damage but 2 → 1 AP.

| Unit | Changes |
|---|---|
| Archers | Cost 390 → 640, HP 54,000 → 96,000, armour 32 → 46, accuracy +10, AP 8 → 16, reload 7 → 13 s |
| Crossbowmen | Cost 420 → 640, HP 54,000 → 96,000, damage 18 → 21, AP 42 → 55, reload 15 → 24 s |
| Repeating Crossbowmen | Range 120 → 220, damage 21 → 16, reload 14 → 20 s, sidearm 9 → 33 |
| Archer Militia | Cost 270 → 400, HP 54,000 → 96,000, reload 7 → 19 s |
| Yi Marksmen | Cost 960 → 860, accuracy +20, damage 40 → 48, AP 10 → 20 |
| Mounted Archers | Cost 660 → 1,540, upkeep 175 → 385, reload 7 → 13 s |

#### Ammunition

About 60 units have ammunition changed in both directions. Examples:

- Nanman Slingers 62 → 31, Wuling Slingers 64 → 36, Sanjiang Poison Darts 30 → 12.
- Xianbei Horse Archers 50 → 60, Imperial Palace Cavalry 46 → 64, Hidden Axes 5 → 20.
- Oil-arrow units get only 2–3 volleys: Faithful Archers 18 → 2, Defenders of Earth 14 → 3.

#### Special projectiles

- **Suppressing Fire** (the contact effect on some arrows) no longer hits allies. It now halves target speed and charge speed, and its reload penalty drops from -50 to -25.
- **Oil arrows**: range 150 → 215, **+100 vs large**, can damage siege vehicles, but they lose Suppressing Fire. The splash does 40 → 200 damage.
- **Nanman javelins**: 20 / 50 → 50 / 20, range 60 → 70, +52 vs cavalry and large, and Shield Breaker. Throwing axes gain +52 vs infantry and Shield Breaker. Rock slings: range 100 → 150, reload 3 s → 10 s.
- **Korean Arrow Storm** becomes a flaming barrage: 20 arrows, 34 → 72 damage, reload 14 s → 30 s.

#### Homing

- **Heart Seeker** (Sun Ren) now homes with a new profile. Its damage changes from 20,000 normal to **3,500 armour-piercing**, and its range goes 250 → 300.
- **Warning Shot** (Huang Zhong) now homes. It hits for 480 / 226 and releases a 35 m shockwave that applies the Warning Shot effect.
- Two more homing profiles are defined (`rew_Daggers`, `rew_Huang_Zhong`) but nothing uses them.

#### Settlement towers

Every arrow tower hits softer and fires much more slowly: reload **3 s → 6–10 s**, and perimeter towers 2 s → 8 s. Base tower damage is halved (level 1: 400 / 100 → 200 / 50). Upgraded towers now set targets on fire through a contact effect instead of an explosion. The pack also adds poison-arrow versions of every tower level (see Compatibility notes).

---

### Cavalry & mounts

Changes cover 47 melee cavalry, 51 shock cavalry and 23 missile cavalry units.

- **Bigger squadrons.** Standard cavalry goes from **40 → 60 riders** (HP 67,200 → 100,800) in 36 units. A few go to 80.
- **Melee cavalry beat infantry but charge less.** Sabre and sword cavalry gain **+40 to +50 vs infantry** on 46 units, but their charge drops (average 192 → 144). Melee defence rises sharply (average 26 → 49). New cavalry-only weapon profiles carry these bonuses.
- **Shock cavalry charge harder.** Charge rises from 253 → 308 on average, with **+20 to +50 vs cavalry** and **+30 vs large**. Lances go 5 → 20 vs cavalry and gain +30 vs large.
- **Less missile armour for melee cavalry:** 42 units go from 50% → 25% missile resistance.
- **Weight classes reshuffled.** 93 mount records are reassigned between the light, medium and heavy horse entities, and 34 more between 190E's "expert" horses. Ground-effect groups change on 82 units to match.
- **Costs rise sharply.** Melee cavalry averages 1,137 → 1,748, shock cavalry 1,230 → 1,673 and missile cavalry 867 → 1,639.

| Unit | Changes |
|---|---|
| Lance Cavalry | Cost 1,050 → 1,540, charge 235 → 285, armour 32 → 46, +20 vs cavalry, +30 vs large |
| Sabre Cavalry | Cost 1,125 → 1,540, MD 9 → 48, charge 191 → 141, +40 vs infantry |
| Heavy Xiliang Cavalry | 40 → 60 men, MD 12 → 38, charge 281 → 392 |
| Jade Dragons | Cost 1,800 → 2,560, 40 → 60 men, MD 28 → 52, spear 7 → 50 vs cavalry |
| White Horse Fellows | 40 → 60 men, +50 vs infantry, accuracy +20, reload 7 → 13 s |
| Cataphracts | Charge 230 → 380, armour 53 → 78, lose their 25% missile block |

#### Horse speeds

- **Cavalry speed revert.** `!!_rew_190e_cavalry_faster_speed_reverted` keeps light, medium and heavy horses and cataphracts at **vanilla run speeds**: heavy 6.2, medium 7.5, light 9.5, cataphract 5.8. It also raises deceleration by 0.2 and adds 100 mass to heavy horses and cataphracts (heavy 500 → 600, cataphract 600 → 700, heavy cataphract 700 → 800). See Compatibility notes.
- 190E's "expert" horses stop harder: deceleration +0.8 to +0.95, charge speed -0.5. The heavy expert horse gets 6.8 → 7.2 run speed and 500 → 600 mass.
- A new cataphract expert horse (700 mass) is created for the **Xiongnu Cataphracts**.
- Several 190E cavalry get the correct mounts (the 190E fixes file). Xianbei Riders, Xianbei Horse Archers, Xiongnu Cavalry, Xiongnu Cataphracts, Hwandudaedo Guards and the Korean Scout Cavalry now ride their intended horses.

---

### Artillery & special units

#### Siege engines

| Unit | Changes |
|---|---|
| Trebuchet / Whirlwind Trebuchet | Cost 1,200 → 3,040, upkeep 320 → 760, HP 24,000 → 36,000, AP 1,200 → 2,000, reload 10 → 27 s, ammo 10 → 12 |
| Multiple Bolt Crossbow / Rapid Dragon Crossbow | Cost 1,200 → 2,200, upkeep 320 → 550, range 400 → 500, bolts now 0 / 800 (all AP) instead of 200 / 300, reload 10 → 20 s, ammo 10 → 6 |
| Bastion versions (fixed wall emplacements) | HP 14,000 → 15,000, **ammo 13 → 9,999** (effectively unlimited), range 400 → 500 |
| Arrow Storm (Korean) | Upkeep 340 → 550, HP 24,000 → 36,000, flaming barrage, reload 14 → 30 s |

- Flaming rocks double their AP (800 → 1,600) and reload in 35 s (was 15 s). Normal rocks: AP 1,200 → 2,000, reload 27 s. All rocks gain +100 vs large.
- Siege engines' campaign action points drop from 1,900 → 1,500, so armies carrying them move more slowly on the map.
- Siege tower HP 60,000 → 80,000. Battering ram HP 20,000 → 40,000, ignition threshold 10,000 → 20,000. Both gain a small autoresolve bonus.

#### Juggernaut

The Juggernaut (Nanman) changes from a short flamethrower into **long-range artillery**:

- Range **65 → 550 m**, one 5,000-damage flaming shell per shot instead of a 15-shot flame burst.
- Reload 9 s → 40 s, ammo 12 → 8.
- Its explosion is smaller but far deadlier: radius 9 → 4 m, damage 50 → 1,000, force 100 → 1,000.
- Cost 1,200 → 3,880, upkeep 320 → 970, HP 48,000 → 36,000.
- It can now damage buildings and vehicles.

The "bomb sling" explosion goes from 100 / 100 → 400 / 150.

#### Elephants

- All elephants gain **+100 vs cavalry and +100 vs large**, and now take extra fire damage (flame modifier 0 → -100).
- War Elephants: cost 1,580 → 3,040, HP 96,000 → 64,000, charge 491 → 391.
- Nanzhong Elephants: cost 1,650 → 3,040. Southern Elephants: 1,225 → 1,860. Jiuzhen Elephants: 16 → 20 elephants.
- Howdah slings: range 100 → 150, reload 3 s → 10 s, ammo 30 → 12–20.

#### Tigers

The two tiger units are rebuilt as pure animal units. The handlers are removed and the soldiers themselves become tigers (0.72 scale).

- **Tiger Warriors** are renamed **Armoured Tigers**. They are armoured tigers with a new tiger-pelt armour (26), fangs at 20 / 20 with +30 vs cavalry and large, charge 164 → 275, and cost 1,000 → 1,860.
- **Tiger Slingers** are renamed **Trained Tigers**. They lose their slings (ammo 46 → 0), use unarmoured pelts (12), have charge 132 → 200, and cost 800 → 1,540.
- Both units cause fear and terror, scare horses, hide in scrub and forest, and ignore heat.

#### Other

- **Wu Engineers** can now attack walls and gates (`can_siege` false → true).
- **Clear a Path** (stance) now deals splash damage.

---

### Armour & shields

#### Armour

| Armour type | Before | After |
|---|---|---|
| Leather partial | 20 | 23 |
| Leather reinforced | 25 | 29 |
| Leather heavy | 26 | 37 |
| Iron partial | 32 | 46 |
| Iron lamellar | 45 | 54 |
| Iron full | 53 | 64 |
| Korean bronze (regular / elite) | 30 / 42 | 40 / 60 |

- The pack adds new copies of the common types (`rew_main_unit_*`) at the same values, plus rattan (26 / 33 / 43), tunic (7) and cataphract (78) armour. Units are pointed at these copies.
- It also adds **139 general armour profiles**, one for each character armour. These are generally lower than the hero versions (see Heroes & generals).
- Character armour ancillaries from DLC07 are adjusted. For example, Cao Ren 41 → 55, Yu Jin 50 → 80, Wen Chou 70 → 65 and Zhang He 43 → 38.

#### Shields

The shared shield types are rewritten, and units move to new copies with the same values:

| Shield | Defence | Armour | Missile block |
|---|---|---|---|
| Infantry tower | 15 → 5 | 20 → 12 | 60% → 80% |
| Infantry large | 20 → 15 | 17 → 7 | 55% → 65% |
| Infantry gourd | 20 → 25 | 10 → 6 | 55% → 45% |
| Infantry oval | 20 | 5 → 3 | 55% → 50% |
| Infantry oval (elite) | 20 | 8 → 5 | 65% → 50% |
| Infantry rattan | 20 | 2 → 1 | 60% → 50% |
| Cavalry gourd | 25 → 30 | 10 → 6 | 60% → 50% |
| Cavalry rattan | 20 → 25 | 5 → 2 | 65% → 55% |
| Cavalry side | 25 | 12 → 3 | 45% → 55% |
| Cavalry side (jade) | 15 → 20 | 27 → 7 | 60% → 55% |
| Cataphract | 0 | 0 → 8 | 25% → 0% |
| Yellow Turban dodging | 0 → 20 | 0 | 40% |
| Hero "no shield" (4 types) | 15 → 0 | 10 → 0 | 35% |

Overall, shields now do less against melee hits (lower armour) and more of their work against arrows.

---

### Weapons

- **Cavalry get their own weapon profiles.** 20 new `_cavalry` versions of standard swords, axes, ji and spears move the bonus from vs cavalry to **vs infantry (+30 to +50)**. Cavalry-mounted ji and long spears carry +20 vs cavalry and +30 vs large.
- **New infantry spear profiles:** long spear (elite) 10 / 42, long spear (weak) 7 / 28, both with +40 vs cavalry and +80 vs large. There is also a heavy "damage over time" spear (25 / 38, hits 2 targets) and a lance (1 / 15, +40 vs large).
- **Building damage** is standardised at about 6 for spears, 12 for swords and 25 for axes and maces, which is down on most heavy weapons. Wuhuan raider axes go 250 → 25, and giant maces 200 → 40.
- **Splash.** Two-handed axes and giant maces can now hit 2 targets per swing.
- **Burning Nanman mace**: 40 / 10 → 52 / 0, now counted as an axe, 250 building damage, 4.0 s swing.
- **Rakes** (Yellow Turban): 37 / 0 → 18 / 8, +20 vs cavalry.
- **Yellow Turban giant mace** (Yue Enforcers and others): 74 / 25 → **0 / 55** (all AP), +20 vs cavalry and large, Shield Breaker.
- **Shield Breaker** is weaker per hit: it now reduces shield defence and shield armour by ×0.10 (was ×0.35).
- **Disorienting Strikes** is a new contact effect on the 190E "bonkai" staff: -10 melee attack and -5 morale for 10 s.
- Poisoned blades and spears lose their AP damage and rely on the poison effect instead.

---

### Abilities

#### Hero ultimate abilities: repeatable, but no longer one-shot

Many signature strikes had 1–4 uses per battle and huge splash damage. They now **recharge without limit** and do a fraction of the damage:

| Ability | Before | After |
|---|---|---|
| God of War | 1 use, 50,000 splash, 10 s | Recharges every 60 s, 7,500 splash, 20 s, but the user's armour drops to 0 and morale -10 |
| Earth-shattering Strike | 12,500 splash, 10 s | 500 splash, 20 s, user's armour and MD drop to 0, speed ×0.1 |
| Sacrificial Strike | 15,000 splash | 3,750 splash, 15 s, user's armour drops to 0 |
| Blow for Blow | 15,000, 60 s recharge | 3,750, 30 s recharge |
| Reckless Strike | 15,000 | 600, recharge 60 → 30 s |
| Gore | 12,500 | 3,375, recharge 60 → 30 s |
| Judgement | 12,500 | 3,375 |
| Binding Fury | 10,000 | 3,000, recharge 60 → 30 s |
| Rage of Lü Bu | 2,500 splash, 10 s | 450 splash, 20 s, recharge 60 → 30 s, MD -100 while active |
| Flames of the Phoenix | 5,000 | 500, 20 s, MD -100 |
| Lord of the Land | 10,000 | 500 |
| Off Guard, Killing Ground | 10,000 | 500 |
| Blazing Roar | 1 use, -100 morale | Every 60 s, -10 morale and -50 MD on enemies, range 50 → 150 |
| Devastating Roar | 2 uses, -50 morale | Every 60 s, -20 morale, -25 MD, lasts 15 → 30 s |
| Heart Seeker | 3 uses, 15 s recharge | Unlimited, 120 s recharge |
| Hail of Arrows | 4 uses, 10 × 2,000 damage | Unlimited (120 s), 5 × 200 / 100 |
| Venomous Shot, Poison Volley | 3–4 uses | Unlimited (120 s) |
| Heavenly Grace, Lord of Heaven, Lord of the People, Way of Great Peace, Undying Vow, Condemned Howl, Xiezhi Roar, Ancient Wisdom, Sight of the Dragon, Fire Bomb, Flying Daggers, Knowledge of the Body | Limited uses | Unlimited with a recharge |

About 25 strike abilities now also affect their user, which is how the new self-debuffs (armour or melee defence dropping to 0) apply.

#### Buffs and auras toned down

- **Scouting abilities** (Foresight, Ancient Wisdom, Sight of the Dragon, Ripples of Perspective) no longer grant 5,000 m vision. They grant 500–800.
- **Stalwart Defender**: resistance 70% → 35%. **Unyielding Earth**: MD +100 → +25, loses 20× bracing, gains +10% resistance.
- **Inward Focus**: now MD +100, +25% resistance and +25% speed, but damage ×0.5 and a much slower attack speed.
- **Hold Firm**, **Focused on Combat**, **Way of the Armament**: multiplicative melee defence becomes flat +3 to +25. Durations are cut to 5–12 s.
- **Elemental Vigour**, **Smouldering Fury**, **Tenacity of Steel**: now add flat melee attack (+5 to +25) and larger base-damage multipliers (up to ×3.5), with shorter durations (10 s).
- **Quickfire**: duration 15 s → 5 s. The missile damage bonus is replaced by +10 to +50 reload speed.
- **Qiao Sisters, Two Zhangs, Power of Love, One with Heaven/People/the Land**: now army-wide (range -1) instead of 5,000 m.
- **Mending**: armour ×1.5 → +25 flat, MD +50 → +15, recharge 60 s → 180 s.
- **Heavenly Presence**: the 2,000-HP heal every 60 s becomes 10 HP per second.
- **Relationship effects** (Fallen Oathsworn/Relative/Friend) no longer heal the hero 6,000–12,000 HP, and the melee defence bonus becomes a penalty (-12 to -50). **Nemesis** doubles damage (×1.5 → ×3) at the cost of -25% resistance and -20 MD. **Rival** goes ×1.25 → ×1.5.
- **Poisoned Blade** becomes a 30-second self-buff: each hit slows the target's attacks by 25 and lowers its MD by 25. It was a thrown 900-damage projectile.

#### Formations

| Formation | Change |
|---|---|
| Turtle | Missile block 100% → 35% (imperial 45% → 35%), bracing 6 → 0.5, speed ×0.75 |
| Hollowed Square | MD +10 → +20, adds ×6 bracing |
| Shield Wall (Spear) | Bracing 8 → 4, +10 shield armour, speed ×0.75 |
| Spear Wall (pike) | Missile block -25 |
| Circle | MD +25 → +10, attack speed -25 → +5 |
| Wedge | Charge speed ×1.5 → ×1.25, charge bonus ×1.25 → ×1.5; the speed and armour penalties are removed |
| Diamond | Loses the speed penalty, gains +10 missile block |
| Loose | Now -10 melee defence |

Unit captains (Jian, Ji, Lance, Archer, Mercenary and Yellow Turban captains) swap their standard formations for the **imperial** versions.

#### Unit abilities added

Summary of `land_units_to_unit_abilites_junctions`: 273 rows added, 30 removed. The pack ships this table as a full replacement with 5,277 rows.

| Ability | Added to |
|---|---|
| Duellist's Challenge, Accept/Reject/Retreat from Duel | 24 strategist heroes; the 22 new hero units |
| Loose (imperial) | 13 captain units, replacing the standard Loose |
| Smoke Screen | Yellow Dragons, Chu Infantry, Dao Swordguards, Dao Infantry Captain, Imperial Guards, Warriors of Xu, Xu Raiders, Archers of Jing, Qi Crossbowmen, Mercenary Infantry and Archers Captains |
| Caltrops | Chu Infantry, Chu Spearmen, Dao Swordguards, Dao Infantry Captain, Imperial Guards, Warriors of Xu, Xu Raiders, Qi Guardsmen, Mercenary Infantry Captain |
| Hollowed Square | Qi Crossbowmen, Heavy Crossbowmen, Heavy Repeating Crossbowmen, Watchmen of the Peace, Chen Royal Guard, Zhanmajian Infantry, Camp Crushers, Bringers of Righteousness, Yan Crossbow, White Dragon Crossbowmen, Immovable Blades, Warriors of Shangdang |
| Qiang Training | Qiang Marauders, Raiders, Hunters, Warriors, Archers and Polearms |
| Loose | Bandit Marauders, Raiders, Warriors, Hunters, Gang; Yue Tribesmen |
| Circle / Shield Wall / Diamond / Wedge (imperial) | Captain units (replacing the standard versions) |
| Turtle (imperial) | Imperial Sword Guard, Imperial Guard Captain |
| Diamond | Northern Sabre Cavalry, Northern Lancer Cavalry |
| Rapid Advance (new) | Swift Skirmishers, Swiftfoot Spears |
| Rally, Hack and Slash (new) | Xiliang Commander |
| Allied Focus (Ranged) (new) | Alliance Sharpshooters: allies in 35 m get +8 melee attack, +5 melee AP |
| Allied Focus (Melee) (new) | The Fellowship: allies in 35 m get ×1.2 missile AP and range |
| Mixed Missile, Hollowed Square (imperial) | Imperial Palace Crossbowmen |
| Shield Wall | Yellow Dragons |
| Mixed Spear | Bringers of Righteousness |

The Yellow Turban Spearmen Captain loses its standard Hollowed Square and gets no imperial replacement.

#### New "Records" abilities

The pack adds 15 new unit abilities, each with an effect that can enable it:

| Ability | Duration / recharge | Effect |
|---|---|---|
| Rally | 20 s / 60 s | +12 morale to allies in 75 m |
| Inspire | 30 s / 120 s | +5 melee attack, ×1.1 melee damage, ×1.05 missile damage |
| Rapid Advance | 30 s / 120 s | +50 charge, ×1.25 speed, immune to fatigue |
| Peerless Charge | 20 s / 60 s | Charge bonus ×1.1 |
| Crushing Blows | 30 s / 120 s | Splash power and range ×1.25 |
| War Cry | 20 s / 60 s | -8 morale to enemies in 50 m |
| Quick Reload | 20 s / 60 s | +10 reload speed |
| Target Weakness | 30 s / 120 s | Enemy resistances -10% |
| Flawless Aiming | 20 s / 60 s | +30 accuracy, ×1.15 missile damage |
| Brace | 20 s / 60 s | Mass ×2, bracing ×10, +5 MD, negates charges |
| Horseslaying Tactics | 20 s / 40 s | +50 bonus vs cavalry, scares horses |
| Second Wind | 20 s / 180 s | Fatigue recovery |
| Hack and Slash | 30 s / 120 s | Attack speed +10, melee damage ×1.15 |
| Raise Shields | 20 s / 60 s | +20 shield defence, +10 shield armour, +20% missile block, slower attacks |
| Push'em Out | 30 s / 60 s | Enemies: -10 MD, mass ×0 |

Only the three units listed above receive these abilities directly. None of the shipped data grants the enabling effects through character skills.

#### Character abilities from 190E's character pack now work in battle

190E attaches about 90 character abilities to the generic heroes and to Lü Bu, Gongsun Zan and Yuan Shu. Examples are Demigod of War, Rage of Lu Ji, Hope of Nam Viet, Yuenü's Tempest, Marksman of Taiyuan, Stomp of the Qilin and Dance of Death. Until now these had no battle implementation. The pack adds it: **90 special abilities, 112 phases, 263 stat effects** and a Ceaseless Gale arrow bombardment. See the Data anomalies in the report.

#### 190E unit abilities rebalanced

- **Hua Tuo's Anesthetic Surgery**: 3 uses → unlimited, but recharge 60 s → 300 s.
- **Peak Breaker, Biting Gale**: splash 3,000 → 150. **Flame Burst (Pan Zhang)**: 5,000 → 200.
- **Eyes of a Hawk** and **Unfaultable Line** become permanent 35 m auras.
- Many 190E faction abilities now last 20 s (were 30–75 s): Xiongnu Knowledge, Defence of Greed, Where are our horses?, Sharpened Axes, From a Far Distance, Shed Your Armor, Custodians of the West, Ceaseless Torrent, Mark of Scorn.
- **Qiang Training**: 600 s → 480 s, now also +10% speed.
- **Deadly Focus**: damage ×1.5 → ×2 and +25% speed, but -100% resistance, recharge 180 s.
- **Vortex abilities.** Sweeping Arc and Seismic Slam go from 1,500 / 1,500 → 200 / 0 and now stop at buildings. Gan Ji's Fire Breath goes 3,000 / 3,000 → 0 / 300, sets fires and now also burns allies.
- **Damage over time.** Poison and burning effects (Poison Shot, Poison Dart, Poison Blade, Venomous Shot, Burning, Nearby Fire) now last 10 s. They tick for more (for example Poison Shot 1 → 16, Venomous Shot 20 → 80) but hit at most 10 soldiers.
- Poison Shot also slows its targets (speed ×0.5, charge ×0.75, damage ×0.75).

#### Ability scaling

`direct_damage_extreme` goes from 1.5 → 1.25. The top tier of ability direct damage is scaled down.

---

### Morale, fatigue & battle rules

#### Battle rules (`_kv_rules`)

| Rule | Before | After | Meaning |
|---|---|---|---|
| `hero_dismount_chance_vs_reflect_units` | 1 | 0 | Mounted heroes are no longer knocked off their horse when charging braced / charge-reflecting units |
| `entity_attack_interval_and_damage_modifier_vs_heroes` | 2 | 1 | Removes the 2× modifier soldiers get to their attack interval and damage against heroes (1 = no modifier) |
| `matched_combat_hero_vs_hero_cavalry_percentage` | 0 | 100 | Mounted hero-vs-hero fights always use paired duel animations |
| `matched_combat_hero_vs_hero_infantry_percentage` | 60 | 100 | Foot hero-vs-hero fights always use paired animations |
| `matched_combat_hero_vs_unit_percentage` | 80 | 0 | Heroes no longer play paired kill animations on regular soldiers |
| `matched_combat_percentage` | 25 | 0 | Regular soldiers never play paired kill animations |
| `pursuit_charge_bonus_modifier` | 4 | 1 | Pursuing routing units no longer multiplies charge bonus by 4 |
| `ward_save_max_value` | 100 | 70 | Damage avoidance (ward save) is capped at 70% |
| `armour_roll_max_value` | -1 | 95 | Armour can block at most 95% of a hit (previously no cap was set) |
| `collision_damage_maximum` | 100,000 | 1,500 | A single charge or collision impact deals at most 1,500 damage |
| `collision_damage_armour_penetration_ratio` | 0.5 | 0.2 | Only 20% of collision damage ignores armour (was 50%) |
| `projectile_friendly_fire_man_height_coefficient` | 3.1 | 1.55 | Halves the soldier height used for friendly-fire checks, so missiles are expected to clear friendly heads more easily (inferred) |
| `hero_duel_blocking_decay_modifier` | 10 | 20 | Duel blocking decays twice as fast |
| `hero_duel_blocking_defence_modifier` | 10 | 2 | Blocking in duels gives much less defence |
| `hero_duel_blocking_max_cached_attacks` | 20 | 2 | Duellists remember only 2 attacks when blocking |
| `hero_duel_blocking_unmounted_vs_unmounted_only` | 1 | 0 | Duel blocking now also applies in mounted duels |
| `hero_duel_brawl_time_min` / `max` | 5 / 10 s | 10 / 20 s | Close-quarters exchanges last twice as long |
| `hero_duel_brawl_to_circle_chance` | 0 | 1 | After a brawl, duellists always break off and circle |
| `hero_duel_circle_to_brawl_chance` | 1 | 0 | Circling no longer triggers a new brawl by chance; brawls follow the timer |
| `hero_duel_circle_radius` | 6 | 50 | Duellists circle much wider |
| `hero_duel_circle_turn_target_radians` | 6.28 | 2.14 | Circling covers about a third of a turn instead of a full circle |
| `hero_duel_reposition_distance` | 15 | 50 | Duellists reposition further apart |
| `hero_duel_time_between_brawls` | 20 s | 30 s | Longer pauses between exchanges |
| `hero_duel_dismount_chance_modifier` | 7 | 1 | Much lower chance of dismounting in a duel |
| `hero_duel_dismount_target` | 0 | 1.4 | Dismounting now needs a build-up past a threshold |
| `hero_duel_dismount_target_decay_per_second` | 0 | 0.04 | That build-up decays over time |
| `hero_duel_dismount_target_decay_recovery_per_hit` | 0.01 | 0.03 | Each hit rebuilds it faster |
| `hero_duel_survival_time_to_survive_seconds_min` / `max` | 60 / 120 s | 30 / 300 s | Wider range for how long a duellist must survive to "win" by holding out |

#### Morale (`_kv_morale`)

| Rule | Before | After | Meaning |
|---|---|---|---|
| `total_casualties_penalty_10` | -2 | 0 | Losing 10% of the unit no longer costs morale |
| `total_casualties_penalty_20` | -5 | -6 | |
| `total_casualties_penalty_30` | -7 | -18 | Losing a third hurts much more |
| `total_casualties_penalty_40` | -18 | -30 | |
| `total_casualties_penalty_50` | -28 | -36 | |
| `total_casualties_penalty_60` | -36 | -48 | |
| `total_casualties_penalty_70` | -48 | -60 | |
| `total_casualties_penalty_80` | -60 | -72 | |
| `recent_casualties_penalty_6` | -3 | 0 | Light recent losses are ignored |
| `recent_casualties_penalty_15` | -8 | -10 | |
| `recent_casualties_penalty_33` | -12 | -22 | Taking heavy losses quickly nearly doubles the penalty |
| `recent_casualties_penalty_50` | -15 | -34 | |
| `extended_casualties_penalty_10` | -6 | 0 | |
| `extended_casualties_penalty_15` | -10 | -6 | |
| `extended_casualties_penalty_33` | -15 | -18 | |
| `extended_casualties_penalty_50` | -25 | -36 | |
| `extended_casualties_penalty_80` | -35 | -72 | Sustained heavy losses are twice as punishing |
| `was_attacked_in_flank` | -3 | -4 | Flanking matters more |
| `was_attacked_in_rear` | -8 | -12 | Rear attacks matter much more |
| `losing_combat` | -3 | -4 | |
| `losing_combat_significantly` | -6 | -8 | |
| `winning_combat` | 3 | 2 | Winning a fight gives less morale |
| `winning_combat_significantly` | 5 | 4 | |
| `charge_bonus` | 15 | 5 | The morale shock of being charged is a third of what it was |
| `charge_timeout` | 60 | 10 | That charge shock wears off after 10 s instead of 60 |
| `cavalry_effect_range` | 20 | 5 | Cavalry only unsettles infantry within 5 m (was 20) |
| `only_units_with_living_commanding_general_may_enter_non_shattered_rout_enabled` | 0 | 1 | Once their general is dead, routing units are expected to shatter rather than be able to rally (inferred) |

Taken together, small losses no longer cause wobbles, but a unit that loses a third or more of its men breaks far sooner. Flanks and rear charges also matter more.

#### Fatigue

The "fresh" bonus is removed: fresh units had +25% melee defence and +5% charge. Every tiredness level now also lowers melee and missile damage, splash power, shield defence and missile block.

| Level | Speed | Attack interval | Reload | Melee damage | Missile damage | Melee defence | Charge | Shield / block |
|---|---|---|---|---|---|---|---|---|
| Active | | ×1.1 → ×1.2 | ×1.1 → ×1.2 | → ×0.95 | → ×0.95 | ×1.1 → ×0.95 | ×1.0 → ×0.95 | → ×0.95 |
| Winded | ×0.85 → ×0.9 | ×1.25 → ×1.5 | ×1.25 → ×1.5 | → ×0.9 | → ×0.9 | → ×0.9 | ×0.85 → ×0.9 | → ×0.9 |
| Tired | ×0.8 → ×0.85 | ×1.5 → ×1.9 | ×1.5 → ×1.9 | ×0.9 → ×0.8 | → ×0.8 | → ×0.85 | | → ×0.8 |
| Very tired | ×0.75 → ×0.8 | ×2.0 → ×2.4 | ×2.0 → ×2.4 | ×0.8 → ×0.7 | → ×0.7 | → ×0.8 | | → ×0.7 |
| Exhausted | ×0.7 → ×0.75 | | | ×0.7 → ×0.5 | → ×0.5 | ×0.7 → ×0.75 | ×0.65 → ×0.5 | → ×0.5 |

Tired units move slightly faster than before, but they fight and shoot much worse. An exhausted unit deals half damage.

---

### Experience

#### Rank thresholds

Higher ranks need far more experience. The same values apply to land and naval units.

| Rank | Before | After |
|---|---|---|
| 2 | 1,070 | 1,100 |
| 3 | 1,776 | 1,950 |
| 4 | 2,546 | 3,050 |
| 5 | 3,364 | 4,400 |
| 6 | 4,226 | 6,050 |
| 7 | 5,124 | 8,000 |
| 8 | 6,054 | 10,350 |
| 9 | 7,014 | 13,100 |

Rank 9 now needs 13,100 XP, almost twice the old 7,014.

#### What each rank gives

- Accuracy per rank is doubled (growth 0.8 → 1.6).
- Attack speed per rank: 1.7 → 1.12.
- Reload speed per rank: **5.2 → 1.12**. Veteran missile units no longer reload dramatically faster.
- In custom battles, buying ranks is much cheaper: rank 9 costs **225 → 18** extra, and the cost multiplier drops from 1.45 → 1.18.

#### Imperial (Han) army bonuses

The Han Empire's base unit bundle loses its +10% movement speed, -21 replenishment and +10 XP. These now come from **Dynasty power levels** instead:

- Movement speed +10 at levels 3–5.
- Unit XP +10 at levels 4–5.
- Replenishment scales from **-34 at level 0 to +4 at level 4** (levels 1–3: -24 / -12 / -4).

---

### Ground & terrain effects

| Terrain | Change |
|---|---|
| Forest | All cavalry lose their bonus vs infantry (×0). Cavalry charge bonus and charge speed ×0.5. Infantry charge ×0.85, infantry charge speed ×0.75, elephant charge speed ×0.65 |
| Forest | Nanman infantry (light, medium, heavy) get **+35% melee defence** |
| Forest | Missile resistance for units in forest 1.25 → 1.40 |
| Forest | Light cavalry speed ×0.85, medium cavalry 0.9 → 0.8, light infantry ×0.9, medium infantry 0.9 → 0.85, heavy infantry 0.75 → 0.8. The melee defence penalty for heavy and medium infantry is removed; light cavalry get ×0.9 melee defence |
| Shallow water | **All infantry and cavalry melee defence ×0.5** |
| Shallow water | Heavy infantry speed 0.5 → 0.8, medium infantry 0.5 → 0.75, light infantry and light cavalry → 0.7, heavy cavalry 0.75 → 0.8 |
| Snow | Speed penalties are harsher: light units 0.85 → 0.65, medium → 0.7, heavy → 0.75 |
| Snow | Nanman melee defence penalty is softened (×0.1–0.25 → ×0.5), elephants ×0 → ×0.5. Some snow melee defence penalties are removed (light cavalry, light infantry, Yaoguai Hunters) |

Units also see further into cover: 40 units go from 50 → 150 m spotting in trees and scrub, and 12 get a longer maximum spotting range (300 → 800 m). The attribute changes are mostly new combinations that pair "hide in forest" with fear, terror, fatigue resistance, snipe, stalk and guerrilla deploy. Ten such groups are added.

---

### New units

The pack adds **44 unit records: a general (bodyguard) and a hero version for each of 22 characters**. The characters' keys point to 190E's character pack ("MTU"):

| Element | Characters |
|---|---|
| Earth | Dong Min, Lady Dong Peishan, Lady Du, Lady Feng, Lady Wu Minyu, Zhang Xun |
| Fire | Chunyu Qiong |
| Metal | Jian Yong, Lady Ma Lanli, Lady Ma Yunlu, Lady Wang Liting |
| Water | Hua Xin, Lady Cai Yan, Lady Gongsun Jinting, Lady Lu Zheng, Lady Yuan Anyang, Yan Xiang |
| Wood | Lady Lu Ji, Lady Trieu, Luo Jun, Shen Pei, Wu Anguo |

- **Generals:** 31 men, 52,080 HP, upkeep 200.
- **Heroes:** 1 model, 24,000 HP, all four duel abilities.
- **Charge by element:** Earth 215, Fire 334, Metal 190, Water 134, Wood 154.
- **Signature weapons** (hero damage / AP):
- ↳ Phoenix Beak glaive (Zhang Xun, Chunyu Qiong): 1,720 / 410.
- ↳ Hidden Flow twin blades (Lady Ma Yunlu): 1,050 / 650.
- ↳ Two-handed spear: 200 / 950 (Luo Jun 150 / 710).
- ↳ Water-class swords: 1,180 / 250.
- ↳ Everyone else: 750 / 400.
- The pack also defines further unique weapons (Line Breaker, Point Piercer, Young Dragon, Comet Spear, Invincible Spear, Sharp Light, Dachui hammer, Juque, Shengxie, Diplomat's blade) and six unique bows. No unit in this pack uses them.

These units have **no in-game names, a placeholder unit card**, armour keys that are not defined anywhere, and no link to any character in 190E or this pack. As shipped, players should not see them.

#### Renamed units

| Unit key | 190E name | Battle Overhaul name |
|---|---|---|
| `3k_dlc06_unit_metal_tiger_warriors` | Tiger Warriors | Armoured Tigers |
| `3k_dlc06_unit_water_tiger_slingers` | Tiger Slingers | Trained Tigers |
| `rew_iro_regional_xu_water_coastal_homeguard` | Shields of Xiapi | Guangling Marines |
| `rew_iro_regional_xu_wood_valiant_vigilantes` | Guangling Marines | Shields of Xiapi |
| `rew_iro_regional_yi_metal_forest_fighters` | Guerilla of the Gorges | Flying Warriors |
| `rew_iro_regional_yi_water_yizhou_stalkers` | Flying Warriors | Guerilla of the Gorges |

The Xu and Yi regional names are swapped between the two packs.

#### New looks

- **Pearl Dragons** and **Yellow Dragons** get new model definitions. Pearl Dragons now fight with a zhanmadao on heavy-infantry bodies, and Yellow Dragons move to the medium infantry entity.
- The Xiliang Commander moves to 190E's super-heavy infantry body.
- Yi Archers and Yi Marksmen get their own faster, lighter battle entities.
- A horse armour model is included.
- The pack also includes unit cards for seven 190E units. They are identical to the ones 190E already ships.

---

### Custom battles

- **Character loadouts rebuilt.** The pack replaces the whole loadout-to-skill table (4,473 rows: +901, -249, 244 level changes). Most changes swap which attribute a character's loadout raises. For example, Guo Jia's third loadout goes from 1 Expertise / 2 Instinct to 2 Expertise / 1 Instinct.
- **Class skills added to loadouts.** 582 rows give custom-battle loadouts their class opening skills, **Strategist, Vanguard, Commander, Sentinel and Champion** (and their alternates). There are 74 Strategist rows, 55 Vanguard, 52 Commander, 49 Sentinel and 40 Champion.
- **Caltrops and Smoke Screen** loadout skill for the **Eight Princes** (Sima Ai, Sima Jiong, Sima Liang, Sima Lun, Sima Wei, Sima Ying, Sima Yong, Sima Yue), plus Guo Jia, Jia Xu, Pang Tong, Huang Gai, Cao Pi, Lady Zhen, Chen Gong, Gao Shun and Zhou Tai.
- **New rosters for famous characters:**

| Unit set | Now available to |
|---|---|
| Imperial | Yellow Turban leaders: Zhang Jue, Zhang Bao, Zhang Liang, Gong Du, He Man, He Yi, Huang Shao, Pei Yuanshao, Zhang Kai |
| Liu Biao | Liu Bei, Guan Yu, Zhang Fei, Zhao Yun, Zhuge Liang, Gan Ning, Wei Yan |
| Tao Qian | Liu Bei, Guan Yu, Zhang Fei, Zhao Yun |
| Kong Rong | Taishi Ci |
| Liu Bei | Huang Zhong |
| Yuan Shao | Lady Zhen |

- **Basic rosters padded.** Ji Infantry, Heavy Ji Infantry, Sabre Infantry, Sabre Cavalry, Lance Cavalry and Archers are added to the elemental "basic 2" sets. Peasant Raiders and Peasant Band are added to the basic set, and Cataphracts to Earth. Gong Du gets a Trebuchet and a Multiple Bolt Crossbow.
- **Elite "Dragons" in more sets.** Azure, Yellow, Jade, Onyx and Pearl Dragons each become available in one more elemental "basic 3" set.
- Multiplayer costs change on 213 units (average 702 → 712).

---

### Autoresolve / matchup deltas

- **The matchup table is emptied.** The pack ships `ccp_unit_vs_unit_deltas_tables` as an empty `data__.tsv`, which removes all **167,584** vanilla rows. Each vanilla row is an attacker unit, a defender unit, and two numbers (`cp_delta_vs_defender`, `cp_delta_vs_attacker`). These are CA's precomputed adjustments to a unit's combat power in that specific matchup, for example how much better a spear unit does against a given cavalry unit. Vanilla values range from 0 to about 1,457, with a median of about 39.
- **Likely effect (inferred, not tested).** Autoresolve and the campaign AI's army-strength estimates would stop applying per-matchup counters. They would fall back to each unit's base combat power (`melee_cp` / `missile_cp`) plus ability and experience bonuses. Rock-paper-scissors counters would then no longer show up in autoresolve predictions and results. On the plus side, vanilla's deltas were calculated for vanilla stats; they did not match this pack's rebalanced units, and they never covered 190E's added units. Other CCP tables, such as the force-melee deltas and starting values, stay as in vanilla.
- **Combat power is rescaled.**
- ↳ Heroes: `melee_cp` averages **493 → 1,388**. Lü Bu goes 815 → 1,800 and Zhuge Liang 305 → 900.
- ↳ Generals: 679 → 1,371.
- ↳ Regular units: 517 → 613 melee and 263 → 433 missile.
- ↳ 147 abilities get new `additional_melee_cp` / `additional_missile_cp` values, mostly 100 for hero strikes and 25 for buffs.
- ↳ Characters should weigh much more heavily in autoresolve than before (inferred).
- **Siege autoresolve.** Siege towers (×1.05) and battering rams (×1.10) get a small autoresolve bonus.

---

### Compatibility notes

- **Cavalry speed conflict with the Campaign Overhaul.**
- ↳ The Campaign Overhaul pack ships `rew_190e_cavalry_faster_speed`. It raises cavalry run speeds: heavy 6.2 → 8.0, medium 7.5 → 8.6, light 9.5 → 9.7, cataphract 5.8 → 7.8 and heavy cataphract 5.8 → 7.5.
- ↳ This pack ships `!!_rew_190e_cavalry_faster_speed_reverted`, which sets the same five horses back to vanilla speeds.
- ↳ With both packs enabled, the `!!_` file name sorts first, so the Battle pack's slower speeds are expected to win.
- ↳ To keep the faster cavalry, the reverted file would have to be removed from the Battle pack.
- **Other overlaps with the Campaign Overhaul.** The two packs set different values for many of the same rows:
- ↳ 387 unit records (cost, upkeep, combat power), 141 melee weapons, 44 land units, 37 projectiles and 21 special abilities.
- ↳ Several `_kv_rules`, the siege vehicles and the imperial Dynasty-power bonuses.
- ↳ Which value wins depends on each file's name. The Battle pack's `!!_` files usually sort ahead of the Campaign pack's `@` and plain-named files. The exceptions are the Campaign pack's `!!!_` files and `!!_minimal_matched_combat…`, which sort ahead of the Battle pack's.
- ↳ As a result, the Campaign pack's Juggernaut explosion, its bastion bolt thrower and its `matched_combat_hero_vs_unit_percentage` of 5 (instead of this pack's 0) are expected to win.
- ↳ The Campaign pack's `ward_save_max_value` of 75 is expected to lose to this pack's 70.
- **Poison towers need the Campaign Overhaul.** The seven poison-arrow tower projectiles in this pack are used only by the Campaign Overhaul's `bandit_poison_towers` effects. On their own they do nothing, and with the Campaign pack enabled this pack's slower, weaker values are expected to replace the Campaign pack's.
- **Full-table replacements.** The pack ships `data__.tsv` replacements for 12 tables:
- ↳ `ccp_unit_vs_unit_deltas`, `custom_battle_loadouts_to_skills`, `ground_type_to_stat_effects`, `land_units_to_unit_abilites_junctions`, `unit_fatigue_effects` and `unit_special_abilities`.
- ↳ `special_ability_phase_stat_effects`, `special_ability_phase_attribute_effects`, `special_ability_stances`, `special_ability_to_auto_deactivate_flags`, `special_ability_to_invalid_target_flags` and `special_ability_to_invalid_usage_flags`.
- ↳ Other mods that add rows to these tables with their own named files still work. Mods that ship their own `data__.tsv` for them will conflict.
- **Campaign-side changes in a battle pack.** Some changes affect the campaign map, not just battles:
- ↳ Unit costs and upkeep.
- ↳ General upkeep and muster time.
- ↳ Unit campaign action points.
- ↳ The Han Dynasty-power bonuses.
- ↳ A new always-on bundle (`rew_3k_main_nothern_army_caps`, applied to every faction) that adjusts the Northern Army unit caps by -1. Its title and description are the placeholders "placeholder" / "test".
- **Savegames.** The pack has no scripts, so it can be switched mid-campaign in principle. However, existing general bodyguards and units keep their current men until they replenish, and costs change immediately.

See the [Battle Overhaul stat tables](#appendix-battle) appendix for every changed value.
