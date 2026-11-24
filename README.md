# Ingroup

Entrenamiento de afinación para viento metal.

Web: https://zumodepato.github.io/InGroup/

## Secciones

- **Oído**: Intervalos (¿la segunda nota está alta o baja?) y Afinar nota (vara).
- **Acordes**
  - *Construir*: te dice el acorde (p. ej. Do mayor · C) y lo construyes a 4 voces (fundamental grave, 5ª, fundamental aguda y 3ª) en afinación pura, con balance de volumen por voz.
  - *Dron*: suena el acorde; quitas una o más voces y las tocas tú encima, con medidor de afinación por micrófono.
  - *Grabar*: graba a la sección y dice cuánto mover cada voz.
- **Corales**: partitura tipo PDF (descargable) con la notación de MuseScore; 33 corales y piezas a 3–6 voces ordenadas por épocas (Renacimiento, Barroco, Clasicismo, Romanticismo). Se pueden quitar voces, cambiar el tempo, ver la partitura de tu voz (trompeta en Si♭, concierto, trompa en Fa o clave de Fa) y medir tu afinación.
- **Boquilla**: ejercicio de embocadura con metrónomo y varios pentagramas.
- **Récords**.

## Tipografías

- Notación: [Leland](https://github.com/musescore/MuseScore/tree/master/fonts/leland), la de MuseScore (SIL OFL 1.1). Textos de partitura: Edwin (SIL OFL 1.1). Subconjuntos en `fonts/` con sus licencias.

## Fuentes de las partituras

- Corales de J. S. Bach: edición digital de Craig Stuart Sapp, basada en la edición de Breitkopf & Härtel (c. 1875). Licencia [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). https://github.com/craigsapp/bach-370-chorales
- Resto de piezas (Wacław z Szamotuł, Gomółka, Palestrina, Marenzio, Gorczycki, Różycki, Elsner, Moniuszko, Żeleński): «Polish Music Heritage in Open Access», Instituto Fryderyk Chopin. Licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). https://github.com/pl-wnifc/humdrum-polish-scores

`corales.js` se genera a partir de esos archivos Humdrum: las voces se ordenan de aguda a grave, los calderones se alargan un tiempo y, para la agrupación de trompetas, cada pieza se transporta y las voces graves se suben de octava para que quepan en la trompeta. Las corales de Bach tienen licencia no comercial: si la app pasa a ser de pago, hay que sustituirlas.
