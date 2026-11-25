"""Textes des nouvelles sections (famille, calendrier, orientation, fiche).

Les amis peuvent modifier librement ces textes : aucune logique ici.
Règle : jamais de formulation de diagnostic ("vous avez", "votre enfant aura").
"""

TX = {
    "fr": {
        "tab_family": "Famille",
        "tab_calendar": "Calendrier",
        "progress": "Votre parcours",
        "privacy_title": "🔒 Confidentialité",
        "privacy_body": ("Rien n'est enregistré sur un disque ni dans une base de données : tout reste "
                         "dans cette session et disparaît à la fermeture. Si vous activez l'explication "
                         "par IA, seuls des pourcentages anonymes sont envoyés (ni nom, ni génotype)."),
        "dev_mode": "Mode développeur",
        "dev_detail": "Détail technique : ",
        "cards_title": "Pour 20 grossesses, la répartition attendue serait :",
        "cards_note": "Illustration pour comprendre un risque : ce n'est pas une prévision pour votre famille.",
        "family_title": "Arbre généalogique",
        "family_intro": ("Ajoutez, si vous les connaissez, les statuts des parents de chaque partenaire. "
                         "L'arbre montre qui est connu, qui ne l'est pas, et les enfants possibles."),
        "family_need": "Indiquez d'abord le résultat des deux partenaires dans l'onglet Résultats.",
        "a_mother": "Mère du partenaire A", "a_father": "Père du partenaire A",
        "b_mother": "Mère du partenaire B", "b_father": "Père du partenaire B",
        "family_unknown": ("Statut inconnu pour : {who}. Un test peut être utile pour ces proches ; "
                           "c'est un professionnel de santé qui peut le conseiller."),
        "family_note": "Aucun nom n'est demandé : seuls des rôles et des statuts apparaissent.",
        "calendar_title": "Calendrier : le risque au fil des grossesses",
        "calendar_intro": ("Le risque de chaque grossesse reste le même, mais la probabilité d'avoir au "
                           "moins un enfant avec une forme drépanocytaire augmente avec le nombre de grossesses."),
        "calendar_need": "Indiquez d'abord le résultat des deux partenaires dans l'onglet Résultats.",
        "calendar_slider": "Nombre de grossesses envisagées",
        "calendar_axis": "Probabilité (%)",
        "calendar_metric": "Au moins un enfant avec une forme drépanocytaire",
        "calendar_none": "Pour cette combinaison, aucun risque d'enfant avec une forme drépanocytaire n'est calculé.",
        "calendar_indep": ("Chaque grossesse est un nouveau tirage : avoir eu un enfant non atteint "
                           "ne change pas le risque de la suivante."),
        "timeline_title": "Votre feuille de route",
        "timeline": [
            ("Avant la grossesse",
             "Faire le point sur le statut de chaque partenaire et des proches dont le statut est inconnu, "
             "et en parler avec un professionnel de santé."),
            ("Conseil génétique",
             "Un conseiller en génétique ou un hématologue interprète votre situation, discute des options "
             "et répond à vos questions."),
            ("Options à discuter",
             "Selon les pays et les centres, des options existent avant ou pendant la grossesse (par exemple "
             "un diagnostic prénatal ou préimplantatoire). Leur disponibilité et leurs conditions sont à "
             "vérifier avec un spécialiste. Cet outil ne recommande aucun choix."),
            ("Pendant et après la grossesse",
             "Un suivi médical adapté et un dépistage du nouveau-né peuvent être proposés. "
             "C'est le professionnel de santé qui décide."),
        ],
        "refer_title": "Avec qui en parler ?",
        "refer_body": ("Un conseiller en génétique ou un hématologue peut interpréter votre situation et "
                       "répondre à vos questions. Si vous ne savez pas où en trouver un, votre médecin "
                       "traitant ou le service de santé de votre région peut vous orienter."),
        "refer_questions_title": "Questions utiles à poser",
        "refer_questions": [
            "Quel est le risque exact pour notre couple, d'après nos résultats ?",
            "Faut-il tester d'autres membres de la famille ?",
            "Quelles options existent avant et pendant une grossesse, et où sont-elles disponibles ?",
            "Quel suivi est conseillé pour un enfant porteur ou atteint ?",
            "Où pouvons-nous faire confirmer nos résultats ?",
        ],
        "refer_directory": ("Pour chercher des centres d'expertise et des laboratoires dans le monde, "
                            "vous pouvez consulter l'annuaire d'Orphanet : https://www.orpha.net "
                            "(vérifiez toujours les coordonnées avant de vous déplacer)."),
        "fiche_title": "Fiche à apporter à la consultation",
        "fiche_intro": ("Un résumé sans nom ni identifiant (résultats, risques, questions) à imprimer ou "
                        "montrer au professionnel de santé."),
        "fiche_button": "📄 Télécharger la fiche",
        "fiche_need": "La fiche est disponible une fois les deux résultats indiqués.",
        "ai_title": "Explication personnalisée (IA)",
        "ai_consent": "J'accepte que les pourcentages (sans nom ni génotype) soient envoyés à un service d'IA.",
        "ai_level": "Niveau de langage",
        "ai_levels": ["simple", "détaillé"],
        "ai_button": "Générer l'explication",
        "ai_questions": "Questions à poser au médecin",
        "ai_ok": "Généré par IA, relu par un garde-fou automatique.",
        "ai_fixed": "Texte standard (l'IA n'était pas disponible).",
        "banner": "ℹ️ Cet outil informe, il ne remplace pas un conseil génétique.",
        "erase": "🗑️ Effacer mes données",
    },
    "en": {
        "tab_family": "Family",
        "tab_calendar": "Calendar",
        "progress": "Your journey",
        "privacy_title": "🔒 Privacy",
        "privacy_body": ("Nothing is saved to disk or to a database: everything stays in this session and "
                         "disappears when you close it. If you turn on the AI explanation, only anonymous "
                         "percentages are sent (no name, no genotype)."),
        "dev_mode": "Developer mode",
        "dev_detail": "Technical detail: ",
        "cards_title": "For 20 pregnancies, the expected split would be:",
        "cards_note": "An illustration to understand a risk: it is not a forecast for your family.",
        "family_title": "Family tree",
        "family_intro": ("Add, if you know them, the statuses of each partner's parents. The tree shows "
                         "who is known, who is not, and the possible children."),
        "family_need": "First enter both partners' results in the Results tab.",
        "a_mother": "Mother of partner A", "a_father": "Father of partner A",
        "b_mother": "Mother of partner B", "b_father": "Father of partner B",
        "family_unknown": ("Status unknown for: {who}. Testing may be useful for these relatives; "
                           "a health professional can advise on it."),
        "family_note": "No name is asked for: only roles and statuses appear.",
        "calendar_title": "Calendar: risk over several pregnancies",
        "calendar_intro": ("The risk of each pregnancy stays the same, but the chance of having at least one "
                           "child with a sickle cell form grows with the number of pregnancies."),
        "calendar_need": "First enter both partners' results in the Results tab.",
        "calendar_slider": "Number of pregnancies considered",
        "calendar_axis": "Probability (%)",
        "calendar_metric": "At least one child with a sickle cell form",
        "calendar_none": "For this combination, no risk of a child with a sickle cell form is calculated.",
        "calendar_indep": ("Each pregnancy is a new draw: having an unaffected child does not change the "
                           "risk of the next one."),
        "timeline_title": "Your roadmap",
        "timeline": [
            ("Before pregnancy",
             "Take stock of each partner's status and of relatives whose status is unknown, and talk about "
             "it with a health professional."),
            ("Genetic counselling",
             "A genetic counsellor or a haematologist interprets your situation, discusses the options and "
             "answers your questions."),
            ("Options to discuss",
             "Depending on the country and centre, options exist before or during pregnancy (for example "
             "prenatal or preimplantation diagnosis). Their availability and conditions must be checked with "
             "a specialist. This tool recommends no choice."),
            ("During and after pregnancy",
             "Suitable medical follow-up and newborn screening may be offered. The health professional decides."),
        ],
        "refer_title": "Who to talk to",
        "refer_body": ("A genetic counsellor or a haematologist can interpret your situation and answer your "
                       "questions. If you do not know where to find one, your family doctor or your local "
                       "health service can refer you."),
        "refer_questions_title": "Useful questions to ask",
        "refer_questions": [
            "What is the exact risk for our couple, based on our results?",
            "Should other family members be tested?",
            "What options exist before and during a pregnancy, and where are they available?",
            "What follow-up is advised for a child who is a carrier or affected?",
            "Where can we get our results confirmed?",
        ],
        "refer_directory": ("To look for expert centres and laboratories worldwide, you can use the Orphanet "
                            "directory: https://www.orpha.net (always check the contact details before "
                            "travelling)."),
        "fiche_title": "Sheet to bring to your consultation",
        "fiche_intro": ("A summary with no name or identifier (results, risks, questions) to print or show "
                        "to the health professional."),
        "fiche_button": "📄 Download the sheet",
        "fiche_need": "The sheet is available once both results are entered.",
        "ai_title": "Personalised explanation (AI)",
        "ai_consent": "I agree that the percentages (no name, no genotype) are sent to an AI service.",
        "ai_level": "Language level",
        "ai_levels": ["simple", "detailed"],
        "ai_button": "Generate explanation",
        "ai_questions": "Questions for your doctor",
        "ai_ok": "AI-generated, checked by an automatic safeguard.",
        "ai_fixed": "Standard text (AI was unavailable).",
        "banner": "ℹ️ This tool informs; it does not replace genetic counselling.",
        "erase": "🗑️ Erase my data",
    },
}
