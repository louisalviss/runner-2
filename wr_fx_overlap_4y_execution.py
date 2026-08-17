#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from datetime import datetime, timezone

# FROZEN execution robustness test. No strategy thresholds are changed.
YEARS=(2022,2023,2024,2025)
PAIRS=['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD']
TF=5
SESSION='LONDON_NY_OVERLAP'
FIXED_R_HAIRCUTS=(0.0,0.025,0.05,0.075,0.10,0.15,0.20)
# Total adverse execution distance per trade, expressed in pips. This is a
# stress grid, not a broker-specific spread claim.
ALL_IN_PIP_COSTS=(0.25,0.50,0.75,1.00,1.50,2.00)

spec=importlib.util.spec_from_file_location('s2024','wr_fx_metal_session_2024.py')
s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
b=s.b
m=b.m

def set_year(year):
    st=datetime(year,1,1,tzinfo=timezone.utc); en=datetime(year+1,1,1,tzinfo=timezone.utc)
    b.START=st; b.END=en; m.START=st; m.END=en

def pip_size(pair): return 0.01 if pair.endswith('JPY') else 0.0001

def qtile(xs,q):
    if not xs: return None
    z=sorted(xs); p=(len(z)-1)*q; lo=int(math.floor(p)); hi=int(math.ceil(p))
    return z[lo] if lo==hi else z[lo]*(hi-p)+z[hi]*(p-lo)

def run_detail(tf,bars,meta,tick):
    # Mechanical copy of the frozen m.run, adding only side/risk metadata.
    if len(bars)<50: return []
    ind=m.calc_ind(bars); pending=None; pos=None; trades=[]
    st=int(m.START.timestamp()*1000); en=int(m.END.timestamp()*1000)
    def emit(pos,x,r,reason,amb):
        trades.append({'tf':tf,'signal':pos['sig'],'entry':pos['ent_t'],'exit':x.ct,
                       'r':r,'reason':reason,'ambiguous':amb,'side':pos['d'],
                       'entry_px':pos['e'],'stop_px':pos['s'],'risk_price':abs(pos['e']-pos['s'])})
    for i,x in enumerate(bars):
        if x.ct>=en: break
        closed=False
        if pos is not None:
            reason,px,amb=m.active_bracket(x,pos['d'],pos['s'],pos['t'])
            if reason:
                r=-1.0 if reason!='TP' else m.TP_R
                emit(pos,x,r,reason,amb); pos=None; closed=True
        if pos is None and pending is not None and i==pending['i']+1 and not closed:
            fill,reason,px,amb=m.entry_bracket(x,pending['d'],pending['e'],pending['s'],pending['t'])
            if fill is not None:
                pos={**pending,'fill':fill,'ent_t':x.ot}; pending=None
                if reason:
                    r=-1.0 if reason!='TP' else m.TP_R
                    emit(pos,x,r,reason,amb); pos=None; closed=True
        if pending is not None and i>=pending['i']+1 and pos is None: pending=None
        allowed,sexit=m.session_flags(x,tf,meta)
        if pos is not None and not closed:
            z=ind[i]
            le=pos['d']==1 and x.c<z['ema'] and not z['ha'] and not z['ema_up']
            se=pos['d']==-1 and x.c>z['ema'] and not z['hb'] and z['ema_up']
            if sexit or le or se:
                r=pos['d']*(x.c-pos['e'])/abs(pos['e']-pos['s'])
                emit(pos,x,r,'SESSION' if sexit else 'EMA',False); pos=None; closed=True
        if x.ct<st: continue
        if pos is not None or pending is not None or closed: continue
        z=ind[i]
        lr=z['ha'] and x.c>z['ema'] and z['ag'] and z['chop_ok'] and z['res'] is not None
        sr=z['hb'] and x.c<z['ema'] and z['ar'] and z['chop_ok'] and z['sup'] is not None
        nl=allowed and z['sra_ok'] and x.c>x.o and lr and x.c>z['res'] and x.l<=z['res']
        ns=allowed and z['sra_ok'] and x.c<x.o and sr and x.c<z['sup'] and x.h>=z['sup']
        if nl or ns:
            d=1 if nl else -1
            e=x.h+tick if d==1 else x.l-tick
            stp=x.l-tick if d==1 else x.h+tick
            if abs(e-stp)>0:
                tgt=e+d*m.TP_R*abs(e-stp)
                pending={'d':d,'e':e,'s':stp,'t':tgt,'i':i,'sig':x.ct}
    return trades

def assert_same(base,detail,pair,year):
    if len(base)!=len(detail): raise AssertionError(f'COUNT_MISMATCH {pair} {year} {len(base)} {len(detail)}')
    for i,(a,z) in enumerate(zip(base,detail)):
        if a['signal']!=z['signal'] or a['reason']!=z['reason'] or abs(float(a['r'])-float(z['r']))>1e-10:
            raise AssertionError(f'TRADE_MISMATCH {pair} {year} idx={i} base={a} detail={z}')

def stat(ts):
    return b.stats(sorted(ts,key=lambda x:(x['signal'],x.get('symbol',''))))

def fixed_haircut(ts,c):
    z=[]
    for t in ts:
        x=dict(t); x['r']=float(t['r'])-c; z.append(x)
    return stat(z)

def pip_cost(ts,pips):
    z=[]
    cr=[]
    for t in ts:
        risk=float(t['risk_price']); ps=pip_size(t['symbol'])
        c=(pips*ps/risk) if risk>0 else 0.0
        x=dict(t); x['cost_r']=c; x['r']=float(t['r'])-c; z.append(x); cr.append(c)
    out=stat(z)
    out['cost_r_distribution']={'mean':sum(cr)/len(cr) if cr else None,'p50':qtile(cr,.5),'p90':qtile(cr,.9),'p95':qtile(cr,.95),'max':max(cr) if cr else None}
    return out

