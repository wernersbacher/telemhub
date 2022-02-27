dateien umstrukturierung:
- alle ldx und ld files kommen in ein verzeichnis (working)
- parquet auf selbe platte wie working/db/etc
- danach wird die zip in slow hdd abgespeichert
- dateien bekommen eindeutige id als dateinamen -> auch nach user löschung kein problem oder nach änderung des users
- damit ordner nicht zu groß wird, wird subordner zufällig angelegt, dieser folder wird in der db (File) abgespeichert, daraus ergibt sich dateipfad
-> unabhängig vom user (pfad)
- beim download wird aber richtiger name aus db verwendet

ordner strukur neu aufbauen, user löschen, daten löschen
lösch logik verschieben auf datei, sodass model mitgelöscht wird? bzw methode delete_files_on_hdd oder so

- contact

admin page:
- roles auswahl übergeben oder zumindest beschreibung dazu
- close reg -> yaml editor
- link zur startseite

move num of elems per page to settings yaml

automatic migration of db https://stackoverflow.com/questions/44961622/how-to-call-flask-migrate-api-in-script

aws:
- installer für bessere ausführung schreiben
- backup sql etc

profil:
- anzahl von hochladen, ingesamten views

design/ui:
- upload verschönern, fortschritt, direkt datei check

- table click verbessern
- notification über erfolg/misserfolg -> verknüpfen mit user 
- passwort vergessen

hardening:
- captcha reg
- views vor doppelten aufrufen sichern? -> ip

doofes zeug:
- cookies? dsgvo
- impressum
- download rechte?

struktur:
- templates verschieben

content
- how to
- faqs