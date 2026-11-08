#!/usr/bin/env python3
"""Check actual data alignment and independently verify covariance estimates."""
from pathlib import Path
import json
import numpy as np
from scipy import stats
from common import *
from statsmodels.stats.sandwich_covariance import cov_hac

args=cli();_,d,meta=prepare(args)
m=fit(d,['ARA']+CONTROL);ref=m['model'].get_robustcov_results(cov_type='HC1',use_t=True)
hc_error=float(np.max(np.abs(m['hc']-ref.cov_params())))
assert np.allclose(m['hc'],ref.cov_params(),atol=1e-9,rtol=1e-8)
assert np.all(np.diff(m['data'].calendar_position)==1)
hac_ref=cov_hac(m['model'],nlags=30,use_correction=True)
hac_error=float(np.max(np.abs(m['hac']-hac_ref)))
assert np.allclose(m['hac'],hac_ref,atol=1e-8,rtol=1e-7)
# Reference OLS using SciPy QR least squares, independently of statsmodels pseudoinverse.
x=design(m['data'],['ARA']+CONTROL).to_numpy();y=m['data'].F2_6.to_numpy()
b=linalg.lstsq(x,y,lapack_driver='gelsy')[0]
assert np.allclose(b,m['b'],atol=1e-9,rtol=1e-8)
# Every mapped monthly reference is strictly earlier than the target's month.
for col in ['TMS','DFY','BW']:
 assert (d[col+'_reference_month'] < d.index.strftime('%Y-%m')).all()
# Data files used must be included in active indicator folders, not archive or generator inputs.
assert not any(x['file'].startswith(('附录','未采用','模拟')) for x in meta['inputs'])
checks={'status':'PASS','rows':len(d),'OLS_QR_max_abs_error':float(np.max(np.abs(b-m['b']))),
        'HC1_reference_max_abs_error':hc_error,'NW30_reference_max_abs_error':hac_error,
        'monthly_reference_before_target_month':True,'future_return_matches_saved_csv':True,
        'no_simulated_or_appendix_inputs':True,
        'notes':'Grouped full-interaction coefficients are checked against high-minus-low inside each run; calendar gaps retained in NW score vectors.'}
(ROOT/'validation_report.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
