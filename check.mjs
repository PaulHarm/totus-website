import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(process.argv[2]||'dist');
const files=fs.readdirSync(root).filter(f=>f.endsWith('.html'));
const errors=[];
let links=0,images=0;
for(const file of files){
  const html=fs.readFileSync(path.join(root,file),'utf8');
  if((html.match(/<h1\b/g)||[]).length!==1)errors.push(file+': must have one H1');
  if(!html.includes('<title>')||!html.includes('name="description"'))errors.push(file+': metadata missing');
  if(!/rel="canonical" href="https:\/\//.test(html))errors.push(file+': absolute canonical URL missing');
  if(!/hreflang="en" href="https:\/\//.test(html))errors.push(file+': absolute language alternate missing');
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  if(new Set(ids).size!==ids.length)errors.push(file+': duplicate IDs');
  for(const m of html.matchAll(/(?:href|src)="([^"]+)"/g)){
    const ref=m[1];if(/^(?:https?:|mailto:|data:)/.test(ref))continue;
    const [p,anchor]=ref.split('#');const dest=p?decodeURIComponent(p.split('?')[0]):file;
    if(!fs.existsSync(path.join(root,dest)))errors.push(file+': missing '+ref);
    else if(anchor&&dest.endsWith('.html')){const target=fs.readFileSync(path.join(root,dest),'utf8');if(!target.includes('id="'+anchor+'"'))errors.push(file+': missing anchor '+ref)}
    links++;
  }
  for(const m of html.matchAll(/<img\b[^>]*>/g)){if(!m[0].includes('alt='))errors.push(file+': image missing alt');images++}
  for(const m of html.matchAll(/aria-controls="([^"]+)"/g))if(!ids.includes(m[1]))errors.push(file+': broken aria-controls '+m[1]);
  if(html.includes('undefined')||html.includes('None'))errors.push(file+': unresolved template value');
}
const original=fs.readdirSync('source-content').filter(f=>f.endsWith('.html'));
for(const f of original)if(!files.includes(f))errors.push('Original route missing: '+f);
const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
for(const f of files.filter(f=>!['index.html','404.html','en404.html'].includes(f)))if(!sitemap.includes('/'+f+'</loc>'))errors.push('Sitemap route missing: '+f);
const summary={pages:files.length,originalRoutes:original.length,localReferences:links,images,errors};
console.log(JSON.stringify(summary,null,2));
if(errors.length)process.exitCode=1;
