# ShootCup Tournament Manager

ShootCup ist eine professionelle Software zur Verwaltung von Schießturnieren. Sie unterstützt die Datenerfassung, Auswertung nach Teiler, Differenz zum Zielteiler oder Ringzahl und bietet eine Live-Anzeige für Zuschauer auf einem zweiten Bildschirm inklusive konfigurierbarer Standbelegung.

## Funktionen

*   **Turnierverwaltung:** Anlegen und Bearbeiten von Turnieren (Name, Datum). Speichern und Laden von Turnieren im JSON-Format.
*   **Datenerfassung:** Einfache Eingabe von optionaler Start-/Scheibennummer, Name des Schützen, Teiler oder Ringzahl. Bestehende Einträge können bearbeitet oder gelöscht werden. Die Datenintegrität wird dabei intern durch eindeutige IDs sichergestellt.
*   **Wertungsmodi:** Unterstützung für zwei getrennte Wertungsmodi pro Turnier: "Teiler" (niedriger ist besser, Zielteiler-Modus möglich) und "Ringzahl" (höher ist besser). Beide Modi unterstützen Nachkommastellen (Zehntelwertung).
*   **Klasseneinteilung:** Teilnehmer können optional in Klassen (z.B. Jugend, Schützenklasse) eingeteilt werden. Die Auswertung und Anzeige (auch auf dem zweiten Bildschirm und im PDF) wird dann übersichtlich nach diesen Klassen gruppiert.
*   **Standbelegung:** Verwaltung der Schießstände (Standard 8, konfigurierbar).
    *   Anzeige der Belegung auf dem zweiten Bildschirm (Grün = Frei, Gelb = Neu belegt, Rot = Länger belegt).
    *   Die Dauer für die "Neu"-Anzeige (Gelb) ist konfigurierbar (Standard 5 Minuten).
    *   Akustisches Signal ("Gong") bei Aktualisierung der Belegung (wenn ein Stand neu belegt oder geändert wird).
*   **Auswertung & Sortierung:** Dynamische Sortierung je nach Wertungsmodus (z.B. nach Klasse, Teiler, Ringzahl oder Differenz zum Ziel). Die Sortierung auf dem zweiten Bildschirm synchronisiert sich mit der Hauptansicht.
*   **Filter:** Filtern der Tabelle nach ausgewählten Namen für gezielte Anzeigen oder PDF-Exporte.
*   **Zweiter Bildschirm:** Vollbildanzeige für Zuschauer mit:
    *   Turnierinformationen (Name, Datum)
    *   Optional: Zielteiler-Anzeige
    *   Optional: Standbelegung (Live-Update)
    *   Rangliste mit automatischem, nahtlosem Scrollen bei vielen Einträgen. Bei gestopptem Scrollen springt die Ansicht automatisch an den Anfang zurück.
*   **PDF Export:** Exportieren der aktuellen Rangliste als PDF (berücksichtigt aktive Filter und Klassen-Gruppierung, exklusive der Platzierungsspalte).
*   **REST-API:** Integrierte lokale REST-API zur automatisierten Übermittlung von Ergebnissen von externen Geräten.
*   **Einstellungen:** Konfiguration von:
    *   Anzahl der Schießstände.
    *   Anzeigedauer für neue Belegungen.
    *   Scroll-Geschwindigkeit des zweiten Bildschirms.
    *   Auswahl des Monitors für die Vollbildanzeige.
    *   Sichtbarkeit von Standbelegung und Zielteiler auf dem zweiten Bildschirm.

## Installation

1.  Python 3 installieren.
2.  Abhängigkeiten installieren:
    ```bash
    pip install -r requirements.txt
    ```
    (Alternativ: `pip install PyQt6 reportlab flask`)

## Starten

Starten Sie die Anwendung über die Kommandozeile:

```bash
python3 main.py
```
Oder (unter Windows):
```bash
python main.py
```

## Bedienung

1.  **Turnierdaten:** Geben Sie oben den Turniernamen und das Datum ein.
2.  **Einstellungen:** Klicken Sie auf den Button "Einstellungen", um die Anzahl der Stände, den Monitor für den zweiten Bildschirm und weitere Optionen zu konfigurieren.
3.  **Zweiter Bildschirm:** Klicken Sie auf "2. Bildschirm öffnen", um das Zuschauerfenster zu öffnen.
4.  **Wertungsmodus:** Wählen Sie zwischen "Teiler" und "Ringzahl". Die Tabellen und Eingabefelder passen sich entsprechend an.
5.  **Zielteiler (nur im Teiler-Modus):** Legen Sie optional einen Zielteiler fest (Standard 0,0).
6.  **Datenerfassung:** Fügen Sie Schützen hinzu, indem Sie (optional) Nr. und Klasse, sowie Name und das Ergebnis eingeben und auf "Hinzufügen" klicken.
7.  **Standbelegung:** Geben Sie die Startnummern für die jeweiligen Stände ein und klicken Sie auf "Update Stände", um die Anzeige zu aktualisieren (inkl. Soundeffekt bei Änderungen).
8.  **Sortierung & Filter:** Wählen Sie die gewünschte Sortierung (z.B. nach Klasse). Nutzen Sie "Nach markierten Namen filtern" für gezielte Ansichten.
9.  **Export:** Nutzen Sie "PDF Export" um die aktuellen (und ggf. gefilterten) Ergebnisse zu drucken. Auch im JSON-Format können Daten exportiert werden (dieser Export ignoriert Filter und exportiert alle Daten).

## REST-API

Die Software verfügt über eine lokale REST-API, über die Schießergebnisse automatisch in das System eingespeist werden können.
*   **Server:** Läuft standardmäßig auf `http://localhost:5003` (Port ist in `config.json` anpassbar).
*   **Endpunkt:** `POST /api/score`
*   **Payload:** Erwartet ein JSON mit `name`, `score`, `type` ("teiler" oder "ringzahl") und optional `klasse`.
Weitere Details zur API finden sich in der `api.yaml`.

## Für Entwickler

*   **Datenintegrität:** Interne Operationen (Update, Löschen) nutzen UUIDs (`id`), da die Startnummer ("Nummer") optional und nicht eindeutig ist.
*   **Nebenläufigkeit:** Der Flask-Server für die REST-API läuft in einem separaten `QThread`, um die PyQt6-Event-Loop nicht zu blockieren.
*   **Testing:** Für Headless CI/CD-Tests der GUI muss vor der Initialisierung der `QApplication` die Umgebungsvariable `QT_QPA_PLATFORM` auf `offscreen` gesetzt werden (z.B. `os.environ['QT_QPA_PLATFORM'] = 'offscreen'`).
