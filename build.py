from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape
import re, json, argparse

ROOT = Path(__file__).parent
parser = argparse.ArgumentParser(description='Build the bilingual TOTUS website.')
parser.add_argument('--output', default='site', help='Output directory, relative to the project root.')
parser.add_argument('--site-url', default='https://totus.info', help='Canonical website origin.')
args = parser.parse_args()
OUT = ROOT / args.output
OUT.mkdir(parents=True, exist_ok=True)
SITE_URL = args.site_url.rstrip('/')
assert SITE_URL.startswith('https://') and '?' not in SITE_URL and '#' not in SITE_URL, 'An HTTPS site origin is required.'
SOURCE = ROOT / 'source-content'
LANG = 'de'
CURRENT = 'index'
ARROW = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="1.5"/></svg>'
NORTH = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12" stroke="currentColor" stroke-width="1.5"/></svg>'
MARK = '<svg class="brand-mark" viewBox="0 0 32 36" fill="none" aria-hidden="true"><path d="M2 3h28v7H19v23h-7V10H2V3Z" fill="currentColor"/><path d="M2 14h6v19H2V14Zm22 0h6v19h-6V14Z" fill="currentColor" opacity=".45"/></svg>'
def t(de,en): return en if LANG=='en' else de
def url(key):
    if LANG=='en': return ('en' if key=='index' else 'en'+key)+'.html'
    return key+'.html'
def link(key,label,cls='text-link'):
    return f'<a class="{cls}" href="{url(key)}">{label}{ARROW}</a>'
def eyebrow(txt): return f'<p class="eyebrow"><span></span>{txt}</p>'

class Node:
    def __init__(self,tag='',attrs=None): self.tag=tag; self.attrs=dict(attrs or []); self.children=[]
    def all(self,pred):
        found=[self] if pred(self) else []
        for c in self.children:
            if isinstance(c,Node): found+=c.all(pred)
        return found
    def text(self): return ''.join(c.text() if isinstance(c,Node) else c for c in self.children).strip()
class DOM(HTMLParser):
    def __init__(self,raw):
        super().__init__(convert_charrefs=True); self.root=Node();self.stack=[self.root];self.feed(raw)
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs);self.stack[-1].children.append(n)
        if tag not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(n)
    def handle_startendtag(self,tag,attrs):
        self.stack[-1].children.append(Node(tag,attrs))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):self.stack[-1].children.append(data)
def nodes(root,tag):return root.all(lambda n:n.tag==tag)
def raw_page(key):return (SOURCE/(key+'.html')).read_text(encoding='utf-8')
def source_data(key):
    root=DOM(raw_page(('en' if LANG=='en' else '')+key)).root
    features=root.all(lambda n:'feature' in n.attrs.get('class','').split() and n.tag=='div')
    modules=[(nodes(n,'h3')[0].text(),nodes(n,'p')[0].text()) for n in features if nodes(n,'h3') and nodes(n,'p')]
    steps=root.all(lambda n:'step' in n.attrs.get('class','').split())
    workflow=[(nodes(n,'h3')[0].text(),nodes(n,'p')[0].text()) for n in steps if nodes(n,'h3') and nodes(n,'p')]
    images=[];labels=[n.text() for n in root.all(lambda n:n.attrs.get('role')=='tab')]
    panels=root.all(lambda n:n.attrs.get('role')=='tabpanel')
    for i,p in enumerate(panels):
        imgs=nodes(p,'img')
        if imgs:images.append((labels[i],imgs[0].attrs['src'],imgs[0].attrs.get('alt','')))
    return modules,workflow,images

PRODUCTS={
 'invest':{'name':'TOTUS Invest','cat':['Gewerbeimmobilien','Commercial real estate'],'kind':'investment','num':'01','image':'investpipeline.png','logo':'totusinvestlogo.png',
 'title':['Jeder Deal verdient<br>eine klare Entscheidung.','Every deal deserves<br>a clear decision.'],
 'desc':['Vom ersten Exposé bis zum Investment Committee. Ein strukturierter Workflow für Ihr gewerbliches Immobilieninvestment.','From the first offering memorandum to the investment committee. One structured workflow for commercial real estate investment.'],
 'short':['Exposés verstehen. Deals bewerten. Fundiert entscheiden.','Understand opportunities. Evaluate deals. Decide with confidence.'],
 'status':['Im Einsatz','In operation'],'color':'sage'},
 'resicore':{'name':'TOTUS ResiCore','cat':['Wohnimmobilien','Residential real estate'],'kind':'investment','num':'02','image':'resicoreobjekt.png','logo':'resicorelogo.png',
 'title':['Das ganze Potenzial.<br>In jedem Objekt.','The full potential.<br>In every property.'],
 'desc':['Wohnimmobilien von der ersten Marktbeobachtung bis zum Exit durchdenken. Mit amtlichen Daten, nachvollziehbaren Bewertungen und klaren Szenarien.','Think residential investments through, from market monitoring to exit. With official data, transparent valuations and clear scenarios.'],
 'short':['Von der Marktchance zum durchdachten Wohninvestment.','From a market opportunity to a considered residential investment.'],
 'status':['Aus dem eigenen Betrieb','Built in our own operations'],'color':'sand'},
 'pani':{'name':'PANI Hausverwaltung','cat':['Verwaltung & Betrieb','Management & operations'],'kind':'operations','num':'03','image':'panihvuebersicht.jpg','logo':'pani-bear.svg',
 'title':['Persönlich gedacht.<br>Digital verbunden.','Personally considered.<br>Digitally connected.'],
 'desc':['Miet- und WEG-Verwaltung, Buchhaltung, KI-Posteingang und Portale. Entwickelt für die Menschen, die jeden Tag Verantwortung für Immobilien tragen.','Tenancy and condominium management, accounting, an AI inbox and portals. Built for the people responsible for properties every day.'],
 'short':['Der Verwaltungsalltag. Als zusammenhängendes System.','Everyday property management. One connected system.'],
 'status':['Pilotstart in Vorbereitung','Pilot launch in preparation'],'color':'pani-sage'},
 'tracker':{'name':'PANI Tracker','cat':['Marktintelligenz','Market intelligence'],'kind':'intelligence','num':'04','image':'paniprojekte.png','logo':'pani-bear.svg',
 'title':['Die nächste Chance<br>beginnt mit einem Signal.','The next opportunity<br>starts with a signal.'],
 'desc':['Das Projektradar für Berlin und Brandenburg. Bauvorhaben entdecken, Potenziale priorisieren und den Weg vom ersten Kontakt zum Mandat verfolgen.','The project radar for Berlin and Brandenburg. Discover developments, prioritise opportunities and follow the path from first contact to mandate.'],
 'short':['Projektentwicklungen erkennen. Beziehungen früher aufbauen.','Spot developments. Build relationships earlier.'],
 'status':['Intern bei PANI im Einsatz','In internal use at PANI'],'color':'pani-stone'}
}
def pval(p,key):return p[key][1 if LANG=='en' else 0]

def pani_brand(key):
    sub='Hausverwaltung' if key=='pani' else 'Tracker'
    return f'<span class="pani-lockup"><img src="pani-bear.svg" alt="" width="31" height="50"><span class="pani-wordmark"><b>PANI</b> <small>{sub}</small></span></span>'

