# ShootCup Tournament Manager

ShootCup ist eine Software zur Verwaltung von Schießturnieren.

## Funktionen

*   **Turnierverwaltung:** Anlegen von Turnieren mit Name und Datum.
*   **Datenerfassung:** Eingabe von Scheibennummer, Name des Schützen und Teiler.
*   **Zielteiler:** Festlegung eines Zielteilers (0,0 bis 1999,9).
*   **Sortierung:** Sortieren der Tabelle nach Nummer, Name, Teiler oder Differenz zum Zielteiler.
*   **Zweiter Bildschirm:** Vollbildanzeige für Zuschauer mit Live-Ranking (nach Zielteiler sortiert).
*   **PDF Export:** Exportieren der aktuellen Tabelle als PDF.
*   **Speichern/Laden:** Speichern des Turnierfortschritts in einer JSON-Datei.

## Installation

1.  Python 3 installieren.
2.  Abhängigkeiten installieren:
    ```bash
    pip install PyQt6 reportlab
    ```

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

1.  Geben Sie oben den Turniernamen und das Datum ein.
2.  Fügen Sie Schützen hinzu, indem Sie Nr., Name und Teiler eingeben und auf "Hinzufügen" klicken.
3.  Wählen Sie einen Zielteiler.
4.  Klicken Sie auf "2. Bildschirm öffnen", um das Zuschauerfenster zu öffnen. (In den Einstellungen können Sie den Monitor wählen).
5.  Nutzen Sie "PDF Export" um die Ergebnisse zu drucken.
