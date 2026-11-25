# LookAtTheSky — Celestron PowerSeeker 127EQ (#21049)

Planificador determinista de sesiones astronómicas familiares, guía práctica de campo, glosario astrofísico para niños y bitácora de observación desde **Barinas, Venezuela (`8.625772, -70.202553`, UTC-4)**.

## Contenido del Repositorio

- **[GUIA_127EQ_Y_GLOSARIO.md](GUIA_127EQ_Y_GLOSARIO.md):** Plan horario de observación (`18:00` a `23:30`), configuración recomendada de oculares (`20 mm` a `50x` y técnica de 2 pasos con `4 mm` a `250x`) y diccionario astronómico explicado en sencillo para aprender con los niños.
- **[BITACORA_SESION_2026-11-24.md](BITACORA_SESION_2026-11-24.md):** Registro completo de nuestra primera sesión y conversación del 24 de noviembre de 2026 (recomendaciones para la Luna Llena, Saturno en el cenit con el ocular de `4 mm`, Las Pléyades, trucos de alineación diurna del buscador y dinámicas con los niños).
- **Manuales Oficiales de Celestron (`docs/manuals/`):**
  - **[Celestron_PowerSeeker_127EQ_21049_Manual_Oficial_Multilingue_ES.pdf](docs/manuals/Celestron_PowerSeeker_127EQ_21049_Manual_Oficial_Multilingue_ES.pdf):** Manual de instrucciones completo original de Celestron para la serie PowerSeeker EQ (incluye el modelo `#21049`). **La sección completa en español está en las páginas 61 a 90** (y en inglés en las páginas 1 a 30).
  - **[Celestron_PowerSeeker_127EQ_21049_Quick_Setup_Guide.pdf](docs/manuals/Celestron_PowerSeeker_127EQ_21049_Quick_Setup_Guide.pdf):** Guía rápida ilustrada de instalación paso a paso para los modelos `114EQ (#21045)` y `127EQ (#21049)`. **La versión en español a color está en las páginas 9 y 10**.
- **[directivas/planificador_sesion_SOP.md](directivas/planificador_sesion_SOP.md):** Procedimiento Operativo Estándar (SOP) y memoria viva de las restricciones y técnicas ópticas del Celestron PowerSeeker 127EQ.
- **[scripts/planificador_sesion.py](scripts/planificador_sesion.py):** Calculadora en Python puro (sin dependencias externas) de efemérides solares, lunares, planetarias (`Venus`, `Marte`, `Júpiter`, `Saturno`) y objetos de cielo profundo (`M45`, `M42`, `M31`, `Doble Cúmulo de Perseo`).

## Cómo calcular el plan para cualquier otra noche

```bash
python3 scripts/planificador_sesion.py --date YYYY-MM-DD
```

También puedes pasar otras coordenadas si viajas con el telescopio:

```bash
python3 scripts/planificador_sesion.py --date 2026-12-05 --lat 8.625772 --lon -70.202553 --tz -4
```

Al ejecutarse, actualiza automáticamente `GUIA_127EQ_Y_GLOSARIO.md` y guarda los reportes detallados (`.md` y `.json`) en `.tmp/`.