def pani_software(key):
    if key=='pani':
        views=[
            (t('Übersicht','Overview'),t('Ihr Haus. Im Überblick.','Your property. At a glance.'),t('Musterobjekt · Berlin','Example property · Berlin'),
             [('24',t('Einheiten','Units')),('03',t('Vorgänge','Cases')),('02',t('Fristen','Deadlines'))],
             [(t('Heizungswartung','Heating maintenance'),t('Termin mit Dienstleister abgestimmt','Service appointment arranged'),t('In Arbeit','In progress')),(t('Eigentümer-Update','Owner update'),t('Unterlagen zusammengestellt','Documents compiled'),t('Zur Prüfung','For review'))]),
            (t('Posteingang','Inbox'),t('Aus Post wird Übersicht.','From inbox to overview.'),t('Dokumente und Anliegen am richtigen Ort.','Documents and requests in the right place.'),
             [('05',t('Eingänge','Incoming')),('03',t('Zugeordnet','Assigned')),('02',t('Zu prüfen','To review'))],
             [('Wartungsprotokoll.pdf',t('Dokument dem Objekt zugeordnet','Document assigned to property'),t('Prüfen','Review')),(t('Anfrage zur Abrechnung','Billing enquiry'),t('KI-Vorschlag zur Zuordnung','AI assignment suggestion'),t('Vorschlag','Suggestion'))]),
            (t('Portale','Portals'),t('Ein Stand. Für alle.','One view. For everyone.'),t('Eigentümer und Mieter informiert halten.','Keep owners and tenants informed.'),
             [('24',t('Einheiten','Units')),('06',t('Dokumente','Documents')),('02',t('Entwürfe','Drafts'))],
             [(t('Jahresabrechnung','Annual statement'),t('Für die Eigentümer vorbereitet','Prepared for the owners'),t('Entwurf','Draft')),(t('Wartungstermin','Maintenance visit'),t('Mitteilung für das Mieterportal','Notice for the tenant portal'),t('Entwurf','Draft'))])]
    else:
        views=[
            (t('Projekte','Projects'),t('Chancen werden sichtbar.','Opportunities become visible.'),'Berlin · Brandenburg',
             [('12',t('Projekte','Projects')),('04',t('Neue Signale','New signals')),('03',t('Im Fokus','In focus'))],
             [(t('Wohnquartier am Park','Parkside residences'),t('Berlin · Neubau · Beispielprojekt','Berlin · New build · Example project'),t('Entdeckt','Discovered')),(t('Höfe am Ufer','Riverside courtyards'),t('Brandenburg · Entwicklung','Brandenburg · Development'),t('Im Fokus','In focus'))]),
            ('Pipeline',t('Vom Signal zum Gespräch.','From signal to conversation.'),t('Nächste Schritte nachvollziehbar planen.','Plan clear next steps.'),
             [('04',t('Entdeckt','Discovered')),('03',t('Geprüft','Reviewed')),('02',t('Im Kontakt','In contact'))],
             [(t('Wohnquartier am Park','Parkside residences'),t('Ansprechpartner recherchieren','Research a contact'),t('Recherche','Research')),(t('Höfe am Ufer','Riverside courtyards'),t('Gespräch vorbereiten','Prepare a conversation'),t('Kontakt','Contact'))]),
            (t('Analyse','Analysis'),t('Potenziale einordnen.','Understand the potential.'),t('Ein gemeinsamer Blick auf den Markt.','A shared perspective on the market.'),
             [('08','Berlin'),('04','Brandenburg'),('03',t('Priorisiert','Prioritised'))],
             [(t('Wohnen','Residential'),t('Projektchancen in der Übersicht','Project opportunities at a glance'),'08'),(t('Gemischt genutzt','Mixed use'),t('Weitere Entwicklungen im Blick','Monitor further developments'),'04')])]
    tabs=''.join(f'<button role="tab" id="pani-demo-tab-{i}" aria-selected="{str(i==0).lower()}" aria-controls="pani-demo-panel-{i}" tabindex="{0 if i==0 else -1}">{v[0]}</button>' for i,v in enumerate(views))
    panels=''
    for i,(_,title,lead,metrics,rows) in enumerate(views):
        stats=''.join(f'<div><strong>{value}</strong><span>{label}</span></div>' for value,label in metrics)
        items=''.join(f'<div class="pani-app-row"><span class="pani-row-mark" aria-hidden="true">{ARROW}</span><div><h4>{name}</h4><p>{detail}</p></div><span class="pani-row-status">{status}</span></div>' for name,detail,status in rows)
        panels+=f'<div class="pani-app-panel" role="tabpanel" id="pani-demo-panel-{i}" aria-labelledby="pani-demo-tab-{i}" {"hidden" if i else ""}><h3>{title}</h3><p class="pani-app-lead">{lead}</p><div class="pani-app-stats">{stats}</div><div class="pani-app-rows">{items}</div></div>'
    return f'''<div class="product-hero-preview pani-app" data-tabs><div class="pani-software-bar">{pani_brand(key)}<span>{t('DESIGNVORSCHAU','DESIGN PREVIEW')}</span></div><div class="pani-app-tabs" role="tablist" aria-label="{t('PANI Software-Vorschau','PANI software preview')}">{tabs}</div><div class="pani-app-content">{panels}</div><p class="pani-app-note">{t('Interaktive Gestaltungsvorschau · fiktive Beispieldaten','Interactive design preview · fictional sample data')}</p></div>'''

PAGES={
 'plattformprodukt':(['Produktüberblick','Product overview'],['Ein Workflow.<br>Der ganze Deal.','One workflow.<br>The whole deal.'],['Sechs Module verbinden Eingang, Analyse und Entscheidung. Ihr Team arbeitet an einem gemeinsamen Stand.','Six modules connect intake, analysis and decisions. Your team works from a shared view.'],'investdashboard.jpg',
 [['Inbox & Triage','Inbox & triage','Exposés erfassen, Informationen strukturieren und den nächsten Schritt bestimmen.','Capture offering memoranda, structure information and determine the next step.'],
 ['Buy-Side Pipeline','Buy-side pipeline','Phasen, Verantwortliche und offene Punkte in einem durchgängigen Prozess.','Stages, owners and open items in one continuous process.'],
 ['Underwriting','Underwriting','Cashflows, Finanzierung und Szenarien nachvollziehbar modellieren.','Model cash flows, financing and scenarios transparently.'],
 ['IC-Memos','IC memos','Deal-Daten und Analyse in einer entscheidungsfähigen Vorlage zusammenführen.','Bring deal data and analysis together in a decision-ready document.'],
 ['Risk Scoring','Risk scoring','Risiken und fehlende Annahmen sichtbar machen, bevor sie zur Überraschung werden.','Make risks and missing assumptions visible before they become surprises.'],
 ['Sell-Side','Sell-side','Mandate, Bieter und Angebote strukturiert begleiten.','Manage mandates, bidders and offers in a structured process.']]),
 'plattformunderwriting':(['Underwriting','Underwriting'],['Annahmen verstehen.<br>Entscheidungen absichern.','Understand assumptions.<br>Support decisions.'],['Ein Modell für Cashflow, Finanzierung und Risiko. Mit Szenarien, die zeigen, welche Annahmen das Ergebnis wirklich bewegen.','One model for cash flow, financing and risk. Scenarios reveal which assumptions really move the outcome.'],'investdealdetail.png',
 [['Cashflow & Rent Roll','Cash flow & rent roll','Mietverträge, Laufzeiten, Leerstand und CapEx in einer strukturierten Zehnjahresplanung.','Leases, terms, vacancy and capex in a structured ten-year projection.'],
 ['Finanzierung','Financing','IRR, NPV und DSCR im Zusammenhang mit Ihrer Kapitalstruktur betrachten.','Assess IRR, NPV and DSCR in the context of your capital structure.'],
 ['Szenarien & Sensitivitäten','Scenarios & sensitivities','Base, Best und Worst Case vergleichen. Mietentwicklung und Exit-Annahmen gezielt hinterfragen.','Compare base, best and worst cases. Challenge rental growth and exit assumptions.'],
 ['Nachvollziehbare Annahmen','Traceable assumptions','Quellen und Annahmen am Deal dokumentieren und für das IC-Memo nutzbar machen.','Document sources and assumptions in the deal and carry them into the IC memo.']]),
 'plattformdealpipeline':(['Deal Pipeline','Deal pipeline'],['Alles in Bewegung.<br>Alles im Blick.','Every deal moving.<br>Nothing out of sight.'],['Von der ersten Nachricht bis zum Closing: klare Phasen, klare Verantwortung und ein gemeinsames Bild Ihrer Pipeline.','From the first message to closing: clear stages, clear ownership and one shared picture of your pipeline.'],'investpipeline.png',
 [['Eine gemeinsame Pipeline','One shared pipeline','Inbox, Screening, Underwriting, Due Diligence, IC Review und Closing.','Inbox, screening, underwriting, due diligence, IC review and closing.'],
 ['Verantwortung sichtbar','Visible ownership','Aufgaben, Zuständigkeiten und Fristen direkt am Deal festhalten.','Keep tasks, owners and deadlines directly with each deal.'],
 ['Kontext bleibt erhalten','Context stays connected','Dokumente, Kommentare und Aktivitäten begleiten das Objekt durch alle Phasen.','Documents, comments and activities follow the asset through every stage.'],
 ['Fortschritt verstehen','Understand progress','Pipeline-Volumen, Durchlaufzeiten und Conversion gemeinsam betrachten.','See pipeline volume, cycle times and conversion together.']]),
 'plattformaiicmemos':(['AI & IC-Memos','AI & IC memos'],['Aus Informationen<br>wird eine Position.','Turn information<br>into a position.'],['KI bereitet vor. Ihr Team prüft, ergänzt und entscheidet. So wird aus Deal-Daten eine nachvollziehbare Investmentvorlage.','AI prepares. Your team reviews, adds context and decides. Deal data becomes a transparent investment proposal.'],'investinbox.png',
 [['Daten statt leerer Seiten','Data instead of blank pages','Vorlagen werden aus Deal-Daten und Underwriting befüllt.','Templates are populated from deal data and underwriting.'],
 ['Ein fundierter erster Entwurf','A grounded first draft','KI unterstützt bei Zusammenfassung, Investmentthese und Risiken. Jede Aussage bleibt prüfbar.','AI supports summaries, investment theses and risks. Every statement remains subject to review.'],
 ['Gemeinsam zur Freigabe','Review together','Kommentare, Versionen und Committee-Voten begleiten die Entscheidung.','Comments, versions and committee votes accompany the decision.'],
 ['Bereit für das Committee','Ready for the committee','Deutsche und englische Fassungen sowie PDF-Export für die finale Vorlage.','German and English versions, with PDF export for the final document.']]),
 'plattformsellside':(['Sell-Side','Sell-side'],['Ein Mandat.<br>Ein klarer Prozess.','One mandate.<br>A clear process.'],['Bieter, Gebote und Datenräume zusammenführen. Für einen Verkaufsprozess, den Ihr Team und Ihre Auftraggeber nachvollziehen können.','Bring bidders, offers and data rooms together. A sale process your team and clients can follow.'],'investmap.jpg',
 [['Mandate strukturieren','Structure mandates','Objektinformationen, Zeitplan und Zuständigkeiten am Mandat bündeln.','Bring asset information, timelines and ownership together within the mandate.'],
 ['Gebote vergleichbar machen','Compare offers','IOI, LOI und finale Bieterrunden mit Konditionen und Fristen verfolgen.','Track IOIs, LOIs and final rounds with terms and deadlines.'],
 ['Zugriff gezielt steuern','Control access','Datenraum-Freigaben, Aktivitäten und Dokumentenzugriffe nachvollziehen.','Track data-room permissions, activity and document access.'],
 ['Auftraggeber informieren','Keep clients informed','Bieteraktivitäten und Prozessfortschritt im Verkäuferreport zusammenführen.','Bring bidder activity and process progress together in seller reports.']])
}

