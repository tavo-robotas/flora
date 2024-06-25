## Flora_AI Jutiklių sistema

Pateikti kodai inicijuoja ir valdo įvairius jutiklius, kontroliuoja rėles ir registruoja duomenis SD kortelėje. Sistema naudoja FreeRTOS užduotis lygiagrečiam veikimui, įskaitant duomenų nuskaitymą, rašymą ir serijinės komunikacijos valdymą. Taipogi gautus duomenis siunčia LED ekranui realiuoju laiku.

### Pagrindiniai Komponentai

- **Jutikliai:**
  - SGP30 (oro kokybė)
  - DHT22 (temperatūra ir drėgmė)
  - GravityTDS (bendras ištirpusių kietųjų dalelių kiekis)
  - RTC_DS3231 (realaus laiko laikrodis)
  - DFROBOT PH jutiklis (tikrina pH lygį vandenyje)
- **Komunikacija:** Serijinė ir I2C.
- **Duomenų registravimas:** SD kortelė duomenų saugojimui.
- **FreeRTOS:** Naudojamas daugiafunkciniam darbui, valdant duomenų nuskaitymą, rašymą ir komandų valdymą.
- **Rėlės:** Naudojamos išoriniams įrenginiams valdyti.

### Inicializacijos Funkcija

- Inicijuoja jutiklius (SGP30, DHT22, RTC_DS3231, GravityTDS, pH).
- Konfigūruoja rėlių kaiščius ir skaito jų būsenas iš EEPROM.
- Inicijuoja SD kortelę duomenų registravimui.
- Sukuria FreeRTOS užduotis serijinių komandų valdymui, jutiklių duomenų nuskaitymui, duomenų rašymui į SD kortelę ir duomenų siuntimui į LED ekraną.

### FreeRTOS Užduotys

1. **Task_SerialCommandHandler:** Valdo gaunamas serijines komandas. Komandos apima visų rėlių įjungimą arba išjungimą, individualių rėlių valdymą, duomenų perdavimo į serijinę jungtį įjungimą/išjungimą ir duomenų registravimo bei atgavimo valdymą.
2. **Task_DataReading:** Nuskaito duomenis iš įvairių jutiklių, įskaitant temperatūrą, drėgmę, CO2, TVOC, pH ir TDS. Apskaičiuoja absoliutų drėgnumą ir siunčia duomenis į tolimesniam apdorojimui.
3. **Task_DataWriting:** Skaito jutiklių duomenis ir rašo juos į SD kortelę.
4. **Task_Send_To_Screen:** Priima jutiklių duomenis ir siunčia juos į LED ekrano valdymo valdiklį per I2C komunikaciją.

### Funkcijų Detalės

- **getAbsoluteHumidity:** Apskaičiuoja absoliutų drėgnumą remiantis temperatūros ir drėgmės rodmenimis.
- **saveRelayStates:** Išsaugo dabartinę rėlių būseną į EEPROM.
- **readRelayStates:** Skaito rėlių būsenas iš EEPROM ir atitinkamai inicijuoja rėles.
- **processCommand:** Apdoroja serijines komandas rėlių valdymui, duomenų registravimo valdymui ir PWM komandų persiuntimui į NodeMCU.
- **plotAllData:** Nuskaito visus duomenis iš SD kortelės ir siunčia juos į serijinę jungtį.
- **flushData:** Ištrina visus duomenis iš SD kortelės ir iš naujo inicijuoja duomenų failą.
- **readDataInRange:** Nuskaito duomenis iš SD kortelės nurodytu laikotarpiu ir siunčia juos į serijinę jungtį.

### Saugojamų SD kortelėje ir siunčiamų duomenų struktūra

- **timestamp:** Laiko žyma iš RTC_DS3231.
- **temperature:** Temperatūros rodmuo iš DHT22.
- **humidity:** Drėgmės rodmuo iš DHT22.
- **moisture:** Drėgmės lygio rodmuo.
- **pH:** pH lygio rodmuo.
- **tdsValue:** Bendras ištirpusių kietųjų dalelių (TDS) kiekis.
- **co2:** CO2 lygio rodmuo iš SGP30.
- **tvoc:** Bendras lakusis organinių junginių (TVOC) lygio rodmuo iš SGP30.

**Pavizdys:** 1925014235, 23, 60, 54, 6.5, 400, 400, 5

### Serial Komandos

- **OFF ALL:** Išjungia visas rėles.
- **ON ALL:** Įjungia visas rėles.
- **OFF `<relay_num>`:** Išjungia konkrečią rėlę.
- **ON `<relay_num>`:** Įjungia konkrečią rėlę.
- **SEND DATA ON:** Įjungia duomenų siuntimą į serijinę jungtį.
- **SEND DATA OFF:** Išjungia duomenų siuntimą į serijinę jungtį.
- **DATA `<start>` `<end>`:** Nuskaito duomenis nurodytu laikotarpiu ir siunčia juos į serijinę jungtį.
- **DATA ALL:** Nuskaito visus duomenis iš SD kortelės ir siunčia juos į serijinę jungtį.
- **DATA FLUSH:** Ištrina visus duomenis iš SD kortelės ir iš naujo inicijuoja duomenų failą.