import numpy as np
from sympy import symbols, S, cos
from celmech.hamiltonian import Hamiltonian
from celmech.poincare import PoincareParticle, Poincare
from celmech.disturbing_function import get_fg_coeffs
from celmech.transformations import ActionAngleToXY, XYToActionAngle
import rebound

'''
Compare with Hadden & Lithwick 2017:
In the code, Z = |scriptZ| and z = arg(scriptZ) from paper
W = |scriptW| and w = arg(scriptW) from paper
Phi and phi in the paper are a generalized eccentricity squared and a generalized pericenter
Cartesian components in code X, Y = sqrt(2*Phi)cos(phi) and sin(phi) are generalized eccentricities
Note A is proportional to scriptZ, but B is not proportional to scriptW, and depends on masses etc. Can solve for B from scriptZ and scriptW
'''

def rotate_Poincare_Gammas_To_Psi1Psi2(Gamma1,gamma1,Gamma2,gamma2,f,g,inverse=False):
    if inverse is True:
        g = -g
    X1,Y1 = ActionAngleToXY(Gamma1,gamma1)
    X2,Y2 = ActionAngleToXY(Gamma2,gamma2)
    norm = np.sqrt(f*f + g*g)
    rotation_matrix = np.array([[f,g],[-g,f]]) / norm
    Psi1X,Psi2X = np.dot(rotation_matrix , np.array([X1,X2]) )
    Psi1Y,Psi2Y = np.dot(rotation_matrix , np.array([Y1,Y2]) )
    Psi1,psi1 = XYToActionAngle(Psi1X,Psi1Y)
    Psi2,psi2 = XYToActionAngle(Psi2X,Psi2Y)
    return Psi1,psi1,Psi2,psi2

def calc_expansion_params(G, m1, m2, M1, M2, j, k, a10):
    p = {'j':j, 'k':k, 'G':G, 'm1':m1, 'M1':M1, 'm2':m2, 'M2':M2, 'a10':a10}       
    p['a20'] = a10*(j/float(j-k))**(2./3.)
    p['Lambda10'] = m1*np.sqrt(G*M1*p['a10'])
    p['Lambda20'] = m2*np.sqrt(G*M2*p['a20'])
    p['n10'] = m1**3*(G*M1)**2/p['Lambda10']**3
    p['n20'] = m2**3*(G*M2)**2/p['Lambda20']**3
    p['nu1'] = -3. * p['n10']/ p['Lambda10']
    p['nu2'] = -3. * p['n20'] / p['Lambda20']
    p['f'],p['g'] = get_fg_coeffs(j,k)
    p['ff']  = p['f']/np.sqrt(p['Lambda10'])
    p['gg']  = p['g']/np.sqrt(p['Lambda20'])
    fac = np.sqrt(k*(p['ff']**2+p['gg']**2))**k
    p['a'] = p['nu1']*(j-k)**2 + p['nu2']*j**2
    p['c'] = -G**2*M2*m2**3*m1/p['Lambda20']**2*fac
    p['eta'] = 2.**((6.-k)/(4.-k))*(p['c']/p['a'])**(2./(4.-k))
    p['tau'] = 8./(p['eta']*p['a'])
    p['Phiscale'] = (p['f']**2 + p['g']**2)/(p['ff']**2 + p['gg']**2)/p['k']/p['eta'] # Phi/Phiscale = 0.5*Z**2
    return p

# will give you the phiprime that yields an equilibrium Xstar, always in the range of phiprime where there exists a separatrix
def get_Phiprime(k, Xstar):
    if k == 1:
        pass
    if k == 2:
        Phiprime = (4.*Xstar**2 - 2.)/3.
    if k == 3:
        pass

    return Phiprime

def get_Xstarunstable(k, Phiprime):
    if k == 1:
        if Phiprime < 1.:
            raise ValueError("k=1 resonance has no unstable fixed point for Phiprime < 1")
        Xstarunstable = np.sqrt(Phiprime)*np.cos(1./3.*np.arccos(-Phiprime**(-1.5)))
    if k == 2:
        if Phiprime < -2./3.:
            raise ValueError("k=2 resonance has no unstable fixed point for Phiprime < -2/3")
        if Phiprime < 2./3.:
            Xstarunstable = 0.
        else:
            Xstarunstable = 0.5*np.sqrt(3.*Phiprime-2.)
    if k == 3:
        if Phiprime < -9./48.:
            raise ValueError("k=3 resonance has no unstable fixed point for Phiprime < -9/48")
        Xstarunstable = (-3.+np.sqrt(9.+48.*Phiprime))/8.

    return Xstarunstable        

