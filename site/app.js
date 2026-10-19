const english=document.documentElement.lang==='en';
const tr=(de,en)=>english?en:de;
const mobileButton=document.querySelector('.mobile-toggle');
const nav=document.querySelector('#navigation');
mobileButton?.addEventListener('click',()=>{const open=mobileButton.getAttribute('aria-expanded')!=='true';mobileButton.setAttribute('aria-expanded',String(open));mobileButton.setAttribute('aria-label',open?tr('Menü schließen','Close menu'):tr('Menü öffnen','Open menu'));nav.classList.toggle('is-open',open);if(open)motion.reveal(nav);else motion.stop(nav)});
const dropdowns=[...document.querySelectorAll('.nav-dropdown')];
dropdowns.forEach(detail=>detail.addEventListener('toggle',()=>{if(detail.open){dropdowns.filter(d=>d!==detail).forEach(d=>d.open=false);motion.animate(detail.querySelector('.mega-menu'),[{opacity:0,transform:'translateY(-7px)'},{opacity:1,transform:'translateY(0)'}],{duration:300})}}));
document.addEventListener('click',event=>{dropdowns.forEach(d=>{if(!d.contains(event.target))d.open=false})});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){dropdowns.forEach(d=>{if(d.open){d.open=false;d.querySelector('summary').focus()}});if(mobileButton?.getAttribute('aria-expanded')==='true'){mobileButton.setAttribute('aria-expanded','false');nav.classList.remove('is-open');mobileButton.focus()}}});
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
  if(button.getAttribute('aria-pressed')==='true')return;
  const cards=[...document.querySelectorAll('[data-category]')];
  const grid=document.querySelector('.product-grid');
  motion.stop(grid);
  const oldHeight=grid.getBoundingClientRect().height;
  const previous=new Map();
  cards.forEach(card=>{motion.stop(card);if(!card.hidden)previous.set(card,card.getBoundingClientRect())});
  document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  let count=0;cards.forEach(card=>{card.hidden=button.dataset.filter!=='all'&&card.dataset.category!==button.dataset.filter;if(!card.hidden)count++});
  const newHeight=grid.getBoundingClientRect().height;
  cards.filter(card=>!card.hidden).forEach((card,i)=>{
    const before=previous.get(card),after=card.getBoundingClientRect();
    if(before)motion.animate(card,[{transform:'translate('+ (before.left-after.left)+'px,'+(before.top-after.top)+'px)'},{transform:'translate(0,0)'}],{duration:480});
    else motion.reveal(card,i*55);
  });
  if(oldHeight!==newHeight)motion.animate(grid,[{height:oldHeight+'px'},{height:newHeight+'px'}],{duration:480});
  document.querySelector('.filter-count').textContent=String(count).padStart(2,'0')+' '+tr('Lösungen','solutions');
}));
document.querySelectorAll('[data-tabs]').forEach(gallery=>{
  const tabs=[...gallery.querySelectorAll('[role=tab]')];
  function activate(tab){if(tab.getAttribute('aria-selected')==='true')return;tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;const panel=document.getElementById(t.getAttribute('aria-controls'));motion.stop(panel);panel.hidden=!active;if(active)motion.swap(panel)})}
  tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>activate(tab));tab.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight')next=(i+1)%tabs.length;if(e.key==='ArrowLeft')next=(i-1+tabs.length)%tabs.length;if(e.key==='Home')next=0;if(e.key==='End')next=tabs.length-1;if(next!==undefined){e.preventDefault();activate(tabs[next]);tabs[next].focus()}})});
});
const dialog=document.getElementById('image-dialog');
document.querySelectorAll('[data-zoom]').forEach(button=>button.addEventListener('click',()=>{dialog.querySelector('img').src=button.dataset.zoom;dialog.querySelector('img').alt=button.dataset.caption;dialog.querySelector('p').textContent=button.dataset.caption;dialog.showModal();document.body.classList.add('dialog-open');motion.animate(dialog,[{opacity:0,transform:'translateY(14px) scale(.98)'},{opacity:1,transform:'translateY(0) scale(1)'}],{duration:400})}));
let closingDialog=false;
function closeImageDialog(){
  if(closingDialog||!dialog.open)return;
  closingDialog=true;
  const finish=()=>{dialog.close();document.body.classList.remove('dialog-open');closingDialog=false};
  const animation=motion.animate(dialog,[{opacity:1,transform:'scale(1)'},{opacity:0,transform:'scale(.985)'}],{duration:160,easing:'ease-out'});
  if(animation)animation.finished.then(finish,finish);else finish();
}
dialog?.querySelector('.dialog-close').addEventListener('click',closeImageDialog);
dialog?.addEventListener('cancel',event=>{event.preventDefault();closeImageDialog()});
dialog?.addEventListener('close',()=>{document.body.classList.remove('dialog-open');closingDialog=false});
dialog?.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeImageDialog()}});
const states=[
 [tr('Ein neuer Deal. Alle Informationen.','A new deal. All the information.'),tr('Ein Exposé wird zur strukturierten Grundlage Ihrer Analyse.','An offering memorandum becomes the structured basis for your analysis.'),tr('Eingegangen','Received'),'Exposé_Berlin.pdf',tr('Eckdaten extrahiert · zur Prüfung bereit','Key data extracted · ready for review')],
 [tr('Ein klarer nächster Schritt.','A clear next step.'),tr('Phase, Zuständigkeit und offene Aufgaben bleiben am Deal.','Stage, ownership and open tasks stay with the deal.'),'Screening',tr('Due-Diligence-Checkliste','Due diligence checklist'),tr('Unterlagen prüfen · Verantwortung zugeordnet','Review documents · owner assigned')],
 [tr('Was trägt das Investment?','What supports the investment?'),tr('Mieten, Kaufpreis und Annahmen im Zusammenhang betrachten.','Consider rents, purchase price and assumptions together.'),'Underwriting',tr('Base Case · Annahmen prüfen','Base case · review assumptions'),tr('5,8 % einfache Anfangsrendite · vor Nebenkosten','5.8% simple initial yield · before transaction costs')],
 [tr('Bereit für Ihre Entscheidung.','Ready for your decision.'),tr('Daten, These und Risiken werden zur Investmentvorlage.','Data, thesis and risks become an investment proposal.'),'IC Review',tr('Investment-Memo · Entwurf','Investment memo · draft'),tr('Menschliche Prüfung und Freigabe erforderlich','Human review and approval required')]
];
document.querySelectorAll('[data-demo]').forEach(demo=>{
  let current=0;
  function change(index){if(current===index)return;current=index;const s=states[index];demo.querySelector('[data-demo-title]').textContent=s[0];demo.querySelector('[data-demo-description]').textContent=s[1];demo.querySelector('[data-demo-tag]').textContent=s[2];demo.querySelector('[data-demo-detail] strong').textContent=s[3];demo.querySelector('[data-demo-detail] div>span').textContent=s[4];demo.querySelectorAll('[data-demo-step]').forEach((b,i)=>b.setAttribute('aria-pressed',String(i===index)));demo.querySelectorAll('.demo-progress>span').forEach((s,i)=>s.classList.toggle('active',i<=index));['[data-demo-title]','[data-demo-description]','[data-demo-tag]','[data-demo-detail]'].forEach((selector,i)=>motion.swap(demo.querySelector(selector),i*35));}
  demo.querySelectorAll('[data-demo-step]').forEach(b=>b.addEventListener('click',()=>change(Number(b.dataset.demoStep))));
  demo.querySelector('[data-demo-next]').addEventListener('click',()=>change((current+1)%states.length));
});
const price=document.getElementById('price'),rent=document.getElementById('rent');
if(price&&rent){function calculate(){const locale=english?'en-GB':'de-DE';document.getElementById('price-value').textContent='€ '+Number(price.value).toLocaleString(locale,{minimumFractionDigits:1,maximumFractionDigits:1})+' M';document.getElementById('rent-value').textContent='€ '+rent.value+' K';document.getElementById('yield').textContent=(Number(rent.value)/(Number(price.value)*1000)*100).toLocaleString(locale,{minimumFractionDigits:2,maximumFractionDigits:2})+' %'}price.addEventListener('input',calculate);rent.addEventListener('input',calculate);calculate()}
const form=document.getElementById('contact-form');
// Keep product context when a visitor requests a demo or switches language.
const enquiryProducts={invest:'TOTUS Invest',resicore:'TOTUS ResiCore',pani:'PANI Hausverwaltung',tracker:'PANI Tracker'};
const requestedProduct=new URLSearchParams(window.location.search).get('product');
if(form&&Object.hasOwn(enquiryProducts,requestedProduct)){
  form.elements.interest.value=enquiryProducts[requestedProduct];
  const language=document.querySelector('.language');
  if(language){const destination=new URL(language.getAttribute('href'),window.location.href);destination.searchParams.set('product',requestedProduct);language.setAttribute('href',destination.pathname+destination.search)}
}
let emailDraft='';
form?.addEventListener('submit',event=>{
  event.preventDefault();if(!form.reportValidity())return;
  const data=new FormData(form);
  const subject=tr('Anfrage: ','Enquiry: ')+data.get('interest');
  emailDraft=tr('Guten Tag TOTUS Team,','Hello TOTUS team,')+'\n\n'+data.get('message')+'\n\n'+tr('Interesse: ','Interest: ')+data.get('interest')+'\n'+tr('Name: ','Name: ')+data.get('name')+'\n'+tr('Unternehmen: ','Company: ')+data.get('company')+'\nE-Mail: '+data.get('email');
  document.getElementById('email-draft').value=emailDraft;
  document.getElementById('email-fallback').hidden=false;
  document.getElementById('form-status').textContent=tr('Ihr Entwurf ist vorbereitet. Bitte senden Sie ihn in Ihrem E-Mail-Programm.','Your draft is ready. Please send it from your email application.');
  window.location.href='mailto:hello@totus.info?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(emailDraft);
});
document.getElementById('copy-enquiry')?.addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(emailDraft);document.getElementById('form-status').textContent=tr('Anfrage kopiert.','Enquiry copied.')}
  catch{const field=document.getElementById('email-draft');field.focus();field.select();document.getElementById('form-status').textContent=tr('Text ausgewählt. Mit Strg+C kopieren.','Text selected. Press Ctrl+C to copy.')}
});
