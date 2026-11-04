#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,secrets,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
WIKI=ROOT/'wiki'; CFG=json.loads((ROOT/'tools/config.json').read_text())
SOURCE_ID=CFG['source_id']; SOURCE_URL=CFG['source_url']; KB_TITLE=CFG['title']; KB_DESC=CFG['description']
def mint_uid():
 if hasattr(uuid,'uuid7'): return str(uuid.uuid7())
 ms=int(time.time()*1000)&((1<<48)-1); n=(ms<<80)|(7<<76)|(secrets.randbits(12)<<64)|(2<<62)|secrets.randbits(62); return str(uuid.UUID(int=n))
def normalise(u):
 u=u.rstrip('/').lower(); return u[8:] if u.startswith('https://') else u
def slugify(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-') or 'entry'
def q(s): return json.dumps(s,ensure_ascii=False)
def summary(s):
 s=s.strip()
 return s if len(s)<=160 else s[:157].rsplit(' ',1)[0].rstrip(',;:')+'…'
def parse_list(path):
 kind=CFG['kind']; entries=[]; section=None; in_collection=(kind!='design')
 if kind=='design': in_collection=False
 for line in path.read_text(encoding='utf-8').splitlines():
  if kind=='design' and line.strip()=='## Collection': in_collection=True; section=None; continue
  if kind=='design' and line.startswith('## ') and line.strip()!='## Collection': in_collection=False; section=None; continue
  if kind=='design' and in_collection and line.startswith('### '): section=line[4:].strip(); continue
  if kind=='beginners' and line.startswith('## '): section=line[3:].strip(); continue
  if not section or (kind=='design' and not in_collection): continue
  if kind=='design':
   m=re.match(r'^\s*- \[\*\*(.+?)\*\*\]\((https?://[^)]+)\)\s+-\s+(.+?)\s*$',line)
  else:
   m=re.match(r'^\s*- \[([^]]+)\]\((https?://[^)]+)\)(.*)$',line)
  if not m: continue
  title,url,tail=m.groups()
  if kind=='beginners':
   # Keep the row description only; discard inline issue-label annotation.
   tail=re.sub(r'^\s*_\([^)]*\)_\s*<br>\s*','',tail).strip()
   tail=re.sub(r'^\s*<br>\s*','',tail).strip()
   tail=tail or 'Beginner-friendly project listed by the source.'
  title=re.sub(r'\\([\\`*_{}\[\]()#+.!|>~-])',r'\1',title).strip()
  entries.append({'title':title,'url':url,'section':section,'summary':tail,'source_key':json.dumps([section,title,url],ensure_ascii=False,separators=(',',':'))})
 if not entries: raise ValueError('No curated entries parsed')
 return entries
def split(text):
 if not text.startswith('---\n'): return {},text
 end=text.find('\n---\n',4)
 if end<0:return {},text
 f={}
 for line in text[4:end].splitlines():
  if ': ' in line and not line.startswith(' '):
   k,v=line.split(': ',1)
   try:f[k]=json.loads(v)
   except:f[k]=v.strip('"')
 return f,text[end+5:]
MANAGED={'uid','title','summary','type','category','url','status','last_checked','created','updated','depth','source_list','source_commit','list_summary','source_key'}
def page(e,date,commit,old=None):
 f,body=split(old or '')
 extras=[]
 if old:
  end=old.find('\n---\n',4)
  for line in old[4:end].splitlines():
   if line and not line.startswith((' ','-','\t')) and ': ' in line:
    key=line.split(':',1)[0]
    if key not in MANAGED: extras.append([line])
   elif extras: extras[-1].append(line)
 uid=f.get('uid') or mint_uid(); created=f.get('created') or date; depth=f.get('depth') or 'stub'; status=f.get('status') or 'unknown'; last=f.get('last_checked')
 old_sources=[]
 if old:
  end=old.find('\n---\n',4); in_sources=False
  skip_retrieved=False
  for line in old[4:end].splitlines():
   if line.startswith('sources:'): in_sources=True; old_sources=[line]; continue
   if in_sources and line and not line.startswith((' ','-','\t')): break
   if in_sources and line.startswith('  - url:') and SOURCE_URL+'/blob/' in line and '/README.md' in line:
    skip_retrieved=True; continue
   if in_sources and skip_retrieved and line.startswith('    retrieved:'):
    skip_retrieved=False; continue
   skip_retrieved=False
   if in_sources: old_sources.append(line)
 new_records=[f'  - path: {q("raw/2026-11-04/README.md")}']
 if (ROOT/'raw/2026-11-04/LICENSE').exists(): new_records.append(f'  - path: {q("raw/2026-11-04/LICENSE")}')
 new_records.append(f'  - path: {q("raw/2026-11-04/capture.json")}')
 source_lines=old_sources if len(old_sources)>1 else ['sources:']
 for record in new_records:
  if not any(record.split(':',1)[0] in line and record.split(':',1)[1].strip().split("/blob/")[-1].rstrip("'\"") in line for line in source_lines): source_lines.append(record)
  
 lines=['---',f'uid: {uid}',f'title: {q(e["title"])}',f'summary: {q(summary(e["summary"]))}','type: entity',f'category: {q(e["section"])}',f'url: {q(e["url"])}',f'status: {status}']
 if last: lines.append(f'last_checked: {q(last)}')
 lines += [f'created: {created}',f'updated: {date}',f'depth: {depth}',f'source_list: {SOURCE_ID}',f'source_commit: {commit}',f'list_summary: {q(e["summary"])}',f'source_key: {q(e["source_key"])}']
 for block in extras: lines.extend(block)
 lines += source_lines+['---']
 body=body if old and depth!='stub' else f'\n{e["summary"]}\n\n- **Resource:** {e["url"]}\n- **List category:** {e["section"]}\n- **Source:** [{SOURCE_ID}]({SOURCE_URL}) — generated stub (`depth: stub`); source list is canon.\n'
 return '\n'.join(lines)+'\n'+body

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',default=str(ROOT/'raw/2026-11-04')); ap.add_argument('--date'); a=ap.parse_args(); source=Path(a.source); capture=source/'capture.json'
 if not (source/'README.md').exists(): sys.exit('source README missing')
 commit=json.loads(capture.read_text())['source_commit'] if capture.exists() else subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
 date=a.date or time.strftime('%Y-%m-%d',time.gmtime()); entries=parse_list(source/'README.md'); WIKI.mkdir(exist_ok=True)
 existing={}
 for p in WIKI.glob('*.md'):
  f,_=split(p.read_text()); key=f.get('source_key')
  if key:existing[key]=p
 used={}; groups={}; matched=set()
 for e in entries:
  p=existing.get(e['source_key'])
  if p is None:
   s=slugify(e['title']); used[s]=used.get(s,0)+1; n=used[s]; p=WIKI/(s+(f'-{n}' if n>1 else '')+'.md')
  p.write_text(page(e,date,commit,p.read_text() if p.exists() else None)); matched.add(p)
  groups.setdefault(e['section'],[]).append((p.stem,e))
 for p in set(existing.values())-matched:
  f,b=split(p.read_text()); p.write_text(re.sub(r'^status: .*$', 'status: "archived"',p.read_text(),count=1,flags=re.M)+f'\n> Delisted from source list at {commit}; retained as a tombstone.\n')
 # stable category slug with collision safety
 cats={}; seen=set()
 for cat in groups:
  s=slugify(cat); base=s;n=2
  while s in seen:s=f'{base}-{n}';n+=1
  seen.add(s);cats[cat]=s
  lines=[f'# {cat}','']
  for slug,e in groups[cat]:lines.append(f'- [{e["title"]}]({slug}.md) — {summary(e["summary"])}')
  (WIKI/f'index-{s}.md').write_text('\n'.join(lines)+'\n')
 lines=[f'# {KB_TITLE}','',KB_DESC,'','Generated by `tools/ingest.py`; do not edit by hand.','','## Categories','']
 for cat,items in groups.items():lines.append(f'- [{cat}](wiki/index-{cats[cat]}.md) — {len(items)} entries')
 (ROOT/'index.md').write_text('\n'.join(lines)+'\n')
 from render_readme import render_readme
 render_readme(ROOT)
 print(f'ingest: {len(entries)} entries from {SOURCE_ID}@{commit}')
if __name__=='__main__':main()

