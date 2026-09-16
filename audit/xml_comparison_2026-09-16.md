# Az XML és a Markdown forrás összehasonlítása

Dátum: 2026. szeptember 16.

## Összefoglaló

**A jelenlegi `source/lakokonyv.md` szakmai törzsszövege és fejezetszerkezete teljesnek bizonyult a most kapott, különálló XML-fejezetekhez képest. Nem találtam az XML-ben olyan hiányzó szakmai bekezdést vagy fejezetet, amelyet most kellene visszaemelni.** Az XML fő többlete az eredeti DocBook-szerkezet, a részletesebb kiadványmetaadatok és a többféle képállomány.

A Markdown több helyen már javított vagy szerkesztett változatot tartalmaz. Az XML automatikus átvétele ezek egy részét visszarontaná. A meglévő mestert érdemes megtartani, az XML-t pedig ellenőrzési és archiválási forrásként használni.

Kiemelt eredmények:

- A bevezetés, mind a 7 fejezet, az 51 alfejezet és a 69 további alfejezet megtalálható a Markdownban, azonos hierarchiával.
- A 212 ábra sorrendje azonos; egyetlen azonosító átnevezése érinti a nappálya-ábrákat.
- A 355 belső hivatkozásból 353 szövege és célja egyezik; a két eltérés ugyanazt a nappálya-számozási ügyet érinti.
- Az 5.59. kép **már szerepel a jelenlegi Markdownban**, és az XML-csomagban is megvan. Az XML azonban hibásan az 5.58. fájljára hivatkozik. A README és a Markdown fejlécének „MISSING” állítása elavult.
- Az 5.31. Markdown-képaláírásban valóban kétszer szerepel az ábraszám.

Az elemzés során a könyv forrását és képállományát nem módosítottam.

## 1. Melyik XML-változat mit jelent?

A tényleges könyvtár `source/xml/` (nem `sources/xml/`). A csomag három részből áll:

1. **`Bito_konyv.xml`:** DocBook 4.5 könyvkeret, bibliográfiai adatokkal és a nyolc tartalmi fájl XInclude-hivatkozásaival.
2. **`00_bevezetes.xml`–`07_lakasallomany.xml`:** külön szerkeszthető fejezetek. Ezeket vettem elsődleges XML-összehasonlítási alapnak.
3. **`xincluded-profiled2355.xml`:** összefűzött, profilozott példány. Tartalma több ponton korábbi állapotot őriz; nem egyszerű másolata a külön fájlok mai tartalmának.

A fájlok megőrzött módosítási dátumai is ezt a sorrendet valószínűsítik: az összefűzött példány 2013. novemberi, több fejezet 2014. februári, a könyvkeret 2014. szeptemberi dátumú. Ezek fájldátumok, nem bizonyított kiadási dátumok. A tartalmi eltérések ettől függetlenül kimutathatók.

### Eltérések a két XML-változat között

- **1. fejezet:** a „csökkent értékű használati tér” toldalékolása változott (`tér nek` → `tér-nek`).
- **3. fejezet:** az előkert és oldalkert képaláírásának összevonása, ábraszám-hivatkozások átvezetése, valamint két, az OTÉK-ot idéző blokk hozzáadása az oldalhatáron álló és az ikres beépítésnél. A hozzáadott szövegek a Markdownban már szerepelnek.
- **4. fejezet, 4.34. ábra:** az összefűzött XML még „Átriumházak sorolása” címet és szöveges képhelyettesítőt tartalmaz; a külön fejezetfájlban ezek üresek. A Markdown ennél beszédesebb címet őriz.
- A bevezetés és a 2., 5., 6., 7. fejezet normalizált `para`-szövegsorozata a két XML-változatban azonos.

Ezért az összefűzött fájlt külön történeti változatként kell kezelni, nem újabb, teljesebb mesterként.

## 2. Tartalmi teljesség és módszer

A vizsgálat közvetlenül a mostani fájlokon futott; nem a korábbi `audit/qa.json` számait vettem át.

