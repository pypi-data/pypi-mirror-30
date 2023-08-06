# -*- coding: utf-8 -*-

### imports ###################################################################
import logging

import matplotlib.pyplot as plt
plt.rcParams["text.usetex"] = False
plt.rcParams["mathtext.fontset"] = "cm"
            
import numpy as np

### logging ###################################################################
logging.getLogger('ftir').addHandler(logging.NullHandler())

###############################################################################
class FTIRData(object):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('ftir')
        
        self.parent = None
        self.modifications = []
        
        for key, value in kwargs.items():
            if key == 'parent':
                self.parent = value

        # inherits modifications from parent object
        if self.parent:
            self.modifications = list(self.parent.modifications)
    
    def __str__(self):
        m_list = []
        
        for m in self.modifications:
            if m[0] == 'boxcar':
                m_str = 'boxcar(' + str(m[1]) + ', ' + str(m[2]) + ')'
            elif m[0] == 'phase shift':
                m_str ='$\epsilon$ = ' + str(m[1])
            elif m[0].find('IFFT') > 0:
                m_str = m[0]
            elif m[0].find('FFT') > 0:
                m_str = m[0]
            else:
                m_str = ''

            if m_str:
                m_list.append(m_str)

        mod_str = ', '.join(m_list)
        
        return mod_str        
    
###############################################################################
class Interferogram(FTIRData):
    def __init__(self, y, **kwargs):
        super(Interferogram, self).__init__(**kwargs)
        
        self.y = y
        self.N = len(self.y)
        self.bit_length = self.N.bit_length()

        self.dx_cm = 1
        flip = False
        roll = False
        
        for key, value in kwargs.items():
            if key == 'dx_cm':
                self.dx_cm = value
            if key == 'flip':
                flip = value
            elif key == 'lwn':
                # spatial resolution is half the laser wavelength [cm]
                self.lwn = value
                self.lambda_laser_cm = 1 / self.lwn
                self.lambda_laser = self.lambda_laser_cm / 100
                self.dx_cm = self.lambda_laser_cm / 2
            elif key == 'roll':
                roll = value

        # scan length [cm]
        self.L_cm = self.N * self.dx_cm
        self.logger.debug('scan length: L = %4.2f cm', self.L_cm)
        
        # search interferogram absolute maximum
        self.i0 = np.argmax(np.abs(self.y))
        I0 = self.y[self.i0]

        # flip sign, so that I0 > 0
        if flip and np.sign(I0) < 0:
            self.y = -self.y

        if roll:
            self.roll()


    @property
    def I0(self):
        return self.y[0]


    def boxcar(self, N1):
        y_L1 = self.y[-N1:]
        y_L2 = self.y[:N1]
        y = np.concatenate((y_L2, y_L1))

        ifg = Interferogram(y, dx_cm=self.dx_cm, parent=self)
        ifg.modifications.append(('boxcar', N1, N1))

        return ifg


    def roll(self):
        imax = np.argmax(self.y)
        
        if imax > 0:
            self.y = np.roll(self.y, -imax)


    def plot(self, **kwargs):
        
        legend = False
        title = False
        
        for key, value in kwargs.items():
            if key == 'legend':
                legend = value
            elif key == 'title':
                title = value
                
        if title:
            plt.title(str(self))
        
        plt.plot(self.i_sample, self.y)

        if legend:
            plt.legend(['$I_0$=%5.2f' % self.I0,])


    def shift(self):
        y_shifted = np.fft.fftshift(self.y)

        ifg = Interferogram(y_shifted, self.dx_cm)
        ifg.modifications.append(('shifted',))
        
        return ifg

    def spectrum(self):
        spec = Spectrum(parent=self)
        
        return spec
    
    def spectrum_org(self, zeroPadding=None):
        if not zeroPadding:
            N = zeroPadding
            Nf = self.N
        else:
            n = int(np.ceil(np.log2(self.N))) + zeroPadding
            N = Nf = 2**n
            
        nu = np.fft.fftfreq(Nf, self.dx_cm)

        spec = Spectrum(np.fft.fft(self.y, N), nu)
        spec.modifications = list(self.modifications)
        spec.modifications.append(('FFT', N))
        
        return spec

    def triangle(self):
        N2 = self.N // 2
        window = np.bartlett(self.N+1)
        triangle = np.fft.fftshift(window[:-1])
        y = self.y * triangle

        ifg = Interferogram(y, dx_cm=self.dx_cm, parent=self)
        ifg.apodisation = triangle
        ifg.modifications.append(('triangle', N2, N2))

        return ifg

    def zeroPad(self, zeroPadding=1):
        pass

###############################################################################
class Spectrum(FTIRData):
    def __init__(self, **kwargs):
        super(Spectrum, self).__init__(**kwargs)

        self.N = self.parent.N
        N2 = self.N // 2

        self.wn = np.fft.fftfreq(self.N, self.parent.dx_cm)
        self.wn[N2:] -= 2 * self.wn[N2]

        self.delta_wn = 1 / self.N / self.parent.dx_cm 
        
        self.I = np.fft.fft(self.parent.y, self.N)

        self.modifications.append('FFT')


    def phase(self):
        Re = np.real(self.I)
        Im = np.imag(self.I)
        phase = np.arctan(Im/Re)
        
        return phase


