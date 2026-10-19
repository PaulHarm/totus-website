# TOTUS Website: vollständiger Review vom 19. Oktober 2026

Geprüft wurden alle 20 deutschen Inhaltsseiten und ihre 20 englischen Fassungen. Die zwei Fehlerseiten wurden zusätzlich vom statischen Seitencheck erfasst. Grundlage: veröffentlichte private Vorschau, generierter HTML-Inhalt, lokale Desktop- und Mobilprüfung sowie die vorhandenen Referenztexte.

## Einschätzung

Die visuelle Basis ist hochwertig und konsistent: klare Typografie, ruhige Farben, nachvollziehbare Navigation und zurückhaltende Bewegung. PANI hat jetzt eine erkennbare eigene Markenidentität innerhalb von TOTUS. Der größte zusätzliche Nutzen liegt bei konkreten Belegen, klarer Produktabgrenzung und einer vollständig durchgängigen Anfrageführung.

## Prioritäten

1. **Identität und Rechtstexte vor dem öffentlichen Livegang prüfen.** Die übernommene USt-ID `DE123456789` wirkt wie ein Platzhalter. Handelsregisterangaben in den ursprünglichen Quellen widersprechen sich. Außerdem enthalten die englischen Rechtstexte weiterhin deutsche Absätze aus der Vorlage. Dies ist keine rechtliche Prüfung; belastbare Unternehmensangaben und freigegebene, vollständige Übersetzungen fehlen. Details stehen in CONTENT-REVIEW.md.
2. **Nachweise für Kunden und Investoren ergänzen.** Es fehlen freigegebene Angaben zu Nutzung, zahlenden Kunden, Geschäftsmodell, messbarem Nutzen und nächsten Meilensteinen. Die Website beschreibt das Produktportfolio gut, kann diese Aussagen aber noch nicht mit konkreten Ergebnissen belegen. Ein knapper Investoreneinstieg mit bestätigten Daten wäre sinnvoll.
3. **Produktentscheidungen erleichtern.** Invest und ResiCore brauchen eine kurze Gegenüberstellung: für welchen Kunden, welche Immobilien, welcher konkrete Prozess und welcher Stand der Verfügbarkeit. PANI-Verwaltungsdienstleistung und PANI-Software sollten weiterhin ausdrücklich auseinandergehalten werden.
4. **Anfragen vereinfachen.** Produktinteresse wird jetzt ins Demoformular übernommen. Der aktuelle Mailentwurf ist transparent, verlangt aber einen zusätzlichen Schritt im E-Mail-Programm. Ein tatsächlich angebundenes Kontaktformular oder verifizierter Kalender wäre die nächste Ausbaustufe.
5. **Inhalte stärker spezialisieren.** Mehrere Produkt- und Funktionsseiten nutzen ähnliche Zwischenüberschriften und denselben Deal-Ablauf. Ein konkretes, belegtes Anwendungsbeispiel pro Seite würde mehr erklären als zusätzliche Animationen.

## Durchgang aller Seiten

Die Empfehlungen gelten jeweils auch für die englische Fassung (`en…`).