def nav():
    products=''.join(f'<a href="{url(k)}"><span class="mini-logo"><img src="{p["logo"]}" alt="" width="24" height="24"></span><span>{p["name"]}<small>{pval(p,"cat")}</small></span>{NORTH}</a>' for k,p in PRODUCTS.items())
    platform=''.join(link(k,v[0][1 if LANG=='en' else 0],'menu-link') for k,v in PAGES.items())
    return f'''<a class="skip" href="#main">{t('Zum Inhalt','Skip to content')}</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="{url('index')}" aria-label="TOTUS CRE — {t('Startseite','Home')}">{MARK}<span>TOTUS<span class="brand-cre">CRE</span></span></a>
<button class="mobile-toggle" aria-controls="navigation" aria-expanded="false" aria-label="{t('Menü öffnen','Open menu')}"><span></span><span></span></button>
<nav id="navigation" aria-label="{t('Hauptnavigation','Main navigation')}">
<details class="nav-dropdown"><summary>{t('Lösungen','Solutions')}<span class="chevron"></span></summary><div class="mega-menu"><p class="eyebrow">{t('UNSER PRODUKTÖKOSYSTEM','OUR PRODUCT ECOSYSTEM')}</p><div class="menu-products">{products}</div><a class="menu-bottom" href="{url('index')}#portfolio">{t('Alle Lösungen entdecken','Explore all solutions')} {ARROW}</a></div></details>
<details class="nav-dropdown"><summary>{t('Plattform','Platform')}<span class="chevron"></span></summary><div class="mega-menu compact">{link('plattform',t('Die TOTUS Plattform','The TOTUS platform'),'menu-link')}{platform}</div></details>
<a href="{url('plattformabout')}" {'aria-current="page"' if CURRENT=='plattformabout' else ''}>{t('Über uns','About us')}</a>
<a href="{url('plattformcontact')}">{t('Kontakt','Contact')}</a>
</nav><div class="header-actions"><a class="language" href="{('index' if CURRENT=='index' else CURRENT)+'.html' if LANG=='en' else ('en' if CURRENT=='index' else 'en'+CURRENT)+'.html'}" aria-label="{t('Switch to English','Zu Deutsch wechseln')}">{t('EN','DE')}</a>{link('plattformdemo',t('Im Gespräch entdecken','Let’s talk'),'button small')}</div></div></header>'''
def footer():
    columns=[
      (t('Lösungen','Solutions'),[(k,p['name']) for k,p in PRODUCTS.items()]),
      (t('Plattform','Platform'),[('plattform','TOTUS CRE'),('plattformprodukt',t('Produktüberblick','Product overview')),('plattformunderwriting','Underwriting'),('plattformdealpipeline','Deal Pipeline'),('plattformaiicmemos','AI & IC-Memos'),('plattformsellside','Sell-Side')]),
      (t('Unternehmen','Company'),[('plattformabout',t('Über uns','About us')),('plattformcareers',t('Karriere','Careers')),('plattformpress',t('Presse','Press')),('plattformcontact',t('Kontakt','Contact')),('plattformsecurity',t('Sicherheit','Security'))])]
    cols=''.join('<div class="footer-col"><h3>'+title+'</h3>'+''.join(f'<a href="{url(k)}">{label}</a>' for k,label in items)+'</div>' for title,items in columns)
    return f'''<footer class="footer"><div class="container"><div class="footer-top"><div class="footer-brand"><a class="brand" href="{url('index')}">{MARK}<span>TOTUS<span class="brand-cre">CRE</span></span></a><p>{t('Immobilienkompetenz.<br>In Software übersetzt.','Real estate expertise.<br>Translated into software.')}</p><span class="location-dot">BERLIN, DE</span></div>{cols}</div><div class="footer-bottom"><span>© 2026 TOTUS CRE</span><div>{link('plattformimprint',t('Impressum','Legal notice'),'plain')}{link('plattformprivacy',t('Datenschutz','Privacy'),'plain')}{link('plattformterms',t('AGB','Terms'),'plain')}</div><span>{t('Aus der Praxis. Für die Praxis.','Built in practice. Built for practice.')}</span></div></div></footer>'''
def cta():
    return f'''<section class="cta-section"><div class="container cta-inner"><div>{eyebrow(t('DER NÄCHSTE SCHRITT','THE NEXT STEP'))}<h2>{t('Was möchten Sie<br>möglich machen?','What would you like<br>to make possible?')}</h2></div><div><p>{t('Ein konkretes Objekt, ein besserer Prozess oder eine neue Idee. Beginnen wir mit einem Gespräch.','A specific property, a better process or a new idea. Let’s start with a conversation.')}</p>{link('plattformcontact',t('Sprechen wir darüber','Let’s talk about it'),'button light')}</div></div></section>'''
def page(key,title,description,body):
    global CURRENT
    CURRENT=key
    file=url(key)
    full=f'''<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} · TOTUS CRE</title><meta name="description" content="{escape(description,quote=True)}"><meta name="theme-color" content="#163a32"><link rel="icon" href="favicon.ico"><link rel="stylesheet" href="styles.css"><link rel="preload" href="interlatin.woff2" as="font" type="font/woff2" crossorigin><link rel="alternate" hreflang="de" href="{'index' if key=='index' else key}.html"><link rel="alternate" hreflang="en" href="{'en' if key=='index' else 'en'+key}.html"><meta property="og:title" content="{escape(title,quote=True)} · TOTUS CRE"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:image" content="https://totus-reimagined.superdove17.chatgpt.site/ogindex.png"><script src="app.js" defer></script></head><body data-page="{key}">{nav()}<main id="main">{body}</main>{footer()}<dialog id="image-dialog" aria-label="{t('Produktansicht vergrößert','Enlarged product view')}"><button class="dialog-close" aria-label="{t('Schließen','Close')}">×</button><img alt=""><p></p></dialog></body></html>'''
    full=full.replace('<script src="app.js" defer>', '<script src="motion.js" defer></script><script src="app.js" defer>')
    full=full.replace('src="architecture.png"', 'src="architecture.webp"')
    canonical=SITE_URL+('/' if key=='index' and LANG=='de' else '/'+file)
    full=full.replace('https://totus-reimagined.superdove17.chatgpt.site/ogindex.png', SITE_URL+'/ogindex.png')
    full=full.replace('</title>', '</title><link rel="canonical" href="'+canonical+'"><meta property="og:url" content="'+canonical+'"><meta property="og:type" content="website">')
    full=re.sub(r'(hreflang="(?:de|en)" href=")([^"]+)', lambda m:m[1]+SITE_URL+'/'+m[2], full)
    if key=='404':full=full.replace('</head>', '<meta name="robots" content="noindex"></head>')
    full=full.replace('<link rel="stylesheet" href="styles.css">', '<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="pani-brand.css">')
    if key in ('pani','tracker'):
        full=full.replace(f'<body data-page="{key}">', f'<body data-page="{key}" class="pani-page">')
        full=full.replace('<meta name="theme-color" content="#163a32">', '<meta name="theme-color" content="#254b3e">')
        full=full.replace('<link rel="icon" href="favicon.ico">', '<link rel="icon" type="image/svg+xml" href="pani-bear.svg">')
    (OUT/file).write_text('\n'.join(line.rstrip() for line in full.splitlines())+'\n',encoding='utf-8')

