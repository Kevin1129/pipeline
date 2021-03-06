import time

from pyomo.environ import *
from pyomo.dae import *
from pdegas import model

start = time.time()
instance = model.create_instance('pdegas.dat')

# discretize model
discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(instance,nfe=1,wrt=instance.DIS,scheme='FORWARD')
discretizer.apply_to(instance,nfe=47,wrt=instance.TIME,scheme='BACKWARD')

# What it should be to match description in paper
#discretizer.apply_to(instance,nfe=48,wrt=instance.TIME,scheme='BACKWARD')

TimeStep = instance.TIME[2]-instance.TIME[1]

def supcost_rule(m,k):
    return sum(m.cs*m.s[k,j,t]*(TimeStep) for j in m.SUP for t in m.TIME.get_finite_elements())
instance.supcost = Expression(instance.SCEN,rule=supcost_rule)

def boostcost_rule(m,k):
    return sum(m.ce*m.pow[k,j,t]*(TimeStep) for j in m.LINK_A for t in m.TIME.get_finite_elements())
instance.boostcost = Expression(instance.SCEN,rule=boostcost_rule)

def trackcost_rule(m,k):
    return sum(m.cd*(m.dem[k,j,t]-m.stochd[k,j,t])**2.0 for j in m.DEM for t in m.TIME.get_finite_elements())
instance.trackcost = Expression(instance.SCEN,rule=trackcost_rule)

def sspcost_rule(m,k):
    return sum(m.cT*(m.px[k,i,m.TIME.last(),j]-m.px[k,i,m.TIME.first(),j])**2.0 for i in m.LINK for j in m.DIS)
instance.sspcost = Expression(instance.SCEN,rule=sspcost_rule)

def ssfcost_rule(m,k):
    return sum(m.cT*(m.fx[k,i,m.TIME.last(),j]-m.fx[k,i,m.TIME.first(),j])**2.0 for i in m.LINK for j in m.DIS)
instance.ssfcost = Expression(instance.SCEN,rule=ssfcost_rule)

def cost_rule(m,k):
    return 1e-6*(m.supcost[k] + m.boostcost[k] + m.trackcost[k] + m.sspcost[k] + m.ssfcost[k])
instance.cost = Expression(instance.SCEN,rule=cost_rule)

def mcost_rule(m):
    return (1.0/m.S)*sum(m.cost[k] for k in m.SCEN)
instance.mcost = Expression(rule=mcost_rule)

# def eqcvar_rule(m,k):
#     return m.cost[k] - m.nu <= m.phi[k];
# instance.eqcvar = Constraint(instance.SCEN,rule=eqcvar_rule)

#def obj_rule(m):
#    return (1.0-m.cvar_lambda)*m.mcost + m.cvar_lambda*m.cvarcost
#instance.obj = Objective(rule=obj_rule)

def obj_rule(m):
    return m.mcost
instance.obj = Objective(rule=obj_rule)

endTime = time.time()-start
print('model creation time = %s' % (endTime,))

for i in instance.SCEN:
    print("Scenario %s = %s" % (
        i, sum(sum(0.5*value(instance.pow[i,j,k])
                   for j in instance.LINK_A)
               for k in instance.TIME.get_finite_elements()) ))

option = dict()
option["print_level"] = 4
option["linear_solver"]="MA57"
solver=SolverFactory('ipopt')
results = solver.solve(instance,options=option,tee=True)

for i in instance.SCEN:
    print("Scenario %s = %s" % (
        i, sum(sum(0.5*value(instance.pow[i,j,k])
                   for j in instance.LINK_A)
               for k in instance.TIME.get_finite_elements()) ))

time = []
dis = []
s1 = []
f0 = []
xdis = 0
for t in instance.TIME:
    time.append(t)
    s1.append(value(instance.s[1,1,t]))

for line in instance.LINK:
    length = value(instance.llength[line])
    for x in instance.DIS:
        xdis = xdis + length*value(x)
        dis.append(xdis)
        f0.append(value(instance.fx[1,line,24,x]))


time = []
dem4 = []
stochd4 = []


for t in instance.TIME:
    time.append(t)
    dem4.append(value(instance.dem[1,1,t]))
    stochd4.append(value(instance.stochd[1,1,t]))

import matplotlib.pyplot as plt
plt.figure(1)
plt.subplot(111)
plt.title('supplier_flowrate vs time')
plt.xlabel('time/h')
plt.ylabel('flowrate/(10x10^4scm/day)')
dem_line, = plt.plot(time,dem4,'b',label="demand")
stochd_line, = plt.plot(time,stochd4,'r',label="stochd")
plt.legend([dem_line,stochd_line],["demand","stochd"])
plt.savefig('demand VS stochd')
