<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Azure Cost Forecasting Engine</h1>
</div>

> 🇬🇧 [English Version](README.md)

**Analyse historischer Azure-Verbrauchsdaten, Kostenprognose fuer die naechsten 30, 60 und 90 Tage, Erkennung von Kosten-Anomalien und priorisierte Optimierungsempfehlungen.**

Kompatibel mit dem [Microsoft FinOps Framework](https://www.finops.org/framework/). Keine externen Bibliotheken fuer Zahlenrechnung erforderlich.

[![Python](https://img.shields.io/badge/Python-3.11+-orange?logo=python)](https://www.python.org)
[![Azure Cost Management](https://img.shields.io/badge/Azure%20Cost%20Management-blue?logo=microsoftazure)](https://learn.microsoft.com/de-de/azure/cost-management-billing/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?logo=linux)](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CI](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine/actions/workflows/ci.yml)

---

## Funktionen

| Funktion | Beschreibung |
|---|---|
| Datenabfrage | Tagesaktuelle Verbrauchsdaten aus der Azure Consumption API mit automatischer Seitennavigation |
| Normalisierung | Aggregation nach Dienst und Tag, lueckenlose Zeitreihe |
| Kostenprognose | Ensemble aus linearer Regression und Holt-Glaettung (30/60/90 Tage) |
| Anomalieerkennung | Tage die den Mittelwert um mehr als 2,5 Standardabweichungen ueberschreiten |
| Trendanalyse | Klassifikation in stabil, steigend oder sinkend |
| Reserved Instances | Dienste mit stabilem Verbrauch (CV unter 15%) als RI-Kandidaten |
| Rightsizing | Dienste mit taeglich steigenden Kosten ueber 1,5% des Mittels |
| Prognosebandbreiten | 80%-Konfidenzintervalle fuer alle Prognosepunkte |
| Demo-Modus | Vollstaendige Analyse mit synthetischen Daten ohne Azure-Zugangsdaten |
| Ausgabeformate | Tabelle, JSON, Markdown, HTML |

---

## Benoetigte Azure RBAC Rolle

| Rolle | Zweck |
|---|---|
| `Cost Management Reader` | Lesezugriff auf Verbrauchsdetails und Abrechnungsdaten |

Keine Schreibberechtigungen erforderlich.

---

## Schnellstart

```bash
git clone https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine
cd azure-cost-forecasting-engine
pip install -e .

# Demo-Modus (keine Zugangsdaten erforderlich)
python cli.py run --demo

# Mit Azure-Zugangsdaten
cp .env.example .env
# .env mit Zugangsdaten befuellen
python cli.py run --history 90

# Markdown-Bericht exportieren
python cli.py run --demo --format md --output report.md
```

---

## Prognosemethodik

| Komponente | Methode | Beschreibung |
|---|---|---|
| Lineare Regression | Kleinste Quadrate | Trendlinie durch alle historischen Datenpunkte |
| Exponentielle Glaettung | Holt (2 Parameter) | Gewichtet aktuelle Daten hoeher, reagiert auf Trendaenderungen |
| Ensemble | Mittelwert beider Methoden | Reduziert Overfitting aus beiden Einzelmodellen |
| Konfidenzintervall | RMSE-basiert, 80% | Weitet sich mit zunehmendem Prognosehorizont |

Keine externen Bibliotheken fuer Zahlenrechnung noetig. Alle Berechnungen mit der Python-Standardbibliothek.

---

## Keine Credential-Speicherung

Zugangsdaten werden ausschliesslich aus Umgebungsvariablen gelesen. Die `.env`-Datei ist gitignoriert. Keine Credentials werden gespeichert, geloggt oder in Berichten ausgegeben.

---

**Autor:** [Rafael Yilmaz](https://github.com/9t29zhmwdh-coder) · **Status:** v0.1.0 · **Letzte Aktualisierung:** 2026-06-18