def portfolio():
    cards=''
    for k,p in PRODUCTS.items():
        cards+=f'''<article class="product-card {p['color']}" data-category="{p['kind']}"><a href="{url(k)}"><div class="product-card-top"><span>{p['num']} / {pval(p,'cat')}</span><span class="round-arrow">{NORTH}</span></div><h3>{pani_brand(k) if k in ('pani','tracker') else p['name']}</h3><p>{pval(p,'short')}</p><div class="product-card-image"><img src="{p['image']}" alt="{p['name']} — {t('Produktansicht','product view')}" width="1400" height="700" loading="lazy"></div><div class="product-card-bottom"><span class="status-dot">{pval(p,'status')}</span><span>{t('Entdecken','Explore')} {ARROW}</span></div></a></article>'''
    filters=[('all',t('Alle Lösungen','All solutions')),('investment','Investment'),('operations',t('Verwaltung','Operations')),('intelligence',t('Marktdaten','Intelligence'))]
    return f'''<section id="portfolio" class="section container"><div class="section-heading"><div>{eyebrow(t('DAS TOTUS ÖKOSYSTEM','THE TOTUS ECOSYSTEM'))}<h2>{t('Vier Systeme.<br>Ein hoher Anspruch.','Four systems.<br>One high standard.')}</h2></div><p>{t('Spezialisiert auf Ihre Aufgaben. Verbunden durch ein gemeinsames Prinzip: komplexe Immobilienprozesse verständlich und steuerbar machen.','Specialised for your work. Connected by one principle: making complex real estate processes clear and manageable.')}</p></div><div class="filter-row" aria-label="{t('Produkte filtern','Filter products')}">{''.join(f'<button data-filter="{k}" aria-pressed="{str(k=="all").lower()}">{label}</button>' for k,label in filters)}<span class="filter-count" aria-live="polite">04 {t('Lösungen','solutions')}</span></div><div class="product-grid">{cards}</div></section>'''
def gallery(images,title=None):
    buttons=''.join(f'<button id="gallery-tab-{i}" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="gallery-panel-{i}" tabindex="{0 if i==0 else -1}">{label}</button>' for i,(label,src,alt) in enumerate(images))
    panels=''.join(f'''<div id="gallery-panel-{i}" role="tabpanel" aria-labelledby="gallery-tab-{i}" {'hidden' if i else ''}><button class="screenshot-button" data-zoom="{src}" data-caption="{escape(alt,quote=True)}" aria-label="{t('Ansicht vergrößern','Enlarge view')}: {escape(label,quote=True)}"><img src="{src}" width="1400" height="700" alt="{escape(alt,quote=True)}" loading="lazy"><span>{t('Ansicht vergrößern','Enlarge view')} ↗</span></button><p class="caption">{escape(alt)} · {t('Ansicht aus der bestehenden Anwendung','View from the existing application')}</p></div>''' for i,(label,src,alt) in enumerate(images))
    return f'''<section class="section gallery-section" id="einblick"><div class="container"><div class="section-heading"><div>{eyebrow(t('EIN BLICK INS SYSTEM','INSIDE THE SYSTEM'))}<h2>{title or t('Substanz, die man sieht.','Substance you can see.')}</h2></div><p>{t('Keine abstrakten Versprechen. Entdecken Sie die Ansichten und Abläufe der bestehenden Anwendung.','More than an abstract promise. Explore the views and workflows of the existing application.')}</p></div><div class="gallery" data-tabs><div class="tab-list" role="tablist" aria-label="{t('Produktansichten','Product views')}">{buttons}</div><div class="gallery-frame"><div class="window-bar"><span></span><span></span><span></span><small>TOTUS / {t('PRODUKTANSICHT','PRODUCT VIEW')}</small></div>{panels}</div></div></div></section>'''
def feature_grid(items):
    return '<div class="feature-grid">'+''.join(f'<article><span class="index-number">{i+1:02}</span><h3>{a}</h3><p>{b}</p></article>' for i,(a,b) in enumerate(items))+'</div>'
def workflow(items):
    return f'''<section class="section container"><div class="section-heading"><div>{eyebrow(t('DER WORKFLOW','THE WORKFLOW'))}<h2>{t('Ein nächster Schritt.<br>Kein verlorener Kontext.','A clear next step.<br>No context lost.')}</h2></div></div><div class="workflow-grid">{''.join(f'<article><span>{i+1:02}</span><h3>{a}</h3><p>{b}</p></article>' for i,(a,b) in enumerate(items))}</div></section>'''

def home():
    hero=f'''<section class="home-hero container"><div class="hero-copy">{eyebrow(t('IMMOBILIENSOFTWARE. AUS BERLIN.','REAL ESTATE SOFTWARE. FROM BERLIN.'))}<h1>{t('Immobilien.<br>Weiter<span class="serif">gedacht.</span>','Real estate.<br>Thought <span class="serif">further.</span>')}</h1><p class="hero-description">{t('Aus Erfahrung wird Software. Aus Informationen werden bessere Entscheidungen. Für den gesamten Immobilienzyklus.','Experience becomes software. Information becomes better decisions. Across the entire real estate lifecycle.')}</p><div class="hero-actions"><a class="button" href="#portfolio">{t('Unsere Lösungen entdecken','Explore our solutions')}{ARROW}</a>{link('plattform',t('Die Plattform','The platform'),'text-link')}</div><div class="hero-footnote"><span class="pulse-dot"></span>{t('Im eigenen Immobilienbetrieb entwickelt.','Developed in our own property operations.')}<br><span>{t('Für Ihren Alltag weitergedacht.','Reimagined for your everyday work.')}</span></div></div><div class="hero-visual"><img class="architecture" src="architecture.png" alt="{t('Architektonische Illustration: moderne Natursteinfassade im Morgenlicht','Architectural illustration: a modern stone facade in morning light')}" width="1122" height="1402" fetchpriority="high"><div class="image-corner">TOTUS PERSPECTIVES / 01</div><div class="hero-glass"><span class="crosshair">＋</span><div><small>{t('UNSER GRUNDSATZ','OUR PRINCIPLE')}</small><p>{t('KI extrahiert.<br>Menschen entscheiden.','AI extracts.<br>People decide.')}</p></div><span class="glass-line"></span></div></div></section>
<div class="product-strip container"><span>{t('EIN ÖKOSYSTEM.<br>VIER PERSPEKTIVEN.','ONE ECOSYSTEM.<br>FOUR PERSPECTIVES.')}</span>{''.join(f'<a href="{url(k)}"><img src="{p["logo"]}" width="27" height="27" alt="">{p["name"]}{NORTH}</a>' for k,p in PRODUCTS.items())}</div>'''
    principle=f'''<section class="section story-section"><div class="container story-grid"><div>{eyebrow(t('WARUM TOTUS','WHY TOTUS'))}<h2>{t('Wir kennen Immobilien.<br><span class="serif">Nicht nur ihre Daten.</span>','We know real estate.<br><span class="serif">Beyond the data.</span>')}</h2></div><div><p class="large-copy">{t('Wir kaufen, verwalten und verkaufen selbst Immobilien in Berlin. Deshalb beginnt unsere Software dort, wo Ihre Arbeit stattfindet: in der Praxis.','We buy, manage and sell properties ourselves in Berlin. That is why our software starts where your work happens: in practice.')}</p><p>{t('Von der ersten Marktchance bis zum laufenden Betrieb übersetzen wir Erfahrung in strukturierte Abläufe. Für weniger Brüche zwischen Informationen, Menschen und Entscheidungen.','From the first market opportunity to daily operations, we translate experience into structured workflows. Connecting information, people and decisions.')}</p>{link('plattformabout',t('Unsere Geschichte kennenlernen','Get to know our story'))}</div></div><div class="container principles"><div><span>01</span><h3>{t('Aus der Praxis entwickelt','Built from experience')}</h3><p>{t('Die eigenen Objekte sind unser erster Prüfstein.','Our own properties are our first proving ground.')}</p></div><div><span>02</span><h3>{t('KI mit Verantwortung','AI with accountability')}</h3><p>{t('Vorbereiten und vorschlagen. Die Entscheidung bleibt bei Ihnen.','Prepare and propose. The decision remains yours.')}</p></div><div><span>03</span><h3>{t('Zusammenhängend gedacht','Designed to connect')}</h3><p>{t('Vom Dokument bis zum Prozess. Mit dem Blick für das Ganze.','From document to process. With the whole picture in view.')}</p></div></div></section>'''
    lifecycle=gallery([(t('01 · Entdecken','01 · Discover'),'paniprojekte.png',t('PANI Tracker: Projektchancen in Berlin und Brandenburg','PANI Tracker: project opportunities in Berlin and Brandenburg')),(t('02 · Bewerten','02 · Evaluate'),'investdealdetail.png',t('TOTUS Invest: Underwriting und Szenarien','TOTUS Invest: underwriting and scenarios')),(t('03 · Entscheiden','03 · Decide'),'resicorevotum.jpg',t('TOTUS ResiCore: dokumentierte Investmententscheidung','TOTUS ResiCore: documented investment decision')),(t('04 · Verwalten','04 · Manage'),'panihvuebersicht.jpg',t('PANI Hausverwaltung: Überblick über den laufenden Betrieb','PANI Hausverwaltung: everyday operations at a glance'))],t('Vom ersten Signal.<br>Bis ins tägliche Geschäft.','From the first signal.<br>To everyday operations.'))
    quote=f'''<section class="quote-section container"><span class="quote-mark">“</span><blockquote>{t('Jede Funktion, die wir ausliefern, hat vorher unseren eigenen Arbeitstag bestanden.','Every feature we ship has first been tested in our own working day.')}</blockquote><div class="quote-person"><span class="avatar">PH</span><p>Paul Harm<small>{t('Gründer, TOTUS CRE','Founder, TOTUS CRE')}</small></p></div></section>'''
    page('index',t('Immobilien. Weitergedacht.','Real estate. Thought further.'),t('Spezialisierte Immobiliensoftware aus Berlin für Investment, Verwaltung und Marktintelligenz.','Specialist real estate software from Berlin for investment, management and market intelligence.'),hero+portfolio()+principle+lifecycle+quote+cta())

