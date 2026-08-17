#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
import wr_fx_overlap_stage3_diag_2018_2025 as d
import wr_fx_overlap_4y_execution as w

# Pristine historical confirmation frozen after the 2018-2025 diagnostic.
# Test ONE discovered Stage3 rule only: FX 5m London-NY overlap signals whose
# side is opposite the sign of the previous 20 completed trading-day net move.
YEARS=(2014,2015,2016,2017)
PAIRS=w.PAIRS
TF=5
SESSION=w.SESSION
COSTS=(0.0,0.25,0.50)


def summarize(ts):
    z={'gross':w.stat(ts)}
    for c in COSTS[1:]: z[f'cost_{c}_pip']=w.pip_cost(ts,c)
    return z

def main():
    out={'schema':'wr-fx-overlap-countertrend-holdout-2014-2017-v1',
         'status':'PRISTINE_HISTORICAL_CONFIRMATION',
         'strategy':'Wave Rider v2.5.13 frozen; 7-major FX; 5m London-NY overlap',
         'rule':'Keep only signals opposite the sign of the previous 20 completed trading-day net move.',
         'years':list(YEARS),'pairs':PAIRS,'cost_grid_pips':list(COSTS),
         'notes':['2014-2017 was not opened in this research path before freezing this single-rule confirmation.',
                  'No alternative Stage3 feature, threshold, pair subset, TP, EMA, CHOP, S/R, or session is scanned.',
                  'Daily trend feature uses completed prior trading days only.',
                  'Instrumented runner is asserted trade-for-trade against the frozen original engine.',
                  'Embedded-news guard remains unreconstructed; HistData/feed caveats remain.'],
         'years_result':{},'pairs_result':{},'combined':{},'errors':[],'assertions':[]}
    alltr=[]
    for year in YEARS:
        w.set_year(year); yt=[]
        for pair in PAIRS:
            try:
                rows=w.b.load_m1(w.b.hist_download(pair,year))
                feat=d.daily_features(rows)
                bars=w.b.aggregate(rows,TF); meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':'forex'}; tick=w.b.tick_for(pair)
                base=w.m.run(TF,bars,meta,tick); det=w.run_detail(TF,bars,meta,tick); w.assert_same(base,det,pair,year)
                keep=[]
                for t in det:
                    if w.s.session_of(t['signal'])!=SESSION: continue
                    k=d.trading_day_key(int(t['signal']//1000)); f=feat.get(k)
                    if not f or not f['trend_sign']: continue
                    if int(t['side'])==int(f['trend_sign']): continue
                    x=dict(t); x['symbol']=pair; x['year']=year; keep.append(x)
                yt.extend(keep); alltr.extend(keep)
                out['assertions'].append({'year':year,'symbol':pair,'all_trades':len(base),'status':'MATCH'})
                print(year,pair,'countertrend',len(keep),'avg',w.stat(keep)['avg_r'],flush=True)
            except Exception as e:
                out['errors'].append({'year':year,'symbol':pair,'error':repr(e)}); print('ERROR',year,pair,repr(e),flush=True)
        out['years_result'][str(year)]=summarize(yt)
    for pair in PAIRS:
        pt=[t for t in alltr if t['symbol']==pair]
        out['pairs_result'][pair]={'summary':summarize(pt),'positive_years':sum((w.stat([t for t in pt if t['year']==y])['avg_r'] or 0)>0 for y in YEARS)}
    out['combined']=summarize(alltr)
    out['combined']['positive_years']=sum((out['years_result'][str(y)]['gross']['avg_r'] or 0)>0 for y in YEARS)
    with open('wr_fx_overlap_countertrend_holdout_2014_2017.json','w') as f: json.dump(out,f,indent=2)
    print('\n=== COUNTERTREND HOLDOUT ===')
    print('combined',out['combined'])
    for y,z in out['years_result'].items(): print(y,z['gross'],flush=True)
    print('pairs',{p:(z['summary']['gross']['n'],z['summary']['gross']['avg_r'],z['positive_years']) for p,z in out['pairs_result'].items()})
    print('ERRORS',out['errors'])

if __name__=='__main__': main()
