"""
Curated playlist name mappings and naming logic.
Maps genre signatures to evocative playlist names.
Differentiates sub-clusters with unique names instead of numbering.
"""

# Each entry: (genre keywords set, playlist name, description)
PLAYLIST_SIGNATURES = [
    # Brazilian
    ({"bossa nova", "samba", "brazilian jazz", "mpb"},
     "Tarde no Rio", "Bossa nova, samba e o auge do jazz brasileiro"),
    ({"new mpb", "mpb", "brazilian rock"},
     "Nova Onda Brasileira", "A nova geracao da musica popular brasileira"),
    ({"samba", "pagode", "samba rock"},
     "Roda de Samba", "Samba de raiz, pagode e samba rock"),
    ({"brazilian hip hop", "brazilian funk", "funk carioca"},
     "Rima Brasileira", "Hip hop e funk brasileiro contemporaneo"),
    ({"brazilian jazz", "bossa nova", "jazz"},
     "Jazz Tropical", "Jazz brasileiro, bossa nova e fusoes tropicais"),
    ({"mpb", "tropicalia", "brazilian rock"},
     "Tropicalia", "Tropicalia e a vanguarda brasileira"),
    ({"axe", "forro", "brazilian pop"},
     "Carnaval Eterno", "Axe, forro e a festa brasileira"),

    # Jazz & Funk
    ({"jazz funk", "acid jazz", "nu jazz", "jazz house"},
     "The Jazz-Funk Session", "Onde o jazz encontra o funk e o groove"),
    ({"jazz", "jazz fusion", "free jazz", "soul jazz"},
     "Blue Notes", "Jazz classico, fusion e exploracoes livres"),
    ({"jazz house", "deep house", "nu jazz"},
     "Jazz After Hours", "Jazz house e grooves noturnos"),
    ({"jazz rap", "nu jazz", "indie jazz"},
     "Jazz Novo", "Jazz rap, indie jazz e a nova escola"),
    ({"soul jazz", "jazz funk", "jazz"},
     "Soul Jazz Cafe", "Soul jazz e o encontro do groove com a improvisacao"),

    # Soul & Funk
    ({"funk", "classic soul", "retro soul", "motown"},
     "Funkadelic Soul", "Funk profundo, soul classico e groove eterno"),
    ({"neo soul", "indie soul", "retro soul"},
     "Velvet Grooves", "Soul contemporaneo e texturas aveludadas"),
    ({"funk", "funk rock", "p-funk"},
     "Funk Machine", "Funk pesado, funk rock e a maquina de grooves"),
    ({"soul", "classic soul", "motown", "northern soul"},
     "Sweet Soul Music", "Soul classico, Motown e classicos atemporais"),
    ({"disco", "post-disco", "boogie"},
     "Disco Fever", "Disco, boogie e a pista de danca dos anos 70-80"),

    # Rock
    ({"psychedelic rock", "acid rock", "classic rock", "space rock"},
     "Caleidoscopio", "Rock psicodelico e expansao mental"),
    ({"progressive rock", "art rock", "krautrock"},
     "Odisseia Prog", "Composicoes epicas e exploracoes art-rock"),
    ({"classic rock", "rock", "blues rock", "hard rock"},
     "Rock Classico", "Os classicos do rock que definiram geracoes"),
    ({"grunge", "alternative rock", "indie rock"},
     "Grunge & Alternative", "Grunge, alternative e o som dos anos 90"),
    ({"garage rock", "punk rock", "post-punk"},
     "Garage & Punk", "Garage rock, punk e energia crua"),
    ({"stoner rock", "doom metal", "sludge metal"},
     "Heavy Fuzz", "Stoner rock, doom e riffs pesados"),
    ({"neo-psychedelic", "shoegaze", "dream pop"},
     "Sonic Dreams", "Neo-psicodelia, shoegaze e paisagens sonoras"),
    ({"surf rock", "garage rock", "rockabilly"},
     "Surf & Twang", "Surf rock, rockabilly e reverb"),
    ({"britpop", "indie", "madchester"},
     "Britpop Chronicles", "Britpop, indie britanico e a cena Manchester"),
    ({"glam rock", "new wave", "post-punk"},
     "Glam & New Wave", "Glam rock, new wave e a era dourada do synth"),
    ({"baroque pop", "chamber pop", "art pop"},
     "Chamber Pop", "Arranjos orquestrais e pop barroco"),

    # Electronic
    ({"trip hop", "downtempo", "electronica"},
     "Frequencias da Madrugada", "Downtempo, trip hop e texturas eletrônicas"),
    ({"french house", "disco house", "nu disco"},
     "Discoteque", "French house, disco house e dancefloor"),
    ({"lo-fi house", "deep house", "house"},
     "Deep Cuts", "House profundo e lo-fi"),
    ({"tech house", "house", "minimal techno"},
     "Underground House", "Tech house, minimal e a pista underground"),
    ({"idm", "ambient", "electronica", "glitch"},
     "Circuitos", "IDM, ambient e eletronica experimental"),
    ({"drum and bass", "jungle", "liquid funk", "breakbeat"},
     "Jungle Massive", "Drum and bass, jungle e breakbeat"),
    ({"dub", "dub techno", "dubstep"},
     "Dub Echoes", "Dub, dub techno e ecos profundos"),
    ({"acid house", "italo disco", "disco house"},
     "Acid Disco", "Acid house, italo disco e grooves analogicos"),
    ({"downtempo", "chillout", "ambient"},
     "Chill Orbit", "Downtempo, ambient e relaxamento cosmico"),

    # Reggae
    ({"reggae", "roots reggae", "dub", "rocksteady"},
     "Riddim Foundation", "Roots reggae, rocksteady e dub pesado"),
    ({"ska", "rocksteady", "reggae"},
     "Ska & Rocksteady", "Ska, rocksteady e o som jamaicano original"),

    # Hip Hop
    ({"hip hop", "east coast hip hop", "boom bap", "old school hip hop"},
     "Golden Era Crates", "Boom bap, old school e classicos East Coast"),
    ({"hip hop", "west coast hip hop", "gangsta rap"},
     "West Side Stories", "West Coast hip hop e g-funk"),
    ({"jazz rap", "conscious hip hop", "hip hop"},
     "Conscious Flows", "Jazz rap, hip hop consciente e lirica"),
    ({"lo-fi beats", "jazz beats", "chillhop"},
     "Lo-Fi Sessions", "Lo-fi beats, jazz beats e estudo"),

    # Blues
    ({"blues", "blues rock", "electric blues"},
     "Blues Highway", "Blues eletrico e raizes"),
    ({"delta blues", "country blues", "folk blues"},
     "Delta Roots", "Blues acustico e as raizes do Delta"),

    # African & World
    ({"afrobeat", "afropop", "highlife"},
     "Afro Pulse", "Afrobeat, highlife e grooves pan-africanos"),
    ({"afrobeat", "afro house", "afro soul"},
     "Afro Fusion", "Afrobeat contemporaneo e fusoes"),
    ({"cumbia", "latin", "salsa"},
     "Cumbia y Mas", "Cumbia, salsa e ritmos latinos"),
    ({"world music", "ethio-jazz", "desert blues"},
     "World Frequencies", "Musica do mundo e fusoes globais"),

    # Singer-songwriter & Folk
    ({"singer-songwriter", "folk", "folk rock"},
     "Acoustic Stories", "Singer-songwriters, folk e historias acusticas"),
    ({"yacht rock", "soft rock", "adult contemporary"},
     "Yacht Club", "Yacht rock, soft rock e o som dos anos 80"),

    # Spoken word & experimental
    ({"spoken word", "poetry", "experimental"},
     "Palavras & Sons", "Spoken word, poesia e experimentacao"),

    # Misc vibes
    ({"funk", "soul", "disco", "boogie", "post-disco"},
     "Grooves & Moves", "Funk, soul, disco e tudo que faz dancar"),
]

