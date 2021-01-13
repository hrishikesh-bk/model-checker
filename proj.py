from z3 import *
from ply_parser import *

p = int(input('Number of labels: '))
n = 2**p

x = []

for k in range(n+1):
	x.append([])
	for i in range(p):
		x[k].append(Bool('x_%i,%i' % (k, i)))
#print(x)

#Transitions
def T(x, y, f):
	if f.type == 'LITERAL':
		if f.child == 'tru':
			return True
		else:
			return False
	elif f.type == 'PROP':
		s = f.child
		n = int(s[1:])
		if s[0] == 'x':
			return x[n]
		else:
			return y[n]
	elif f.type == 'NOT':
		return Not(T(x, y, f.child))
	elif f.type == 'OR':
		return Or(T(x, y, f.left), T(x, y, f.right))
	#And
	else:
		return And(T(x, y, f.left), T(x, y, f.right))

#Initial state(s)
def I(x, f):
	if f.type == 'LITERAL':
		if f.child == 'tru':
			return True
		else:
			return False
	elif f.type == 'PROP':
		s = f.child
		n = int(s[1:])
		return x[n]
	elif f.type == 'NOT':
		return Not(I(x, f.child))
	elif f.type == 'OR':
		return Or(I(x, f.left), I(x, f.right))
	#And
	else:
		return And(I(x, f.left), I(x, f.right))

#trans = parser.parse('(((!x0).(!x1)).((!y0)=(y1)))')
# print(T(x[0], x[1], trans))

#init = parser.parse('(!x0)')
# print(I(x[0], init))

#Compares x with every element in l
def chkInL(l, n, x):
	l1 = []
	for i in range(n):
		l1.append([])
		for j in range(p):
			l1[i].append(l[i][j] == x[j])
		l1[i] = And(l1[i])
	return Or(l1)

#Computes recurrence diameter
def rD(transition):
	s = Solver()
	d = 0
	l1 = []
	l2 = []

	while True:
		s.push()
		l1.append(T(x[d], x[d+1], transition))
		l2.append(x[d])

		a = And(l1)
		b = chkInL(l2, d+1, x[d+1])
#		print(b)

		s.add(Not(Or(Not(a), b)))
		#There does not exist x0, ..,xd such that a !=> b, i.e. we have found the recurrence diameter
		if s.check() == unsat:
			return d
		d+=1

# print(rD(trans))

#Executes bmc
def genT(init, trans, f, n):
	s = Solver()

	for k in range(n+1):
		#[M]k
		if k == 0:
			s.add(I(x[0], init))
		else:
			s.add(T(x[k-1], x[k], trans))

		s.push()
		s.add(genTk(trans, f, k))
		if s.check() == unsat:
			#do something
			#print('!',s,'genT\n')
			return 'unsat'
		else:
			s.pop()
			continue
	return 'sat'
	#else f is not satisfied
	#do something

def bmc(init,trans,f):
	f1 = FormulaMonadic('NOT', f)
	st = genT(init,trans,f1, n)
	if st=='sat':
		return 'unsat'
	else:
		return 'sat'
#Executes an instance of bmc
def genTk(trans, f, k):
	l = []
	for i in range(k+1):
		l.append(T(x[k], x[i], trans))
#	print((l, callFunction(x, 0, k, f)))
	a1 = Or(l)
	a = And(Not(a1), callFunction(x,0,k,f))
#	print(a)
	b = []
	for i in range(k+1):
		b.append(And(l[i], And(callFunctionL(x, 0, k, i, f))))
#	print('a--------------',a)
#	print('b------------',b)
	b1 = b
	b1.append(a)
#	print(b1,'-------------b1')
	return Or(b1)