def get_Hsep(k, Phiprime):
    Xu = get_Xstarunstable(k, Phiprime)
    Hsep = Xu**4 - 3.*Phiprime/2.*Xu**2 + np.abs(Xu)**(k-1)*Xu
    return Hsep

def get_Xsep(k, Phiprime):
    if k==2:
        if Phiprime < -2./3.:
            raise ValueError("k=2 resonance has no separatrix for Phiprime < -2/3")
        else:
            Hsep = get_Hsep(k, Phiprime)
            disc = np.sqrt((1.+1.5*Phiprime)**2+4.*Hsep)
            Xsep = -np.sqrt((1+1.5*Phiprime+disc)/2.)
            
        return Xsep

def get_Xplusminus(k, Phiprime):
    pass

def get_second_order_Phiprime(Xstar):
    return (4*Xstar**2 + 2.*np.abs(Xstar)/Xstar)/3.

class Andoyer(object):
    def __init__(self, j, k, X, Y, a10=1., G=1., m1=1.e-5, M1=1., m2=1.e-5, M2=1., Psi2=0., psi2=0., Phiprime=1.5, K=0., deltalambda=np.pi, lambda1=0.):
        self.X = X
        self.Y = Y
        self.Psi2 = Psi2
        self.psi2 = psi2 
        self.Phiprime = Phiprime
        self.K = K
        self.deltalambda = deltalambda
        self.lambda1 = lambda1

        self.params = calc_expansion_params(G, m1, m2, M1, M2, j, k, a10)

    @property
    def Phi(self):
        Phi, phi = XYToActionAngle(self.X, self.Y)
        return Phi
    
    @property
    def SPhi(self):
        return self.Phi/self.params['Phiscale']
    
    @property
    def phi(self):
        Phi, phi = XYToActionAngle(self.X, self.Y)
        return np.mod(phi, 2.*np.pi)
    
    @property
    def lambda2(self):
        return self.deltalambda + self.lambda1
   
    @property
    def Z(self):
        return np.sqrt(2.*self.SPhi)

    @property
    def psi1(self): # phi = jlambda2 - (j-k)lambda1 + kpsi1
        p = self.params
        theta = p['j']*self.deltalambda + p['k']*self.lambda1 # jlambda2 - (j-k)lambda1
        psi1 = np.mod( (self.phi - theta) / p['k'] ,2*np.pi)
        return psi1
    
    @property
    def SX(self):
        return self.Z*np.cos(self.phi)
    
    @property
    def SY(self):
        return self.Z*np.sin(self.phi)
        
    @property
    def Brouwer(self):
        p = self.params
        return -3.*self.Phiprime/p['a']/p['tau']

    @property
    def dL1(self):
        p = self.params
        return -(p['j']-p['k'])*(self.Brouwer + self.Phi*p['eta'])
    
    @property
    def dL2(self):
        p = self.params
        return self.K*p['eta'] -p['j']/(p['j']-p['k'])*self.dL1

    @classmethod
    def from_Z(cls, j, k, Z, phi, Phiprime, a10=1., G=1., m1=1.e-5, M1=1., m2=1.e-5, M2=1., Psi2=0., psi2=0., K=0., deltalambda=np.pi, lambda1=0.):
        p = calc_expansion_params(G, m1, m2, M1, M2, j, k, a10)
        SPhi = 0.5*Z**2
        Phi = SPhi*p['Phiscale']
        X = np.sqrt(2.*Phi)*np.cos(phi)
        Y = np.sqrt(2.*Phi)*np.sin(phi)
        return cls(j, k, X, Y, a10, G, m1, M1, m2, M2, Psi2, psi2, Phiprime, K, deltalambda, lambda1)
    
    @classmethod
    def from_elements(cls, j, k, Zstar, libfac, a10=1., G=1., m1=1.e-5, M1=1., m2=1.e-5, M2=1., Psi2=0., psi2=0., K=0., deltalambda=np.pi, lambda1=0.):
        p = calc_expansion_params(G, m1, m2, M1, M2, j, k, a10)
        #Psi1star = 0.5*Zstar**2*(p['f']**2 + p['g']**2)/(p['ff']**2 + p['gg']**2)
        #Phistar = Psi1star/k/p['eta']
        #Xstar = -np.sqrt(2*Phistar)
        Xstar = -Zstar*np.sqrt(p['Phiscale']) 
        Phiprime = get_second_order_Phiprime(Xstar)
        Xsep = get_Xsep(k, Phiprime)
        deltaX = np.abs(Xstar-Xsep)
        X = Xstar - deltaX*libfac
        Y = 0
        return cls(j, k, X, Y, a10, G, m1, M1, m2, M2, Psi2, psi2, Phiprime, K, deltalambda, lambda1)

    @classmethod
    def from_Poincare(cls,pvars,j,k,a10,i1=1,i2=2):
        p1 = pvars.particles[i1]
        p2 = pvars.particles[i2]
        p = calc_expansion_params(pvars.G, p1.m, p2.m, p1.M, p2.M, j, k, a10)
        
        dL1 = p1.Lambda-p['Lambda10']
        dL2 = p2.Lambda-p['Lambda20']

        Psi1,psi1,Psi2,psi2 = rotate_Poincare_Gammas_To_Psi1Psi2(p1.Gamma,p1.gamma,p2.Gamma,p2.gamma,p['ff'],p['gg'])
        K  = dL2 + j * dL1 / float(j-k) 
        Brouwer = -dL1/(j-k) - Psi1 / k
        b =  p['a'] * Brouwer + j * p['nu2'] * K

        # scale momenta
        Psi1 /= p['eta']
        K /= p['eta']
        Psi2 /= p['eta']

        phi = j * p2.l - (j-k) * p1.l + k * psi1
        Phi = Psi1 / k 
        X = np.sqrt(2*Phi)*np.cos(phi)
        Y = np.sqrt(2*Phi)*np.sin(phi)
        Phiprime = - p['tau'] * b / 3.
        
        andvars = cls(j, k, X, Y, a10, pvars.G, p1.m, p1.M, p2.m, p2.M, Psi2, psi2, Phiprime, K, p2.l-p1.l, p1.l)
        return andvars

    def to_Poincare(self):
        p = self.params
        j = p['j']
        k = p['k']
       
        # Unscale momenta
        Psi2 = self.Psi2*p['eta']
        K = self.K*p['eta']
        Psi1 = k*self.Phi*p['eta']
        b = -3. * self.Phiprime / p['tau']

        Brouwer = (b - j * p['nu2'] * K) / p['a']
        lambda2 = self.lambda1 + self.deltalambda
        theta = j*self.deltalambda + k*self.lambda1 # jlambda2 - (j-k)lambda1
        psi1 = np.mod( (self.phi - theta) / k ,2*np.pi)
        dL1 = -(j-k) * (Brouwer + Psi1 / k)
        dL2 =((j-k) * K - j * dL1)/(j-k) 
        Lambda1 = p['Lambda10']+dL1
        Lambda2 = p['Lambda20']+dL2 

        Gamma1,gamma1,Gamma2,gamma2 = rotate_Poincare_Gammas_To_Psi1Psi2(Psi1,psi1,Psi2,self.psi2,p['ff'],p['gg'], inverse=True)
        pvars = Poincare(p['G'])
        pvars.add(p['m1'], Lambda1, self.lambda1, Gamma1, gamma1, p['M1'])
        pvars.add(p['m2'], Lambda2, lambda2, Gamma2, gamma2, p['M2'])
        return pvars

    @classmethod
    def from_Simulation(cls, sim, j, k, a10=None, i1=1, i2=2, average=True):
        if a10 is None:
            a10 = sim.particles[i1].a
        pvars = Poincare.from_Simulation(sim, average)
        ps = sim.particles
        return Andoyer.from_Poincare(pvars, j, k, a10, i1, i2)

    def to_Simulation(self, average=True):
        pvars = self.to_Poincare()
        return pvars.to_Simulation(average)
    
class AndoyerHamiltonian(Hamiltonian):
    def __init__(self, andvars):
        X, Y, Phi, phi, Phiprime, k = symbols('X, Y, Phi, phi, Phiprime, k')
        pqpairs = [(X, Y)]
        Hparams = {Phiprime:andvars.Phiprime, k:andvars.params['k']}

        H = (X**2 + Y**2)**2 - S(3)/S(2)*Phiprime*(X**2 + Y**2) + (X**2 + Y**2)**((k-S(1))/S(2))*X
        if andvars.params['tau'] < 0:
            H *= -1

        super(AndoyerHamiltonian, self).__init__(H, pqpairs, Hparams, andvars)  
        self.Hpolar = 4*Phi**2 - S(3)*Phiprime*Phi + (2*Phi)**(k/S(2))*cos(phi)

    def state_to_list(self, state):
        return [state.X, state.Y] 

    def update_state_from_list(self, state, y):
        state.X = y[0]
        state.Y = y[1]
