import re
import unicodedata
from steam_utils import get_appId
from steam_utils import get_appDetail

def normalizar_nombre(nombre):
    # quitar acentos
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode()

    # lower
    nombre = nombre.lower()

    # quitar paréntesis y corchetes
    nombre = re.sub(r"\([^)]*\)", "", nombre)
    nombre = re.sub(r"\[[^\]]*\]", "", nombre)

    # quitar guiones y símbolos
    nombre = re.sub(r"[-–—:™®']", " ", nombre)

    # palabras basura
    basura = ["ps4", "ps5", "xbox", "switch", "nsw", "edition", "deluxe", "complete"]
    for b in basura:
        nombre = re.sub(rf"\b{b}\b", "", nombre)

    # espacios múltiples
    nombre = re.sub(r"\s+", " ", nombre).strip()

    return nombre

def resolver_appids(game_names):
    found_appids = []
    games_without_id = []

    for game in game_names:
        clean_name = normalizar_nombre(game)
        appid = get_appId(clean_name)

        if appid is not None:
            found_appids.append({
                "name": game,
                "clean_name": clean_name,
                "appid": appid
            })
        else:
            games_without_id.append(game)

    return found_appids, games_without_id

def cargar_detalles_juegos(found_appids):
    successful = []
    problem_games = []

    for game in found_appids:
        details, status = get_appDetail(game["appid"])

        if details:
            details["name"] = game["clean_name"]
            successful.append(details)
            if "warnings" in details:
                problem_games.append({
                    "appid": game["appid"],
                    "issues": details["warnings"]
                })
        else:
            problem_games.append({
                "appid": game["appid"],
                "issues": [status]
            })

    return successful, problem_games