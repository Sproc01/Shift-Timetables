from pyomo.environ import *
from pyomo.opt import SolverFactory

def printOut(filename, instance, not_officials):
    output=open(filename,'w')
    baseFmtStr = "{{{{:{{pad}}>{num}}}}}"
    output.write('Sunday;')
    for d in instance.Sunday:
        output.write(baseFmtStr.format(num=2).format(pad=' ').format(str(d))+';')
    output.write('\n')
    output.write('\n')
    for d in instance.Days:
        output.write(baseFmtStr.format(num=2).format(pad=' ').format(str(d))+';')
    output.write('\n')
    for p in instance.People:
        for d in instance.Days:
            rest=True
            for pd in instance.PartDays:
                if value(instance.x[pd,d,p])==1:
                    if not_officials:
                        output.write(' '+pd+';')
                        rest=rest and False
                    elif pd=='M' and d not in instance.Sunday:
                        output.write('  ;')
                    else:
                        output.write(baseFmtStr.format(num=2).format(pad=' ').format(str(pd))+';')
                    rest=rest and False
            if rest:
                output.write(' R;')
        output.write('\n')
    output.close()