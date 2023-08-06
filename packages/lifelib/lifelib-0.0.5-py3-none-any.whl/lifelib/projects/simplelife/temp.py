import simplelife


model = simplelife.build(load_saved=False)

import modelx as mx
mx.core.api._system.callstack.max_depth = 1000
proj = model.Projection
data = []
#for i in range(1, 301, 10):
#    print(i)
#    ncf = [proj(i).pv_NetLiabilityCashflow(t) for t in range(50)]
#    data.append(ncf)
    
for i in range(10, 301, 10):
    print(i)
    ncf = proj(i).pv_NetLiabilityCashflow(0)
    data.append(ncf)