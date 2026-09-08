"""Copy for each Bride's Cheat Sheet issue. Rendered by make_cheat_sheet.py.

Keeping the copy next to the renderer means an issue can be corrected and
re-rendered later — the slides are JPEGs, so the words are otherwise gone once
they are baked in.

Slide plan: 1 cover, 2-6 content (the last of those bridges to the product),
7 CTA. Product order is always save the date -> website, because the website is
the invitation.
"""

SPECS = {
    "06": {
        "number": "6",
        "eyebrow": "WEDDING BUDGET MATH",
        "title": ["Paper vs digital:", "the honest math"],
        "gold_word": "honest",
        "subtitle": "What 120 invitations really cost — counted both ways.",
        "closing": ["Same guests.", "One tenth the cost."],
        "save_line": "SAVE THIS BEFORE YOU ORDER PAPER",
        "cards": [
            {
                "badge": "THE PAPER SIDE",
                "title": ["What printing", "actually costs"],
                "rows": [
                    "Invitations for 120 guests: $300–500",
                    "Postage, both directions: $120–180",
                    "Reprints when a detail changes: $80+",
                ],
                "note": "One wrong time and you reprint the whole run.",
            },
            {
                "badge": "THE DIGITAL SIDE",
                "title": ["What a template", "actually costs"],
                "rows": [
                    "Animated save the date: under $10",
                    "Wedding website with RSVP: under $15",
                    "Sending it: free, the same evening",
                ],
            },
            {
                "badge": "THE HIDDEN COST",
                "title": ["Time, not money"],
                "rows": [
                    "Paper: order, proof, print, wait, post",
                    "Digital: edit in Canva, send tonight",
                    "Venue changed? Edit the link, not the run",
                ],
                "note": "Six weeks of waiting, or one evening.",
            },
            {
                "badge": "BE FAIR TO PAPER",
                "title": ["Paper still", "wins at one thing"],
                "rows": [
                    "One keepsake invitation for your album",
                    "Grandparents who won't open a link",
                    "A framed copy for the wall",
                ],
                "note": "Print two. Send the rest as a link.",
            },
            {
                "badge": "THE REAL MATH",
                "title": ["$500 on paper.", "$25 on a link."],
                "rows": [
                    "Animated save the date, editable in Canva",
                    "Wedding website with RSVP built in",
                    "Same guests, same information, same week",
                ],
                "note": "The difference funds your second photographer.",
            },
        ],
    },
    "07": {
        "number": "7",
        "eyebrow": "RSVP WORDING THAT WORKS",
        "title": ["How to ask so", "people actually reply"],
        "gold_word": "actually",
        "subtitle": "Four lines you can copy — and the one that gets ignored.",
        "closing": ["Ask clearly.", "They reply the same day."],
        "save_line": "SAVE THIS BEFORE YOU SEND YOURS",
        "cards": [
            {
                "badge": "THE ONE THAT FAILS",
                "title": ["“Please let", "us know”"],
                "quote": [
                    "“Please let us know",
                    "if you can make it.”",
                ],
                "note": "No date, no method, no number. Nobody replies.",
            },
            {
                "badge": "COPY THIS ONE",
                "title": ["Give them", "a deadline"],
                "quote": [
                    "“Kindly reply by 1 June.",
                    "After that we confirm",
                    "final numbers with the venue.”",
                ],
                "note": "A reason beats a request every time.",
            },
            {
                "badge": "COPY THIS ONE",
                "title": ["Name who", "is invited"],
                "quote": [
                    "“We have reserved 2 seats",
                    "in your name. Reply below",
                    "to confirm both.”",
                ],
                "note": "Settles the plus-one question without a word about it.",
            },
            {
                "badge": "COPY THIS ONE",
                "title": ["Make replying", "one tap"],
                "quote": [
                    "“RSVP on our website —",
                    "it takes 30 seconds,",
                    "no account needed.”",
                ],
                "note": "Every extra step costs you replies.",
            },
            {
                "badge": "THE FULL TEMPLATE",
                "title": ["All four,", "in one block"],
                "quote": [
                    "“We have reserved 2 seats in your name.",
                    "Kindly reply by 1 June — after that we",
                    "confirm numbers with the venue.",
                    "RSVP on our website, 30 seconds, no account.”",
                ],
                "note": "The RSVP form is built into the website template.",
            },
        ],
    },
}
