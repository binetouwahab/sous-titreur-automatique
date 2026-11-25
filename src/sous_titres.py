
import textwrap


def _secondes_vers_srt(secondes):
    """Convertit des secondes en format HH:MM:SS,mmm."""

    millisecondes = round(secondes * 1000)

    heures, reste = divmod(millisecondes, 3600000)
    minutes, reste = divmod(reste, 60000)
    secondes_entieres, millisecondes = divmod(reste, 1000)

    return (
        f"{heures:02d}:"
        f"{minutes:02d}:"
        f"{secondes_entieres:02d},"
        f"{millisecondes:03d}"
    )


def segments_vers_srt(segments, chemin_srt):
    """Transforme des segments Whisper en fichier SRT."""

    blocs = []
    numero = 1

    for segment in segments:

        debut = float(segment["start"])
        fin = float(segment["end"])
        texte = segment["text"].strip()

        if not texte:
            continue

        if fin < debut:
            raise ValueError("La fin du segment précède son début.")

        # Découper le texte en lignes de 42 caractères maximum
        lignes = textwrap.wrap(texte, width=42)

        # Regrouper les lignes deux par deux
        groupes = [
            lignes[i:i + 2]
            for i in range(0, len(lignes), 2)
        ]

        # Répartir la durée selon le nombre de caractères
        longueurs = [len(" ".join(groupe)) for groupe in groupes]
        total_caracteres = sum(longueurs)

        duree = fin - debut
        caracteres_cumules = 0

        for i, groupe in enumerate(groupes):

            debut_sous_titre = (
                debut + duree * caracteres_cumules / total_caracteres
            )

            caracteres_cumules += longueurs[i]

            if i == len(groupes) - 1:
                fin_sous_titre = fin
            else:
                fin_sous_titre = (
                    debut + duree * caracteres_cumules / total_caracteres
                )

            texte_sous_titre = "\n".join(groupe)

            bloc = (
                f"{numero}\n"
                f"{_secondes_vers_srt(debut_sous_titre)} --> "
                f"{_secondes_vers_srt(fin_sous_titre)}\n"
                f"{texte_sous_titre}"
            )

            blocs.append(bloc)
            numero += 1

    # Écrire tous les sous-titres dans le fichier SRT
    with open(chemin_srt, "w", encoding="utf-8") as fichier:
        fichier.write("\n\n".join(blocs) + "\n")
