#!/usr/bin/env python3
"""
Planificador determinista de sesiones de observación astronómica y glosario práctico
para el telescopio Celestron PowerSeeker 127EQ (Modelo #21049).
Basado en directivas/planificador_sesion_SOP.md.
"""

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

TELESCOPE_SPECS = {
    "model": "Celestron PowerSeeker 127EQ (#21049)",
    "design": "Reflector Newtoniano Bird-Jones",
    "aperture_mm": 127,
    "focal_length_mm": 1000,
    "focal_ratio": 7.87,
    "mount": "Ecuatorial Alemana Manual (CG-1)",
    "eyepieces": {
        "20mm": {"magnification": 50, "fov_deg": 1.0, "status": "BASE (usar para buscar, centrar, Luna entera y cúmulos)"},
        "4mm": {"magnification": 250, "fov_deg": 0.16, "status": "PLANETARIO EN CENIT (cambiar tras centrar con 20 mm cuando Alt > 65°, ideal para anillos de Saturno)"},
        "barlow_3x": {"magnification": "150x / 750x", "status": "EVITAR con 4 mm (750x excede el límite físico del espejo de 127 mm)"},
    },
}

PLANET_ELEMENTS = {
    "Venus":   (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255,  0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    "Earth":   (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0,         0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    "Mars":    (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891,   0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    "Jupiter": (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909,  -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    "Saturn":  (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448,  -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
}

DEEP_SKY_CATALOG = [
    {"id": "M45", "name": "Las Pléyades (Siete Cabritas)", "ra_deg": 56.87, "dec_deg": 24.11, "type": "Cúmulo abierto", "kid_tip": "Racimo de estrellas azules brillantes; pedirles que cuenten cuántas ven con el ocular de 20 mm."},
    {"id": "M42", "name": "Gran Nebulosa de Orión", "ra_deg": 83.82, "dec_deg": -5.39, "type": "Nebulosa de emisión", "kid_tip": "Una 'nube fantasma' donde están naciendo estrellas nuevas; buscar las 4 estrellitas del Trapecio en el centro."},
    {"id": "M31", "name": "Galaxia de Andrómeda", "ra_deg": 10.68, "dec_deg": 41.27, "type": "Galaxia espiral", "kid_tip": "Se ve como una mota ovalada de algodón; la luz que entra a sus ojos salió hace 2.5 millones de años."},
    {"id": "NGC 869/884", "name": "Doble Cúmulo de Perseo", "ra_deg": 35.0, "dec_deg": 57.13, "type": "Cúmulo doble", "kid_tip": "Dos cofres de joyas estelares juntos en el mismo campo del ocular de 20 mm."},
]

GLOSSARY = [
    ("Apertura (127 mm)", "El diámetro del espejo principal al fondo del tubo. Es el 'embudo de luz': mientras más grande, más brillantes y detallados se ven los astros."),
    ("Distancia Focal (1000 mm)", "El recorrido que hace la luz dentro del telescopio hasta enfocar. Define qué tan grandes se ven las cosas."),
    ("Aumento (Magnificación)", "Se calcula dividiendo la Distancia Focal del telescopio (1000 mm) entre los milímetros del ocular. Con el ocular de 20 mm: 1000 / 20 = 50x (50 veces más cerca)."),
    ("Relación Focal (f/7.87)", "El resultado de dividir la distancia focal (1000) entre la apertura (127). Es como la apertura de una cámara: f/7.87 es un término medio versátil para Luna, planetas y cúmulos."),
    ("Ocular (20 mm / 4 mm)", "El lente pequeño intercambiable donde pones el ojo. Regla contraintuitiva: mientras MÁS GRANDE es el número en mm (20 mm), MENOS aumento da, pero la imagen es MÁS brillante, nítida y fácil de encontrar."),
    ("Lente Barlow (3x)", "Un tubo con lente que triplica el aumento del ocular. En el 127EQ conviene no usarla con niños porque oscurece la imagen y amplifica cualquier temblor."),
    ("Diseño Bird-Jones", "El diseño interno de tu 127EQ: usa un espejo esférico en un tubo corto (~50 cm) con un lente corrector dentro del enfocador para lograr 1000 mm de focal en un tubo compacto."),
    ("Montura Ecuatorial (EQ / CG-1)", "El mecanismo de ejes inclinados entre el trípode y el tubo. Está diseñado para que, una vez alineado con el Norte, puedas seguir un astro girando un solo mando flexible a medida que la Tierra rota."),
    ("Buscador (Finderscope)", "La 'mira telescópica' pequeñita montada encima del tubo principal. Tiene mucho campo visual y sirve para apuntar primero antes de mirar por el ocular."),
    ("Altura (Altitud, 0° a 90°)", "Qué tan alto está un astro sobre el horizonte. 0° es pegado al suelo/horizonte; 45° es a mitad de camino; 90° es el Cenit (exactamente arriba de tu cabeza)."),
    ("Azimut (0° a 360°)", "La dirección de brújula hacia donde debes mirar: Norte = 0°, Este = 90°, Sur = 180°, Oeste = 270°."),
    ("Cenit", "El punto del cielo que está exactamente en vertical sobre tu cabeza (Altura = 90°). Allí la atmósfera es más delgada y las imágenes se ven más limpias."),
    ("Terminador Lunar", "La línea que separa el día y la noche en la Luna. En Cuarto Creciente o Menguante los cráteres sobre esa línea proyectan sombras largas espectaculares."),
    ("Limbo Lunar", "El borde exterior del disco de la Luna. En noches de Luna Llena es donde mejor se ven de perfil las montañas y paredes de cráteres."),
    ("Seeing (Estabilidad atmosférica)", "Qué tan quieto o turbulento está el aire arriba. Si las estrellas titilan mucho o la Luna parece 'hervir' como asfalto caliente, hay mal seeing (común cerca del horizonte)."),
]


def jd_from_utc(dt_utc: datetime) -> float:
    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day + (dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = int(y / 100)
    b = 2 - a + int(a / 4)
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def gmst_deg(jd: float) -> float:
    t = (jd - 2451545.0) / 36525.0
    st = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t
    return st % 360.0


def az_to_cardinal(az_deg: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    idx = int(((az_deg + 11.25) % 360.0) / 22.5)
    return dirs[idx]


def radec_to_altaz(ra_deg: float, dec_deg: float, lat_deg: float, lon_deg: float, jd: float):
    lst_deg = (gmst_deg(jd) + lon_deg) % 360.0
    ha_rad = math.radians((lst_deg - ra_deg) % 360.0)
    dec_rad = math.radians(dec_deg)
    lat_rad = math.radians(lat_deg)
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    alt_rad = math.asin(max(-1.0, min(1.0, sin_alt)))
    cos_az = (math.sin(dec_rad) - math.sin(alt_rad) * math.sin(lat_rad)) / (math.cos(alt_rad) * math.cos(lat_rad) + 1e-12)
    az_rad = math.acos(max(-1.0, min(1.0, cos_az)))
    if math.sin(ha_rad) > 0:
        az_rad = 2.0 * math.pi - az_rad
    return math.degrees(alt_rad), math.degrees(az_rad)


def sun_radec(jd: float):
    n = jd - 2451545.0
    l_deg = (280.460 + 0.9856474 * n) % 360.0
    g_rad = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam_deg = (l_deg + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2.0 * g_rad)) % 360.0
    lam_rad = math.radians(lam_deg)
    eps_rad = math.radians(23.439 - 0.0000004 * n)
    ra_deg = math.degrees(math.atan2(math.cos(eps_rad) * math.sin(lam_rad), math.cos(lam_rad))) % 360.0
    dec_deg = math.degrees(math.asin(math.sin(eps_rad) * math.sin(lam_rad)))
    return ra_deg, dec_deg, lam_deg


def moon_radec(jd: float):
    t = (jd - 2451545.0) / 36525.0
    l0 = (218.3164477 + 481267.88123421 * t) % 360.0
    m = math.radians((134.9633964 + 477198.8675055 * t) % 360.0)
    ms = math.radians((357.5291092 + 35999.0502909 * t) % 360.0)
    d = math.radians((297.8501921 + 445267.1114034 * t) % 360.0)
    f = math.radians((93.2720950 + 483202.0175233 * t) % 360.0)
    lon = (
        l0
        + 6.289 * math.sin(m)
        + 1.274 * math.sin(2 * d - m)
        + 0.658 * math.sin(2 * d)
        + 0.214 * math.sin(2 * m)
        - 0.186 * math.sin(ms)
        - 0.114 * math.sin(2 * f)
    )
    lat = 5.128 * math.sin(f) + 0.280 * math.sin(m + f) + 0.277 * math.sin(m - f) + 0.173 * math.sin(2 * d - f)
    eps = math.radians(23.439291 - 0.0130042 * t)
    lon_r = math.radians(lon % 360.0)
    lat_r = math.radians(lat)
    x = math.cos(lat_r) * math.cos(lon_r)
    y = math.cos(eps) * math.cos(lat_r) * math.sin(lon_r) - math.sin(eps) * math.sin(lat_r)
    z = math.sin(eps) * math.cos(lat_r) * math.sin(lon_r) + math.cos(eps) * math.sin(lat_r)
    ra_deg = math.degrees(math.atan2(y, x)) % 360.0
    dec_deg = math.degrees(math.asin(z))
    return ra_deg, dec_deg, lon % 360.0


def helio_xyz(name: str, t_centuries: float):
    a0, e0, i0, l0, w0, o0, da, de, di, dl, dw, do = PLANET_ELEMENTS[name]
    a = a0 + da * t_centuries
    e = e0 + de * t_centuries
    inc = math.radians(i0 + di * t_centuries)
    l_deg = (l0 + dl * t_centuries) % 360.0
    w_deg = (w0 + dw * t_centuries) % 360.0
    o_deg = (o0 + do * t_centuries) % 360.0
    m_rad = math.radians((l_deg - w_deg) % 360.0)
    arg_p = math.radians((w_deg - o_deg) % 360.0)
    o_rad = math.radians(o_deg)
    ecc_anom = m_rad
    for _ in range(6):
        ecc_anom = m_rad + e * math.sin(ecc_anom)
    xp = a * (math.cos(ecc_anom) - e)
    yp = a * math.sqrt(1.0 - e * e) * math.sin(ecc_anom)
    x = (math.cos(arg_p) * math.cos(o_rad) - math.sin(arg_p) * math.sin(o_rad) * math.cos(inc)) * xp + (
        -math.sin(arg_p) * math.cos(o_rad) - math.cos(arg_p) * math.sin(o_rad) * math.cos(inc)
    ) * yp
    y = (math.cos(arg_p) * math.sin(o_rad) + math.sin(arg_p) * math.cos(o_rad) * math.cos(inc)) * xp + (
        -math.sin(arg_p) * math.sin(o_rad) + math.cos(arg_p) * math.cos(o_rad) * math.cos(inc)
    ) * yp
    z = (math.sin(arg_p) * math.sin(inc)) * xp + (math.cos(arg_p) * math.sin(inc)) * yp
    return x, y, z


def planet_radec(name: str, jd: float):
    t = (jd - 2451545.0) / 36525.0
    ex, ey, ez = helio_xyz("Earth", t)
    px, py, pz = helio_xyz(name, t)
    dx, dy, dz = px - ex, py - ey, pz - ez
    eps = math.radians(23.439291 - 0.0130042 * t)
    x_eq = dx
    y_eq = dy * math.cos(eps) - dz * math.sin(eps)
    z_eq = dy * math.sin(eps) + dz * math.cos(eps)
    ra_deg = math.degrees(math.atan2(y_eq, x_eq)) % 360.0
    dec_deg = math.degrees(math.atan2(z_eq, math.sqrt(x_eq * x_eq + y_eq * y_eq)))
    return ra_deg, dec_deg


def moon_phase_name(elong_deg: float) -> str:
    if elong_deg < 22.5 or elong_deg >= 337.5:
        return "Luna Nueva"
    if elong_deg < 67.5:
        return "Creciente Cóncava"
    if elong_deg < 112.5:
        return "Cuarto Creciente"
    if elong_deg < 157.5:
        return "Gibosa Creciente"
    if elong_deg < 202.5:
        return "Luna Llena"
    if elong_deg < 247.5:
        return "Gibosa Menguante"
    if elong_deg < 292.5:
        return "Cuarto Menguante"
    return "Menguante Cóncava"


def build_plan(date_str: str, lat: float, lon: float, tz_offset: float) -> dict:
    tz = timezone(timedelta(hours=tz_offset))
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    slots = []
    for hr in range(18, 24):
        for mn in (0, 30):
            dt_loc = datetime(base_date.year, base_date.month, base_date.day, hr, mn, tzinfo=tz)
            jd = jd_from_utc(dt_loc.astimezone(timezone.utc))
            s_ra, s_dec, s_lam = sun_radec(jd)
            m_ra, m_dec, m_lam = moon_radec(jd)
            s_alt, _ = radec_to_altaz(s_ra, s_dec, lat, lon, jd)
            m_alt, m_az = radec_to_altaz(m_ra, m_dec, lat, lon, jd)
            elong = (m_lam - s_lam) % 360.0
            illum = (1.0 - math.cos(math.radians(elong))) / 2.0 * 100.0

            p_data = {}
            for pname in ("Venus", "Mars", "Jupiter", "Saturn"):
                pra, pdec = planet_radec(pname, jd)
                palt, paz = radec_to_altaz(pra, pdec, lat, lon, jd)
                p_data[pname] = {"alt": round(palt, 1), "az": round(paz, 1), "cardinal": az_to_cardinal(paz)}

            dso_data = {}
            for dso in DEEP_SKY_CATALOG:
                dalt, daz = radec_to_altaz(dso["ra_deg"], dso["dec_deg"], lat, lon, jd)
                dso_data[dso["id"]] = {"alt": round(dalt, 1), "az": round(daz, 1), "cardinal": az_to_cardinal(daz)}

            slots.append(
                {
                    "time": dt_loc.strftime("%H:%M"),
                    "sun_alt": round(s_alt, 1),
                    "moon": {
                        "alt": round(m_alt, 1),
                        "az": round(m_az, 1),
                        "cardinal": az_to_cardinal(m_az),
                        "illum_pct": round(illum, 1),
                        "phase": moon_phase_name(elong),
                    },
                    "planets": p_data,
                    "dso": dso_data,
                }
            )

    return {
        "date": date_str,
        "location": {"lat": lat, "lon": lon, "tz_utc": tz_offset},
        "telescope": TELESCOPE_SPECS,
        "slots": slots,
    }


def render_markdown(plan: dict) -> str:
    m0 = plan["slots"][3]["moon"]  # 19:30 reference
    lines = [
        f"# Plan de Observación y Guía 127EQ ({plan['date']})",
        "",
        f"- **Ubicación:** `{plan['location']['lat']}, {plan['location']['lon']}` (UTC{plan['location']['tz_utc']:+g})",
        f"- **Telescopio:** {plan['telescope']['model']} (`D={plan['telescope']['aperture_mm']} mm`, `F={plan['telescope']['focal_length_mm']} mm`, `f/{plan['telescope']['focal_ratio']}`)",
        f"- **Fase Lunar de esta noche:** **{m0['phase']}** ({m0['illum_pct']}% iluminada)",
        "",
        "## 1. Bitácora Horaria (18:00 a 23:30)",
        "",
        "| Hora | Luna (Altura / Rumbo) | Saturno (Altura / Rumbo) | Pléyades M45 (Altura / Rumbo) | Nebulosa Orión M42 |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for s in plan["slots"]:
        m = s["moon"]
        sat = s["planets"]["Saturn"]
        m45 = s["dso"]["M45"]
        m42 = s["dso"]["M42"]
        m_str = f"**{m['alt']}°** ({m['cardinal']}, {m['az']}°)" if m["alt"] > 0 else f"Bajo horiz. ({m['alt']}°)"
        sat_str = f"**{sat['alt']}°** ({sat['cardinal']}, {sat['az']}°)" if sat["alt"] > 0 else f"Bajo horiz. ({sat['alt']}°)"
        m45_str = f"**{m45['alt']}°** ({m45['cardinal']})" if m45["alt"] > 0 else f"Bajo horiz. ({m45['alt']}°)"
        m42_str = f"**{m42['alt']}°** ({m42['cardinal']})" if m42["alt"] > 0 else f"Bajo horiz. ({m42['alt']}°)"
        lines.append(f"| **{s['time']}** | {m_str} | {sat_str} | {m45_str} | {m42_str} |")

    lines.extend(
        [
            "",
            "## 2. Configuración Recomendada del Telescopio",
            "",
            "- **Técnica de 2 pasos (20 mm -> 4 mm):**",
            "  1. **Ocular de 20 mm (50x):** Úsalo siempre primero para localizar, centrar el astro, ver la Luna completa y cúmulos como las Pléyades.",
            "  2. **Ocular de 4 mm (250x):** Cuando un planeta brillante como Saturno está muy alto cerca del cenit (`Alt > 65°`, como a las 20:30 con `79.5°`), céntralo primero con el de 20 mm, cámbialo con cuidado al de 4 mm y enfoca suave para resolver mejor los anillos.",
            "- **Barlow 3x:** No combinar con el de 4 mm (750x supera el límite óptico de 127 mm).",
            "",
            "## 3. Diccionario Astronómico Práctico (Para aprender con los niños)",
            "",
        ]
    )
    for term, desc in GLOSSARY:
        lines.append(f"- **{term}:** {desc}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Planificador de sesión astronómica para Celestron PowerSeeker 127EQ")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Fecha YYYY-MM-DD")
    parser.add_argument("--lat", type=float, default=8.625772, help="Latitud en grados decimales")
    parser.add_argument("--lon", type=float, default=-70.202553, help="Longitud en grados decimales")
    parser.add_argument("--tz", type=float, default=-4.0, help="Zona horaria respecto a UTC")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    tmp_dir = root / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    plan = build_plan(args.date, args.lat, args.lon, args.tz)
    md_content = render_markdown(plan)

    md_path = tmp_dir / f"plan_observacion_{args.date}.md"
    json_path = tmp_dir / f"plan_observacion_{args.date}.json"
    guide_path = root / "GUIA_127EQ_Y_GLOSARIO.md"

    md_path.write_text(md_content, encoding="utf-8")
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    guide_path.write_text(md_content, encoding="utf-8")


if __name__ == "__main__":
    main()
