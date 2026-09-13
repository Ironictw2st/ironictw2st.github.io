// data/roadmap.js
// HAND-MAINTAINED - this file is not generated. Edit it directly to update the roadmap.
//
// Each stage renders as one card on roadmap.html, in the order listed here.
//   status:  "done" | "next" | "planned" | "future" | "tba"   (controls the chip colour)
//   label:   heading shown on the card
//   blurb:   optional one-line description under the heading
//   groups:  [{ title (optional sub-heading), items: [...] }]
//   An item may be a plain string, or { text, note } for a smaller grey follow-up line,
//   or { text, computed: "factions-without-mechanic" } to append the live list of factions
//   whose mechanic is not in the public build yet, read from FACTION_DATA.

const ROADMAP_DATA = [
  {
    id: "current",
    label: "In the Game Now",
    status: "done",
    blurb: "Everything already live in the current Steam build.",
    groups: [
      {
        title: "Scope",
        items: [
          "Every faction on the map is playable",
          "Unique units across the rosters",
          "Named historical characters with their own titles, traits, equipment and skill trees",
          "Faction mechanics for the great majority of warlords"
        ]
      },
      {
        title: "Added in the August 2026 update",
        items: [
          "Korea fleshed out — Goguryeo, Silla, Gaya, Buyeo, Dongye, Baekje and Tamno with their own roster, tech tree and court",
          "Nomadic Hordes — Wuhuan, Xiongnu and Xianbei armies become wandering settlements you build inside",
          "Ma Teng's Stables — breed, train and break in horses across six bloodlines",
          "Governor Edicts — Gongsun Zan's five inspectors each enact a regional edict",
          "Trial by Combat — Lü Bu wins his Greatest Warriors through a duel",
          "The Black Market — You Tu earns Enforcement in battle and spends it on equipment cases",
          "Around 90 new Faction Council options, plus a Bandit Council",
          "60+ new units across Korea, the southern warlords, the Liu vassals and the Yellow Turban splinters"
        ]
      }
    ]
  },
  {
    id: "minor",
    label: "Next Minor Update",
    status: "next",
    blurb: "Close to ready. Smaller in scope than a full release.",
    groups: [
      {
        items: [
          "Liu Pan's mechanic",
          "Vassal Contracts",
          "Imperial Succession",
          { text: "Offspring Raising", note: "Shape your children as they grow" }
        ]
      }
    ]
  },
  {
    id: "major",
    label: "Next Major Update",
    status: "planned",
    blurb: "The next full release.",
    groups: [
      {
        title: "Faction mechanics",
        items: [
          "Zhang Xian",
          "Fei Zhan",
          "Zhu Fu",
          "Pan Lin",
          "Shi Huang",
          "Lai Gong",
          { text: "Any remaining Han faction without its own mechanic", computed: "factions-without-mechanic" }
        ]
      },
      {
        title: "Campaign systems",
        items: [
          "Late game scenarios",
          "Nomadic tribes become their own culture",
          "A new tech tree",
          "New victory conditions"
        ]
      }
    ]
  },
  {
    id: "after",
    label: "The Update After",
    status: "planned",
    groups: [
      {
        items: [
          "Nanman factions fleshed out",
          "Korean factions fleshed out",
          "More victory conditions"
        ]
      }
    ]
  },
  {
    id: "campaign194",
    label: "194 Campaign",
    status: "future",
    blurb: "A second start date, four years into the war.",
    groups: [{ items: ["The 194 campaign map and its starting positions"] }]
  },
  {
    id: "tba",
    label: "Beyond",
    status: "tba",
    blurb: "Not decided yet.",
    groups: []
  }
];

const ROADMAP_STATUS_LABEL = {
  done: "In the game",
  next: "Up next",
  planned: "Planned",
  future: "Further out",
  tba: "To be announced"
};