def product(key):
    p=PRODUCTS[key];modules,steps,images=source_data(key)
    if key=='tracker':
        modules[0]=(modules[0][0],t('Portale, Baugenehmigungen, Landesplanung und Regionalnachrichten automatisch im Blick.','Automatically monitor portals, building permits, regional planning and local news.'))
    body=f'''<section class="product-hero container"><div class="breadcrumb"><a href="{url('index')}#portfolio">{t('Lösungen','Solutions')}</a><span>/</span>{p['name']}</div><div class="product-hero-grid"><div>{eyebrow(p['name'].upper()+' / '+pval(p,'cat').upper())}<h1>{pval(p,'title')}</h1><p class="hero-description">{pval(p,'desc')}</p><div class="hero-actions">{link('plattformdemo',t('Persönlich kennenlernen','Discover it together'),'button')}<a href="#einblick" class="text-link">{t('Einblicke ansehen','Explore the views')}{ARROW}</a></div><span class="status-pill">{pval(p,'status')}</span></div><div class="product-hero-preview {p['color']}"><div class="preview-label"><img src="{p['logo']}" width="32" height="32" alt="">{p['name']}</div><img class="preview-image" src="{p['image']}" width="1400" height="700" alt="{p['name']} — {t('Produktansicht','product view')}"><span class="preview-caption">{t('ENTWICKELT AUS DER PRAXIS','BUILT FROM EXPERIENCE')} {NORTH}</span></div></div></section>'''
    if key in ('pani','tracker'):
        body=body.replace(eyebrow(p['name'].upper()+' / '+pval(p,'cat').upper()), f'<div class="pani-brand-intro">{pani_brand(key)}</div>'+eyebrow(t('SOFTWARE FÜR '+pval(p,'cat').upper(),'SOFTWARE FOR '+pval(p,'cat').upper())))
        preview_start=body.index('<div class="product-hero-preview')
        body=body[:preview_start]+pani_software(key)+'</div></section>'
        body+=f'''<section class="pani-origin container"><div>{eyebrow(t('DIE MENSCHEN HINTER DER MARKE','THE PEOPLE BEHIND THE BRAND'))}<h2>{t('Persönlich geführt.<br>In Berlin zu Hause.','Personally run.<br>At home in Berlin.')}</h2></div><p>{t('PANI verbindet persönliche Hausverwaltung mit strukturierten digitalen Abläufen. Lernen Sie die Menschen und Leistungen hinter der Marke kennen.','PANI combines personal property management with structured digital processes. Meet the people and explore the services behind the brand.')}</p><a class="text-link" href="https://www.pani-hv.de/{'en.html' if LANG=='en' else ''}">{t('PANI kennenlernen','Meet PANI')}{NORTH}</a></section>'''
    product_gallery=gallery(images)
    if key in ('pani','tracker'):
        product_gallery=product_gallery.replace('TOTUS / ', 'PANI / ')
    body+=product_gallery
    body+=f'<section class="section container"><div class="section-heading"><div>{eyebrow(t("DIE MÖGLICHKEITEN","THE CAPABILITIES"))}<h2>{t("Die Details machen<br>den Unterschied.","The details make<br>the difference.")}</h2></div><p>{t("Spezialisiert auf die Aufgaben, die Ihren Alltag bestimmen.","Specialised for the work that shapes your day.")}</p></div>{feature_grid(modules)}</section>'
    body+=workflow(steps)+cta()
    body=body.replace(f'href="{url("plattformdemo")}"', f'href="{url("plattformdemo")}?product={key}"')
    page(key,p['name'],pval(p,'desc'),body)

def mock_deal():
    return f'''<div class="deal-demo" data-demo><div class="demo-heading"><span class="demo-brand">{MARK} TOTUS INVEST</span><span class="demo-badge">{t('INTERAKTIVES BEISPIEL','INTERACTIVE EXAMPLE')}</span></div><div class="demo-layout"><div class="demo-sidebar"><small>WORKSPACE</small><button data-demo-step="0" aria-pressed="true">01 <span>Inbox</span><i>3</i></button><button data-demo-step="1" aria-pressed="false">02 <span>Pipeline</span></button><button data-demo-step="2" aria-pressed="false">03 <span>Underwriting</span></button><button data-demo-step="3" aria-pressed="false">04 <span>IC-Memo</span></button><div class="demo-sidebar-foot">B / {t('Berlin Portfolio','Berlin portfolio')}<span>{t('Beispiel-Workspace','Example workspace')}</span></div></div><div class="demo-main"><div class="demo-status"><span class="status-dot">{t('BEISPIELDATEN','ILLUSTRATIVE DATA')}</span><span>CRE-001</span></div><h3 data-demo-title>{t('Ein neuer Deal. Alle Informationen.','A new deal. All the information.')}</h3><p data-demo-description>{t('Ein Exposé wird zur strukturierten Grundlage Ihrer Analyse.','An offering memorandum becomes the structured basis for your analysis.')}</p><div class="demo-property"><span class="building-icon">▥</span><div><strong>{t('Bürohaus am Park','Parkside Office')}</strong><small>BERLIN · OFFICE · 4.200 M²</small></div><span class="property-tag" data-demo-tag>{t('Eingegangen','Received')}</span></div><div class="demo-metrics"><div><span>{t('Kaufpreis','Asking price')}</span><strong>€ 12,5 <small>M</small></strong></div><div><span>{t('Jahresnettomiete','Annual net rent')}</span><strong>€ 725 <small>K</small></strong></div><div><span>{t('Anfangsrendite','Initial yield')}</span><strong>5,8 <small>%</small></strong></div></div><div class="demo-detail" data-demo-detail><span class="document-icon">↳</span><div><strong>Exposé_Berlin.pdf</strong><span>{t('Eckdaten extrahiert · zur Prüfung bereit','Key data extracted · ready for review')}</span></div><span class="check">✓</span></div><div class="demo-progress"><span class="active"></span><span></span><span></span><span></span></div><div class="demo-controls"><small>{t('Wählen Sie einen Schritt, um den Ablauf zu erkunden.','Select a step to explore the workflow.')}</small><button data-demo-next aria-label="{t('Nächster Schritt','Next step')}">{ARROW}</button></div></div></div><p class="demo-disclaimer">{t('Illustrativer Ablauf mit fiktiven Daten. Keine Verbindung zur Live-Anwendung.','Illustrative workflow with fictional data. Not connected to the live application.')}</p></div>'''

