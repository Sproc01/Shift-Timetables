from pyomo.environ import *
from pyomo.opt import SolverFactory

def obj_rule(model): #objective function
    return 0

def constr_rule1(model, s, j): #constraint only one shift per day
    return model.x['M',s,j]+model.x['P', s, j]<=1

def constr_rule2(model,s,j): #constraint exactly 3 mornings a week 
    if s in model.Monday:
        return sum(model.x['M',i,j] for i in [s, s+1, s+2,s+3, s+4, s+5, s+6])==3
    else:
        return Constraint.Skip

def constr_rule3(model, s, j): #constraint exactly 3 afternoons a week 
    if s in model.Monday:
        return sum(model.x['P',i,j] for i in [s, s+1, s+2,s+3, s+4, s+5, s+6])==3
    else:
        return Constraint.Skip

def constr_rule4(model, s, j): #constraint to set ysj according to x's
    if s in model.Sunday:
        return model.x['M',s,j]+model.x['P',s,j]<=model.y[s,j]
    else:
        return Constraint.Skip

#constraints for rest sunday then work saturday or viceversa
def constr_rule5(model, s, j):
    if s in model.Sunday:
        return model.x['M',s-1,j]+model.x['P',s-1,j]<=-model.y[s,j]+1
    else:
        return Constraint.Skip

def constr_rule6(model, s, j):
    if s in model.Sunday:
        return model.x['M',s-1,j]+model.x['P',s-1,j]>=-model.y[s,j]+1
    else:
        return Constraint.Skip
    
def constr_rule7(model, j): #constraint only one sunday in a month
    return sum(model.x['M',s,j]+model.x['P',s,j] for s in model.Sunday)==1

#constraints such that always different shifts for the two people
def constr_rule8(model, s):
    return model.x['M',s,1]+model.x['M',s,2]<=1

def constr_rule9(model, s):
    return model.x['P',s,1]+model.x['P',s,2]<=1

def constr_rule14(model, s, j): #constraint same shift after the weekend
    if s in model.Monday:
        return model.x['M',s,j]==model.x['M',s-3,j]
    else:
        return Constraint.Skip
    
def constr_rule15(model, s, j): #constraint same shift for 3 days in a row
    if s in model.Monday:
        return 0.5*(model.x['M',s,j]+model.x['M',s+1,j])==model.x['M',s+2,j]
    else:
        return Constraint.Skip

#constraint from previous month(february)
def constr_rule10(model):
    return sum(model.x['P',s,1] for s in [1, 2, 3])==2

def constr_rule11(model):
    return sum(model.x['M',s,2] for s in [1, 2, 3])==2

def constr_rule12(model):
    return sum(model.x['P',s,1] for s in model.Sunday)==1
	
def constr_rule13(model):
    return sum(model.x['P',s,2] for s in model.Sunday)==1

def buildmodel():
    model=AbstractModel()
    model.Days = Set()
    model.People = Set()
    model.PartDays = Set()
    model.Monday=Set()
    model.Sunday=Set()
    # variables
    model.x = Var(model.PartDays, model.Days,model.People, domain=Boolean)
    model.y=Var(model.Days, model.People, domain=Boolean)
    # objective
    model.obj = Objective(rule=obj_rule, sense=minimize)
    # constraints
    model.constrs1 = Constraint(model.Days, model.People, rule=constr_rule1)
    model.constrs2 = Constraint(model.Days, model.People, rule=constr_rule2)
    model.constrs3 =  Constraint(model.Days, model.People,rule=constr_rule3)
    model.constrs4 =  Constraint(model.Days, model.People,rule=constr_rule4)
    model.constrs5 =  Constraint(model.Days, model.People,rule=constr_rule5)
    model.constrs6 =  Constraint(model.Days, model.People,rule=constr_rule6)
    model.constrs7 =  Constraint(model.People,rule=constr_rule7)
    model.constrs8 =  Constraint(model.Days,rule=constr_rule8)
    model.constrs9 =  Constraint(model.Days, rule=constr_rule9)
    model.constrs10 =  Constraint(rule=constr_rule10)
    model.constrs11 =  Constraint(rule=constr_rule11)
    model.constrs12 =  Constraint(rule=constr_rule12)
    model.constrs13 =  Constraint(rule=constr_rule13)
    model.constrs14 =  Constraint(model.Days, model.People,rule=constr_rule14)
    model.constrs15 =  Constraint(model.Days, model.People,rule=constr_rule15)
    return model

if __name__ == '__main__':
    import sys
    model = buildmodel()
    opt = SolverFactory('cplex_persistent')
    s=sys.argv[1]
    instance = model.create_instance(s)
    opt.set_instance(instance)
    res = opt.solve(tee=True)
    matrix=[ [ '' for i in range(len(instance.Days)) ] for j in range(2) ]
    Days=[]
    output=open('output_Radio.txt','w')
    baseFmtStr = "{{{{:{{pad}}>{num}}}}}"
    output.write('Sunday: ')
    for d in instance.Sunday:
        output.write(baseFmtStr.format(num=2).format(pad=' ').format(str(d))+'|')
    output.write('\n')
    output.write('\n')
    for d in instance.Days:
        output.write(baseFmtStr.format(num=2).format(pad=' ').format(str(d))+'|')
    output.write('\n')
    for p in instance.People:
        for d in instance.Days:
            rest=True
            for pd in instance.PartDays:
                if value(instance.x[pd,d,p])==1:
                    output.write(' '+pd+'|')
                    rest=rest and False
            if rest:
                output.write(' R|')
        output.write('\n')
    output.close()