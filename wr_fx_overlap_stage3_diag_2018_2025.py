#!/usr/bin/env python3
from __future__ import annotations
import json, math
from datetime import datetime, timezone
import wr_fx_overlap_4y_execution as w

# Exploratory Stage3 diagnostic, frozen before running. No WR parameter changes.
YEARS=tuple(range(2018,2026))
PAIRS=w.PAIRS
TF=5
SESSION=w.SESSION
LOOKBACK_DAYS=20
REGIME_HISTORY=252
MIN_REGIME_HISTORY=60
COST_PIPS=0.25


def trading_day_key(ts):
    # FX trading day boundary follows the parent fixed-EST 17:00 close = 22:00 UTC.
    return (int(ts)-22*3600)//86400

def daily_features(rows):
    d={}
    for ts,o,h,l,c in rows:
        k=trading_day_key(ts)
        if k not in d: d[k]=[ts,o,h,l,c]
        else:
            z=d[k]; z[2]=max(z[2],h); z[3]=min(z[3],l); z[4]=c
    keys=sorted(d); vals={}
    ers=[]; atrs=[]
    for i,k in enumerate(keys):
        if i<LOOKBACK_DAYS: continue
        prev=[d[keys[j]] for j in range(i-LOOKBACK_DAYS,i)]
        closes=[x[4] for x in prev]
        # Need the close immediately before the 20-day window for a true 20-step ER.
        if i-LOOKBACK_DAYS-1>=0:
            c0=d[keys[i-LOOKBACK_DAYS-1]][4]
            seq=[c0]+closes
            denom=sum(abs(seq[j]-seq[j-1]) for j in range(1,len(seq)))
            er=abs(seq[-1]-seq[0])/denom if denom>0 else 0.0
            trend_sign=1 if seq[-1]>seq[0] else (-1 if seq[-1]<seq[0] else 0)
        else:
            er=None; trend_sign=0
        lastc=closes[-1]
        atr=sum(x[2]-x[3] for x in prev)/len(prev)/lastc if lastc else None
        hist_er=[x for x in ers[-REGIME_HISTORY:] if x is not None]
        hist_atr=[x for x in atrs[-REGIME_HISTORY:] if x is not None]
        er_med=sorted(hist_er)[len(hist_er)//2] if len(hist_er)>=MIN_REGIME_HISTORY else None
        atr_med=sorted(hist_atr)[len(hist_atr)//2] if len(hist_atr)>=MIN_REGIME_HISTORY else None
        vals[k]={'er20':er,'atr20_pct':atr,'trend_sign':trend_sign,'er_hist_median':er_med,'atr_hist_median':atr_med,
                 'trend_high':None if er_med is None or er is None else er>=er_med,
                 'vol_high':None if atr_med is None or atr is None else atr>=atr_med}
        ers.append(er); atrs.append(atr)
    return vals

def stats(ts): return w.stat(sorted(ts,key=lambda x:(x['signal'],x['symbol'])))

def cost025(ts): return w.pip_cost(ts,COST_PIPS)

def summarize_group(ts):
    return {'gross':stats(ts),'cost_0p25_pip':cost025(ts) if ts else stats([])}

def main():
    out={'schema':'wr-fx-overlap-stage3-diag-2018-2025-v1','status':'EXPLORATORY_CAUSAL_REGIME_DIAGNOSTIC',
         'strategy':'Wave Rider v2.5.13 frozen; 7-major FX; 5m London-NY overlap',
         'years':list(YEARS),'features':{
           'ER20':'20 completed trading-day close-to-close efficiency ratio',
           'ATR20_PCT':'mean high-low range of previous 20 completed trading days divided by last close',
           'TREND_ALIGNMENT':'signal side equals sign of 20-day net daily price change',
           'HIGH_LOW_THRESHOLD':'causal per-symbol median of up to previous 252 daily regime observations; minimum 60'
         },'cost_stress_pips':COST_PIPS,
         'notes':['Exploratory Stage3 discovery only, not a new production rule.',
                  'All features use completed prior trading days only; no future outcome enters feature computation.',
                  'No TP/EMA/CHOP/SR/session threshold is changed.',
                  'A useful regime finding should have the same sign in 2018-2021 and 2022-2025 and preferably survive 0.25-pip cost stress.',
                  'Embedded-news guard remains unreconstructed; HistData/feed caveats remain.'],
         'groups':{},'by_year':{},'by_pair':{},'errors':[]}
    trades=[]; cache={}; feats={}
    for year in YEARS:
        w.set_year(year); yt=[]
        for pair in PAIRS:
            try:
                key=(pair,year)
                if key not in cache: cache[key]=w.b.load_m1(w.b.hist_download(pair,year))
                # Feature history from current annual file; early-year trades without sufficient history are left unclassified.
                feats[key]=daily_features(cache[key])
                bars=w.b.aggregate(cache[key],TF); meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':'forex'}; tick=w.b.tick_for(pair)
                base=w.m.run(TF,bars,meta,tick); det=w.run_detail(TF,bars,meta,tick); w.assert_same(base,det,pair,year)
                for t in det:
                    if w.s.session_of(t['signal'])!=SESSION: continue
                    x=dict(t); x['symbol']=pair; x['year']=year
                    ts_sec=int(t['signal']//1000); k=w.trading_day_key(ts_sec) if hasattr(w,'trading_day_key') else trading_day_key(ts_sec)
                    f=feats[key].get(k)
                    if not f: continue
                    x.update(f); x['aligned']=f['trend_sign']!=0 and int(t['side'])==int(f['trend_sign'])
                    x['era']='PRIOR_2018_2021' if year<=2021 else 'RECENT_2022_2025'
                    yt.append(x); trades.append(x)
                print(year,pair,'classified',sum(t['symbol']==pair for t in yt),flush=True)
            except Exception as e:
                out['errors'].append({'year':year,'symbol':pair,'error':repr(e)}); print('ERROR',year,pair,repr(e),flush=True)
        out['by_year'][str(year)]=summarize_group(yt)
    # Predetermined diagnostic groups.
    groups={
      'ALL_CLASSIFIED':trades,
      'ALIGNED':[t for t in trades if t['aligned']],
      'COUNTERTREND':[t for t in trades if not t['aligned']],
      'TREND_HIGH':[t for t in trades if t['trend_high'] is True],
      'TREND_LOW':[t for t in trades if t['trend_high'] is False],
      'VOL_HIGH':[t for t in trades if t['vol_high'] is True],
      'VOL_LOW':[t for t in trades if t['vol_high'] is False],
      'TREND_HIGH_ALIGNED':[t for t in trades if t['trend_high'] is True and t['aligned']],
      'TREND_LOW_ALIGNED':[t for t in trades if t['trend_high'] is False and t['aligned']],
      'HIGH_TREND_HIGH_VOL_ALIGNED':[t for t in trades if t['trend_high'] is True and t['vol_high'] is True and t['aligned']],
      'HIGH_TREND_LOW_VOL_ALIGNED':[t for t in trades if t['trend_high'] is True and t['vol_high'] is False and t['aligned']],
    }
    for name,z in groups.items():
        eras={era:summarize_group([t for t in z if t['era']==era]) for era in ('PRIOR_2018_2021','RECENT_2022_2025')}
        out['groups'][name]={'combined':summarize_group(z),'eras':eras}
    for pair in PAIRS:
        z=[t for t in trades if t['symbol']==pair]
        out['by_pair'][pair]={'all':summarize_group(z),'aligned':summarize_group([t for t in z if t['aligned']]),
                             'trend_high_aligned':summarize_group([t for t in z if t['trend_high'] is True and t['aligned']])}
    with open('wr_fx_overlap_stage3_diag_2018_2025.json','w') as f: json.dump(out,f,indent=2)
    print('\n=== STAGE3 DIAG ===')
    for name,x in out['groups'].items():
        c=x['combined']['gross']; a=x['eras']['PRIOR_2018_2021']['gross']; b=x['eras']['RECENT_2022_2025']['gross']; net=x['combined']['cost_0p25_pip']
        print(name,'N',c['n'],'gross',round(c['avg_r'],4) if c['avg_r'] is not None else None,'prior',round(a['avg_r'],4) if a['avg_r'] is not None else None,'recent',round(b['avg_r'],4) if b['avg_r'] is not None else None,'net25',round(net['avg_r'],4) if net.get('avg_r') is not None else None,flush=True)
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
