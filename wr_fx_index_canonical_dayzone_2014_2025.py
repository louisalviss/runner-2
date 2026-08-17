#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, os, re, statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

# Frozen diagnostic. No WR core parameter is changed.
YEARS=tuple(range(2014,2026))
TF=5
GROUPS={
  'forex':['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'],
  'index':['SPXUSD','NSXUSD'],
}
ON_OFFSETS={-2,-1,0,2,3}
TZ_VN=ZoneInfo('Asia/Ho_Chi_Minh')
TZ_NY=ZoneInfo('America/New_York')
ANCHOR_HOUR=8
NEWS_GUARD_MIN=15
UA={'User-Agent':'Mozilla/5.0 WaveRiderResearch/1.0'}

BASE='wr_histdata_long_2024.py'
spec=importlib.util.spec_from_file_location('base',BASE)
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

MONTHS={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}

def trading_day_key_ms(ms:int, anchor_hour:int=ANCHOR_HOUR)->date:
    d=datetime.fromtimestamp(ms/1000,timezone.utc).astimezone(TZ_VN)
    k=d.date()
    if (d.hour,d.minute) < (anchor_hour,0): k-=timedelta(days=1)
    return k

def trading_day_key_dt(d:datetime, anchor_hour:int=ANCHOR_HOUR)->date:
    x=d.astimezone(TZ_VN); k=x.date()
    if (x.hour,x.minute) < (anchor_hour,0): k-=timedelta(days=1)
    return k

def fetch_bls(year:int):
    url=f'https://www.bls.gov/schedule/{year}/home.htm'
    r=requests.get(url,headers=UA,timeout=45); r.raise_for_status()
    soup=BeautifulSoup(r.content,'html.parser')
    ev=[]
    for tr in soup.find_all('tr'):
        td=[x.get_text(' ',strip=True) for x in tr.find_all(['td','th'])]
        if len(td)<3: continue
        ds,ts,rel=td[0],td[1],td[2]
        typ='CPI' if 'Consumer Price Index' in rel else ('NFP' if 'Employment Situation' in rel else None)
        if not typ: continue
        try:
            d=datetime.strptime(ds,'%A, %B %d, %Y')
            tt=datetime.strptime(ts.strip(),'%I:%M %p').time()
        except Exception:
            continue
        local=datetime(d.year,d.month,d.day,tt.hour,tt.minute,tzinfo=TZ_NY)
        ev.append({'type':typ,'dt':local.astimezone(timezone.utc),'source':url,'title':rel})
    return ev

def fetch_fomc_historical(year:int):
    url=f'https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm'
    r=requests.get(url,headers=UA,timeout=45); r.raise_for_status()
    soup=BeautifulSoup(r.content,'html.parser'); ev=[]
    pat=re.compile(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:-(\d{1,2}))?\s+Meeting\s+-\s+'+str(year)+r'$')
    for h in soup.find_all(['h4','h5','h6']):
        txt=' '.join(h.get_text(' ',strip=True).split())
        if 'unscheduled' in txt.lower(): continue
        m=pat.match(txt)
        if not m: continue
        mon=MONTHS[m.group(1)]; day=int(m.group(3) or m.group(2))
        local=datetime(year,mon,day,14,0,tzinfo=TZ_NY)
        ev.append({'type':'FOMC','dt':local.astimezone(timezone.utc),'source':url,'title':txt})
    return ev

def fetch_fomc_recent(year:int):
    url='https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
    r=requests.get(url,headers=UA,timeout=45); r.raise_for_status()
    text=BeautifulSoup(r.content,'html.parser').get_text('\n',strip=True)
    marker=f'{year} FOMC Meetings'
    i=text.find(marker)
    if i<0: raise RuntimeError(f'FOMC_RECENT_SECTION_NOT_FOUND {year}')
    ends=[]
    for y in range(2021,2028):
        if y==year: continue
        j=text.find(f'{y} FOMC Meetings',i+len(marker))
        if j>=0: ends.append(j)
    sec=text[i:min(ends) if ends else len(text)]
    lines=[x.strip() for x in sec.splitlines() if x.strip()]
    month_tokens={'January','February','March','April','May','June','July','August','September','October','November','December','Jan/Feb','Apr/May'}
    ev=[]
    for idx,x in enumerate(lines[:-1]):
        if x not in month_tokens: continue
        ds=lines[idx+1].replace('*','').strip()
        m=re.fullmatch(r'(\d{1,2})(?:-(\d{1,2}))?',ds)
        if not m: continue
        months=x.split('/')
        mon=MONTHS[months[-1]] if len(months)>1 else MONTHS[x]
        day=int(m.group(2) or m.group(1))
        local=datetime(year,mon,day,14,0,tzinfo=TZ_NY)
        ev.append({'type':'FOMC','dt':local.astimezone(timezone.utc),'source':url,'title':f'{x} {ds} FOMC Meeting'})
    # de-duplicate because page text can repeat navigation fragments
    z={e['dt'].isoformat():e for e in ev}
    return list(z.values())

