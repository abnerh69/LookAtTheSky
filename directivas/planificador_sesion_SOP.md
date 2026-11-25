# Directiva: Planificador de Sesiones y Glosario Astronómico (`planificador_sesion_SOP.md`)

## 1. Objetivo
Calcular efemérides astronómicas locales (Sol, Luna, planetas visibles y objetos de cielo profundo brillantes) sin dependencias pesadas externas, adaptadas específicamente a la óptica del telescopio **Celestron PowerSeeker 127EQ (Modelo #21049)**, y generar un reporte interactivo/legible con recomendaciones de oculares, horarios óptimos para observar con niños y un glosario práctico de términos astronómicos.

## 2. Entradas
- **Ubicación geográfica:** Latitud (`--lat`, por defecto `8.625772` Barinas, Venezuela), Longitud (`--lon`, por defecto `-70.202553`), Zona horaria UTC (`--tz`, por defecto `-4.0`).
- **Fecha y ventana horaria:** Fecha local (`--date`, por defecto fecha actual del sistema) y rango horario nocturno (`18:00` a `23:30`).
- **Parámetros ópticos fijos del Celestron PowerSeeker 127EQ (#21049):**
  - Diseño: Reflector Newtoniano Bird-Jones
  - Apertura ($D$): `127 mm`
  - Distancia focal ($F$): `1000 mm` ($f/7.87$)
  - Oculares incluidos: `20 mm` (50x, imagen erecta/diagonal o estándar) y `4 mm` (250x), más Barlow `3x`.

## 3. Lógica y Pasos de Operación
1. **Cálculo de Tiempo Juliano (JD) y Tiempo Sidéreo Local (LST):**
   - Convertir cada marca horaria local a UTC y calcular `JD` y `GMST` / `LST`.
2. **Efemérides Solares y Lunares:**
   - Calcular coordenadas ecuatoriales ($\alpha$, $\delta$) del Sol y la Luna.
   - Determinar elongación, porcentaje de iluminación lunar, edad aproximada y nombre de la fase.
   - Transformar a coordenadas horizontales locales: **Altura (`Alt`)** y **Azimut (`Az`)** más punto cardinal (`E`, `ENE`, `SE`, etc.).
3. **Efemérides Planetarias y Cielo Profundo (Catálogo Familiar):**
   - Resolver posición heliocéntrica y geocéntrica para **Venus, Marte, Júpiter y Saturno**.
   - Evaluar visibilidad de objetos brillantes aptos para el 127EQ a 50x: **Pléyades (M45)**, **Nebulosa de Orión (M42)**, **Cúmulo de Ptolomeo (M7)**, **Doble Cúmulo de Perseo**, **Galaxia de Andrómeda (M31)**.
4. **Criterio de Visibilidad y Ventana Infantil (18:30 - 21:30):**
   - Filtrar objetos con `Alt >= 15°` (para evitar extinción y turbulencia atmosférica severa cerca del horizonte) cuando el Sol tenga `Alt <= -6°` (crepúsculo civil/náutico).
   - Asignar ocular recomendado del kit 127EQ según el brillo y tamaño angular del objeto.
5. **Generación de Reporte y Glosario:**
   - Guardar salida detallada en `.tmp/plan_observacion_YYYY-MM-DD.md` y mostrar resumen ejecutivo en consola si se solicita (`--print`).

## 4. Restricciones y Casos Borde (Memoria Viva)
- **Uso en dos pasos del Ocular de `4 mm` (250x) en Planetas cercanos al Cenit:** Aunque el diseño Bird-Jones del 127EQ pierde brillo a 250x y es difícil de usar para buscar objetos desde cero, **sí es utilizable con éxito en Saturno/Júpiter cuando el planeta está muy alto (`Alt > 65°`, cerca del cenit, donde la turbulencia atmosférica o *seeing* es mínima)**. La técnica obligatoria es:
  1. Centrar primero el planeta con precisión usando el ocular de `20 mm` (50x).
  2. Cambiar con cuidado al ocular de `4 mm` (250x) sin mover el tubo y reenfocar suavemente para distinguir la estructura de los anillos de Saturno.
  3. Seguir evitando combinar el `4 mm` con la lente Barlow `3x` (750x).
- **Deslumbramiento lunar:** Cuando la iluminación lunar supera el `85%` y la altura supera los `25°`, advertir sobre el brillo intenso en apertura de 127 mm y recomendar observar al inicio del anochecer o con luz ambiental suave.
- **Portabilidad:** El script debe funcionar con la librería estándar de Python (`math`, `datetime`, `argparse`, `json`, `pathlib`) para no fallar si `astropy` o `ephem` no están instalados en el entorno.
