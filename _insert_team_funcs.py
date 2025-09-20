from pathlib import Path

path = Path('modules/estudio_scraper.py')
text = path.read_text(encoding='utf-8')
needle = 'def obtener_datos_completos_partido'
if needle not in text:
    raise SystemExit('Function marker not found')
first, second = text.split(needle, 1)
if 'def get_team_league_info_from_script_of' in first:
    raise SystemExit('Functions already present')
team_funcs = '''def get_team_league_info_from_script_of(soup):
    script_tag = soup.find("script", string=re.compile(r"var _matchInfo = "))
    if not (script_tag and script_tag.string):
        return (None,) * 3 + ("N/A",) * 3
    content = script_tag.string

    def find_val(pattern):
        match = re.search(pattern, content)
        return match.group(1).replace("'", "") if match else None

    home_id = find_val(r"hId:\s*parseInt\('(\d+)'\)")
    away_id = find_val(r"gId:\s*parseInt\('(\d+)'\)")
    league_id = find_val(r"sclassId:\s*parseInt\('(\d+)'\)")
    home_name = find_val(r"hName:\s*'([^']*)'") or "N/A"
    away_name = find_val(r"gName:\s*'([^']*)'") or "N/A"
    league_name = find_val(r"lName:\s*'([^']*)'") or "N/A"
    return home_id, away_id, league_id, home_name, away_name, league_name


def get_match_datetime_from_script_of(soup):
    """Extrae fecha/hora del script _matchInfo si está disponible."""
    result = {"match_date": None, "match_time": None, "match_datetime": None}
    try:
        script_tag = soup.find("script", string=re.compile(r"var _matchInfo = "))
        if not (script_tag and script_tag.string):
            return result
        content = script_tag.string

        def find_val(pattern):
            match = re.search(pattern, content)
            return match.group(1) if match else None

        match_time_txt = find_val(r"matchTime:\s*'([^']+)'")
        start_date = find_val(r"startDate:\s*'([^']+)'")
        door_time = find_val(r"doorTime:\s*'([^']+)'")

        normalized_date = None
        normalized_time = None

        if match_time_txt:
            from datetime import datetime
            for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M"):
                try:
                    dt = datetime.strptime(match_time_txt, fmt)
                    normalized_date = dt.strftime("%Y-%m-%d")
                    normalized_time = dt.strftime("%H:%M")
                    break
                except Exception:
                    continue

        if not normalized_date and start_date:
            normalized_date = start_date
            if door_time:
                match = re.match(r"(\d{2}):(\d{2})", door_time)
                if match:
                    normalized_time = f"{match.group(1)}:{match.group(2)}"

        if normalized_date:
            result["match_date"] = normalized_date
            result["match_time"] = normalized_time
            result["match_datetime"] = f"{normalized_date} {normalized_time}".strip()
    except Exception:
        pass
    return result


'''
first = first.rstrip() + '\n\n' + team_funcs
path.write_text(first + needle + second, encoding='utf-8')
