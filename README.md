Tento projekt by měl řešit chytrou domácnost při minimální ceně a maximální spolehlivosti.

Technicky bude server (nejčastěji PC) a klienti ESP32/arduino. Klienti posílají data ze senzorů, jež jsou k mikrokontrolérům dratově připojeny, Server je zpracuje. Následně server muže nastavit výstupy
ESP32, to muže být přes tranzistor a relé připojoeno na 230V, tedy bude možnost řídit vyšší výkony.

Uživatel na webové stránce sensors.html přidá senzory, ty se nádledně uloží do data.json.
Uživatel na webové stránce outputs_settings.html přidá výstupy, ty se nádledně uloží do outputs.json.

monitor.html načítá json data z data.json a zobrazuje je na webu. elementy jsou automaticky vegenerovány při přijmutí http požadavku z app.py. Tedy se jich vygeneruje stejný počet jako je senzorů.
outputs.html načitá json data z outputs.json a zobrazí je. Elementy josu též automaticky generovány při přijmutí http požadavku z app.py. Tedy se jich vygeneruje stejný počet jako je výstupů. Zároven bude 
možnost přednastavovat hodnoty pro výstupy.

reciever.html bude nabízet možnost výběru přenosového protokolu/media (wifi, com, bluetooth). Při výběru WiFi bude uživatel moci vybrat ip adresy esp32 zařízení, ze ktrrých chce číst/posílat data.
Při výběru COM si vybere port. Dále tam bude možnost zvolit si virtuální ESP32 bud přes WiFi nebo COM. Bude možnost je kdykoliv vypnout. Jedná se vesměs o simulace, abych nemusel vše zapojovat. 

esp32WiFi je simulátor, který generuje data a odesíla po WiFi, není-li možno ho mít fyzicky. Bude se moct jednat o jiný počítač či jiný terminál na PC. Principiálně přečte data z data.json a bude generovat
value k daným pinům. Bude využívat protokol MQTT.

esp32_Serial je simulátor fyzického připojneí PC a esp32/arduina, využije virtuální COM port (COM6, COM7). Principiálně přečte data z data.json a bude generovat value k daným pinům.

jsonmanager.py obsahuje funkce pro práci z json, obecně to zjednodušuje.

database.py bude obsahuje funkce pro ukládání dat do databaze a čtení dat z databáze.