class SpectrumOrg(FTIRData):
    def interp(nu_P, nu_max, N):
        w_p_pos = nu_P[:, 0]
        P_pos = nu_P[:, 1]

        w_p_neg = -w_p_pos[-1::-1]
        P_neg = P_pos[-1::-1]

        w_p = np.concatenate((w_p_neg, w_p_pos))
        P_p = np.concatenate((P_neg, P_pos))

        nu_pos = np.linspace(0, nu_max, N, endpoint=False)
        nu_neg = np.linspace(-nu_max, 0, N, endpoint=False)

        nu = np.concatenate((nu_pos, nu_neg))
        P = np.interp(nu, w_p, P_p)

        spec = Spectrum(P, nu)
        spec.modifications.append(('interpolated spectrum S(nu)', nu_max, N))
        return spec

        
    def __init__(self, P, nu, **kwargs):
        super(Spectrum, self).__init__(**kwargs)
        
        self.P = P
        self.N = len(P)
        self.nu = nu
        self.dnu = nu[1]
        

    def interferogram(self):
        dx_cm = np.fft.fftfreq(self.N, self.dnu)[1]
        y = np.real(np.fft.ifft(self.P))

        ifg = Interferogram(y, dx_cm)
        ifg.modifications = list(self.modifications)
        ifg.modifications.append(('IFFT: S(nu) -> I(x)',))
        
        return ifg

        
    def phase_shift(self, epsilon):
        '''
        phi = np.linspace(-epsilon, epsilon, self.N)
        P_phi = np.exp(-1j * phi) * self.P
        '''
        
        phi = 2 * np.pi * self.nu * epsilon / self.dnu / self.N
        
        P_phi = np.exp(1j * phi) * self.P
                      
        spec = Spectrum(P_phi, self.nu)
        spec.modifications = list(self.modifications)
        spec.modifications.append(('phase shift', epsilon))
        
        return spec


    def plot(self, function_name='real', style='-', full_spectrum=False):

        if function_name == 'complex':
            self.plot('abs')
            self.plot('real', 'k')
            self.plot('imag', 'r--')
        else:
            f = getattr(np, function_name)
            plt.plot(self.nu[:self.N//2], f(self.P[:self.N//2]), style)

###############################################################################
if __name__ == '__main__':

    ### interpolate spectrum
    nu_P = np.array((
            (1, 0.0),
            (20, 0.0),
            (21, 0.9),
            (22, 0.0),
            (25, 0.0),
            (30, 1.0),
            (44, 1.0),
            (45, 0.01),
            (46, 1.0),
            (55, 1.0),
            (58, 0.0),
            (60, 0.0)))

    nu_p = nu_P[:, 0]
    P_p = nu_P[:, 1]
    
    nu_max = 60

    N = 2**10
    N1 = 50
    N2 = 50

    spectrum_org = Spectrum.interp(nu_P, nu_max, N)

    ifg_org = spectrum_org.interferogram()
    ifg_boxed = ifg_org.boxcar(N1, N2)

    spectrum = ifg_org.spectrum()
        
    nu_boxed = ifg_boxed.spectrum().nu

    # phase shift
    epsilon = -0.9
    spectrum_phi = spectrum_org.phase_shift(epsilon)


    ifg_phi = spectrum_phi.interferogram()
    # ifg_phi.roll()

    ifg_phase_shifted_boxed = ifg_phi.boxcar(N1, N2)
    P_phi = ifg_phase_shifted_boxed.spectrum().P

    ifg_org_centered = ifg_org.boxcar(128).shift()
    ifg_phase_shifted_centered = ifg_phase_shifted_boxed.shift()

    spectrum_phase_shifted_boxed = ifg_phase_shifted_boxed.spectrum()

    '''
    i_max = np.argmax(ifg_shifted)
    (a, b, c) = np.polyfit([-1, 0, 1], ifg_shifted[i_max-1:i_max+2], 2)
    x0 = - b / 2 / a
    '''
    
    ### plots
    plt.close('all')
    plt.figure(1)
    plt.subplot(3,3,1)
    plt.title('original spectrum')
    plt.plot(nu_p, P_p, 'o')
    spectrum_org.plot()
    
    plt.subplot(3,3,2)
    plt.title('FT -> IFG')
    ifg_org.plot(legend=True)
    
    plt.subplot(3,3,3)
    plt.title('IFT -> spectrum')
    plt.plot(nu_p, P_p, 'o')
    spectrum.plot()
    
    plt.subplot(3,3,5)
    ifg_boxed.plot(title=True)
    
    plt.subplot(3,3,6)
    plt.plot(nu_p, np.real(P_p), 'o')
    ifg_boxed.spectrum().plot()
    
    plt.subplot(3,3,7)
    plt.title('phase angle')
    spectrum_phase_shifted_boxed.plot('angle')
    plt.ylim([-np.pi, np.pi])
    
    plt.subplot(3,3,8)
    ifg_phase_shifted_boxed.plot(legend=True, title=True)
    
    plt.subplot(3,3,9)
    plt.plot(nu_p, np.real(P_p), 'o')
    
    spectrum_phase_shifted_boxed.plot('complex')
    
    plt.tight_layout()
    
    '''
    plt.figure()
    plt.plot(np.fft.fftshift(y))
    '''
    
    phase_shift= np.array([
            (-1.2, -0.33),
            (-1.1, 0.4),
            (-1, -0.48),
            (-0.9, 0.46),
            (-0.8, 0.40),
            (-0.5, 0.24),
            (0, 0),
            (0.5, -0.24),
            (1,-0.48),
            (1.1, 0.40),
            (1.2, 0.33)
            
    ])
    
    '''
    plt.figure()
    plt.plot(phase_shift[:,0], phase_shift[:,1], 'o-')
    
    plt.figure()
    nu = np.fft.fftfreq(2*N, dx)
    plt.plot(nu[:N], np.real(ifg_org.spectrum())[:N])
    '''