def stop_dist(ts):
    pips=[t['risk_price']/pip_size(t['symbol']) for t in ts]
    return {'n':len(pips),'p10':qtile(pips,.1),'p25':qtile(pips,.25),'p50':qtile(pips,.5),'p75':qtile(pips,.75),'p90':qtile(pips,.9),'mean':sum(pips)/len(pips) if pips else None}

def main():
    out={'schema':'wr-fx-overlap-4y-execution-v1','status':'FROZEN_4Y_EXECUTION_ROBUSTNESS',
         'strategy':'Wave Rider v2.5.13 frozen core/lifecycle Python replication',
         'hypothesis':'7-major FX family, 5m, London-New York overlap only',
         'years':list(YEARS),'pairs':PAIRS,'tf':TF,'session':SESSION,
         'fixed_r_haircuts':list(FIXED_R_HAIRCUTS),'all_in_pip_cost_grid':list(ALL_IN_PIP_COSTS),
         'notes':['Instrumented runner is asserted trade-for-trade against the frozen original runner before use.',
                  'No strategy parameter or session definition is optimized in this run.',
                  'Pip cost is a model-free all-in adverse execution-distance stress grid, not a live broker quote.',
                  'Embedded-news guard is not reconstructed. HistData bid M1/feed differences remain a limitation.'],
         'gross_match_assertions':[],'years':{},'pairs_summary':{},'combined':{},'leave_one_pair_out':{},'errors':[]}
    alltr=[]; cache={}
    for year in YEARS:
        set_year(year); yt=[]
        for pair in PAIRS:
            try:
                key=(pair,year)
                if key not in cache: cache[key]=b.load_m1(b.hist_download(pair,year))
                bars=b.aggregate(cache[key],TF); meta={'session':'1700-1700','timezone':'Etc/GMT+5','type':'forex'}; tick=b.tick_for(pair)
                base=m.run(TF,bars,meta,tick); det=run_detail(TF,bars,meta,tick); assert_same(base,det,pair,year)
                keep=[]
                for t in det:
                    if s.session_of(t['signal'])==SESSION:
                        x=dict(t); x['symbol']=pair; x['year']=year; x['quarter']=f"{year}Q{(datetime.fromtimestamp(t['signal']/1000,timezone.utc).month-1)//3+1}"; keep.append(x)
                yt.extend(keep); alltr.extend(keep)
                out['gross_match_assertions'].append({'year':year,'symbol':pair,'all_trades':len(base),'status':'MATCH'})
                print(year,pair,'all',len(base),'keep',len(keep),'avg',stat(keep)['avg_r'],flush=True)
            except Exception as e:
                out['errors'].append({'year':year,'symbol':pair,'error':repr(e)}); print('ERROR',year,pair,repr(e),flush=True)
        qs={f'{year}Q{i}':stat([t for t in yt if t['quarter']==f'{year}Q{i}']) for i in range(1,5)}
        out['years'][str(year)]={'gross':stat(yt),'quarters':qs,'positive_quarters':sum((v['avg_r'] or 0)>0 for v in qs.values() if v['n']>0),'stop_pips':stop_dist(yt)}
    alltr=sorted(alltr,key=lambda x:(x['signal'],x['symbol']))
    for pair in PAIRS:
        pt=[t for t in alltr if t['symbol']==pair]
        ys={str(y):stat([t for t in pt if t['year']==y]) for y in YEARS}
        out['pairs_summary'][pair]={'gross':stat(pt),'years':ys,'positive_years':sum((v['avg_r'] or 0)>0 for v in ys.values() if v['n']>0),'stop_pips':stop_dist(pt)}
    out['combined']={'gross':stat(alltr),'stop_pips':stop_dist(alltr),
                     'fixed_r_cost_stress':{str(c):fixed_haircut(alltr,c) for c in FIXED_R_HAIRCUTS},
                     'pip_cost_stress':{str(c):pip_cost(alltr,c) for c in ALL_IN_PIP_COSTS},
                     'positive_years':sum((out['years'][str(y)]['gross']['avg_r'] or 0)>0 for y in YEARS),
                     'positive_quarters':sum((q['avg_r'] or 0)>0 for y in YEARS for q in out['years'][str(y)]['quarters'].values() if q['n']>0)}
    for drop in PAIRS:
        z=[t for t in alltr if t['symbol']!=drop]
        out['leave_one_pair_out'][drop]=stat(z)
    with open('wr_fx_overlap_4y_execution.json','w') as f: json.dump(out,f,indent=2)
    c=out['combined']; print('\nCOMBINED',c['gross']); print('stop',c['stop_pips']); print('positive years',c['positive_years'],'/4 quarters',c['positive_quarters'],'/16')
    print('pair totals',{p:(x['gross']['n'],round(x['gross']['total_r'],2),round(x['gross']['avg_r'],3),x['positive_years']) for p,x in out['pairs_summary'].items()})
    print('fixed cost',{k:(round(v['total_r'],2),round(v['avg_r'],3),v['ci95_avg_r']) for k,v in c['fixed_r_cost_stress'].items()})
    print('pip cost',{k:(round(v['total_r'],2),round(v['avg_r'],3),v['ci95_avg_r'],v['cost_r_distribution']) for k,v in c['pip_cost_stress'].items()})
    print('LOO',{p:(round(v['total_r'],2),round(v['avg_r'],3),v['ci95_avg_r']) for p,v in out['leave_one_pair_out'].items()}); print('ERRORS',out['errors'])

if __name__=='__main__': main()