# ─── Sub-cluster differentiation ────────────────────────────────
# Maps (base_name, differentiating trait) -> (sub_name, sub_description)
# Used when multiple playlists would share the same base name.

# Genre-based differentiators: if a sub-cluster's top genres include one
# of these distinguishing genres, use the mapped name variant.
GENRE_DIFFERENTIATORS = {
    "Caleidoscopio": [
        ({"space rock"}, "Cosmos Psicodelico", "Space rock e viagens interestelares"),
        ({"stoner rock"}, "Stoner Visions", "Stoner rock e psicodelia pesada"),
        ({"surf rock"}, "Acid Surf", "Surf rock psicodelico e garage"),
        ({"brazilian rock", "mpb"}, "Psicodelia Brasileira", "Rock psicodelico brasileiro e MPB experimental"),
        ({"baroque pop", "art pop"}, "Sonic Dreams", "Neo-psicodelia, art pop e paisagens sonoras"),
        ({"neo-psychedelic", "shoegaze"}, "Reverb & Haze", "Neo-psicodelia, shoegaze e texturas etéreas"),
        ({"blues rock"}, "Acid Blues", "Blues rock psicodelico e jams acidas"),
        ({"progressive rock", "art rock"}, "Odisseia Cosmica", "Prog e art rock com alma psicodelica"),
        ({"alternative rock", "indie"}, "Indie Psicodelico", "Indie e alternative com toque psicodelico"),
    ],
    "Golden Era Crates": [
        ({"brazilian hip hop", "brazilian trap"}, "Boom Bap Brasil", "Boom bap e hip hop brasileiro"),
        ({"west coast hip hop", "g-funk"}, "West Side Stories", "West Coast, g-funk e o som da California"),
        ({"jazz rap"}, "Conscious Flows", "Jazz rap e hip hop consciente"),
        ({"old school hip hop"}, "Old School Anthems", "Old school hip hop e os classicos originais"),
        ({"new mpb", "samba"}, "Samba Rap", "Onde o samba encontra o rap brasileiro"),
    ],
    "Tarde no Rio": [
        ({"latin jazz"}, "Jazz Tropical", "Jazz brasileiro e fusoes tropicais"),
        ({"forró tradicional", "forró"}, "Forró & Raizes", "Forró, samba e raizes nordestinas"),
        ({"samba"}, "Samba de Raiz", "Samba, bossa e as raizes cariocas"),
        ({"brazilian rock"}, "MPB Rock", "MPB com pegada de rock e experimentação"),
    ],
    "Soul Jazz Cafe": [
        ({"trip hop", "downtempo"}, "Frequencias da Madrugada", "Trip hop, downtempo e jazz esfumacado"),
        ({"funk", "soul jazz"}, "Funk Jazz Grooves", "Funk pesado com improvisacao jazz"),
        ({"spoken word", "vocal jazz"}, "Spoken Jazz", "Spoken word, vocal jazz e poesia sonora"),
        ({"neo-psychedelic"}, "Jazz Psicodelico", "Jazz experimental com toque psicodelico"),
    ],
    "The Jazz-Funk Session": [
        ({"nu jazz", "indie jazz"}, "Nu Jazz Collective", "Nu jazz, indie jazz e o jazz do seculo XXI"),
        ({"jazz house"}, "Jazz After Hours", "Jazz house e grooves noturnos de pista"),
        ({"trip hop", "downtempo"}, "Downtempo Jazz", "Jazz com texturas downtempo e trip hop"),
    ],
    "Nova Onda Brasileira": [
        ({"axé", "forró"}, "Nordeste em Festa", "Axé, forró e a energia do Nordeste"),
        ({"brazilian rock", "psychedelic rock"}, "Rock Brasileiro", "Rock brasileiro e psicodelia nacional"),
        ({"brega", "tecnobrega"}, "Brega Pop", "Brega, tecnobrega e o pop brasileiro"),
        ({"forró tradicional", "samba"}, "Raizes do Brasil", "Forró, samba e as raizes brasileiras"),
        ({"space rock"}, "Cosmonautas BR", "Rock brasileiro espacial e experimental"),
    ],
    "Funkadelic Soul": [
        ({"retro soul", "jazz fusion"}, "Retro Soul Revival", "Retro soul e fusoes modernas"),
        ({"blues"}, "Soul & Blues", "Soul com raizes no blues profundo"),
        ({"pop soul"}, "Pop Soul Classics", "Pop soul e os classicos que tocam o coracao"),
    ],
    "Rock Classico": [
        ({"grunge", "post-grunge"}, "Rock Pesado 90s", "Rock pesado, grunge e o som dos anos 90"),
        ({"glam rock", "art rock"}, "Glam Rock Anthems", "Glam rock, art rock e energia teatral"),
        ({"hard rock", "rock and roll"}, "Rock & Roll Machine", "Hard rock e rock and roll puro"),
    ],
    "Riddim Foundation": [
        ({"rocksteady"}, "Rocksteady Riddims", "Rocksteady, ska e o som original jamaicano"),
        ({"dub"}, "Dub Chamber", "Dub pesado e ecos profundos"),
    ],
    "Grunge & Alternative": [
        ({"stoner rock"}, "Riffs Pesados", "Stoner rock, grunge e riffs devastadores"),
        ({"funk rock"}, "Alt Rock Funk", "Alternative com groove e funk rock"),
    ],
    "Acoustic Stories": [
        ({"southern gothic", "indie folk"}, "Southern Gothic", "Southern gothic, indie folk e historias sombrias"),
        ({"outlaw country", "classic country"}, "Outlaw Country", "Country fora da lei e folk americano"),
        ({"folk", "traditional folk"}, "Folk Roots", "Folk tradicional e as raizes acusticas"),
    ],
    "Afro Pulse": [
        ({"afro soul", "latin afrobeats"}, "Afro Soul Moderne", "Afro soul e afrobeats contemporaneos"),
        ({"brass band"}, "Afro Brass", "Afrobeat com metais e highlife"),
    ],
    "Sweet Soul Music": [
        ({"soul blues"}, "Soul Blues", "Soul blues e as baladas mais profundas"),
        ({"northern soul"}, "Northern Soul", "Northern soul e os classicos da pista"),
    ],
    "Velvet Grooves": [
        ({"alternative r&b", "r&b"}, "R&B Alternativo", "R&B alternativo e neo soul contemporaneo"),
    ],
    "Blues Highway": [
        ({"comedy", "tango", "brega"}, "Ecletico Acustico", "Blues, brega, tango e sons ecleticos"),
    ],
    "Grooves & Moves": [
        ({"italo disco", "eurodance"}, "Italo Dancefloor", "Italo disco, eurodance e energia pura"),
    ],
    "Glam & New Wave": [
        ({"synthpop", "punk", "proto-punk"}, "Synth & Punk", "Synthpop, punk e a energia new wave"),
    ],
    "Yacht Club": [
        ({"aor"}, "AOR Classics", "AOR, soft rock e os classicos radiofônicos"),
    ],
    "Odisseia Prog": [
        ({"baroque pop", "art pop"}, "Chamber Pop", "Art pop, baroque pop e arranjos orquestrais"),
    ],
    "Blue Notes": [
        ({"free jazz", "jazz ballads"}, "Late Night Jazz", "Jazz intimista, baladas e free jazz"),
    ],
    "Rima Brasileira": [
        ({"brazilian trap"}, "Trap Brasil", "Trap brasileiro e o novo som das ruas"),
    ],
    "Palavras & Sons": [
        ({"samba", "boom bap"}, "Palavra Cantada", "Spoken word com samba e hip hop"),
    ],
    "Jazz Novo": [
        ({"acid jazz", "retro soul"}, "Acid Jazz Revival", "Acid jazz, retro soul e grooves novos"),
    ],
}