def platform():
    hero=f'''<section class="platform-hero"><div class="container"><div class="platform-intro">{eyebrow(t('DIE TOTUS PLATTFORM','THE TOTUS PLATFORM'))}<h1>{t('Ein klarer Blick.<br>Auf den ganzen Deal.','A clear perspective.<br>On the whole deal.')}</h1><p>{t('Vom Exposé bis zum Investment Committee. Verbinden Sie Daten, Analyse und Zusammenarbeit zu einer fundierten Entscheidung.','From offering memorandum to investment committee. Connect data, analysis and collaboration in an informed decision.')}</p><div class="hero-actions">{link('plattformdemo',t('Plattform kennenlernen','Explore the platform'),'button light')}<a class="text-link" href="#ablauf">{t('Workflow erkunden','Explore the workflow')}{ARROW}</a></div></div><div class="platform-preview" id="ablauf">{mock_deal()}</div></div></section>'''
    features=[]
    for key,v in PAGES.items():
        features.append(f'<a class="platform-feature" href="{url(key)}"><span class="index-number">{len(features)+1:02}</span><div><h3>{v[0][1 if LANG=="en" else 0]}</h3><p>{v[2][1 if LANG=="en" else 0]}</p></div>{NORTH}</a>')
    section=f'<section class="section container"><div class="section-heading"><div>{eyebrow(t("VOM EINGANG BIS ZUR ENTSCHEIDUNG","FROM INTAKE TO DECISION"))}<h2>{t("Jeder Schritt zählt.<br>Alles bleibt verbunden.","Every step matters.<br>Everything stays connected.")}</h2></div><p>{t("Eine durchgängige Arbeitsumgebung für professionelle Immobilieninvestments.","A continuous working environment for professional real estate investment.")}</p></div><div class="platform-features">{"".join(features)}</div></section>'
    trust=f'<section class="section trust-section"><div class="container split"><div>{eyebrow(t("VERTRAUEN ALS GRUNDLAGE","BUILT ON TRUST"))}<h2>{t("Transparente Daten.<br>Klare Verantwortung.","Transparent data.<br>Clear accountability.")}</h2></div><div><p class="large-copy">{t("KI unterstützt die Vorbereitung. Ihr Team behält die Kontrolle über Annahmen, Freigaben und Entscheidungen.","AI supports the preparation. Your team stays in control of assumptions, approvals and decisions.")}</p>{link("plattformsecurity",t("Sicherheit & Arbeitsweise","Security & approach"))}</div></div></section>'
    page('plattform',t('Die Investment-Plattform','The investment platform'),t('Ein strukturierter Workflow vom Exposé zum IC-Memo.','A structured workflow from offering memorandum to IC memo.'),hero+section+trust+cta())

def feature_page(key,v):
    i=1 if LANG=='en' else 0
    body=f'''<section class="detail-hero container"><div class="breadcrumb">{link('plattform',t('Plattform','Platform'),'plain')}<span>/</span>{v[0][i]}</div>{eyebrow('TOTUS CRE / '+v[0][i].upper())}<h1>{v[1][i]}</h1><div class="detail-hero-bottom"><p class="hero-description">{v[2][i]}</p>{link('plattformdemo',t('Im Gespräch entdecken','Explore it together'),'button')}</div></section>'''
    body+=gallery([(v[0][i],v[3],t('Einblick in die bestehende TOTUS Invest Anwendung','A view of the existing TOTUS Invest application'))],t('Für fundierte<br>Investmentarbeit.','For informed<br>investment work.'))
    body+=f'<section class="section container">{feature_grid([(item[i],item[i+2]) for item in v[4]])}</section>'
    if key=='plattformunderwriting':body+=calculator()
    else:body+=f'<section class="section container"><div class="section-heading"><div>{eyebrow(t("ZUSAMMENSPIEL","CONNECTED WORK"))}<h2>{t("Das Ergebnis ist<br>der nächste Anfang.","Every outcome is<br>the next beginning.")}</h2></div><p>{t("Informationen bleiben am Deal. Die nächste Phase beginnt mit dem Wissen aus der vorherigen.","Information stays with the deal. The next stage starts with the knowledge from the last.")}</p></div>{mock_deal()}</section>'
    page(key,v[0][i],v[2][i],body+cta())

def calculator():
    return f'''<section class="section calculator-section"><div class="container split"><div>{eyebrow(t('SENSITIVITÄT VERSTEHEN','UNDERSTAND SENSITIVITY'))}<h2>{t('Eine Annahme.<br>Eine andere Perspektive.','One assumption.<br>A different perspective.')}</h2><p>{t('Erkunden Sie, wie Kaufpreis und Jahresnettomiete die einfache Anfangsrendite verändern. Ein kleiner Einblick in das Denken in Szenarien.','Explore how purchase price and annual net rent change the simple initial yield. A small introduction to scenario thinking.')}</p><small>{t('Illustratives Rechenbeispiel, kein vollständiges Underwriting. Ohne Erwerbsnebenkosten, Finanzierung und Steuern.','Illustrative calculation, not full underwriting. Excludes transaction costs, financing and taxes.')}</small></div><div class="calculator"><div class="calc-label">{t('BEISPIEL: BÜROHAUS AM PARK','EXAMPLE: PARKSIDE OFFICE')}</div><label for="price">{t('Kaufpreis','Purchase price')}<output id="price-value">€ 12,5 M</output></label><input id="price" type="range" min="8" max="20" step="0.1" value="12.5"><label for="rent">{t('Jahresnettomiete','Annual net rent')}<output id="rent-value">€ 725 K</output></label><input id="rent" type="range" min="300" max="1200" step="5" value="725"><div class="calc-result"><span>{t('Einfache Anfangsrendite','Simple initial yield')}</span><output id="yield" aria-live="polite">5,80 %</output></div><p>{t('Jahresnettomiete ÷ Kaufpreis × 100','Annual net rent ÷ purchase price × 100')}</p></div></div></section>'''

def about():
    hero=f'''<section class="about-hero container"><div>{eyebrow(t('ÜBER TOTUS CRE','ABOUT TOTUS CRE'))}<h1>{t('Erfahrung ist<br>unser <span class="serif">Ausgangspunkt.</span>','Experience is<br>our <span class="serif">starting point.</span>')}</h1><p class="hero-description">{t('Wir bauen die Software, mit der wir selbst arbeiten wollen. Für Immobilienmenschen, die mehr Klarheit in ihren Alltag bringen möchten.','We build the software we want to work with ourselves. For real estate professionals who want to bring more clarity to their day.')}</p></div><div class="about-photo"><img src="architecture.png" alt="{t('Architektonische Illustration einer Natursteinfassade','Architectural illustration of a stone facade')}" width="1122" height="1402"><span>BERLIN / PERSPEKTIVE</span></div></section>'''
    body=f'''<section class="section container split"><div>{eyebrow(t('UNSER URSPRUNG','OUR ORIGINS'))}<h2>{t('Immobilien sind<br>unser tägliches Geschäft.','Real estate is<br>our daily business.')}</h2></div><div><p class="large-copy">{t('TOTUS CRE verbindet die Arbeit mit eigenen Immobilien in Berlin mit der Entwicklung spezialisierter Software.','TOTUS CRE combines operating our own properties in Berlin with developing specialised software.')}</p><p>{t('Was als Antwort auf konkrete Aufgaben beginnt, wird zu einem System: Exposés verstehen, Investitionen prüfen, Verwaltung organisieren und Marktchancen erkennen. Paul Harm gründete TOTUS CRE mit genau diesem Blick auf die Praxis.','What starts as an answer to a practical task becomes a system: understanding offering memoranda, evaluating investments, organising management and spotting opportunities. Paul Harm founded TOTUS CRE with this practical perspective.')}</p></div></section>'''
    body+=f'<section class="section trust-section"><div class="container">{eyebrow(t("WAS UNS LEITET","WHAT GUIDES US"))}<h2>{t("Klar in der Haltung.<br>Sorgfältig im Detail.","Clear in our principles.<br>Careful in the details.")}</h2>{feature_grid([(t("Fachlichkeit vor Effekt","Expertise before spectacle"),t("Immobilienprozesse bestimmen die Software. Nicht umgekehrt.","Property processes shape the software. Not the other way around.")),(t("Menschen entscheiden","People decide"),t("KI schafft eine Grundlage. Verantwortung lässt sich nicht automatisieren.","AI prepares a foundation. Accountability cannot be automated.")),(t("Ein Team, das mitdenkt","A team that thinks with you"),t("Von Konzept und Entwicklung bis zum Betrieb behalten wir den Zusammenhang im Blick.","From concept and development to operations, we keep the whole picture in view."))])}</div></section>'
    page('plattformabout',t('Über uns','About us'),t('Immobilienkompetenz und Softwareentwicklung aus Berlin.','Real estate expertise and software development from Berlin.'),hero+body+cta())

