#!/usr/bin/env python3
import hashlib,importlib.util,re,shutil,subprocess,sys,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
import ingest

def digest(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
def main():
 entries=ingest.parse_list(ROOT/'raw/2026-11-04/README.md'); pages={}; ids=set()
 for p in (ROOT/'wiki').glob('*.md'):
  f,b=ingest.split(p.read_text())
  if not f:continue
  assert f['type']=='entity' and f['uid'] not in ids; uuid.UUID(f['uid']);ids.add(f['uid'])
  assert f['status']=='unknown' and 'last_checked' not in f
  assert f['depth']=='stub' and len(f['summary'])<=160
  pages[f['source_key']]=(p,f)
 assert len(entries)==len(pages),(len(entries),len(pages))
 for e in entries:
  p,f=pages[e['source_key']]
  assert (f['title'],f['url'],f['category'],f['list_summary'])==(e['title'],e['url'],e['section'],e['summary'])
 seen=set();pending=[ROOT/'index.md']
 while pending:
  p=pending.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith('#'):continue
   q=(p.parent/target.split('#')[0]).resolve();assert q.is_relative_to(ROOT.resolve()) and q.exists(),q
   if q.suffix=='.md':pending.append(q)
 assert all(p.resolve() in seen for p,_ in pages.values())
 for line in (ROOT/'raw/MANIFEST.sha256').read_text().splitlines():
  expected,name=line.split('  ',1);assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
 with tempfile.TemporaryDirectory() as td:
  work=Path(td)/'kb';shutil.copytree(ROOT,work,ignore=shutil.ignore_patterns('__pycache__','.git'))
  cmd=[sys.executable,str(work/'tools/ingest.py'),'--date','2026-11-04'];before=digest(work);subprocess.run(cmd,check=True);assert before==digest(work),'ingest is not idempotent'
 print(f'PASS: {len(entries)} entries, UUIDs, source coverage, status/depth, links, checksums, idempotent ingest')
if __name__=='__main__':main()
