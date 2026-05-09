# AR IoT Smart Home

Diplomový projekt zameraný na monitorovanie a ovládanie IoT zariadení pomocou rozšírenej reality a 3D identifikátorov.

Projekt prepája laboratórny model inteligentnej domácnosti s mobilnou AR aplikáciou vytvorenou v prostredí Unity. Používateľ môže po rozpoznaní 3D identifikátora sledovať aktuálne hodnoty zo senzorov a zároveň ovládať vybrané akčné členy. Súčasťou riešenia je aj doplnková webová aplikácia na monitoring historických dát a nastavovanie alarmových limitov.

---

## Hlavné funkcionality

* **Rozpoznávanie 3D identifikátorov** pomocou Vuforia Engine.
* **Zobrazovanie AR panela** nad rozpoznaným objektom.
* **Zobrazenie aktuálnych senzorických hodnôt:**
  * Teplota 
  * Vlhkosť 
  * Intenzita osvetlenia 
  * Vzdialenosť 
* **Ovládanie akčných členov** (RGB LED a servomotor) cez AR aplikáciu.
* **WebSocket komunikácia** v reálnom čase medzi Unity aplikáciou a Raspberry Pi.
* **Sériová komunikácia** medzi Raspberry Pi a Arduinom.
* **Webový dashboard** pre:
  * Aktuálne hodnoty a alarmové stavy
  * Historické grafy
  * Nastavovanie alarmových limitov

---

## Štruktúra projektu

* `unity-app/ARIoTSmartHome/` – projekt mobilnej AR aplikácie v Unity
* `raspberry-pi-server/` – serverová časť systému pre Raspberry Pi
* `raspberry-pi-dashboard/` – doplnková webová monitorovacia aplikácia
* `arduino/smart_home_controller/` – program pre mikrokontrolér Arduino

---

## Použité technológie

* Unity 2022.3
* Vuforia Engine
* Raspberry Pi 5
* Arduino Uno
* Python & Flask
* WebSocket
* SQLite
* HTML / CSS / JavaScript

---

## Hardvérové prvky

### Senzory
* **DHT22** – teplota a vlhkosť
* **HC-SR04** – vzdialenosť
* **GL5528** – intenzita osvetlenia (fotorezistor)

### Akčné členy
* RGB LED
* Jednofarebné LED diódy
* Servomotor SG90

---

## Základný princíp fungovania

1. **Arduino** číta údaje zo senzorov a odosiela ich cez sériové rozhranie.
2. **Raspberry Pi** prijíma údaje, spracováva ich a posiela ich do Unity aplikácie cez WebSocket.
3. **Unity aplikácia** po rozpoznaní 3D identifikátora zobrazí AR panel s aktuálnymi údajmi.
4. **Používateľ** môže cez AR panel interaktívne ovládať RGB LED a servomotor.
5. **Webový dashboard** beží paralelne, zobrazuje aktuálne a historické dáta a umožňuje nastavovať alarmové limity.

---

## Spustenie projektu

### 1. Arduino
Nahraj sketch z priečinka:
```text
arduino/smart_home_controller/
```

### 2. Raspberry Pi server
Prejdi do priečinka servera, aktivuj virtuálne prostredie a spusti ho:
```bash
cd raspberry-pi-server
source .venv/bin/activate
python src/main.py
```

### 3. Webový dashboard
Prejdi do priečinka dashboardu, aktivuj virtuálne prostredie a spusti aplikáciu:
```bash
cd raspberry-pi-dashboard
source .venv/bin/activate
python app.py
```
Dashboard bude dostupný v prehliadači na adrese: `http://IP_ADRESA_RASPBERRY_PI:5000`

### 4. Unity / Android aplikácia
1. Otvor projekt v prostredí **Unity**.
2. Nastav správnu **IP adresu** Raspberry Pi v komunikačnom skripte.
3. Vytvor **Android build** (`.apk`).
4. Nainštaluj aplikáciu do tabletu alebo mobilu.
5. Po spustení aplikácie nasmeruj kameru na 3D identifikátor.

---

## Poznámky
* Tablet a Raspberry Pi musia byť pripojené **do rovnakej WiFi siete**.
* Na úspešné rozpoznávanie identifikátorov je vhodné použiť bežné alebo silné osvetlenie.
* Dôležitú úlohu zohráva aj pozadie a povrch pod identifikátorom. Pri nevhodnom pozadí alebo slabom osvetlení môže dôjsť k pomalšiemu alebo nesprávnemu rozpoznaniu.