# Audio-profile based differentiators (fallback when genres don't differentiate)
AUDIO_DIFFERENTIATORS = {
    "Caleidoscopio": [
        (lambda p: p["Acousticness"] > 0.6, "Acustico", "Psicodelia acustica e folk psicodelico"),
        (lambda p: p["Energy"] > 0.78, "Eletrico", "Rock psicodelico em alta voltagem"),
        (lambda p: p["Valence"] > 0.7, "Radiante", "Rock psicodelico vibrante e solar"),
        (lambda p: p["Valence"] < 0.3, "Sombrio", "Psicodelia sombria e introspectiva"),
        (lambda p: p["Energy"] < 0.45, "Crepuscular", "Psicodelia lenta e meditativa"),
    ],
    "Golden Era Crates": [
        (lambda p: p["Energy"] > 0.72, "High Energy", "Hip hop com energia total"),
        (lambda p: p["Danceability"] > 0.78, "Dancefloor", "Hip hop que faz a pista bombar"),
        (lambda p: p["Valence"] < 0.4, "Introspectivo", "Hip hop sombrio e introspectivo"),
    ],
    "Tarde no Rio": [
        (lambda p: p["Acousticness"] > 0.65, "Acustico", "Bossa e MPB acusticos e intimistas"),
        (lambda p: p["Energy"] > 0.6, "Vibrante", "MPB e samba com energia e alegria"),
        (lambda p: p["Valence"] > 0.75, "Solar", "Bossa nova e samba pra dia de sol"),
        (lambda p: p["Energy"] < 0.35, "Noturno", "Bossa nova e jazz para noites quietas"),
    ],
    "Soul Jazz Cafe": [
        (lambda p: p["Valence"] > 0.8, "Groovy", "Soul jazz vibrante e cheio de groove"),
        (lambda p: p["Acousticness"] > 0.5, "Acustico", "Jazz intimista e arranjos acusticos"),
        (lambda p: p["Energy"] > 0.75, "On Fire", "Soul jazz eletrizante e cheio de energia"),
    ],
    "Nova Onda Brasileira": [
        (lambda p: p["Acousticness"] > 0.6, "Raizes", "MPB acustica e raizes brasileiras"),
        (lambda p: p["Energy"] > 0.75, "Eletrica", "Nova MPB com energia e atitude rock"),
    ],
    "Riddim Foundation": [
        (lambda p: p["Danceability"] > 0.8, "Dancefloor", "Reggae e rocksteady pra dancar"),
        (lambda p: p["Energy"] > 0.58, "Energetico", "Reggae com energia e vibração alta"),
    ],
}