| Seite | Sinnvollste nächste Verbesserung |
| --- | --- |
| Startseite | Ein belastbarer Praxisbeleg und ein klarer Einstieg für Kunden beziehungsweise Investoren. |
| TOTUS Invest | Zielkunde, typischer Deal und konkretes Arbeitsergebnis unmittelbar unter dem Einstieg benennen. |
| TOTUS ResiCore | Die Abgrenzung zu Invest anhand eines Wohnimmobilien-Beispiels zeigen. |
| PANI Hausverwaltung | Pilotzugang und Startvoraussetzungen konkretisieren; neue Designvorschau und bestehende Anwendung klar beschriftet lassen. |
| PANI Tracker | Ein nachvollziehbares Beispiel vom gefundenen Signal bis zur Kontaktaufnahme ergänzen. |
| Plattform | In einem Satz erklären, wie die Plattform und die vier Produktmarken zusammenhängen. |
| Produktüberblick | Module mit jeweils einem klaren Ein- und Ergebnis beschreiben; Wiederholungen zur Plattform kürzen. |
| Underwriting | An einem freigegebenen Beispiel erklären, wie Annahmen in die Entscheidung eingehen. Der einfache Renditerechner ersetzt kein vollständiges Underwriting. |
| Deal Pipeline | Übergabekriterien zwischen Phasen und eine konkrete Verantwortlichkeit sichtbar machen. |
| AI & IC-Memos | Ein anonymisiertes Eingabedokument, den Entwurf und die menschliche Prüfung nebeneinander zeigen. |
| Sell-Side | Einen konkreten Verkaufsablauf mit Mandat, Bieterstatus und Verkäuferreport erläutern. |
| Über uns | Freigegebene Gründerfotos, Rollen und kurze biografische Nachweise ergänzen. |
| Kontakt | Reale Rückmeldeerwartung und möglichst einen direkt angebundenen Anfrageweg ergänzen. |
| Demo | Jetzt eigener Einstieg und übernommenes Produktinteresse; als Nächstes Agenda und bestätigte Buchungsmöglichkeit ergänzen. |
| Karriere | Eindeutig zwischen aktiven Stellen und Initiativgesprächen unterscheiden. |
| Presse | Einen datierten Faktenbogen und freigegebene Personenfotos bereitstellen. |
| Sicherheit | Je Produkt zwischen verfügbaren Funktionen und geplanten Maßnahmen unterscheiden; bestätigte Hosting-/Verarbeitungsangaben ergänzen. |
| Impressum | USt-ID und Registerdaten verifizieren; verbleibende deutsche Absätze der englischen Version übersetzen und freigeben. |
| Datenschutz | Mit tatsächlich eingesetztem Hosting, Kontaktweg und Softwarebetrieb abgleichen; englische Fassung vervollständigen. |
| AGB | Mit tatsächlichem Vertrags- und Leistungsmodell abgleichen; englische Fassung vervollständigen. |

## In diesem Durchgang umgesetzt

- Demoanfragen aus Invest, ResiCore, PANI und Tracker wählen das passende Produkt vor. Der Sprachwechsel erhält diese Auswahl.
- Demo- und Kontaktseite haben unterschiedliche Einstiege und Beschreibungen.
- Aktive Navigationspunkte funktionieren auch auf den von Sites verwendeten URLs ohne `.html`.
- Rechtstexte und ihre Inhaltsverzeichnisse sind auf Mobilgeräten besser lesbar.
- Canonical- und Sprach-URLs, Open-Graph-URL sowie eine vollständige Sitemap mit 40 Inhaltsseiten werden passend zur Zieldomain erzeugt. Fehlerseiten sind von der Indexierung ausgenommen.
- Der Generator unterstützt die GitHub-Ausgabe nach `site/` mit der Domain `https://totus.info`, ohne private Site-Konfiguration in GitHub zu übernehmen.

## Prüfung und Grenzen

- 80 Layoutprüfungen: alle 40 Inhaltsseiten bei 1280 und 390 Pixel Breite, nach Laden der Seite, ohne dokumentweiten horizontalen Überlauf oder als defekt erkannte Bilder.
- Statischer Check für alle 42 Seiten: bestehende Routen, lokale Dateien und Anker, Metadaten, Sitemap, IDs, Bildalternativen und ARIA-Verweise.
- Gezielte Interaktionsprüfung für Produktanfrage, Sprachwechsel, Navigation und bestehende Animationen.
- Keine erfundenen Kunden-, Umsatz- oder Erfolgszahlen ergänzt. Keine rechtliche Freigabe, kein Cross-Browser-Zertifikat und keine Core-Web-Vitals-Messung.

Der GitHub-Pull-Request löst den STRATO-Livegang nicht aus. Der vorhandene Workflow veröffentlicht erst Änderungen an `site/` auf `main`.
