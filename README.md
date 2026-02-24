# ShootCup Tournament Manager

ShootCup ist eine professionelle Software zur Verwaltung von Schießturnieren. Sie unterstützt die Datenerfassung, Auswertung nach Teiler oder Differenz zum Zielteiler und bietet eine Live-Anzeige für Zuschauer auf einem zweiten Bildschirm inklusive konfigurierbarer Standbelegung.

## Funktionen

*   **Turnierverwaltung:** Anlegen und Bearbeiten von Turnieren (Name, Datum). Speichern und Laden von Turnieren im JSON-Format.
*   **Datenerfassung:** Einfache Eingabe von Startnummer (optional), Name des Schützen und Teiler. Bestehende Einträge können bearbeitet oder gelöscht werden.
*   **Standbelegung:** Verwaltung der Schießstände (Standard 8, konfigurierbar).
    *   Anzeige der Belegung auf dem zweiten Bildschirm (Grün = Frei, Gelb = Neu belegt, Rot = Länger belegt).
    *   Die Dauer für die "Neu"-Anzeige (Gelb) ist konfigurierbar (Standard 5 Minuten).
    *   Akustisches Signal ("Gong") bei Aktualisierung der Belegung.
*   **Auswertung & Sortierung:** Sortieren der Tabelle nach Eingabereihenfolge, Name, Teiler oder Differenz zum Zielteiler. Die Sortierung auf dem zweiten Bildschirm kann optional mit der Hauptansicht synchronisiert werden.
*   **Filter:** Filtern der Tabelle nach ausgewählten Namen für gezielte Anzeigen oder PDF-Exporte.
*   **Zweiter Bildschirm:** Vollbildanzeige für Zuschauer mit:
    *   Turnierinformationen (Name, Datum)
    *   Optional: Zielteiler-Anzeige
    *   Optional: Standbelegung (Live-Update)
    *   Rangliste mit automatischem, nahtlosem Scrollen bei vielen Einträgen.
*   **PDF Export:** Exportieren der aktuellen Rangliste als PDF (berücksichtigt aktive Filter und Sortierung).
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
    (Alternativ: `pip install PyQt6 reportlab`)

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
4.  **Zielteiler:** Legen Sie optional einen Zielteiler fest (Standard 0,0).
5.  **Datenerfassung:** Fügen Sie Schützen hinzu, indem Sie Nr., Name und Teiler eingeben und auf "Hinzufügen" klicken.
6.  **Standbelegung:** Geben Sie die Startnummern für die jeweiligen Stände ein und klicken Sie auf "Update Stände", um die Anzeige zu aktualisieren (inkl. Soundeffekt).
7.  **Sortierung:** Wählen Sie die gewünschte Sortierung. Aktivieren Sie "Sortierung anzeigen", um diese auf den zweiten Bildschirm zu übertragen.
8.  **Export:** Nutzen Sie "PDF Export" um die Ergebnisse zu drucken. Mit "Nach markierten Namen filtern" können Sie die Liste vor dem Export einschränken.
