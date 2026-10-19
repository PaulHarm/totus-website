# TOTUS CRE — Website

Statische, zweisprachige Website für totus.info. Der überarbeitete Auftritt umfasst 40 deutsche und englische Inhaltsseiten sowie zwei Fehlerseiten. Die 25 ursprünglichen HTML-Routen bleiben erreichbar. PANI erhält sein Original-Bärenlogo, eigene Typografie und interaktive, als solche gekennzeichnete Designvorschauen.

## Lokal bearbeiten und prüfen

Python 3 und Node.js reichen aus; ein Frontend-Framework oder Paketinstallation ist nicht erforderlich.

```sh
python build.py --output site --site-url https://totus.info
node check.mjs site
node verify-motion.cjs site
node --check site/app.js
node server.mjs site
```

Die Vorschau läuft unter http://127.0.0.1:4173. Inhalte und HTML-Vorlagen werden in `build.py` bearbeitet. `source-content/` enthält die ursprünglichen Texte als Build-Eingaben; diese Dateien werden nicht veröffentlicht. Design und Interaktionen liegen in `site/styles.css`, `site/pani-brand.css`, `site/app.js` und `site/motion.js`.

Die fertigen Bild- und Schriftdateien liegen in `site/`. Optional erneuert `python optimize-assets.py site` das WebP-Titelbild (Pillow erforderlich); `python prepare-pani-brand.py site` extrahiert das Original-PANI-Logo aus dem gespeicherten SVG-Sprite. Bildherkunft und PANI-Markenquellen stehen in IMAGE-PROMPT.md und PANI-BRAND.md.

## Verhalten

- Responsive Navigation, vollständige Sprachpaare, Produktfilter und tastaturbedienbare Galerien.
- Zurückhaltende Animationen mit Unterstützung für reduzierte Bewegung, Tastaturfokus und Druckansicht.
- Produktbezogene Demoanfragen mit Vorauswahl und erhaltenem Kontext beim Sprachwechsel.
- Das Anfrageformular bereitet einen E-Mail-Entwurf vor; es sendet keine Nachricht automatisch und besitzt keinen Server-Endpunkt.
- Produktansichten aus der bestehenden Anwendung sowie ausdrücklich fiktive interaktive Beispiele.
- Canonical-/Sprach-Metadaten, Sitemap und robots.txt für die gewählte Zieldomain.

## Veröffentlichung und offene Inhalte

Der vorhandene GitHub-Actions-Workflow `.github/workflows/deploy.yml` überträgt `site/` per SFTP zu STRATO, sobald Änderungen an diesem Verzeichnis auf `main` landen. Ein separater Branch oder Pull Request veröffentlicht noch nichts auf totus.info. Die bestehenden Workflows bleiben unverändert.

Vor dem öffentlichen Livegang sind die übernommenen Unternehmens-/Registerangaben, englischen Rechtstexte und produktbezogenen Sicherheitsangaben zu prüfen. Siehe [CONTENT-REVIEW.md](CONTENT-REVIEW.md). Der vollständige Seitendurchgang mit priorisierten Verbesserungen steht in [WEBSITE-REVIEW.md](WEBSITE-REVIEW.md).

Die separat veröffentlichte [private Designvorschau](https://totus-reimagined.superdove17.chatgpt.site/) wird über Sites verwaltet. Ihre Zugangsdaten und Hosting-Konfiguration gehören nicht in dieses Repository.
