ENG: The first is a program handling the RFID card reader. Acting as an MQTT publisher, this program will transmit information about the identifier of the used card and the exact time of its use. Please ensure that an RFID card placed against the reader is read only once, even if it is constantly held against the reader. Please inform the user via an audio and visual signal that the card has been read.
The second program is a client that, acting as an MQTT subscriber, will receive information about RFID card usage and record the event.

PL: Pierwszy to program obsługujący czytnik kart RFID. Program ten, jako wydawca (publisher) protokołu MQTT, będzie wysyłał informację o identyfikatorze użytej karty i dokładnym czasie jej użycia. Proszę zadbać, aby karta RFID przyłożona do czytnika była odczytywana jeden raz, jeśli jest stale przyłożona do czytnika. Proszę sygnałem dźwiękowym i wizualnym poinformować użytkownika karty, że została ona odczytana.
Drugi program to klient, który jako subskrybent protokołu MQTT będzie odbierał informacje o użyciu kart RFID i zapisywał
fakt użycia.
