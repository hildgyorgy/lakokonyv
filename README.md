# Lakókönyv

A BME Lakóépülettervezési Tanszék 2013-as digitális tankönyvének rekonstruált, statikus webes kiadása.

## Szerkezet

- `source/lakokonyv.md` – az egyetlen kanonikus szerkesztési forrás.
- `source/images/` – az eredeti, nagyfelbontású képanyag; ezeket a build nem módosítja.
- `template/book.html` – minimális HTML-sablon.
- `assets/book.css` – a kiadvány stílusa.
- `build/build.py` – függőségmentes Python build és ellenőrzés.
- `dist/workbench.html` – helyi munkapad az ábrák egyenkénti kézi méretezéséhez.
- `audit/` – reconciliation manifest, gépi audit és forrás-ujjlenyomatok.
- `dist/` – generált kimenet, nem verziózandó.

## Build

Python 3.10 vagy újabb szükséges. A projekt gyökeréből:

```sh
python3 build/build.py
```

A parancs újragenerálja a `dist/index.html`, `dist/book.css` és `dist/images/` fájlokat. Ellenőrzi a belső hivatkozásokat és a Markdownban megadott képútvonalakat. A dokumentált `MISSING` elem – az 5.59. ábra – figyelmeztetésként megmarad; nem helyettesítjük találgatással.

## Nyitott szerkesztői ügyek

- `REVIEW`: a 3.14 / 3.15 / 3.16 nappálya-ábrák számozási anomáliája.
- `MISSING`: 5.59. ábra – „Zöldhomlokzat spontán kialakulása”. Az eredeti kép egyik fennmaradt forrásban sincs meg.

A rekonstruált szöveget és ábraszámozást első körben nem modernizáljuk és nem szerkesztjük át stilisztikailag.

## Ábra-munkapad

Nyisd meg a `dist/workbench.html` oldalt, állítsd be az ábrák szélességét, majd válaszd a „Méretlista exportálása” gombot. Az exportált `image_layout.json` fájlt másold az `audit/image_layout.json` helyére, és futtasd újra a buildet. A végleges méretek ekkor bekerülnek a generált könyvoldalba; a `source/images/` fájlai változatlanok maradnak.
