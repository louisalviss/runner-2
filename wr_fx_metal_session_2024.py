#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# PREDECLARED hypothesis test: keep Wave Rider v2.5.13 unchanged and only
# classify already-generated trades by economically meaningful market sessions.
BASE='/tmp/runner2/wr_histdata_long_2024.py' if os.path.exists('/tmp/runner2/wr_histdata_long_2024.py') else 'wr_histdata_long_2024.py'
spec=importlib.util.spec_from_file_location('base2024', BASE)
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

PAIRS={
    'forex':['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'],
    'metal':['XAUUSD','XAGUSD'],
}
TFS=(3,5)
SESSIONS=('ASIA','LONDON_ONLY','LONDON_NY_OVERLAP','NY_ONLY','OFF_SESSION')
TZ_TOKYO=ZoneInfo('Asia/Tokyo')
TZ_LONDON=ZoneInfo('Europe/London')
TZ_NY=ZoneInfo('America/New_York')

def in_local_window(dt_utc, tz, sh, eh):
    x=dt_utc.astimezone(tz)
    m=x.hour*60+x.minute
    return sh*60 <= m < eh*60

def session_of(signal_ms):
    d=datetime.fromtimestamp(signal_ms/1000, timezone.utc)
    asia=in_local_window(d,TZ_TOKYO,9,16)
    london=in_local_window(d,TZ_LONDON,8,16)
    ny=in_local_window(d,TZ_NY,8,17)
    if london and ny: return 'LONDON_NY_OVERLAP'
    if london: return 'LONDON_ONLY'
    if ny: return 'NY_ONLY'
    if asia: return 'ASIA'
    return 'OFF_SESSION'

def quarter_of(signal_ms):
    d=datetime.fromtimestamp(signal_ms/1000,timezone.utc)
    return f"2024Q{(d.month-1)//3+1}"

def main():
    out={
      'schema':'wr-fx-metal-session-2024-v1',
      'status':'PREDECLARED_SESSION_BREAKDOWN',
      'strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication',
      'window':{'start':b.START.isoformat(),'end_exclusive':b.END.isoformat()},
      'pairs':PAIRS,'timeframes':list(TFS),
      'session_definition':{
        'ASIA':'Tokyo 09:00-16:00 local, only when neither London nor NY is active',
        'LONDON_ONLY':'London 08:00-16:00 local while NY 08:00-17:00 local is inactive',
        'LONDON_NY_OVERLAP':'London and New York windows simultaneously active',
        'NY_ONLY':'New York 08:00-17:00 local while London is inactive',
        'OFF_SESSION':'all remaining times; includes rollover/thin periods',
        'dst':'Europe/London and America/New_York handled by IANA zoneinfo; Tokyo has no DST',
        'attribution':'session of signal candle close, not exit time',
      },
      'notes':[
        'No Wave Rider parameter changed; this is a post-stratification of the frozen 2024 run protocol.',
        'Gross R only; spread/slippage/commission are not deducted.',
        'Embedded-news guard is not reconstructed, matching the parent 2024 structural validation limitation.',
        'Session analysis is hypothesis-driven but still uses 2024 already seen at aggregate level; positive findings require later independent-year confirmation.'
      ],
      'groups':{},'errors':[]
    }
    for group,pairs in PAIRS.items():
        group_tr=[]; cells=[]
        print('\nGROUP',group,flush=True)
        for pair in pairs:
            try:
                zp=b.hist_download(pair,2024); m1=b.load_m1(zp)
                meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':group}
                tick=b.tick_for(pair)
                for tf in TFS:
                    bars=b.aggregate(m1,tf)
                    tr=b.m.run(tf,bars,meta,tick)
                    for t in tr:
                        t['symbol']=pair; t['session_bucket']=session_of(t['signal']); t['quarter']=quarter_of(t['signal'])
                    group_tr.extend(tr)
                    for sess in SESSIONS:
                        st=[t for t in tr if t['session_bucket']==sess]
                        qs={q:b.stats([t for t in st if t['quarter']==q]) for q in ('2024Q1','2024Q2','2024Q3','2024Q4')}
                        cells.append({'symbol':pair,'tf':tf,'session':sess,**b.stats(st),'quarters':qs})
                    print(pair,tf,'trades',len(tr),flush=True)
            except Exception as e:
                out['errors'].append({'group':group,'symbol':pair,'error':repr(e)}); print('ERROR',pair,repr(e),flush=True)
        by_tf={}
        for tf in TFS:
            by_sess={}
            for sess in SESSIONS:
                tr=[t for t in group_tr if t['tf']==tf and t['session_bucket']==sess]
                symstats={p:b.stats([t for t in tr if t['symbol']==p]) for p in pairs}
                qs={q:b.stats([t for t in tr if t['quarter']==q]) for q in ('2024Q1','2024Q2','2024Q3','2024Q4')}
                nonempty=[v for v in symstats.values() if v['n']>0]
                by_sess[sess]={
                    'pooled':b.stats(tr),
                    'symbols':symstats,
                    'positive_symbols':sum((v['avg_r'] or 0)>0 for v in nonempty),
                    'negative_symbols':sum((v['avg_r'] or 0)<0 for v in nonempty),
                    'symbols_with_trade':len(nonempty),
                    'quarters':qs,
                    'positive_quarters':sum((v['avg_r'] or 0)>0 for v in qs.values() if v['n']>0),
                    'quarters_with_trade':sum(v['n']>0 for v in qs.values()),
                }
            by_tf[str(tf)]=by_sess
        out['groups'][group]={'cells':cells,'timeframes':by_tf}
    with open('wr_fx_metal_session_2024.json','w') as f: json.dump(out,f,indent=2)
    print('\n=== SESSION SUMMARY ===')
    for g,z in out['groups'].items():
        print('\n',g)
        for tf,smap in z['timeframes'].items():
            print(' TF',tf)
            for s,x in smap.items():
                p=x['pooled']; print(s,'N',p['n'],'AvgR',p['avg_r'],'PF',p['pf_r'],'CI',p['ci95_avg_r'],'sym+',x['positive_symbols'],'/',x['symbols_with_trade'],'q+',x['positive_quarters'],'/',x['quarters_with_trade'])
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
