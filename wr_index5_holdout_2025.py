#!/usr/bin/env python3
from __future__ import annotations
import io, json, os, time, zipfile, importlib.util
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

# FROZEN after reviewing the 2024 long validation and BEFORE opening 2025.
START=datetime(2025,1,1,tzinfo=timezone.utc)
END=datetime(2026,1,1,tzinfo=timezone.utc)
PAIRS=['SPXUSD','NSXUSD']
TF=5

engine=os.environ.get('WR_ENGINE','/tmp/runner3/formal-tests/wr_cross_asset_screen.py')
spec=importlib.util.spec_from_file_location('wr_engine',engine)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.START=START; m.END=END
FIXED_EST=timezone(timedelta(hours=-5))

def hist_download(pair,year=2025,outdir='/tmp/histdata'):
    os.makedirs(outdir,exist_ok=True)
    fn=os.path.join(outdir,f'DAT_ASCII_{pair}_M1_{year}.zip')
    ref=f'https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{pair.lower()}/{year}'
    s=requests.Session(); r=s.get(ref,timeout=45); r.raise_for_status()
    soup=BeautifulSoup(r.content,'html.parser'); el=soup.find('input',{'id':'tk'})
    if not el: raise RuntimeError(f'NO_TOKEN {pair} {year}')
    data={'tk':el.attrs['value'],'date':str(year),'datemonth':str(year),'platform':'ASCII','timeframe':'M1','fxpair':pair}
    hdr={'Referer':ref,'Origin':'https://www.histdata.com','Content-Type':'application/x-www-form-urlencoded'}
    z=s.post('https://www.histdata.com/get.php',data=data,headers=hdr,timeout=180); z.raise_for_status()
    open(fn,'wb').write(z.content)
    if not zipfile.is_zipfile(fn): raise RuntimeError(f'NOT_ZIP {pair} bytes={len(z.content)}')
    return fn

def load_m1(zpath):
    rows=[]
    with zipfile.ZipFile(zpath) as z:
        names=[n for n in z.namelist() if n.lower().endswith(('.csv','.txt'))]
        if not names: raise RuntimeError(f'NO_CSV {zpath}')
        with z.open(names[0]) as f:
            txt=io.TextIOWrapper(f,encoding='utf-8',errors='replace')
            for line in txt:
                p=line.strip().replace(',',';').split(';')
                if len(p)<5: continue
                try:
                    dt=datetime.strptime(p[0].strip(),'%Y%m%d %H%M%S').replace(tzinfo=FIXED_EST).astimezone(timezone.utc)
                    o,h,l,c=map(float,p[1:5])
                except Exception: continue
                rows.append((int(dt.timestamp()),o,h,l,c))
    rows.sort(key=lambda x:x[0]); return rows

def aggregate(rows,tf=5):
    sec=tf*60; buckets={}
    for ts,o,h,l,c in rows:
        k=(ts//sec)*sec; buckets.setdefault(k,[]).append((ts,o,h,l,c))
    out=[]
    for k in sorted(buckets):
        z=sorted(buckets[k])
        if len(z)!=tf or z[0][0]!=k: continue
        if any(z[i+1][0]-z[i][0]!=60 for i in range(len(z)-1)): continue
        out.append(m.Bar(k,tf,z[0][1],max(x[2] for x in z),min(x[3] for x in z),z[-1][4]))
    return out

def stats(ts): return m.summarize(ts)

def period_stats(trades):
    qs={f'2025Q{i}':[] for i in range(1,5)}; ms={f'2025-{i:02d}':[] for i in range(1,13)}
    for t in trades:
        d=datetime.fromtimestamp(t['signal']/1000,timezone.utc); qs[f'2025Q{(d.month-1)//3+1}'].append(t); ms[f'2025-{d.month:02d}'].append(t)
    return {k:stats(v) for k,v in qs.items()},{k:stats(v) for k,v in ms.items()}

def main():
    result={'schema':'wr-index5-holdout-2025-v1','status':'PRISTINE_HOLDOUT_2025','hypothesis':'Index 5m broad family only, frozen from 2024 screen','strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication','window':{'start':START.isoformat(),'end_exclusive':END.isoformat()},'source':{'provider':'HistData','format':'Generic ASCII M1 bid OHLC','timezone':'fixed EST UTC-5 without DST','aggregation':'strict contiguous M1 -> 5m; no gap fill'},'notes':['Only SPXUSD and NSXUSD at 5m are tested. No other 2025 asset/timeframe is opened.','Gross R; no spread/slippage/commission deduction.','Embedded-news guard is not represented in the Python replication.','Index feeds can differ from CFD broker or CME futures.'],'cells':[],'pooled':None,'quarters':{},'months':{},'errors':[]}
    alltr=[]
    for pair in PAIRS:
        try:
            m1=load_m1(hist_download(pair)); bars=aggregate(m1,TF); meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':'index'}
            tr=m.run(TF,bars,meta,.1)
            for x in tr: x['symbol']=pair
            alltr.extend(tr); q,mo=period_stats(tr); sm=stats(tr)
            result['cells'].append({'symbol':pair,'tf':TF,'m1_rows':len(m1),'bars':len(bars),**sm,'quarters':q,'months':mo})
            print(pair,'M1',len(m1),'bars',len(bars),'N',sm['n'],'avgR',sm['avg_r'],'PF',sm['pf_r'],'CI',sm['ci95_avg_r'],flush=True)
        except Exception as e:
            result['errors'].append({'symbol':pair,'error':repr(e)}); print('ERROR',pair,repr(e),flush=True)
        time.sleep(.5)
    q,mo=period_stats(alltr); result['pooled']=stats(alltr); result['quarters']=q; result['months']=mo
    with open('wr_index5_holdout_2025.json','w') as f: json.dump(result,f,indent=2)
    print('POOLED',result['pooled']); print('ERRORS',result['errors'])
if __name__=='__main__': main()
