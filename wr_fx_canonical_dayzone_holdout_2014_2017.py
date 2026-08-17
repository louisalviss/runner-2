#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from datetime import datetime, timezone

# PRISTINE HOLDOUT: frozen after 2018-2025 full canonical T-day x Zone discovery.
# No rule, pair, timeframe, or Wave Rider parameter is changed.
YEARS=tuple(range(2014,2018))
SYMBOLS=['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD']
TF=5

spec=importlib.util.spec_from_file_location('main','wr_fx_index_canonical_dayzone_2014_2025.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.YEARS=YEARS
b=m.b

def set_year(y):
    st=datetime(y,1,1,tzinfo=timezone.utc); en=datetime(y+1,1,1,tzinfo=timezone.utc)
    b.START=st; b.END=en; b.m.START=st; b.m.END=en

def main():
    events,audit=m.fetch_tv_calendar(YEARS)
    event_days=sorted({m.trading_day_key_dt(e['dt']) for e in events})
    out={
      'schema':'wr-fx-canonical-dayzone-holdout-2014-2017-v1',
      'status':'PRISTINE_HOLDOUT',
      'frozen_from':'2018-2025 full canonical T-day x Zone discovery',
      'strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication',
      'tf':TF,'symbols':SYMBOLS,'years':list(YEARS),
      'canonical':{
        'event_types':['CPI release','Non Farm Payrolls','Fed Interest Rate Decision'],
        't_on':['T-2','T-1','T0','T+2','T+3'],'t_off':['T+1','outside event window'],
        'zone_A':'02:00-08:00 VN only after prior event in same 08:00-anchored trading day',
        'zone_B':'16:00-19:00 VN','zone_C':'23:00-02:00 VN','other_time':'OFF',
        'news_guard':'±15m','overlap_precedence':'T0 overrides; otherwise any T+1 state OFF'
      },
      'calendar_audit':audit,'errors':[]
    }
    alltr=[]
    for y in YEARS:
        set_year(y)
        for sym in SYMBOLS:
            try:
                m1=b.load_m1(b.hist_download(sym,y)); bars=b.aggregate(m1,TF)
                meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':'forex'}; tick=b.tick_for(sym)
                tr=b.m.run(TF,bars,meta,tick); ann=[]
                for t in tr:
                    t['symbol']=sym; t['year']=y
                    a=m.annotate(t,events,event_days); ann.append(a); alltr.append(a)
                print(y,sym,'all',len(tr),'canonical',sum(x['canonical_on'] for x in ann),flush=True)
            except Exception as e:
                out['errors'].append({'year':y,'symbol':sym,'error':repr(e)}); print('ERROR',y,sym,repr(e),flush=True)
    out['summary']=m.group_summary(alltr,SYMBOLS)
    json.dump(out,open('wr_fx_canonical_dayzone_holdout_2014_2017.json','w'),indent=2)
    s=out['summary']
    print('\n=== PRISTINE FX CANONICAL HOLDOUT 2014-2017 ===')
    print('BASE',s['all_time_baseline'])
    print('FULL',s['canonical_full'],'years+',s['positive_years'],'/',s['years_with_trade'],'symbols+',s['positive_symbols'],'/',s['symbols_with_trade'])
    print('ZONES',[(z,s['zones'][z]['n'],s['zones'][z]['avg_r']) for z in ('A','B','C')])
    print('T',[(q,s['t_labels'][q]['n'],s['t_labels'][q]['avg_r']) for q in ('T-2','T-1','T0','T+1','T+2','T+3')])
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
