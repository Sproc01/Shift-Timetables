from pyomo.environ import *
from pyomo.opt import SolverFactory
import sys
sys.path.append('.')
from OutputFun import printOut

def obj_rule(model):
    if len(model.Sunday)==5:
        return sum(model.y[k,j] for k in model.Sunday for j in model.People)
    else:
        return 0

def constr_rule0(model, s, j): #one shift per day
    return model.x['M',s,j]+model.x['P',s,j]<=1

def constr_rule1(model, s, j):#6 days at work every week
    if s in model.Monday:
        if s==29:
            return Constraint.Skip
        else:
            return sum(model.x['M',k,j]+model.x['P', k, j] for k in [s,s+1,s+2,s+3,s+4,s+5,s+6])==6
    else:
        return Constraint.Skip
    
def constr_rule2(model,j):#only one sunday at work each month
    if len(model.Sunday)==5:
        return sum(model.x['M', k, j]+model.x['P',k,j] for k in model.Sunday)>=1
    else:
        return sum(model.x['M', k, j]+model.x['P',k,j] for k in model.Sunday)==1
    
def constr_rule3(model,j):#one saturday afternoon at work each month
    return sum(model.x['P', k, j] for k in model.Saturday)==1

def constr_rule4(model,j):#eleven afternoons each month
    return sum(model.x['P', k, j] for k in model.Days)==11

def constr_rule5(model,s, j): #at least two afternoon each week
    if s in model.Monday:
        if s==29:
            return Constraint.Skip
        else:
            return sum(model.x['P', k, j] for k in [s,s+1,s+2,s+3,s+4,s+5,s+6])>=2
    else:
        return Constraint.Skip
    
def constr_rule6(model,s): #at least one person each sunday morning
    if s in model.Sunday:
        return sum(model.x['M', s, j]+model.x['P',s,j] for j in model.People)>=1
    else:
        return Constraint.Skip
    
def constr_rule8(model, s, j): #constraint to set ysj according to x's
    if s in model.Sunday:
        return model.x['M',s,j]+model.x['P',s,j]<=model.y[s,j]
    else:
        return Constraint.Skip

#constraint work on sunday rest on saturday or viceversa
def constr_rule9(model, s, j):
    if s in model.Sunday:
        return model.x['M',s-1,j]+model.x['P',s-1,j]<=-model.y[s,j]+1
    else:
        return Constraint.Skip

def constr_rule10(model, s, j):
    if s in model.Sunday:
        return model.x['M',s-1,j]+model.x['P',s-1,j]>=-model.y[s,j]+1
    else:
        return Constraint.Skip
    
#if five sunday in a month, the last sunday is the same as the first sunday but with inverted shift
def constr_rule25(model, j): #morning->afternoon
    if len(model.Sunday)==5:
        return model.x['M',model.Sunday[1], j]==model.x['P',model.Sunday[len(model.Sunday)], j]
    else:
        return Constraint.Skip
    
def constr_rule26(model, j): #afternoon->morning
    if len(model.Sunday)==5:
        return model.x['P',model.Sunday[1], j]==model.x['M',model.Sunday[len(model.Sunday)], j]
    else:
        return Constraint.Skip

#constraints fixed afternoon for every person
def constr_rule11(model, s, j): #monday
    if s in model.Monday and j in [2,3,5]:
        return model.x['P',s,j]==1
    else:
        return Constraint.Skip
    
def constr_rule12(model, s, j): #tuesday
    if s in model.Tuesday and j in [1,4]:
        return model.x['P',s,j]==1
    else:
        return Constraint.Skip
    
def constr_rule13(model, s, j): #wednesday
    if s in model.Wednesday and j==2:
        return model.x['P',s,j]==1
    else:
        return Constraint.Skip
    
def constr_rule14(model, s, j): #thursday
    if s in model.Thursday and j in [1,3,5]:
        return model.x['P',s,j]==1
    else:
        return Constraint.Skip
    
def constr_rule15(model, s, j): #friday
    if s in model.Friday and j==4:
        return model.x['P',s,j]==1
    else:
        return Constraint.Skip
    
#constr from previous month
#shift on sunday
def constr_rule16(model):
    return sum(model.x['M',k,1] for k in model.Sunday)==1

def constr_rule17(model):
    return sum(model.x['P',k,2] for k in model.Sunday)==1

def constr_rule18(model):
    return sum(model.x['P',k,3] for k in model.Sunday)==1

def constr_rule19(model):
    return sum(model.x['P',k,4] for k in model.Sunday)==1

def constr_rule20(model):
    return sum(model.x['P',k,5] for k in model.Sunday)==1

def constr_rule21(model):
    return sum(model.x['M',k,6] for k in model.Sunday)==1

def buildmodel():
    model=AbstractModel()
    model.Days = Set()
    model.People = Set()
    model.PartDays = Set()
    model.Monday = Set()
    model.Tuesday = Set()
    model.Wednesday = Set()
    model.Thursday = Set()
    model.Friday = Set()
    model.Saturday = Set()
    model.Sunday = Set()
    # variables
    model.x = Var(model.PartDays, model.Days,model.People, domain=Boolean)
    model.y = Var(model.Days, model.People, domain=Boolean)
    # objective
    model.obj = Objective(rule=obj_rule, sense=minimize)
    # constraints
    model.constrs0 = Constraint(model.Days, model.People, rule=constr_rule0)
    model.constrs1 = Constraint(model.Days, model.People, rule=constr_rule1)
    model.constrs2 = Constraint(model.People, rule=constr_rule2)
    model.constrs3 = Constraint(model.People, rule=constr_rule3)
    model.constrs4 = Constraint(model.People, rule=constr_rule4)
    model.constrs5 = Constraint(model.Days, model.People, rule=constr_rule5)
    model.constrs6 = Constraint(model.Days, rule=constr_rule6)
    model.constrs8 = Constraint(model.Days, model.People, rule=constr_rule8)
    model.constrs9 = Constraint(model.Days, model.People, rule=constr_rule9)
    model.constrs10 = Constraint(model.Days, model.People, rule=constr_rule10)
    model.constrs11 = Constraint(model.Days, model.People, rule=constr_rule11)
    model.constrs12 = Constraint(model.Days, model.People, rule=constr_rule12)
    model.constrs13 = Constraint(model.Days, model.People, rule=constr_rule13)
    model.constrs14 = Constraint(model.Days, model.People, rule=constr_rule14)
    model.constrs15 = Constraint(model.Days, model.People, rule=constr_rule15)
    model.constrs16 = Constraint(rule=constr_rule16)
    model.constrs17 = Constraint(rule=constr_rule17)
    model.constrs18 = Constraint(rule=constr_rule18)
    model.constrs19 = Constraint(rule=constr_rule19)
    model.constrs20 = Constraint(rule=constr_rule20)
    model.constrs25 = Constraint(model.People, rule=constr_rule25)
    model.constrs26 = Constraint(model.People, rule=constr_rule26)
    return model

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc != 2:
        print('Usage: python3 model_Agents.py <datafile>')
        sys.exit(1)
    model = buildmodel()
    opt = SolverFactory('cplex_persistent')
    s=sys.argv[1]
    instance = model.create_instance(s)
    opt.set_instance(instance)
    res = opt.solve(tee=True)
    printOut('Output/output_Agents.csv', instance, True)