Az XML-ből a szöveget a beágyazott kiemelésekkel és hivatkozásfeliratokkal együtt olvastam ki. A Markdownból eltávolítottam a formázás jelöléseit és a linkcélokat. Egységesítettem az Unicode-ábrázolást, a szóközöket és a központozás körüli felesleges szóközöket. A szakmai szöveget, számértékeket és hivatkozásfeliratokat nem írtam át.

Az XML összesen 1444 `para` elemet tartalmaz. Ebből 1248 nem üres, közvetlenül összevethető szövegegységet vizsgáltam; a többi jellemzően ábrát, listát vagy más blokkot befoglaló szerkezeti elem. A listák címszavait, az alcímet, a fejezetcímeket és az ábrák címeit külön ellenőriztem.

| Forrásrész | Vizsgált szövegegység | Normalizálás után változatlanul megtalálható |
|---|---:|---:|
| Bevezetés | 13 | 13 |
| 1. A lakás | 405 | 405 |
| 2. A lakókörnyezet | 87 | 87 |
| 3. Családi házak | 236 | 235 |
| 4. Alacsony, nagy sűrűségű beépítések | 147 | 147 |
| 5. Többszintes, többlakásos lakóépületek | 269 | 269 |
| 6. Hétvégi házak, nyaralók | 46 | 46 |
| 7. A lakásállomány fenntartása és fejlesztése | 45 | 44 |
| **Összesen** | **1248** | **1246** |

A két kivétel:

- Egy mondatban az XML „3.14., 3.15. ábra”, a Markdown „3.14., 3.16. ábra” szöveget használ. Ez ábraszámozási javítás, nem hiányzó mondat.
- A 7. fejezet egyik `para` eleme csupán egy `*` elválasztójel. A Markdownban ez is megvan a 4462. sorban; a formázást eltávolító gépi összevetés nem kezelte szövegként.

**Az 1247 érdemi szövegegységből 1246 normalizáltan egyezik, egyben ábraszám-változás van.** Ez szöveges jelenlétvizsgálat, nem bájtszintű azonosság és nem a teljes vizuális tördelés ellenőrzése.

## 3. Szerkezet

| Elem | Külön XML-fejezetek | Markdown |
|---|---:|---:|
| Bevezetés + főfejezetek | 1 + 7 | 1 + 7 |
| Első alfejezetszint | 51 `sect1` | 51 `##` |
| Második alfejezetszint | 69 `sect2` | 69 megfelelő `###` |
| Ábra | 212 `figure` | 212 ábrahorgony |
| Megjegyzés | 103 `note` | 100 „Megjegyzés” + 3 saját című blokk |
| Explicit azonosító | 340 | 340 |
| Belső hivatkozás | 355 | 355 |

A Markdown összesen 9 első, 51 második és 72 harmadik szintű címsort használ. A könyvcím az extra első szintű cím; a „Közreműködők”, „Kivonat” és „Az európai fejlődés” a három további harmadik szintű cím. Utóbbi az XML-ben `subtitle`, tehát ez sem új szakmai tartalom.

Mind a 128 XML-fejezet/alfejezet azonosítója és hierarchiaszintje megfeleltethető. A főfejezetek száma az XML-ben a szerkezetből következik, a Markdownban a cím szövegének része. Az alfejezetcímek egyeznek.

A három saját című megjegyzés a családi házak fejezetében található: a falusi házak, a városias házak és az új kortárs törekvések történeti/magyarázó blokkjai. A 100 darab szó szerinti „Megjegyzés” cím tehát nem jelent három hiányzó megjegyzést.

Az XML gazdagabb szerkezeti információt őriz: 10 definíciós listát (`variablelist`), 19 címszót, 9 felsorolást, 4 idézetblokkot, továbbá kiemeléseket, felső indexeket és külön szöveges képhelyettesítőket. Ezek jelentős része a Markdownban olvasható formában megmaradt, de az eredeti DocBook-elemtípusok nem mindenütt állíthatók vissza egyértelműen pusztán a Markdownból.

## 4. Ábrák, képaláírások és hivatkozások

### 4.1. Nappálya-ábrák: a számozási hiba az XML-ben is jelen van

