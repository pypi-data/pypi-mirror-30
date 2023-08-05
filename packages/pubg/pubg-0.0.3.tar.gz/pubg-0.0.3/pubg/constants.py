class Region:
    """Class containing available regions."""
    xbox_as = 'xbox-as'  # Asia
    xbox_eu = 'xbox-eu'  # Europe
    xbox_na = 'xbox-na'  # North America
    xbox_oc = 'xbox-oc'  # Oceania
    pc_krjp = 'pc-krjp'  # Korea / Japan
    pc_na = 'pc-na'  # North America
    pc_eu = 'pc-eu'  # Europe
    pc_oc = 'pc-oc'  # Oceania
    pc_kakao = 'pc-kakao'
    pc_sea = 'pc-sea'  # South East Asia
    pc_sa = 'pc-sa'  # South and Central America
    pc_as = 'pc-as'  # Asia


class Endpoint:
    base = 'https://api.playbattlegrounds.com'
    matches = '/shards/{region}/matches'
    match = '/shards/{region}/matches/{id}'
    status = '/status'
