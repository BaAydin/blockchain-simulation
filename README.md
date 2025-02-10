# Blockchain Simulation

Dieses Repository enthält verschiedene Simulationen einer Blockchain sowie verschiedener Konsensmechanismen, die im Rahmen einer Masterarbeit verwendet wurden. Die Skripte sind nicht für den produktiven Einsatz gedacht, sondern dienen lediglich der Visualisierung und Analyse.

## Übersicht

Die Simulation umfasst folgende Konsensmechanismen:

- **Proof of Authority (PoA)**  
  - Blöcke werden sofort durch eine festgelegte Autorität validiert.
  - Die Blockzeit wird hauptsächlich durch Netzwerkverzögerung beeinflusst.
  - Transaktionen und Blockgrößen sind variabel.
  - Eine grafische Benutzeroberfläche (GUI) ermöglicht eine visuelle Darstellung des Blockchain-Wachstums.

- **Proof of Work (PoW)**  
  - Blöcke müssen durch einen rechenintensiven Mining-Prozess validiert werden.
  - Die Schwierigkeit kann dynamisch angepasst werden.
  - Blockgrößen sind anpassbar.
  - Die GUI zeigt die Mining-Zeit pro Block sowie Statistiken zur Performance.

## Funktionen der Simulation

### Proof of Authority (PoA)
- Blöcke werden ohne Mining generiert.
- Validierungsverzögerung kann in der GUI eingestellt werden.
- Transaktionsgrößen sind anpassbar.
- Grafische Darstellung der Blockerstellung.
- Statistik über Blockerstellungszeiten und Systemauslastung.

### Proof of Work (PoW)
- Blöcke werden über einen Mining-Prozess mit Nonce-Suche validiert.
- Die Schwierigkeit kann angepasst werden, um die Hashrate zu simulieren.
- Visuelle Darstellung der Mining-Zeit pro Block.
- Anzeige der durchschnittlichen Mining-Zeit.
- Simulation der Skalierbarkeit durch einstellbare Blockgrößen.

## Anforderungen

Die Simulation erfordert folgende Abhängigkeiten:

- Python 3.x
- `tkinter` für die GUI
- `matplotlib` für die grafische Darstellung
- `psutil` für Systemstatistiken

Alle benötigten Bibliotheken sind standardmäßig in Python enthalten, mit Ausnahme von `matplotlib` und `psutil`, die über `pip` installiert werden können:

# Hinweis
Dieses Projekt dient ausschließlich zu Forschungs- und Simulationszwecken. Es ist keine echte Blockchain und nicht für produktive Anwendungen geeignet.