| Részlet | XML | Markdown |
|---|---|---|
| Első érintett ábra azonosítója | `abra_3_15` | `abra_3_14` |
| Hozzátartozó képfájlnév | `abra_3_14_napdiaszerk.png` | ugyanaz az alapnév |
| Első szöveges hivatkozás | „3.14.” → `abra_3_15` | „3.14.” → `abra_3_14` |
| Második hivatkozás | „3.15. ábra” → `abra_3_16` | „3.16. ábra” → `abra_3_16` |

A Markdown a fájlnévhez és a jelenlegi ábraazonosítókhoz igazítja a hivatkozásokat. Az XML az eredeti következetlenség bizonyítéka; nem ad önmagában teljesen konzisztens alternatív számozást. A `changelog.txt` a 3.12. ábra megnevezésének változását is dokumentálja, ami összhangban áll a környékbeli szerkesztési változásokkal.

Az átnevezést figyelembe véve a 212 ábra sorrendje egyezik. Mindkét összehasonlított forrásban feloldható az összes belső hivatkozás. Az XML azonosítói nem ismétlődnek.

### 4.2. Az 5.59. ábra tényleges állapota

A `05_tobblakasos.xml` 1701. során kezdődő ábra címe „Zöldhomlokzat spontán kialakulása”, de mindkét képváltozatnál az `abra_5_58_oslohoablak.png` fájlt adja meg. Ez hibás kép-hozzárendelés.

A csomagban ettől függetlenül létezik az `images/E5/abra_5_59_spontan_zoldhoml.png`, valamint JPG és webes változata is. A PNG-t vizuálisan ellenőriztem: növényzettel befuttatott homlokzatot ábrázol, alul a megfelelő beégetett képaláírással.

A jelenlegi Markdown 4160. sora már a `source/images/abra_5_59_spontan_zoldhoml.png` képet használja. Ezt is megnéztem: ugyanaz a fénykép, az alsó képaláírás levágásával. **Jelenleg nincs ezen a helyen pótlandó kép.** A README, a Markdown YAML-fejlécének státuszszövege és a korábbi audit hiányjelzése frissítendő.

### 4.3. Képaláírás-eltérések

A 212 ábra címének összevetése 9 eltérést mutatott:

- **1.25., 1.30., 3.1., 5.3.:** kettős magyar idézőjelek helyett egyszeres idézőjelek a Markdown-képaláírásban.
- **3.10.:** XML: „Medgyasszai Péter”; Markdown: „Medgyasszay Péter”. Névátírási eltérés; ebben a vizsgálatban külső névjegyzékkel nem ellenőriztem.
- **4.4.:** az évszámtartományban gondolatjel/kötőjel eltérés.
- **4.34.:** az XML címe üres; a Markdown címe „átriumházak sorolása (példák)”. A Markdown több információt őriz.
- **5.31.:** a Markdown teljes képaláírása: „5.31. ábra – 5.31. ábra Példák fogatolt elrendezések tájolási változataira”. A második „5.31. ábra” fölösleges, az XML címében nincs benne.
- **6.6.:** `m2` helyett `m²` a Markdownban.

Az XML `title` és `textobject/phrase` mezői sem mindig azonosak: például a t’ Hool-i együttes szöveges képhelyettesítője eltérő központozást tartalmaz. Ezeket nem érdemes automatikusan két külön tartalomként átvenni.

## 5. Képállomány: az XML-csomag valódi többlete

Az XML képmappája a rejtett rendszerfájlok nélkül **711 fájlt** tartalmaz:

- 375 PNG;
- 172 JPG;
- 164 PDF.

A jelenlegi `source/images/` mappában 214 nem rejtett fájl van. A Markdown 213 képelőfordulása 211 külön fájlra mutat; ebben a könyv eleji tanszéki logó is benne van. Az előfordulások száma nem azonos az önálló illusztrációk számával.

A DocBook ábránként webes és nyomdai képváltozatot különböztet meg (`condition="web"`, `condition="print"`), méretezési adatokkal. A 424 ábra-képfájlhivatkozásból 419 létező útvonalra mutat. Öt nyomdai útvonal nem található a megadott helyén:

