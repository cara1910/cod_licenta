# Sistem embedded de detecție bazat pe procesare de imagini pe Raspberry Pi

## 1. Descrierea proiectului

Acest proiect implementează un sistem inteligent de supraveghere video folosind Raspberry Pi, Raspberry Pi Camera, OpenCV, MobileNet SSD, Flask și SQLite.

Aplicația permite:
- autentificarea utilizatorilor;
- resetarea parolei prin e-mail;
- vizualizarea unui dashboard web;
- accesarea fluxului video live;
- detectarea persoanelor în timp real;
- salvarea imaginilor detectate;
- afișarea istoricului pe zile;
- trimiterea notificărilor prin e-mail;
- accesarea aplicației de la distanță prin Tailscale.

## 2. Repository Git

Adresa repository-ului: https://github.com/cara1910/cod-licenta

## 3. Structura proiectului

licenta-sys/
-app.py
-camera.py
-detection.py
-surveillance.py
-database.py
-email_notifier.py
-manager_stocare.py
-config.py
-requirements.txt
-templates/
  -index.html
  -dashboard.html
  -live.html
  -reset-request.html
  -reset-password.html
  -reset-confirmation.html
  -send-link.html
-static/
  -css/
  -js/
  -detections/
-models/
  -MobileNetSSD_deploy.prototxt
  -MobileNetSSD_deploy.caffemodel
- README.md

## 4. Tehnologii utilizate

- **Python 3** - limbajul principal de programare.
- **Flask** - framework web folosit pentru aplicația web.
- **SQLite** - bază de date locală pentru utilizatori, token-uri și detecții.
- **OpenCV** - procesare de imagine și rularea modelului MobileNet SSD.
- **Picamera2** - capturarea imaginilor de la camera Raspberry Pi.
- **MobileNet SSD** - model de detecție persoane.
- **HTML/CSS/JavaScript** - interfața web.
- **SMTP Gmail** - trimiterea e-mailurilor.
- **Tailscale** - acces securizat la distanță și HTTPS.

## 5. Cerințe software

Pe Raspberry Pi trebuie să fie instalate:

- Raspberry Pi OS;
- Python 3;
- pip;
- Git;
- SQLite;
- bibliotecile necesare camerei Raspberry Pi;
- Tailscale, dacă se dorește acces de la distanță.

## 6. Instalarea proiectului

### 6.1. Clonarea repository-ului
git clone <repository_url>
cd licenta-sys

Dacă proiectul este copiat manual, se intră direct în folderul proiectului:
cd ~/Desktop/licenta-sys

### 6.2. Crearea mediului virtual
python3 -m venv venv

### 6.3. Activarea mediului virtual
source venv/bin/activate

După activare, în terminal ar trebui să apară o linie de forma:
(venv) carina@carina:~/Desktop/licenta-sys $

### 6.4. Instalarea dependențelor
pip install -r requirements.txt

Dacă fișierul `requirements.txt` nu există încă, acesta poate fi generat de pe sistemul unde aplicația funcționează deja:
pip freeze > requirements.txt

## 7. Configurarea aplicației

Nu este necesară configurarea manuală a aplicației. Parametrii principali sunt deja definiți în fișierul `config.py`.

Singura configurare opțională este schimbarea contului Gmail utilizat pentru trimiterea notificărilor prin e-mail.
Exemplu:

EMAIL_SENDER = "adresa@gmail.com"
EMAIL_PASSWORD = "app_password_google"

Parola utilizată nu este parola contului Google, ci un App Password generat după activarea autentificării în doi pași.

## 8. Inițializarea bazei de date

Baza de date este creată automat de aplicație.
Nu trebuie creată manual.

În `app.py`, la pornirea aplicației, se apelează funcția:
init_db()

Această funcție se află în `database.py` și creează tabelele necesare dacă acestea nu există deja.
Tabelele folosite sunt:
- `users` - pentru utilizatori;
- `detections` - pentru detecțiile salvate;
Deci, prin „configurarea bazei de date” se înțelege:

1. existența fișierului SQLite, de exemplu `surveillance.db`;
2. rularea funcției `init_db()`;
3. crearea automată a tabelelor necesare;
4. salvarea utilizatorilor și detecțiilor în baza de date.