def contact(demo=False):
    key='plattformdemo' if demo else 'plattformcontact'
    title=t('Ihr Workflow. Unsere Demo.','Your workflow. Our demo.') if demo else t('Lernen wir uns kennen.','Let’s get to know each other.')
    intro=t('Bringen Sie Ihre Fragen und Ihren Prozess mit. Gemeinsam sehen wir uns an, welche TOTUS-Lösung zu Ihrem Vorhaben passt.','Bring your questions and your workflow. Together, we will explore which TOTUS solution fits your project.') if demo else t('Zeigen Sie uns Ihre Perspektive. Wir zeigen Ihnen, was mit TOTUS möglich ist.','Share your perspective. We’ll show you what is possible with TOTUS.')
    body=f'''<section class="contact-section container"><div class="contact-copy">{eyebrow(t('PERSÖNLICH. KONKRET. UNVERBINDLICH.','PERSONAL. PRACTICAL. NO OBLIGATION.'))}<h1>{title}</h1><p class="hero-description">{intro}</p><a class="big-email" href="mailto:hello@totus.info">hello@totus.info {NORTH}</a><div class="contact-address"><small>BERLIN</small><p>Seegefelder Straße 22<br>13583 Berlin</p></div><div class="contact-notes"><span>01</span><p>{t('Ihr Vorhaben kennenlernen','Understand your project')}</p><span>02</span><p>{t('Passende Lösungen gemeinsam ansehen','Explore the right solutions together')}</p><span>03</span><p>{t('Den nächsten Schritt definieren','Define the next step')}</p></div></div><div class="contact-form-wrap"><div class="form-intro"><span>{t('IHR ANLIEGEN','YOUR ENQUIRY')}</span><span>↗</span></div><h2>{t('Womit können wir helfen?','How can we help?')}</h2><form id="contact-form"><div class="form-row"><label>{t('Ihr Name','Your name')}<input name="name" autocomplete="name" required placeholder="Alex Morgan"></label><label>{t('Unternehmen','Company')}<input name="company" autocomplete="organization" placeholder="{t('Ihr Unternehmen','Your company')}"></label></div><label>{t('E-Mail-Adresse','Email address')}<input name="email" type="email" autocomplete="email" required placeholder="alex@unternehmen.de"></label><label>{t('Ich interessiere mich für','I am interested in')}<select name="interest"><option value="TOTUS Plattform">{t('TOTUS Plattform / Demo','TOTUS platform / demo')}</option><option>TOTUS Invest</option><option>TOTUS ResiCore</option><option>PANI Hausverwaltung</option><option>PANI Tracker</option><option>{t('Partnerschaft & Investment','Partnership & investment')}</option><option>{t('Individuelles Softwareprojekt','Custom software project')}</option></select></label><label>{t('Was beschäftigt Sie?','What is on your mind?')}<textarea name="message" rows="4" required placeholder="{t('Erzählen Sie uns kurz von Ihrem Vorhaben …','Tell us a little about your project …')}"></textarea></label><p class="form-note">{t('Ihre Angaben werden in eine E-Mail übernommen. Erst in Ihrem E-Mail-Programm senden Sie die Anfrage.','Your details will be added to an email draft. You send the enquiry from your email application.')} <a href="{url('plattformprivacy')}">{t('Datenschutz','Privacy')}</a></p><button class="button" type="submit">{t('E-Mail vorbereiten','Prepare email')}{ARROW}</button><p id="form-status" role="status"></p><div id="email-fallback" hidden><p>{t('Kein E-Mail-Programm geöffnet? Kopieren Sie Ihren Text und senden Sie ihn an hello@totus.info.','No email application opened? Copy your message and send it to hello@totus.info.')}</p><button type="button" class="text-link" id="copy-enquiry">{t('Anfrage kopieren','Copy enquiry')}{ARROW}</button><textarea id="email-draft" readonly aria-label="{t('Vorbereitete Anfrage','Prepared enquiry')}"></textarea></div></form></div></section>'''
    if demo:body+=f'<section class="section gallery-section"><div class="container"><div class="section-heading"><div>{eyebrow(t("VORAB ENTDECKEN","EXPLORE FIRST"))}<h2>{t("Ein Deal.<br>Vier Perspektiven.","One deal.<br>Four perspectives.")}</h2></div></div>{mock_deal()}</div></section>'
    else:
        contacts=[('Support','support@totus.info'),(t('Presse','Press'),'press@totus.info'),(t('Karriere','Careers'),'careers@totus.info'),(t('Sicherheit','Security'),'security@totus.info')]
        body+='<section class="container contact-channels">'+''.join(f'<div><small>{label}</small><a href="mailto:{email}">{email} ↗</a></div>' for label,email in contacts)+'</section>'
    page(key,title,intro,body)

def careers():
    body=f'''<section class="detail-hero container">{eyebrow(t('KARRIERE BEI TOTUS','CAREERS AT TOTUS'))}<h1>{t('Bauen Sie mit.<br>An Software mit Substanz.','Build with us.<br>Software with substance.')}</h1><div class="detail-hero-bottom"><p class="hero-description">{t('Immobilien, Technologie und echte Verantwortung. Für Menschen, die Probleme verstehen wollen, bevor sie Lösungen bauen.','Real estate, technology and real responsibility. For people who want to understand problems before building solutions.')}</p><a class="button" href="mailto:careers@totus.info">{t('Kontakt aufnehmen','Get in touch')}{ARROW}</a></div></section>
<section class="section gallery-section"><div class="container">{eyebrow(t('UNSERE ARBEIT','OUR WORK'))}{feature_grid([(t('Nähe zum Problem','Close to the problem'),t('Direkter Einblick in echte Immobilienprozesse.','Direct insight into real property processes.')),(t('Raum für Verantwortung','Room for ownership'),t('Von der Idee bis zur Anwendung mitgestalten.','Shape the work from idea to application.')),(t('Ein zusammenhängendes Produkt','A connected product'),t('Frontend, Backend und KI im Kontext verstehen.','Understand frontend, backend and AI in context.'))])}</div></section>
<section class="section container"><div class="section-heading"><div>{eyebrow(t('WIR MÖCHTEN SIE KENNENLERNEN','WE WOULD LIKE TO MEET YOU'))}<h2>{t('Ihre Perspektive<br>könnte uns fehlen.','Your perspective<br>could be what we need.')}</h2></div><p>{t('Sprechen Sie mit uns über diese Tätigkeitsfelder und aktuelle Möglichkeiten.','Talk to us about these areas and current opportunities.')}</p></div><div class="job-list"><a href="mailto:careers@totus.info?subject=Senior%20Frontend%20Engineer"><span><small>ENGINEERING</small><h3>Senior Frontend Engineer</h3></span><span>Berlin / Remote DACH</span>{NORTH}</a><a href="mailto:careers@totus.info?subject=Founder%20Associate"><span><small>BUSINESS & OPERATIONS</small><h3>Founder Associate</h3></span><span>Berlin</span>{NORTH}</a></div><p class="caption">{t('Aktuelle Verfügbarkeit und Konditionen besprechen wir persönlich. Initiativbewerbungen sind willkommen.','We discuss current availability and terms personally. Speculative applications are welcome.')}</p></section>'''
    page('plattformcareers',t('Karriere','Careers'),t('Immobilien und Technologie gemeinsam weiterdenken.','Think real estate and technology further, together.'),body+cta())