def match_playlist_name(top_genres, audio_profile, mode="descriptive"):
    """
    Match a cluster's top genres against the signature table.
    Returns (base_name, name, description).
    base_name is used for grouping duplicates.

    mode="descriptive": match PLAYLIST_SIGNATURES first, fall back to generated names.
    mode="creative": skip signatures entirely, always generate genre+audio-descriptor names.
    """
    if mode == "creative":
        return _generate_name(top_genres, audio_profile)

    genre_set = set(g for g, _ in top_genres[:8])

    best_score = 0
    best_match = None

    for sig_genres, name, description in PLAYLIST_SIGNATURES:
        intersection = genre_set & sig_genres
        union = genre_set | sig_genres
        jaccard = len(intersection) / len(union) if union else 0
        top_bonus = 0.15 if top_genres and top_genres[0][0] in sig_genres else 0
        score = jaccard + top_bonus

        if score > best_score:
            best_score = score
            best_match = (name, name, description)

    if best_score >= 0.15 and best_match:
        return best_match

    return _generate_name(top_genres, audio_profile)


def differentiate_name(base_name, top_genres, audio_profile, used_names):
    """
    Given a base_name that's already taken, find a differentiated name
    based on the sub-cluster's unique genres and audio profile.
    """
    genre_set = set(g for g, _ in top_genres[:8])

    # Try genre-based differentiators first
    if base_name in GENRE_DIFFERENTIATORS:
        for diff_genres, diff_name, diff_desc in GENRE_DIFFERENTIATORS[base_name]:
            if diff_name not in used_names and genre_set & diff_genres:
                return diff_name, diff_desc

    # Try audio-based differentiators
    if base_name in AUDIO_DIFFERENTIATORS:
        for condition, suffix, diff_desc in AUDIO_DIFFERENTIATORS[base_name]:
            candidate = f"{base_name} — {suffix}"
            if candidate not in used_names and condition(audio_profile):
                return candidate, diff_desc

    # Final fallback: use the most distinctive genre not in the base signature
    base_sig_genres = set()
    for sig_genres, name, _ in PLAYLIST_SIGNATURES:
        if name == base_name:
            base_sig_genres = sig_genres
            break

    unique_genres = [g for g, _ in top_genres[:5] if g not in base_sig_genres]
    if unique_genres:
        diff_genre = unique_genres[0].title()
        candidate = f"{base_name} + {diff_genre}"
        desc = f"{base_name} com enfase em {diff_genre.lower()}"
        if candidate not in used_names:
            return candidate, desc

    # Absolute fallback with audio descriptor
    descriptor = _audio_descriptor(audio_profile)
    candidate = f"{base_name} — {descriptor}"
    if candidate not in used_names:
        return candidate, f"{base_name} com vibe {descriptor.lower()}"

    # Last resort: numbered (should rarely happen now)
    i = 2
    while f"{base_name} {i}" in used_names:
        i += 1
    return f"{base_name} {i}", f"Mais {base_name.lower()}"


