#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
import requests

# Frozen diagnostic: canonical T-day x Zone on 5m only.
# 2014-2017 is deliberately NOT opened here; retain it as pristine holdout if discovery survives.
YEARS=tuple(range(2018,2026))
TF=5
GROUPS={
  'forex':['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'],
  'index':['SPXUSD','NSXUSD'],
}
ON_OFFSETS={-2,-1,0,2,3}
TZ_VN=ZoneInfo('Asia/Ho_Chi_Minh')
ANCHOR_HOUR=8
NEWS_GUARD_MIN=15
TV_CAL='https://economic-calendar.tradingview.com/events'
UA={'Origin':'https://www.tradingview.com','User-Agent':'Mozilla/5.0 WaveRiderResearch/1.0'}

spec=importlib.util.spec_from_file_location('base','wr_histdata_long_2024.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)


def trading_day_key_ms(ms:int)->date:
    d=datetime.fromtimestamp(ms/1000,timezone.utc).astimezone(TZ_VN); k=d.date()
    if (d.hour,d.minute)<(ANCHOR_HOUR,0): k-=timedelta(days=1)
    return k


def trading_day_key_dt(d:datetime)->date:
    x=d.astimezone(TZ_VN); k=x.date()
    if (x.hour,x.minute)<(ANCHOR_HOUR,0): k-=timedelta(days=1)
    return k


def iso_z(d:datetime):
    return d.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')


def fetch_tv_calendar(years):
    # TradingView used Inflation Rate YoY as the US CPI-release headline in older history;
    # from 2021 onward it also exposes CPI. Both are the same release timestamp, deduped below.
    wanted={'CPI':'CPI','Inflation Rate YoY':'CPI','Non Farm Payrolls':'NFP','Fed Interest Rate Decision':'FOMC'}
    raw=[]; start=datetime(min(years),1,1,tzinfo=timezone.utc); end=datetime(max(years)+1,1,1,tzinfo=timezone.utc); cur=start
    while cur<end:
        nxt=min(cur+timedelta(days=35),end)
        p={'from':iso_z(cur),'to':iso_z(nxt-timedelta(milliseconds=1)),'countries':'US'}
        r=requests.get(TV_CAL,params=p,headers=UA,timeout=45); r.raise_for_status(); payload=r.json()
        if payload.get('status') not in ('ok','success',None): raise RuntimeError(f'TV_CAL_STATUS {payload.get("status")}')
        raw.extend(payload.get('result',[])); cur=nxt
    selected={}
    for x in raw:
        typ=wanted.get(x.get('title')); ds=x.get('date')
        if not typ or not ds: continue
        dt=datetime.fromisoformat(ds.replace('Z','+00:00')).astimezone(timezone.utc)
        if dt.year not in years: continue
        key=(typ,dt.isoformat())
        # Prefer explicit CPI title over Inflation Rate YoY when both exist at same timestamp.
        prev=selected.get(key)
        if prev and prev['title']=='CPI': continue
        selected[key]={'type':typ,'dt':dt,'title':x.get('title'),'source':'TradingView Economic Calendar','source_detail':x.get('source'),'id':x.get('id'),'ticker':x.get('ticker')}
    events=sorted(selected.values(),key=lambda x:x['dt'])
    audit={}
    for y in years:
        e=[x for x in events if x['dt'].year==y]; counts={k:sum(x['type']==k for x in e) for k in ('CPI','NFP','FOMC')}
        # Actual releases can be delayed/omitted; hard-fail only for implausible coverage.
        if not (10<=counts['CPI']<=13 and 10<=counts['NFP']<=13 and 6<=counts['FOMC']<=12):
            raise RuntimeError(f'CALENDAR_AUDIT_FAIL {y} {counts}')
        audit[str(y)]={'counts':counts,'events':[{'type':x['type'],'utc':x['dt'].isoformat(),'vn':x['dt'].astimezone(TZ_VN).isoformat(),'trading_day':str(trading_day_key_dt(x['dt'])),'title':x['title'],'source_detail':x.get('source_detail'),'ticker':x.get('ticker')} for x in e]}
    expected_2024={('NFP','2024-01-05T13:30:00+00:00'),('CPI','2024-01-11T13:30:00+00:00'),('FOMC','2024-01-31T19:00:00+00:00')}
    actual={(x['type'],x['dt'].isoformat()) for x in events}; miss=expected_2024-actual
    if miss: raise RuntimeError(f'OFFICIAL_SPOT_AUDIT_FAIL missing={sorted(miss)}')
    return events,audit


def zone_of(ms:int):
    d=datetime.fromtimestamp(ms/1000,timezone.utc).astimezone(TZ_VN); m=d.hour*60+d.minute
    if 2*60<=m<8*60: return 'A'
    if 16*60<=m<19*60: return 'B'
    if m>=23*60 or m<2*60: return 'C'
    return 'OFF'


def labels_for_day(k:date,event_days:list[date]):
    offs=sorted({(k-e).days for e in event_days if -4<=(k-e).days<=4})
    if 0 in offs: return 'T0',True,offs
    if 1 in offs: return 'T+1',False,offs
    allowed=[d for d in offs if d in ON_OFFSETS]
    if not allowed: return 'OFF',False,offs
    rank={-1:0,-2:1,2:2,3:3}; d=sorted(allowed,key=lambda q:(abs(q),rank.get(q,9)))[0]
    return f'T{d:+d}',True,offs


def same_td_prior_event(signal_ms:int,events):
    k=trading_day_key_ms(signal_ms); s=datetime.fromtimestamp(signal_ms/1000,timezone.utc)
    return any(trading_day_key_dt(e['dt'])==k and e['dt']<s for e in events)


def news_guarded(t,events):
    for p in (t.get('signal'),t.get('entry')):
        if not p: continue
        d=datetime.fromtimestamp(p/1000,timezone.utc)
        if any(abs((d-e['dt']).total_seconds())<=NEWS_GUARD_MIN*60 for e in events): return True
    return False


def annotate(t,events,event_days):
    x=dict(t); z=zone_of(t['signal']); k=trading_day_key_ms(t['signal']); lab,day_on,offs=labels_for_day(k,event_days)
    a_ok=(z!='A') or same_td_prior_event(t['signal'],events); guarded=news_guarded(t,events); zone_ok=(z in ('A','B','C')) and a_ok
    x.update({'zone':z,'trading_day':str(k),'t_label':lab,'t_offsets':offs,'day_on':day_on,'zone_ok':zone_ok,'zone_a_event_ok':a_ok,'news_guarded':guarded,'canonical_on':day_on and zone_ok and not guarded})
    return x


def stats(tr): return b.stats(tr)


def group_summary(trades,symbols):
    full=[t for t in trades if t['canonical_on']]
    by_year={str(y):stats([t for t in full if t['year']==y]) for y in YEARS}
    by_zone={z:stats([t for t in full if t['zone']==z]) for z in ('A','B','C')}
    by_t={lab:stats([t for t in trades if t['t_label']==lab and t['zone_ok'] and not t['news_guarded']]) for lab in ('T-2','T-1','T0','T+1','T+2','T+3','OFF')}
    matrix={z:{lab:stats([t for t in trades if t['zone']==z and t['t_label']==lab and t['zone_ok'] and not t['news_guarded']]) for lab in ('T-2','T-1','T0','T+1','T+2','T+3')} for z in ('A','B','C')}
    sym={s:stats([t for t in full if t['symbol']==s]) for s in symbols}; non=[v for v in sym.values() if v['n']>0]
    return {'all_time_baseline':stats(trades),'canonical_full':stats(full),'pre2022':stats([t for t in full if t['year']<=2021]),'y2022_2025':stats([t for t in full if t['year']>=2022]),'retention':len(full)/len(trades) if trades else None,'symbols':sym,'positive_symbols':sum((v['avg_r'] or 0)>0 for v in non),'symbols_with_trade':len(non),'years':by_year,'positive_years':sum((v['avg_r'] or 0)>0 for v in by_year.values() if v['n']>0),'years_with_trade':sum(v['n']>0 for v in by_year.values()),'zones':by_zone,'t_labels':by_t,'zone_x_t':matrix,'guarded_count':sum(t['news_guarded'] for t in trades),'zone_a_ineligible_count':sum(t['zone']=='A' and not t['zone_ok'] for t in trades)}


def set_year(y):
    st=datetime(y,1,1,tzinfo=timezone.utc); en=datetime(y+1,1,1,tzinfo=timezone.utc); b.START=st; b.END=en; b.m.START=st; b.m.END=en


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--group',choices=GROUPS,required=True); args=ap.parse_args(); group=args.group; symbols=GROUPS[group]
    events,audit=fetch_tv_calendar(YEARS); event_days=sorted({trading_day_key_dt(e['dt']) for e in events})
    out={'schema':'wr-canonical-dayzone-fx-index-2018-2025-v3','status':'FROZEN_CANONICAL_T_DAY_ZONE_DISCOVERY','strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication','group':group,'symbols':symbols,'tf':TF,'years':list(YEARS),'untouched_holdout':'2014-2017 deliberately unopened in this path','canonical':{'event_types':['CPI release','Non Farm Payrolls','Fed Interest Rate Decision'],'t_on':['T-2','T-1','T0','T+2','T+3'],'t_off':['T+1','T+4+ / outside event window'],'zone_A':'02:00-08:00 VN only after prior major event in same 08:00-anchored trading day','zone_B':'16:00-19:00 VN','zone_C':'23:00-02:00 VN','other_time':'OFF','trading_day_anchor':'08:00 Asia/Ho_Chi_Minh','news_guard':'±15m around major event','overlap_precedence':'T0 overrides; otherwise any T+1 state is OFF; remaining allowed overlaps are ON'},'calendar':{'machine_source':'TradingView Economic Calendar historical endpoint','normalization':'CPI and Inflation Rate YoY at same BLS release timestamp are one CPI anchor','official_spot_audit':'2024 NFP/CPI/FOMC January anchor dates cross-checked against BLS/Federal Reserve','audit':audit},'source_notes':['HistData M1 bid OHLC; fixed EST UTC-5 source convention; strict contiguous aggregation.','Gross R only; no spread/slippage/commission deduction.','Fed Interest Rate Decision includes extraordinary decisions if present.'],'errors':[]}
    alltr=[]
    for y in YEARS:
        set_year(y)
        for sym in symbols:
            try:
                m1=b.load_m1(b.hist_download(sym,y)); bars=b.aggregate(m1,TF); meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':group}; tick=b.tick_for(sym); tr=b.m.run(TF,bars,meta,tick); ann=[]
                for t in tr:
                    t['symbol']=sym; t['year']=y; a=annotate(t,events,event_days); ann.append(a); alltr.append(a)
                print(group,y,sym,'all',len(tr),'canonical',sum(x['canonical_on'] for x in ann),flush=True)
            except Exception as e:
                out['errors'].append({'year':y,'symbol':sym,'error':repr(e)}); print('ERROR',y,sym,repr(e),flush=True)
    out['summary']=group_summary(alltr,symbols); path=f'wr_{group}_canonical_dayzone_2018_2025.json'; json.dump(out,open(path,'w'),indent=2)
    s=out['summary']; print('\n===',group.upper(),'CANONICAL T×ZONE 2018-2025 ==='); print('BASE',s['all_time_baseline']); print('FULL',s['canonical_full'],'retention',s['retention'],'years+',s['positive_years'],'/',s['years_with_trade'],'symbols+',s['positive_symbols'],'/',s['symbols_with_trade']); print('PRE22',s['pre2022']); print('2022_25',s['y2022_2025']); print('ZONES',[(z,s['zones'][z]['n'],s['zones'][z]['avg_r']) for z in ('A','B','C')]); print('T',[(q,s['t_labels'][q]['n'],s['t_labels'][q]['avg_r']) for q in ('T-2','T-1','T0','T+1','T+2','T+3')]); print('ERRORS',out['errors'])

if __name__=='__main__': main()
