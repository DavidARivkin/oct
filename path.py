import numpy as np
from path import *

def poly3(x1,x2,t1,t2,r1,r2):
	"""
	Returns the polynomial coeficients for a curve with the position and 
	the derivative defined at two points of the curve.
	"""
	from numpy.linalg import solve
	A = np.array([
	[	3*t1**2,	2*t1, 	1,	0	],
	[	3*t2**2,	2*t2,	1,	0	],
	[	t1**3  , 	t1**2,	t1,	1	],
	[	t2**3  , 	t2**2,	t2,	1	],
	])
	B = np.array([r1, r2, x1, x2])
	return solve(A,B)

def line(begin,end,lineDensity):
	lineDensity = float(lineDensity)
	v = np.array(end) - np.array(begin)
	length = np.sqrt(sum(v**2))
	t = np.linspace(0,1,length*lineDensity)	
	t.shape += (1,)
	line = begin + v*t
	return line.T

def make_scan_3D_path(x0,xf,y0,yf,numRecords,numTomograms):
	x = np.linspace(x0,xf,numRecords)
	x.shape = (1,) + x.shape
	X = x*np.ones((numTomograms,1))
	y = np.linspace(y0,yf,numTomograms)
	y.shape = y.shape + (1,)
	Y = y*np.ones(numRecords)
	scan_path = np.dstack([X,Y])
	return scan_path

def make_return_3D_path(x0,xf,y0,yf,tf,r,N,numTomograms):
	f = np.poly1d(poly3(x0,xf,0,tf,r,r))
	path = f(np.linspace(0,tf,N))
	path.shape += (1,)
	path_x = path*np.ones(numTomograms)
	path_x = path_x.T
	y = np.linspace(y0,yf,numTomograms)
	intervals = [[y[i],y[i+1]] for i in range(numTomograms-1)]+[[y[-1]]*2]
	path_y = np.vstack([np.linspace(i[0],i[1],N) for i in intervals])
	p = np.dstack((path_x,path_y))
	return p

def make_return_continuous_path(x0,xf,y0,yf,tf,rx,ry,N):
	x0,xf = xf,x0
	y0,yf = yf,y0
	def path(x0,xf,rx):
		f = np.poly1d(poly3(x0,xf,0,tf,rx,rx))
		return f(np.linspace(0,tf,N))
	path_x = path(x0,xf,rx)
	path_y = path(y0,yf,ry)
	p = np.vstack((path_x,path_y))
	return p

def make_line_path(x0,y0,xf,yf,N):
	X = np.linspace(x0,xf,N)
	Y = np.linspace(y0,yf,N)
	return np.vstack((X,Y)).T

def make_position_path(x0,r,t,N):
	f = np.poly1d(poly3(0,x0,0,t,0,r))
	return f(np.linspace(0,t,N))

def make_2d_position_path(x0,y0,rx,ry,t,N):
	X = make_position_path(x0,rx,t,N)
	Y = make_position_path(y0,ry,t,N)
	return np.vstack((X,Y))

def third_order_line(x1,x2,t1,t2,r1,r2):
    	f = np.poly1d(poly3(x1,x2,t1,t2,r1,r2))
	return f(np.arange(t1,t2))

def single_scan_path(X0,Xf,t,lineDensity):
	pitch = 1/float(lineDensity)
	num = (Xf-X0)*lineDensity
	start = third_order_line(0,X0,0,t,0,pitch)
	scan = np.linspace(X0,Xf,num)
	park = third_order_line(Xf,0,0,t,pitch,0)
	return np.hstack([start,scan[0:-1],park])

class Path:
	def __init__(self,P0,Pf,N):
		self.P0,self.Pf = P0,Pf
		if type(N) == list:
			self.numTomograms = N[0]
			self.numRecords = N[1]
			self.i = 0
			self.scan_path = self.make_scan_3D_path()
			self.next = self.next_3D
			self.return_positions = self.make_return_3D_positions()
			self.next_return = self.next_return_3D
			self.has_next = self.has_next_3D
		else:
			self.numRecords = N
			self.next = self.next_single
			self.scan_path = self.make_line_path()
			self.return_positions = P0
			self.next_return = self.next_return_single
			self.has_next = lambda : True

	def has_next_3D(self):
		print self.i,self.numTomograms
		return self.i<self.numTomograms

	def next_single(self):
		return self.scan_path

	def next_3D(self):
		self.i += 1
		return self.scan_path[self.i-1]

	def next_return_single(self):
		return self.return_positions

	def next_return_3D(self):
		return self.return_positions[self.i-1]

	def make_scan_3D_path(self):
		x0,y0 = self.P0[0],self.P0[1]
		xf,yf = self.Pf[0],self.Pf[1]
		numTomograms = self.numTomograms
		numRecords = self.numRecords
		x = np.linspace(x0,xf,numRecords)
		x.shape = (1,) + x.shape
		X = x*np.ones((numTomograms,1))
		y = np.linspace(y0,yf,numTomograms)
		y.shape = y.shape + (1,)
		Y = y*np.ones(numRecords)
		scan_path = np.dstack([X,Y])
		return scan_path
	
	def make_return_3D_positions(self):
		positions = self.scan_path[:,0]
		positions[0,:] = [0,0]
		np.roll(positions,-1)
		return positions

	def make_line_path(self):
		x0,y0 = self.P0[0],self.P0[1]
		xf,yf = self.Pf[0],self.Pf[1]
		N = self.numRecords
		X = np.linspace(x0,xf,N)
		Y = np.linspace(y0,yf,N)
		return np.vstack((X,Y)).T

