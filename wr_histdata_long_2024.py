#!/usr/bin/env python3
from __future__ import annotations
import csv, io, json, math, os, sys, time, zipfile, importlib.util
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# PREDECLARED before opening results.
START=datetime(2024,1,1,tzinfo=timezone.utc)
END=datetime(2025,1,1,tzinfo=timezone.utc)
PAIRS={
 'forex':['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'],
 'metal':['XAUUSD','XAGUSD'],
 'index':['SPXUSD','NSXUSD'],
}
TF=(3,5,10)

# Reuse the already-frozen Python replication of WR v2.5.13 core/lifecycle.
engine=os.environ.get('WR_ENGINE','/tmp/runner3/formal-tests/wr_cross_asset_screen.py')
spec=importlib.util.spec_from_file_location('wr_engine',engine)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.START=START; m.END=END

# HistData M1 is fixed EST (UTC-5), explicitly without DST.
FIXED_EST=timezone(timedelta(hours=-5))

def hist_download(pair,year=2024,outdir='/tmp/histdata'):
    os.makedirs(outdir,exist_ok=True)
    fn=os.path.join(outdir,f'DAT_ASCII_{pair}_M1_{year}.zip')
    if os.path.exists(fn) and zipfile.is_zipfile(fn): return fn
    ref=f'https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{pair.lower()}/{year}'
    s=requests.Session()
    r=s.get(ref,timeout=45); r.raise_for_status()
    soup=BeautifulSoup(r.content,'html.parser'); el=soup.find('input',{'id':'tk'})
    if not el: raise RuntimeError(f'NO_TOKEN {pair} {year}')
    data={'tk':el.attrs['value'],'date':str(year),'datemonth':str(year),'platform':'ASCII','timeframe':'M1','fxpair':pair}
    hdr={'Referer':ref,'Origin':'https://www.histdata.com','Content-Type':'application/x-www-form-urlencoded'}
    z=s.post('https://www.histdata.com/get.php',data=data,headers=hdr,timeout=180)
    z.raise_for_status(); open(fn,'wb').write(z.content)
    if not zipfile.is_zipfile(fn):
        raise RuntimeError(f'NOT_ZIP {pair} bytes={len(z.content)} head={z.text[:100]!r}')
    return fn

def load_m1(zpath):
    rows=[]
    with zipfile.ZipFile(zpath) as z:
        names=[n for n in z.namelist() if n.lower().endswith(('.csv','.txt'))]
        if not names: raise RuntimeError(f'NO_CSV {zpath} {z.namelist()}')
        with z.open(names[0]) as f:
            txt=io.TextIOWrapper(f,encoding='utf-8',errors='replace',newline='')
            for line in txt:
                p=line.strip().replace(',',';').split(';')
                if len(p)<5: continue
                try:
                    dt=datetime.strptime(p[0].strip(),'%Y%m%d %H%M%S').replace(tzinfo=FIXED_EST).astimezone(timezone.utc)
                    o,h,l,c=map(float,p[1:5])
                except Exception: continue
                rows.append((int(dt.timestamp()),o,h,l,c))
    rows.sort(key=lambda x:x[0]); return rows

