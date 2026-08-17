#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from datetime import datetime, timezone

# FROZEN on 2026-08-17 before opening 2022/2023 in this research path.
# Only the two strongest candidates surviving 2024 + 2025 are evaluated.
YEARS=(2022,2023)
FX_PAIRS=['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD']
COST_HAIRCUT_R=(0.0,0.025,0.05,0.075,0.10,0.15,0.20)

# Reuse frozen data/aggregation/session machinery.
spec=importlib.util.spec_from_file_location('s2024','wr_fx_metal_session_2024.py')
s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
b=s.b

HYPOTHESES={
  'SPX_5M_ALL_DAY': {
    'group':'index','pairs':['SPXUSD'],'tf':5,'session':None,
    'rationale':'SPXUSD 5m remained positive in both 2024 screen and 2025 pristine index holdout.'
  },
  'FX_5M_LONDON_NY_OVERLAP': {
    'group':'forex','pairs':FX_PAIRS,'tf':5,'session':'LONDON_NY_OVERLAP',
    'rationale':'Forex 5m London-NY overlap was positive in 2024 session analysis and replicated in 2025 confirmation.'
  },
}

def set_year(year):
    st=datetime(year,1,1,tzinfo=timezone.utc); en=datetime(year+1,1,1,tzinfo=timezone.utc)
    b.START=st; b.END=en; b.m.START=st; b.m.END=en
    return st,en

def quarter_of(ms,year):
    d=datetime.fromtimestamp(ms/1000,timezone.utc)
    return f'{year}Q{(d.month-1)//3+1}'

def haircut_stats(trades, haircut):
    z=[]
    for t in trades:
        x=dict(t); x['r']=float(t['r'])-haircut; z.append(x)
    return b.stats(z)

def main():
    out={
      'schema':'wr-core-candidates-2022-2023-v1',
      'status':'FROZEN_MULTIYEAR_CONFIRMATION',
      'strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication',
      'years':list(YEARS),
      'hypotheses':HYPOTHESES,
      'cost_haircut_r_per_trade':list(COST_HAIRCUT_R),
      'notes':[
        '2022 and 2023 were not opened in this research path before this frozen run.',
        'No alternative asset, timeframe, session, TP, EMA, CHOP, or S/R parameter is scanned.',
        'FX session attribution is identical to the prior DST-aware 2024/2025 definition.',
        'Cost haircut is a model-free stress test in R/trade, not a broker-specific spread/slippage estimate.',
        'Embedded-news guard is not reconstructed, matching prior structural validation limitation.',
        'HistData M1 bid OHLC is aggregated strictly; index/CFD broker feeds can differ.'
      ],
      'results':{},'errors':[]
    }
    cache={}
    for hname,h in HYPOTHESES.items():
        hall=[]; year_results={}
        print('\nHYP',hname,flush=True)
        for year in YEARS:
            set_year(year); yt=[]; by_symbol={}
            for pair in h['pairs']:
                try:
                    key=(pair,year)
                    if key not in cache:
                        cache[key]=b.load_m1(b.hist_download(pair,year))
                    bars=b.aggregate(cache[key],h['tf'])
                    meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':h['group']}
                    tick=b.tick_for(pair)
                    tr=b.m.run(h['tf'],bars,meta,tick)
                    keep=[]
                    for t in tr:
                        if h['session'] is None or s.session_of(t['signal'])==h['session']:
                            x=dict(t); x['symbol']=pair; x['year']=year; x['quarter']=quarter_of(t['signal'],year); keep.append(x)
                    yt.extend(keep); hall.extend(keep); by_symbol[pair]=b.stats(keep)
                    print(year,pair,'all',len(tr),'keep',len(keep),'avg',by_symbol[pair]['avg_r'],flush=True)
                except Exception as e:
                    out['errors'].append({'hypothesis':hname,'year':year,'symbol':pair,'error':repr(e)}); print('ERROR',hname,year,pair,repr(e),flush=True)
            quarters={f'{year}Q{i}':b.stats([t for t in yt if t['quarter']==f'{year}Q{i}']) for i in range(1,5)}
            nonempty=[v for v in by_symbol.values() if v['n']>0]
            year_results[str(year)]={
              'pooled':b.stats(yt),'symbols':by_symbol,
              'positive_symbols':sum((v['avg_r'] or 0)>0 for v in nonempty),
              'symbols_with_trade':len(nonempty),
              'quarters':quarters,
              'positive_quarters':sum((v['avg_r'] or 0)>0 for v in quarters.values() if v['n']>0),
              'quarters_with_trade':sum(v['n']>0 for v in quarters.values()),
              'cost_stress':{str(c):haircut_stats(yt,c) for c in COST_HAIRCUT_R},
            }
        by_year={str(y):b.stats([t for t in hall if t['year']==y]) for y in YEARS}
        out['results'][hname]={
          'years':year_results,
          'combined':b.stats(hall),
          'combined_cost_stress':{str(c):haircut_stats(hall,c) for c in COST_HAIRCUT_R},
          'positive_years':sum((v['avg_r'] or 0)>0 for v in by_year.values() if v['n']>0),
          'years_with_trade':sum(v['n']>0 for v in by_year.values()),
        }
    with open('wr_core_candidates_2022_2023.json','w') as f: json.dump(out,f,indent=2)
    print('\n=== MULTIYEAR CONFIRMATION ===')
    for name,x in out['results'].items():
        p=x['combined']; print(name,'N',p['n'],'TotR',p['total_r'],'AvgR',p['avg_r'],'PF',p['pf_r'],'CI',p['ci95_avg_r'],'years+',x['positive_years'],'/',x['years_with_trade'])
        for y,z in x['years'].items():
            q=z['pooled']; print(' ',y,'N',q['n'],'TotR',q['total_r'],'AvgR',q['avg_r'],'PF',q['pf_r'],'CI',q['ci95_avg_r'],'sym+',z['positive_symbols'],'/',z['symbols_with_trade'],'q+',z['positive_quarters'],'/',z['quarters_with_trade'])
        print(' cost stress:',[(c,round(v['avg_r'],4) if v['avg_r'] is not None else None,round(v['total_r'],2)) for c,v in x['combined_cost_stress'].items()])
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
