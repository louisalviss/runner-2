#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from datetime import datetime, timezone

# PREDECLARED after viewing only the 2024 session breakdown.
# 2025 FX/metal data had not been opened in this research path before this run.
START=datetime(2025,1,1,tzinfo=timezone.utc)
END=datetime(2026,1,1,tzinfo=timezone.utc)

spec=importlib.util.spec_from_file_location('s2024','wr_fx_metal_session_2024.py')
s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
b=s.b
b.START=START; b.END=END; b.m.START=START; b.m.END=END

HYPOTHESES={
  'FX_3M_ASIA': {'group':'forex','pairs':['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'],'tf':3,'session':'ASIA'},
  'FX_5M_LONDON_NY_OVERLAP': {'group':'forex','pairs':['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'],'tf':5,'session':'LONDON_NY_OVERLAP'},
  'METAL_3M_ASIA': {'group':'metal','pairs':['XAUUSD','XAGUSD'],'tf':3,'session':'ASIA'},
  'XAU_5M_LONDON_NY_OVERLAP': {'group':'metal','pairs':['XAUUSD'],'tf':5,'session':'LONDON_NY_OVERLAP'},
}

def q_of(ms):
    d=datetime.fromtimestamp(ms/1000,timezone.utc)
    return f"2025Q{(d.month-1)//3+1}"

def main():
    out={
      'schema':'wr-fx-metal-session-confirm-2025-v1',
      'status':'INDEPENDENT_YEAR_CONFIRMATION_OF_PREDECLARED_2024_SESSION_HYPOTHESES',
      'strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication',
      'window':{'start':START.isoformat(),'end_exclusive':END.isoformat()},
      'hypotheses':HYPOTHESES,
      'notes':[
        'Only four hypotheses selected from the completed 2024 session breakdown are evaluated.',
        'No scan across alternative sessions/timeframes is performed in 2025.',
        'Session definitions are identical to 2024 and DST-aware via IANA zoneinfo.',
        'Gross R only; spread/slippage/commission are not deducted.',
        'Embedded-news guard is not reconstructed, matching the parent structural validation limitation.'
      ],
      'results':{},'errors':[]
    }
    cache={}
    for name,h in HYPOTHESES.items():
        pooled=[]; by_symbol={}
        print('\nHYP',name,flush=True)
        for pair in h['pairs']:
            try:
                if pair not in cache:
                    zp=b.hist_download(pair,2025); cache[pair]=b.load_m1(zp)
                meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':h['group']}
                bars=b.aggregate(cache[pair],h['tf'])
                tr=b.m.run(h['tf'],bars,meta,b.tick_for(pair))
                keep=[]
                for t in tr:
                    sess=s.session_of(t['signal'])
                    if sess==h['session']:
                        t['symbol']=pair; t['quarter']=q_of(t['signal']); keep.append(t)
                pooled.extend(keep); by_symbol[pair]=b.stats(keep)
                print(pair,'all',len(tr),'kept',len(keep),'avg',by_symbol[pair]['avg_r'],flush=True)
            except Exception as e:
                out['errors'].append({'hypothesis':name,'symbol':pair,'error':repr(e)}); print('ERROR',pair,repr(e),flush=True)
        quarters={q:b.stats([t for t in pooled if t['quarter']==q]) for q in ('2025Q1','2025Q2','2025Q3','2025Q4')}
        nonempty=[v for v in by_symbol.values() if v['n']>0]
        out['results'][name]={
          'pooled':b.stats(pooled),'symbols':by_symbol,
          'positive_symbols':sum((v['avg_r'] or 0)>0 for v in nonempty),
          'symbols_with_trade':len(nonempty),
          'quarters':quarters,
          'positive_quarters':sum((v['avg_r'] or 0)>0 for v in quarters.values() if v['n']>0),
          'quarters_with_trade':sum(v['n']>0 for v in quarters.values()),
        }
    with open('wr_fx_metal_session_confirm_2025.json','w') as f: json.dump(out,f,indent=2)
    print('\n=== 2025 CONFIRMATION ===')
    for name,x in out['results'].items():
        p=x['pooled']; print(name,'N',p['n'],'TotR',p['total_r'],'AvgR',p['avg_r'],'PF',p['pf_r'],'CI',p['ci95_avg_r'],'sym+',x['positive_symbols'],'/',x['symbols_with_trade'],'q+',x['positive_quarters'],'/',x['quarters_with_trade'])
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