def calendar(years):
    all_ev=[]; audit={}
    for y in years:
        e=fetch_bls(y)
        e+=fetch_fomc_historical(y) if y<=2020 else fetch_fomc_recent(y)
        e=sorted(e,key=lambda x:x['dt'])
        counts={k:sum(x['type']==k for x in e) for k in ('CPI','NFP','FOMC')}
        # Hard fail rather than silently run with a broken calendar.
        if not (11<=counts['CPI']<=13 and 11<=counts['NFP']<=13 and 6<=counts['FOMC']<=9):
            raise RuntimeError(f'CALENDAR_AUDIT_FAIL {y} {counts}')
        audit[str(y)]={'counts':counts,'events':[{'type':x['type'],'utc':x['dt'].isoformat(),'vn':x['dt'].astimezone(TZ_VN).isoformat(),'trading_day':str(trading_day_key_dt(x['dt'])),'title':x['title'],'source':x['source']} for x in e]}
        all_ev+=e
    return sorted(all_ev,key=lambda x:x['dt']),audit

def zone_of(ms:int):
    d=datetime.fromtimestamp(ms/1000,timezone.utc).astimezone(TZ_VN)
    m=d.hour*60+d.minute
    if 2*60 <= m < 8*60: return 'A'
    if 16*60 <= m < 19*60: return 'B'
    if m>=23*60 or m<2*60: return 'C'
    return 'OFF'

def labels_for_day(k:date,event_days:list[date]):
    offs=sorted({(k-e).days for e in event_days if -4 <= (k-e).days <= 4})
    # Canonical precedence: fresh T0 overrides; otherwise T+1 is OFF.
    if 0 in offs: primary='T0'; on=True
    elif 1 in offs: primary='T+1'; on=False
    else:
        allowed=[d for d in offs if d in ON_OFFSETS]
        on=bool(allowed)
        if allowed:
            # deterministic reporting only; ON/OFF is unchanged if multiple allowed labels overlap
            rank={-1:0,-2:1,2:2,3:3}
            d=sorted(allowed,key=lambda q:(abs(q),rank.get(q,9)))[0]
            primary=f'T{d:+d}'
        else: primary='OFF'
    return primary,on,offs

def same_td_prior_event(signal_ms:int, events):
    k=trading_day_key_ms(signal_ms)
    s=datetime.fromtimestamp(signal_ms/1000,timezone.utc)
    return any(trading_day_key_dt(e['dt'])==k and e['dt']<s for e in events)

def news_guarded(t,events):
    pts=[t.get('signal'),t.get('entry')]
    for p in pts:
        if not p: continue
        d=datetime.fromtimestamp(p/1000,timezone.utc)
        if any(abs((d-e['dt']).total_seconds()) <= NEWS_GUARD_MIN*60 for e in events): return True
    return False

def annotate(t,events,event_days):
    x=dict(t)
    z=zone_of(t['signal']); k=trading_day_key_ms(t['signal'])
    lab,day_on,offs=labels_for_day(k,event_days)
    a_ok=(z!='A') or same_td_prior_event(t['signal'],events)
    guarded=news_guarded(t,events)
    x.update({'zone':z,'trading_day':str(k),'t_label':lab,'t_offsets':offs,'day_on':day_on,'zone_ok':z in ('A','B','C') and a_ok,'zone_a_event_ok':a_ok,'news_guarded':guarded})
    x['canonical_on']=x['day_on'] and x['zone_ok'] and not guarded
    return x

def stats(tr): return b.stats(tr)

