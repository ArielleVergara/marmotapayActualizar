import requests

search_url = 'https://steamcommunity.com/actions/SearchApps/'
details_url = 'https://store.steampowered.com/api/appdetails?appids='

def get_appId(appName):
    data = requests.get(search_url + appName).json()

    # 1. coincidencia exacta
    for result in data:
        if result["name"].lower() == appName.lower():
            return result["appid"]

    # 2. fallback: primer resultado
    if data:
        return data[0]["appid"]

    return None

def extract_age_rating(data):
    rating_sources = [
        ("ESRB", lambda d: d["ratings"]["esrb"]["rating"]),
        ("PEGI", lambda d: d["ratings"]["pegi"]["rating"]),
        ("DEJUS", lambda d: d["ratings"]["dejus"]["rating"]),
        ("REQUIRED_AGE", lambda d: d["required_age"]),
    ]

    for system, getter in rating_sources:
        try:
            value = getter(data)
            if value not in (None, "", 0):
                return value, system
        except (KeyError, TypeError):
            pass

    return None, None

def get_appDetail(appid):
    if appid is None:
        return None, "appid_none"

    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        return None, {"error": "request_error", "detail": str(e)}

    app = result.get(str(appid))
    if not app or not app.get("success"):
        return None, {"error": "api_failed"}

    data = app.get("data", {})

    warnings = []
    details = {"appid": appid}

    #Descripción
    try:
        details["short_description"] = data["short_description"]
    except KeyError:
        details["short_description"] = None
        warnings.append("missing_short_description")

    #Fecha de lanzamiento
    try:
        details["release_date"] = data["release_date"]["date"]
    except (KeyError, TypeError):
        details["release_date"] = None
        warnings.append("missing_release_date")

    #Géneros
    try:
        details["genres"] = [g["description"] for g in data["genres"]]
    except (KeyError, TypeError):
        details["genres"] = []
        warnings.append("missing_genres")

    # Clasificación por edad (ESRB → PEGI → DEJUS → required_age)
    age_rating, age_rating_system = extract_age_rating(data)

    if age_rating is None:
        warnings.append("missing_age_rating")


    details["age_rating"] = age_rating
    details["age_rating_system"] = age_rating_system

    if warnings:
        details["warnings"] = warnings

    return details, "success"