def press():
    fact=t('TOTUS CRE entwickelt spezialisierte Immobiliensoftware in Berlin. Das Portfolio umfasst TOTUS Invest für gewerbliche Investmentprozesse, TOTUS ResiCore für Wohnimmobilien, PANI Hausverwaltung und PANI Tracker für Markt- und Projektinformationen. Der Grundsatz: KI extrahiert, Menschen entscheiden.','TOTUS CRE develops specialist real estate software in Berlin. Its portfolio includes TOTUS Invest for commercial investment workflows, TOTUS ResiCore for residential property, PANI Hausverwaltung for property management and PANI Tracker for market and project intelligence. Its principle: AI extracts, people decide.')
    body=f'''<section class="detail-hero container">{eyebrow(t('PRESSE & MEDIEN','PRESS & MEDIA'))}<h1>{t('Eine klare Geschichte.<br>Direkt aus Berlin.','A clear story.<br>Straight from Berlin.')}</h1><div class="detail-hero-bottom"><p class="hero-description">{t('Informationen über TOTUS CRE, Bildmaterial und ein direkter Kontakt für Ihre Fragen.','Information about TOTUS CRE, imagery and a direct contact for your questions.')}</p><a class="button" href="mailto:press@totus.info">press@totus.info {ARROW}</a></div></section>
<section class="section container split"><div>{eyebrow(t('KURZPROFIL','COMPANY PROFILE'))}<h2>{t('Über TOTUS CRE.','About TOTUS CRE.')}</h2></div><div><p class="large-copy">{fact}</p><dl class="facts"><div><dt>{t('Standort','Location')}</dt><dd>{t("Berlin, Deutschland","Berlin, Germany")}</dd></div><div><dt>{t('Gründer','Founder')}</dt><dd>Paul Harm</dd></div><div><dt>{t('Schwerpunkt','Focus')}</dt><dd>Real Estate Software</dd></div></dl></div></section>
<section class="section gallery-section"><div class="container"><div class="section-heading"><div>{eyebrow(t('MATERIALIEN','MATERIALS'))}<h2>{t('Für Ihre Redaktion.','For your newsroom.')}</h2></div></div><div class="press-assets"><a href="brand-totus.svg" download><div class="press-logo">{MARK}<strong>TOTUS CRE</strong></div><span>{t('Wort-Bild-Marke · SVG','Brand mark · SVG')} ↓</span></a><a href="investpipeline.png" download><img src="investpipeline.png" width="1400" height="644" alt="TOTUS Invest"><span>{t('Produktansicht · PNG','Product view · PNG')} ↓</span></a></div><p class="caption">{t('Für redaktionelle Anfragen, weitere Materialien und Freigaben: press@totus.info.','For editorial enquiries, further materials and approvals: press@totus.info.')}</p></div></section>'''
    page('plattformpress',t('Presse','Press'),fact,body)

def security():
    body=f'''<section class="detail-hero container">{eyebrow(t('SICHERHEIT & VERANTWORTUNG','SECURITY & ACCOUNTABILITY'))}<h1>{t('Vertrauen entsteht<br>durch <span class="serif">Nachvollziehbarkeit.</span>','Trust comes<br>from <span class="serif">transparency.</span>')}</h1><p class="hero-description">{t('Sensible Immobilieninformationen verdienen klare Zuständigkeiten, kontrollierte Zugriffe und nachvollziehbare Entscheidungen.','Sensitive real estate information deserves clear ownership, controlled access and traceable decisions.')}</p></section>
<section class="section gallery-section"><div class="container">{feature_grid([(t('Rollen & Zugriffe','Roles & access'),t('Mandantenfähige Workspaces und rollenbasierte Berechtigungen strukturieren die Zusammenarbeit.','Multi-tenant workspaces and role-based permissions structure collaboration.')),(t('Zwei-Faktor-Authentifizierung','Two-factor authentication'),t('Ein zusätzlicher Faktor unterstützt den Schutz des Benutzerzugangs.','An additional factor helps protect account access.')),(t('Audit-Trail','Audit trail'),t('Änderungen lassen sich bis auf Feldebene nachvollziehen.','Changes can be traced at field level.')),(t('Kontrollierter KI-Einsatz','Controlled use of AI'),t('KI unterstützt bei Extraktion und Entwürfen. Prüfung und Freigabe bleiben beim Team.','AI supports extraction and drafting. Review and approval remain with the team.'))])}</div></section>
<section class="section container split"><div>{eyebrow(t('DUE DILIGENCE','DUE DILIGENCE'))}<h2>{t('Die richtigen Fragen<br>gehören an den Anfang.','The right questions<br>belong at the start.')}</h2></div><div><p class="large-copy">{t('Hosting, Datenverarbeitung, Rollenmodell und Ihre Anforderungen besprechen wir konkret für den vorgesehenen Einsatz.','We discuss hosting, data processing, the permissions model and your requirements for the intended use.')}</p><p>{t('Für technische Fragen oder die verantwortungsvolle Meldung einer Sicherheitslücke erreichen Sie uns direkt.','Contact us directly with technical questions or to responsibly report a security vulnerability.')}</p><a class="text-link" href="mailto:security@totus.info">security@totus.info {ARROW}</a></div></section>'''
    page('plattformsecurity',t('Sicherheit','Security'),t('Klare Zuständigkeiten und kontrollierte Zugriffe.','Clear ownership and controlled access.'),body+cta())

def translations(raw):
    part=raw.split('    en: {',1)
    if len(part)<2:return {}
    return {k:v.replace("\\'","'").replace('\\"','"').replace('\\n',' ') for k,v in re.findall(r"""['"]([^'"]+)['"]\s*:\s*'((?:\\.|[^'\\])*)'""",part[1])}
def legal_html(n,tr):
    if isinstance(n,str):return escape(n)
    if n.tag in ['svg','script','style','button']:return ''
    attrs=''
    if n.attrs.get('id'):attrs+=' id="'+escape(n.attrs['id'],quote=True)+'"'
    if n.tag=='a':
        href=n.attrs.get('href','#')
        if href.endswith('.html') and '/' not in href:href=url(href[:-5])
        if href.startswith(('http','mailto:','#')) or '.html' in href:attrs+=' href="'+escape(href,quote=True)+'"'
    tag=n.tag if n.tag in ['a','section','div','p','span','strong','b','em','i','h2','h3','h4','ul','ol','li','br','table','thead','tbody','tr','td','th'] else 'div'
    key=n.attrs.get('data-i18n') or n.attrs.get('data-i18n-html')
    if key and key in tr:
        inner=tr[key] if 'data-i18n-html' in n.attrs else escape(tr[key])
    else:inner=''.join(legal_html(c,tr) for c in n.children)
    return '<'+tag+attrs+'>'+inner+('' if tag=='br' else '</'+tag+'>')
def legal(key,title):
    raw=raw_page(key);root=DOM(raw).root
    sections=root.all(lambda n:n.tag=='section' and re.match(r'sec-\d+',n.attrs.get('id','')))
    tr=translations(raw) if LANG=='en' else {}
    toc=[];content=[]
    for n in sections:
        head=nodes(n,'h2')
        if not head:continue
        label=tr.get(head[0].attrs.get('data-i18n'),head[0].text())
        toc.append(f'<a href="#{n.attrs["id"]}">{escape(label)}</a>')
        content.append(legal_html(n,tr))
    body=f'''<section class="legal-hero container">{eyebrow(t('RECHTLICHES','LEGAL'))}<h1>{title}</h1><p>{t('Angaben und Bestimmungen von TOTUS CRE.','Information and terms from TOTUS CRE.')}</p></section><section class="container legal-layout"><aside><span class="eyebrow">{t('INHALT','CONTENTS')}</span>{''.join(toc)}</aside><article class="legal-content">{''.join(content)}</article></section>'''
    page(key,title,title+' · TOTUS CRE',body)
    return len(content)

for LANG in ['de','en']:
    home()
    for k in PRODUCTS:product(k)
    platform()
    for k,v in PAGES.items():feature_page(k,v)
    about();contact();contact(True);careers();press();security()
    for key,title in [('plattformimprint',t('Impressum','Legal notice')),('plattformprivacy',t('Datenschutz','Privacy policy')),('plattformterms',t('Allgemeine Geschäftsbedingungen','Terms and conditions'))]:
        count=legal(key,title)
        assert count>0, 'Missing legal content: '+key
LANG='de'
page('404','Seite nicht gefunden','Seite nicht gefunden',f'<section class="detail-hero container">{eyebrow("404 / NICHT GEFUNDEN")}<h1>Eine neue<br>Perspektive finden.</h1><p>Diese Seite konnten wir nicht finden.</p>{link("index","Zur Startseite","button")}</section>')
LANG='en'
page('404','Page not found','Page not found',f'<section class="detail-hero container">{eyebrow("404 / NOT FOUND")}<h1>Find a new<br>perspective.</h1><p>We could not find this page.</p>{link("index","Back to the homepage","button")}</section>')
(OUT/'brand-totus.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="560" height="120" viewBox="0 0 560 120"><g transform="translate(10 12) scale(2.6)" fill="#163a32"><path d="M2 3h28v7H19v23h-7V10H2V3Z"/><path d="M2 14h6v19H2V14Zm22 0h6v19h-6V14Z" opacity=".45"/></g><text x="115" y="85" font-family="Arial,sans-serif" font-size="72" font-weight="600" letter-spacing="-3" fill="#163a32">TOTUS CRE</text></svg>',encoding='utf-8')
content_files=sorted(f.name for f in OUT.glob('*.html') if f.name not in ('404.html','en404.html'))
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap+=''.join('  <url><loc>'+SITE_URL+('/' if f=='index.html' else '/'+f)+'</loc></url>\n' for f in content_files)
(OUT/'sitemap.xml').write_text(sitemap+'</urlset>\n',encoding='utf-8')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+SITE_URL+'/sitemap.xml\n',encoding='utf-8')
print('Generated',len(list(OUT.glob('*.html'))),'pages. All original same-site HTML routes retained.')