def callFunction(x, i, k, f):
	#print(globals()[f.type](x, i, k, f),"bbbb)
	if f.type == 'X':
		return X(x, i, k, f)
	elif f.type == 'F':
		return F(x, i, k, f)
	elif f.type == 'U':
		return U(x, i, k, f)
	elif f.type == 'G':
		return G(x, i, k, f)
	#And
	elif f.type == 'R':
		return Rl(x,i,k, f)
	elif f.type == 'PROP': 
		return PROP(x, i, k, f)
	elif f.type == 'LITERAL': 
		return LITERAL(x, i, k, f)
	elif f.type == 'NOT':
		return Not(callFunction(x, i, k, f.child))
	elif f.type == 'OR':
		return Or(callFunction(x, i, k, f.left),callFunction(x, i, k, f.right))
	else:
		return And(callFunction(x, i, k, f.left),callFunction(x, i, k, f.right))	

#def callFunctionL(x, i, k, l, f):
#	return(globals()[f.type](x, i, k, l, f))

def PROP(x, i, k, f):
	s = f.child
	n = int(s[1:])
#	print(i,type(i),'adsf',n,type(n))
	return x[i][n]

def LITERAL(x, i, k, f):
	if f.child == 'tru':
		return True
	return False

def F(x, i, k, f):
	f1 = f.child		#f = F(f1)
	l = []
	for j in range(i, k+1):
		l.append(callFunction(x, j, k, f1))
	return Or(l)

def G(x, i, k, f):
	return False

def X(x, i, k, f):
	if i < k:
		return callFunction(x, i+1, k, f.child)
	else:
		return False

def U(x, i, k, f):
	fl = f.left
	fr = f.right
	l = []
	for j in range(i, k+1):
		lj = [callFunction(x, j, k, fr)]
		for ij in range(i, j):
			lj.append(callFunction(x, ij, k, fl))
		l.append(And(lj))
	return Or(l)

def R(x, i, k, f):
	fl = f.left
	fr = f.right
	l = []
	for j in range(i, k+1):
		lj = [callFunction(x, j, k, fl)]
		for ij in range(i, j+1):
			lj.append(callFunction(x, ij, k, fr))
		l.append(And(lj))
	return Or(l)

#def callFunction(x, i, k, f):
	#print(globals()[f.type](x, i, k, f),"bbbb)
#	return(globals()[f.type](x, i, k, f))
def callFunctionL(x, i, k, l, f):
#	return(globals()[f.type](x, i, k, l, f))
	if f.type == 'X':
		return Xl(x, i, k, l, f)
	elif f.type == 'F':
		return Fl(x, i, k, l, f)
	elif f.type == 'U':
		return Ul(x, i, k, l, f)
	elif f.type == 'G':
		return Gl(x, i, k, l, f)
	#And
	elif f.type == 'R':
		return Rl(x,i,k,l,f)
	elif f.type == 'PROP': 
		return PROP(x, i, k, f)
	elif f.type == 'LITERAL': 
		return LITERAL(x, i, k, f)
	elif f.type == 'NOT':
		return Not(callFunctionL(x, i, k, l, f.child))
	elif f.type == 'OR':
		return Or(callFunctionL(x, i, k, l, f.left),callFunctionL(x, i, k, l, f.right))
	else:
		return And(callFunctionL(x, i, k, l, f.left),callFunctionL(x, i, k, l, f.right))		

def Fl(x, i, k, l1, f):
	f1 = f.child
	l = []
	for j in range(min(i, l1), k+1):
		l.append(callFunctionL(x, j, k, l1, f1))
	return Or(l)

def Gl(x, i, k, l1, f):
	f1 = f.child
	l = []
	for j in range(min(i, l1), k+1):
		l.append(callFunctionL(x, j, k, l1, f1))
	return And(l)

def Xl(x, i, k, l1, f):
	return callFunction(x, i+1, k, f)

def Ul(x, i, k, l1, f):
	fl = f.left
	fr = f.right
	l = []
	for j in range(i, k+1):
		lj = [callFunctionL(x, j, k, l1, fr)]
		for ij in range(i, j):
			lj.append(callFunctionL(x, ij, k, l1, fl))
		l.append(And(lj))
	for j in range(l1, i):
		lj = [callFunctionL(x, j, k, l1, fr)]
		for ij in range(i, k+1):
			lj.append(callFunctionL(x, ij, k, l1, fl))
		for ij in range(l1, j):
			lj.append(callFunctionL(x, ij, k, l1, fl))
		l.append(And(lj))
	return Or(l)