def _generate_name(top_genres, audio_profile):
    """Generate a playlist name from genre + audio descriptors."""
    if not top_genres:
        descriptor = _audio_descriptor(audio_profile)
        return "Mix", f"{descriptor} Mix", f"Uma selecao {descriptor.lower()} de sons variados"

    main_genre = top_genres[0][0].title()
    descriptor = _audio_descriptor(audio_profile)
    name = f"{main_genre} — {descriptor}"
    description = f"{main_genre} e sons relacionados com vibe {descriptor.lower()}"
    return name, name, description


def _audio_descriptor(profile):
    """Pick a vibe descriptor based on audio features."""
    energy = profile.get("Energy", 0.5)
    valence = profile.get("Valence", 0.5)
    acousticness = profile.get("Acousticness", 0.3)
    danceability = profile.get("Danceability", 0.5)
    instrumentalness = profile.get("Instrumentalness", 0.2)

    if energy < 0.35 and acousticness > 0.5:
        return "Acustico"
    if energy < 0.4 and valence < 0.4:
        return "Noturno"
    if energy > 0.75 and danceability > 0.7:
        return "Eletrico"
    if valence > 0.7 and energy > 0.5:
        return "Solar"
    if instrumentalness > 0.5:
        return "Instrumental"
    if danceability > 0.75:
        return "Groovy"
    if energy > 0.7:
        return "Intenso"
    if valence > 0.6:
        return "Vibrante"
    if acousticness > 0.5:
        return "Organico"
    return "Ecletico"