def aggregate(rows,tf):
    sec=tf*60; buckets={}
    for ts,o,h,l,c in rows:
        k=(ts//sec)*sec; buckets.setdefault(k,[]).append((ts,o,h,l,c))
    out=[]
    for k in sorted(buckets):
        z=sorted(buckets[k])
        # Require every underlying M1 bar and exact minute continuity: no synthetic gap fill.
        if len(z)!=tf: continue
        if any(z[i+1][0]-z[i][0]!=60 for i in range(len(z)-1)): continue
        if z[0][0]!=k: continue
        out.append(m.Bar(k,tf,z[0][1],max(x[2] for x in z),min(x[3] for x in z),z[-1][4]))
    return out

def tick_for(pair):
    if pair.endswith('JPY'): return .001
    if pair in ('XAUUSD','XAGUSD'): return .001 if pair=='XAUUSD' else .00001
    if pair in ('SPXUSD','NSXUSD'): return .1
    return .00001

def stats(ts):
    return m.summarize(ts)

def block_stats(trades):
    # Calendar quarter blocks, predeclared. Attribution by signal candle.
    qs={f'2024Q{i}':[] for i in range(1,5)}
    for t in trades:
        d=datetime.fromtimestamp(t['signal']/1000,timezone.utc)
        q=(d.month-1)//3+1; qs[f'2024Q{q}'].append(t)
    return {k:stats(v) for k,v in qs.items()}

def month_stats(trades):
    ms={f'2024-{i:02d}':[] for i in range(1,13)}
    for t in trades:
        d=datetime.fromtimestamp(t['signal']/1000,timezone.utc); ms[f'{d.year}-{d.month:02d}'].append(t)
    return {k:stats(v) for k,v in ms.items()}

def main():
    result={'schema':'wr-histdata-long-2024-v1','status':'INDEPENDENT_HISTORICAL_VALIDATION_2024','strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication','window':{'start':START.isoformat(),'end_exclusive':END.isoformat()},'holdout_policy':'2025 deliberately NOT opened by this run','source':{'provider':'HistData','format':'Generic ASCII M1 bid OHLC','timezone':'fixed EST UTC-5 without DST','aggregation':'strict contiguous M1 -> 3m/5m/10m; no gap fill'},'notes':['Gross R; no spread/slippage/commission deduction.','Embedded-news guard is NOT represented in the Python replication; this validates structural core/lifecycle, not news-calendar filtering.','24h session proxy uses fixed EST daily close 17:00, consistent with 22:00 UTC daily boundary; bars are treated as in-market when present.','SPXUSD/NSXUSD are HistData index feeds and can differ from a CFD broker or CME futures.'],'groups':{},'errors':[]}
    for group,pairs in PAIRS.items():
        cells=[]; alltr=[]
        print('\nGROUP',group,flush=True)
        for pair in pairs:
            try:
                zp=hist_download(pair); m1=load_m1(zp)
                print(pair,'M1',len(m1),'from',datetime.fromtimestamp(m1[0][0],timezone.utc),'to',datetime.fromtimestamp(m1[-1][0],timezone.utc),flush=True)
                meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':group}
                tick=tick_for(pair)
                for tf in TF:
                    bars=aggregate(m1,tf); tr=m.run(tf,bars,meta,tick)
                    for x in tr: x['symbol']=pair
                    alltr.extend(tr); sm=stats(tr)
                    cells.append({'symbol':pair,'tf':tf,'m1_rows':len(m1),'bars':len(bars),**sm,'quarters':block_stats(tr),'months':month_stats(tr)})
                    print(pair,tf,'bars',len(bars),'trades',sm['n'],'avgR',sm['avg_r'],'CI',sm['ci95_avg_r'],flush=True)
            except Exception as e:
                result['errors'].append({'group':group,'symbol':pair,'error':repr(e)}); print('ERROR',pair,repr(e),flush=True)
            time.sleep(.4)
        tfout={}
        for tf in TF:
            tr=[x for x in alltr if x['tf']==tf]
            cs=[x for x in cells if x['tf']==tf]
            tfout[str(tf)]={'pooled':stats(tr),'positive_cells':sum((x['avg_r'] or 0)>0 for x in cs if x['n']>0),'negative_cells':sum((x['avg_r'] or 0)<0 for x in cs if x['n']>0),'cells_with_trade':sum(x['n']>0 for x in cs),'quarters':block_stats(tr),'months':month_stats(tr)}
        result['groups'][group]={'cells':cells,'timeframes':tfout}
    with open('wr_histdata_long_2024.json','w') as f: json.dump(result,f,indent=2)
    print('\n=== SUMMARY ===')
    for g,z in result['groups'].items():
        print(g)
        for tf,x in z['timeframes'].items():
            p=x['pooled']; print(tf,'N',p['n'],'avgR',p['avg_r'],'PF',p['pf_r'],'CI',p['ci95_avg_r'],'cells+',x['positive_cells'],'/',x['cells_with_trade'])
    print('ERRORS',result['errors'])
if __name__=='__main__': main()