def Rl(x, i, k, l1, f):
	fl = f.left
	fr = f.right
	l = []
	lj = []
	for j in range(min(i, l1), k):
		lj.append(callFunctionL(x, i, k, l1, fr))
	for j in range(i, k+1):
		lj = [callFunctionL(x, j, k, l1, fl)]
		for ij in range(i, j+1):
			lj.append(callFunctionL(x, i, k, l1, fr))
		l.append(And(lj))
	for j in range(l1, i):
		lj = [callFunctionL(x, j, k, l1, fl)]
		for ij in range(i, k+1):
			lj.append(callFunctionL(x, ij, k, l1, fr))
		for ij in range(l1, j+1):
			lj.append(callFunctionL(x, ij, k, l1, fr))
		l.append(And(lj))
	return Or(l)
#Convert property into logical formula 
def P(x, f):
	if f.type == 'LITERAL':
		if f.child == 'tru':
			return True
		else:
			return False
	elif f.type == 'PROP':
		s = f.child
		n = int(s[1:])
		return x[n]
	elif f.type == 'NOT':
		return Not(P(x, f.child))
	elif f.type == 'OR':
		return Or(P(x, f.left), P(x, f.right))
	#And
	else:
		return And(P(x, f.left), P(x, f.right))

#trans = parser.parse('(((!x0).(!x1)).((!y0)=(y1)))')
# print(T(x[0], x[1], trans))

#init = parser.parse('(!x0)')
# print(I(x[0], init))
def equal(x, y):
	l = []
	for i in range(p):
		l.append(x[i] == y[i])
	return And(l)

def kInduction(init, trans, q):
	#Convert q to logical formula
	sC1 = Solver()
	sC2 = Solver()
	cC = Solver()			#Counter example check
	loopLimit = rD(trans)
	y = []
	path = []
	noLoop = []
	satCondition1 = []
	satCondition2 = []

	for k in range(loopLimit+1):
		y.append([])
		for i in range(p):
			y[k].append(Bool('y_%i,%i' % (k, i)))
		if k == 0:
			satCondition1.append(I(y[0], init))
			cC.add(I(y[0], init))
		else:
			path.append(T(y[k-1], y[k], trans))

			for i in range(k):
				noLoop.append(Not(equal(y[k], y[i])))
			satCondition2.append(P(y[k-1], q))
			satCondition1.append(Not(I(y[k], init)))
		#Check conditions now
		sC1.push()
		sC1.add(And(satCondition1))
		sC1.add(And(noLoop))
		sC1.add(And(path))
		sC2.push()
		sC2.add(And(satCondition2))
		sC2.add(And(noLoop))
		sC2.add(Not(P(y[k], q)))
		sC2.add(And(path))
		if sC1.check() == unsat or sC2.check() == unsat:
			return True
		cC.push()
#		print('path:',path)
		cC.add(And(path))
		cC.add(Not(P(y[k], q)))
#		print(cC)
		if cC.check() == sat:
			return cC.model()
		sC1.pop()
		sC2.pop()
		cC.pop()
def main():
#	trans = parser.parse('(((!x0).(!x1)).((!y0)=(y1)))')
#	print(x[0],"dfafda")
#	print(x[1],'dfafdadfadfdfasdfdfda')
#	print(T(x[0], x[1], trans))

#	init = parser.parse('(!x0)')
#	print(I(x[0], init))
#	print('---------------------------')
	init = parser.parse(input('Enter initial states: '))
	trans = parser.parse(input('Enter transitions: '))
	f = parser.parse(input('Enter LTL formula: '))
#
	#print(str(f))
	#x

	#x and y

	#etc

	print('formula:',f,'\n')
	print('init:',init,'\n')
	print('trans:',trans,'\n')
#	print('---------------------------------!!!!!!!!!!!--------------------')
	sp = bmc(init,trans,f)
	print('BMC:',sp)


	rd1=rD(trans)
	print('Recurrence Diameter:',rd1 )

	sf = parser.parse(input('Enter safety condition:'))
	kind = kInduction(init,trans,sf)
	print('k-Induction result:',kind)


if __name__ == "__main__":
    main()