Pentru prima rulare este suficient să porniți aplicația:
python3 app.py

Dacă baza de date nu există, aplicația o creează automat.

## 9. Lansarea aplicației

### Varianta cu venv

1. Intrarea în folderul proiectului
cd ~/Desktop/licenta-sys

2. Activarea mediului virtual
source venv/bin/activate

3. Pornirea aplicației Flask
python3 app.py

Dacă aplicația pornește corect, în terminal va apărea ceva de forma:

 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.20.10.14:5000
   
## Varianta fără venv

1. Deschideți un terminal pe Raspberry Pi.

2. Accesați directorul proiectului:
cd ~/Desktop/licenta-sys

3. Porniți aplicația:
python3 app.py

4. După pornirea aplicației, serverul Flask va fi disponibil la:
http://127.0.0.1:5000

sau prin rețeaua Tailscale la adresa configurată.

## 10. Accesarea aplicației

### Acces local pe Raspberry Pi
http://127.0.0.1:5000

### Acces din aceeași rețea locală

Se folosește IP-ul Raspberry Pi:
http://172.20.10.14:5000

### Acces prin Tailscale

Dacă Tailscale este configurat, se poate accesa aplicația folosind IP-ul Tailscale:
http://100.99.58.108:5000

sau prin Tailscale Serve/HTTPS:
https://carina.tail9976f3.ts.net

## 11. Pornirea accesului HTTPS prin Tailscale Serve

Pentru ca aplicația să fie accesibilă prin domeniul Tailscale HTTPS, trebuie ca aplicația Flask să fie deja pornită:
python3 app.py

Apoi, într-un alt terminal:
tailscale serve 5000

sau, dacă cere permisiuni:
sudo tailscale serve 5000

După pornire, terminalul va afișa o adresă de forma:
https://carina.tail9976f3.ts.net

Această adresă poate fi folosită pentru accesarea aplicației prin HTTPS.

## 12. Funcționalități implementate

Aplicația oferă următoarele funcționalități:

- creare cont utilizator;
- autentificare;
- logout;
- resetare parolă prin e-mail;
- generare token unic de resetare;
- expirare token după un interval stabilit;
- dashboard cu statistici;
- selectarea zilei pentru istoric;
- listarea imaginilor salvate;
- deschiderea imaginilor salvate;
- flux video live;
- detecție persoane în timp real;
- afișarea chenarelor de detecție;
- afișarea scorului de încredere;
- număr persoane detectate;
- salvare automată a imaginilor;
- salvare detecții în SQLite;
- management automat al spațiului de stocare;
- notificări automate prin e-mail;
- acces securizat la distanță prin Tailscale.

## 13. Rolul principalelor fișiere

### `app.py`
Fișierul principal al aplicației Flask. Definește rutele web, pornește serverul și leagă interfața web de camera, detector, baza de date și notificări.

### `camera.py`
Inițializează Raspberry Pi Camera și furnizează frame-uri video către aplicație.

### `detection.py`
Încarcă modelul MobileNet SSD și detectează persoanele din fiecare frame.

### `surveillance.py`
Conține logica de supraveghere: salvare imagini, desenare chenare și decizia de salvare a evenimentelor.

### `database.py`
Gestionează baza de date SQLite: utilizatori, autentificare, token-uri de resetare și detecții.

### `email_notifier.py`
Trimite e-mailuri pentru resetarea parolei și pentru alertele de supraveghere.

### `manager_stocare.py`
Verifică spațiul disponibil și șterge automat cele mai vechi imagini când spațiul ocupat depășește pragul stabilit.

### `config.py`
Conține setările aplicației: praguri, căi, SMTP, porturi și parametri generali.

## 14. Concluzie

Proiectul integrează componente hardware și software într-un sistem complet de supraveghere inteligentă. Raspberry Pi gestionează camera și serverul web, OpenCV și MobileNet SSD detectează persoanele, SQLite salvează datele, Flask oferă interfața web, iar Gmail SMTP și Tailscale extind aplicația cu notificări și acces securizat la distanță.
