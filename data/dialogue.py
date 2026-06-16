"""All narrative text constants for Khonshu, bosses, endings, and lore.

Narrative voice: Khonshu — calm, god-like, second-person address.
Egyptian mythology preserved throughout: Ma'at, Book of the Dead, Thoth,
Horus opposition, three distinct endings (Good / Dream / Khonshu).
"""

# ---------------------------------------------------------------------------
# Opening narration — shown in DungeonScene via TypewriterRenderer
# ---------------------------------------------------------------------------

KHONSHU_INTRO = (
    "You venture deeper into the dungeon, drawn by a voice you cannot place. "
    "The walls are old — older than memory. You sense a presence watching."
)

# Alias used by main.py import: `from data.dialogue import INTRO_TEXT`
INTRO_TEXT = KHONSHU_INTRO

# ---------------------------------------------------------------------------
# Scarab Amulet reveal — shown during Horus boss fight when ScarabAmulet is used
# ---------------------------------------------------------------------------

SCARAB_DIALOGUE = (
    "A light washes over you. Horus's eyes seem to widen as his prepared attack falters. "
    "He takes a step back. As he does, the dungeon unravels — it is not a dungeon of nightmares. "
    "It is a prison. One built to contain a god.\n\n"
    "\"You... you see the truth now. Good. My work here is done.\"\n\n"
    "The voice of Khonshu, once so calm, carries an edge of fear for the first time."
)

# ---------------------------------------------------------------------------
# Three narrative endings (Requirement 17.1)
# ---------------------------------------------------------------------------

GOOD_ENDING = (
    "The Dungeon Heart shatters. Khonshu's chains snap one by one, and the god of the moon "
    "stands before you — not as a narrator, but as a prisoner freed.\n\n"
    "\"You have done what no mortal has managed. The dungeon was my cage, not your trial. "
    "Go now. The world above remembers nothing of this place. But I will remember you.\"\n\n"
    "The light takes you. You wake in the morning sun."
)

DREAM_ENDING = (
    "You lay down your weapon and follow Horus into the rift between worlds. "
    "The dungeon dissolves into golden light — Ma'at's feather drifts past your hand.\n\n"
    "\"This is the dream,\" Horus says. \"Not death. Not war. Rest.\"\n\n"
    "You do not return. But somewhere, in the quiet moments before sleep, "
    "you can still feel the warmth of the sun god's realm."
)

KHONSHU_ENDING = (
    "The darkness settles around you like a shroud. Khonshu's voice fills the silence.\n\n"
    "\"Rest, my child. The mortal world is mine to take. You fought well — better than most. "
    "But the moon does not negotiate with stars.\"\n\n"
    "You close your eyes. The dungeon claims another soul for its keeper."
)

# ---------------------------------------------------------------------------
# Boss introductions — rendered via TypewriterRenderer before each fight
# (Requirement 13.9)
# ---------------------------------------------------------------------------

ANUBIS_INTRO = (
    "The scales appear before you — brass and ancient, their chains wrapped in linen. "
    "A jackal-headed figure steps from the shadows.\n\n"
    "\"I am Anubis. I weigh what you carry. Every sin, every sacrifice. "
    "Your heart has grown heavy on this journey. Let us see if it is worthy.\""
)

SET_INTRO = (
    "The air turns to sand. The torches gutter and die as a red storm rolls through the corridor.\n\n"
    "\"Chaos is not evil,\" the figure says, his voice like splitting stone. "
    "\"It is honest. And I am very honest about what I intend to do to you.\""
)

HORUS_INTRO = (
    "He stands at the threshold of the seventh floor, wings half-spread, golden eye burning.\n\n"
    "\"I am Horus. I opposed Khonshu before you were born, and I will oppose him long after. "
    "But first — I need to know if you can be trusted. Show me.\""
)

KHONSHU_BOSS_INTRO = (
    "The dungeon trembles. The narrator's voice drops from the ceiling like stone.\n\n"
    "\"I see. So it comes to this. You found the truth hidden in that amulet. "
    "I had hoped you would not.\n\n"
    "Very well. If you insist on freedom, you will have to take it from me.\""
)

# ---------------------------------------------------------------------------
# Lore fragments — one shown per lore Room (Requirement 17.5)
# Pick from this list in DungeonScene; each floor should surface a different entry.
# ---------------------------------------------------------------------------

LORE_FRAGMENTS = [
    (
        "Scratched into the wall: 'Ma'at's feather is lighter than it looks. "
        "The scales do not lie. But those who carry guilt find it heavier than iron.'"
    ),
    (
        "A scrap of papyrus: 'Thoth recorded everything. The wars of gods, the weight of souls, "
        "the names of the forgotten. He never took sides. He never had to.'"
    ),
    (
        "Faded hieroglyphs: 'The Book of the Dead is not a book of death. "
        "It is a map. Those who know its words do not fear what waits in the dark.'"
    ),
    (
        "Carved in the ceiling: 'Ra travels through the underworld each night. "
        "He does not emerge unchanged. Neither will you.'"
    ),
    (
        "Inscribed on a broken column: 'Khonshu marks the hours. "
        "His eye is the moon. Some say his patience is infinite. "
        "Others say it simply looks that way from where we stand.'"
    ),
    (
        "A worn tablet: 'The dungeon was not built by human hands. "
        "Its corridors shift with the will of its keeper. "
        "You are not exploring a place. You are walking through a mind.'"
    ),
    (
        "On the floor, in fresh blood: 'Horus was here. "
        "He says the truth is in the amulet. I don't know what that means yet.'"
    ),
]

# ---------------------------------------------------------------------------
# Saving Roll dialogue — Khonshu narrates the mechanic (Requirement 9.7)
# ---------------------------------------------------------------------------

SAVING_ROLL_PROMPT = (
    "My followers do not accept death. "
    "Put your sanity on the line — ten points for one number. "
    "How much of your sanity will you wager?"
)

SAVING_ROLL_CHANGE = "I keep change."

SAVING_ROLL_SUCCESS = "Use this chance wisely. Not many return from death."

SAVING_ROLL_FAILURE = "Unlucky. Close your eyes."