- 3.1.: `images/E3/abra_3_01_fesusbe.pdf`;
- 3.2.: `images/E3/abra_3_02_mezovr.pdf`;
- 3.10.: `images/abra_3_10_magyarkuti_haz.jpg`;
- 3.16.: `images/E3/abra_3_16_napdiagram.pdf`;
- 3.19.: `images/E3/abra_3_19_kertlatv.pdf`.

A négy hiányzó PDF mellett létezik azonos alapnevű PNG az E3 könyvtárban. A 3.10. JPG az `images/E3/` alkönyvtárban található meg, tehát ott útvonalhiba van. Mind a 212 webes ábraútvonal létezik, bár az 5.59. útvonala tartalmilag hibás.

A jelenlegi képmappa 52 fájljának találtam bájtra azonos másolatát az XML-képek között. A többi eltérés önmagában nem bizonyít más illusztrációt vagy jobb felbontást: eltérhet a vágás, képaláírás, képméret vagy kódolás. Az 5.59. képnél a levágott alsó képaláírást közvetlenül is ellenőriztem. A teljes képállomány képpontonkénti és vizuális minőségi összevetése nem volt része ennek az elemzésnek.

**A 164 PDF értékes további képforrás lehet**, például későbbi nyomdai vagy nagyobb méretű kiadáshoz. Nem ellenőriztem minden PDF belső felépítését, így nem állítom, hogy mindegyik vektoros vagy minden esetben jobb minőségű.

## 6. Metaadatok és feldolgozhatóság

A könyvkeret a Markdownhoz képest további kiadványadatokat tárol: első kiadás, szerzői beosztás, intézményi postacím, tárgyszavak, külön jogi szövegmező és három projektlogó helye. A cím, szerző, közreműködők közül Pandula András és Novák Ágnes, a 2013-as év, a kiadó/projekt és a hárombekezdéses kivonat a Markdownban is megvan.

Oliver Sales fordítói közreműködését és a rekonstrukció eredetét, állapotát rögzítő adatokat a Markdown őrzi; a mostani könyvkeret nem tartalmazza ezeket. A névmezők is óvatosságot igényelnek: a keretben például `surname=János`, `firstname=Bitó` szerepel. Gépi bibliográfiai importnál ez felcserélt névrészeket eredményezhet.

Az XML-könyvkeret külső DocBook DTD-re és XInclude-modulra támaszkodik; a fejezetekben `&frac12;` és `&ndash;` entitás is van. A vizsgálathoz nem töltöttem le külső DTD-t: helyben kezeltem a szükséges entitásokat és a `xi` névteret. **Ez elemzési célú XML-beolvasás volt, nem teljes DocBook DTD-validálás.**

## 7. Javasolt következő lépések

1. **A Markdown maradjon a szerkesztési mester.** Nincs indok a teljes könyv újrakonvertálására.
2. **Az XML-csomagot változatlan forrásarchívumként őrizzük meg**, az összefűzött fájlt külön változatként megjelölve.
3. **Frissítsük a régi hiányjelzéseket:** az 5.59. már megvan, ezért a README és a rekonstrukciós státusz jelenleg félrevezető.
4. **Javítsuk az 5.31. dupla ábraszámát**, és külön szerkesztői döntéssel zárjuk le a nappálya-ábrák számozási ügyét.
5. **Készítsünk képváltozat-jegyzéket** a webes PNG-k, eredeti képek és PDF-ek összerendelésével, ha később képminőség-javítás vagy nyomdai kiadás lesz a cél. A meglévő, már megvágott webes képek automatikus cseréje nem indokolt.

## Gépi melléklet

A részletes számlálások, fejezet- és ábrajegyzékek, két XML-változat bekezdéseltérései, képfájl-egyezések, képméretek és a bemeneti fájlok SHA-256 ujjlenyomatai az `audit/xml_comparison_data.json` fájlban találhatók.

A vizsgálat a helyi források összehasonlítása; nem a könyvben szereplő szakmai vagy jogszabályi állítások mai érvényességének felülvizsgálata.