def group_summary(trades,symbols):
    full=[t for t in trades if t['canonical_on']]
    by_year={}; by_zone={}; by_t={}; matrix={}
    for y in YEARS:
        z=[t for t in full if int(t['trading_day'][:4])==y]
        by_year[str(y)]=stats(z)
    for z in ('A','B','C'):
        q=[t for t in full if t['zone']==z]; by_zone[z]=stats(q)
    for lab in ('T-2','T-1','T0','T+1','T+2','T+3','OFF'):
        q=[t for t in trades if t['t_label']==lab and t['zone_ok'] and not t['news_guarded']]
        by_t[lab]=stats(q)
    for z in ('A','B','C'):
        matrix[z]={}
        for lab in ('T-2','T-1','T0','T+1','T+2','T+3'):
            q=[t for t in trades if t['zone']==z and t['t_label']==lab and t['zone_ok'] and not t['news_guarded']]
            matrix[z][lab]=stats(q)
    sym={s:stats([t for t in full if t['symbol']==s]) for s in symbols}
    non=[v for v in sym.values() if v['n']>0]
    return {
      'all_time_baseline':stats(trades),'canonical_full':stats(full),
      'retention':len(full)/len(trades) if trades else None,
      'symbols':sym,'positive_symbols':sum((v['avg_r'] or 0)>0 for v in non),'symbols_with_trade':len(non),
      'years':by_year,'positive_years':sum((v['avg_r'] or 0)>0 for v in by_year.values() if v['n']>0),'years_with_trade':sum(v['n']>0 for v in by_year.values()),
      'zones':by_zone,'t_labels':by_t,'zone_x_t':matrix,
      'guarded_count':sum(t['news_guarded'] for t in trades),
      'zone_a_ineligible_count':sum(t['zone']=='A' and not t['zone_ok'] for t in trades),
    }

def set_year(y):
    st=datetime(y,1,1,tzinfo=timezone.utc); en=datetime(y+1,1,1,tzinfo=timezone.utc)
    b.START=st; b.END=en; b.m.START=st; b.m.END=en


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--group',choices=GROUPS,required=True); args=ap.parse_args()
    group=args.group; symbols=GROUPS[group]
    events,audit=calendar(YEARS); event_days=sorted({trading_day_key_dt(e['dt']) for e in events})
    out={'schema':'wr-canonical-dayzone-fx-index-2014-2025-v1','status':'FROZEN_CANONICAL_T_DAY_ZONE_VALIDATION','strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication','group':group,'symbols':symbols,'tf':TF,'years':list(YEARS),'canonical':{'event_types':['CPI','NFP','FOMC'],'t_on':['T-2','T-1','T0','T+2','T+3'],'t_off':['T+1','T+4+ / outside event window'],'zone_A':'02:00-08:00 VN only after prior major event in same 08:00-anchored trading day','zone_B':'16:00-19:00 VN','zone_C':'23:00-02:00 VN','other_time':'OFF','trading_day_anchor':'08:00 Asia/Ho_Chi_Minh','news_guard':'15m pre / 15m post event','overlap_precedence':'T0 overrides; otherwise any T+1 state is OFF; remaining allowed overlaps are ON'},'source_notes':['HistData M1 bid OHLC; fixed EST UTC-5 source convention; strict contiguous aggregation.','FOMC scheduled policy-decision dates from Federal Reserve official pages; modeled at 14:00 America/New_York. Unscheduled emergency meetings are excluded.','CPI and Employment Situation dates/times are parsed from official BLS annual release calendars.','Gross R only; no spread/slippage/commission deduction in this run.'],'calendar_audit':audit,'errors':[]}
    alltr=[]
    for y in YEARS:
        set_year(y)
        for sym in symbols:
            try:
                m1=b.load_m1(b.hist_download(sym,y)); bars=b.aggregate(m1,TF)
                meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':group}; tick=b.tick_for(sym)
                tr=b.m.run(TF,bars,meta,tick)
                for t in tr:
                    t['symbol']=sym; t['year']=y
                    alltr.append(annotate(t,events,event_days))
                print(group,y,sym,'all',len(tr),'canonical',sum(x['canonical_on'] for x in alltr if x.get('year')==y and x.get('symbol')==sym),flush=True)
            except Exception as e:
                out['errors'].append({'year':y,'symbol':sym,'error':repr(e)}); print('ERROR',y,sym,repr(e),flush=True)
    out['summary']=group_summary(alltr,symbols)
    path=f'wr_{group}_canonical_dayzone_2014_2025.json'
    with open(path,'w') as f: json.dump(out,f,indent=2)
    s=out['summary']; print('\n===',group.upper(),'CANONICAL DAY×ZONE ===')
    print('BASE',s['all_time_baseline']); print('FULL',s['canonical_full'],'retention',s['retention'],'years+',s['positive_years'],'/',s['years_with_trade'],'symbols+',s['positive_symbols'],'/',s['symbols_with_trade'])
    print('ZONES',[(z,s['zones'][z]['n'],s['zones'][z]['avg_r']) for z in ('A','B','C')])
    print('T',[(q,s['t_labels'][q]['n'],s['t_labels'][q]['avg_r']) for q in ('T-2','T-1','T0','T+1','T+2','T+3')])
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
