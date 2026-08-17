#!/usr/bin/env python3
# Frozen prior-era extension of the already-frozen 4Y FX-overlap execution test.
# No strategy/session/pair selection changes. This wrapper only changes the years.
import os
import wr_fx_overlap_4y_execution as w

w.YEARS=(2018,2019,2020,2021)
w.main()
os.replace('wr_fx_overlap_4y_execution.json','wr_fx_overlap_prior_2018_2021.json')
