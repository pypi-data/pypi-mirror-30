import math as m

## Define fundamental constants
from constant import *
# c = 299792458.0
# m_e = 9.10938291e-31
# e = 1.602176565e-19
# hbar = 1.054571726e-34
# k_e = 8.9875517873681e9
# from math import pi
# epsil0 = 8.854187817620e-12


## Calculate derived constants
#alpha = 1/137.0 # it is just an approximate value
# The relatively accurate alpha value is as the following:
alpha = e**2 * k_e / (hbar * c)
a0 = hbar / (m_e * c * alpha)
E_h = alpha**2 * m_e * c**2
c_au = c * alpha

## Mapping from a.u.(atomic unit) to SI unit system
au2si = {
    "energy" : E_h,
    "length" : a0,
    "time" : hbar / E_h,
    "velocity" : alpha * c,
    "momentum" : hbar / a0,
    "frequency" : E_h / hbar,
    "ang_freq" : E_h / hbar,
    "electric_field" : E_h / (e*a0),
    "electric_potential" : E_h / e
}

## Mapping from SI unit to a.u. system
si2au = {}
for key in au2si:
    si2au[key] = 1.0 / au2si[key]

fw2fwhm = {
    'sin-square' : 1.0 - 2.0 / m.pi * m.asin(1.0 / 2**0.25)
}

def duration_to_num_cycles(wavelength_nm, duration, duration_unit, envelope_shape='sin-square'):
    assert type(duration_unit) is str
    if duration_unit.lower() == 'fs'.lower():
        dur_si = duration * 1e-15
    elif duration_unit.lower() == 'si'.lower():
        dur_si = duration
    elif duration_unit.lower() == 'as'.lower():
        dur_si = duration
    else: raise IOError("Unsupported unit: %s" % duration_unit)
    
    dur_au_fwhm = si2au['time'] * dur_si
    dur_au_fw = dur_au_fwhm / fw2fwhm[envelope_shape]

    #wavelegnth_nm = 800
    wavelength_si = wavelength_nm * 1e-9
    freq_si = c / wavelength_si
    ang_freq_si = freq_si * 2.0 * m.pi
    ang_freq_au = si2au['ang_freq'] * ang_freq_si
    period_au = 2.0 * m.pi / ang_freq_au

    num_cycles = dur_au_fw / period_au
    
    return num_cycles


## Not implemented yet
##def convert2au(quantity_name, unit='si'):
##    if quantity_name not in au2si.keys():
##        raise KeyError("Unsupported quantity name: %s" % (quantity_name))
##    if unit == 'si':
##        return au2si[quantity_name]
##    return 0

def intensity2maxEletricField(intensity, unit_in='W/cm^2', unit_out='au'):
    ## Convert unit to SI unit
    if unit_in.lower() == 'W/cm^2'.lower():
        intensity_si = 1e4 * intensity
    elif unit_in.lower() == 'si':
        intensity_si = intensity
    else:
        raise IOError("Unsupported input unit: %s" % (unit_in))
    
    ## Convert intensity in SI unit to max electric field, also in SI unit
    maxElectricField_si = m.sqrt(intensity_si / (c * epsil0 / 2))

    ## Convert unit to desired output unit
    if unit_out.lower() == 'au':
        maxElectricField = maxElectricField_si * si2au['electric_field']
    elif unit_out.lower() == 'si':
        maxElectricField = maxElectricField_si
        
    ## Return max electric field, converted from intensity
    return maxElectricField


def max_electric_field_2_intensity(max_electric_field, unit_in='au', unit_out='W/cm^2'):
    if unit_in.lower() == 'au':
        pass
    else: raise IOError("Unsupported input unit: %s" % (unit_in))

    E0_si = max_electric_field * au2si['electric_field']
    inten_si = (E0_si ** 2) * c * epsil0 * 0.5
    inten_Wcm2 = inten_si * 1e-4

    if unit_out.lower() == 'w/cm^2'.lower():
        pass
    else: raise IOError("Unsupported ouput unit: %s" % (unit_out))
    
    return inten_Wcm2

def wavelength2angFreq(wavelength, unit_in, unit_out='au'):
    if unit_in.lower() == 'nm'.lower():
        wavelength_si = wavelength * 1e-9
    elif unit_in.lower() == 'um'.lower():
        wavelength_si = wavelength * 1e-6
    else:
        raise IOError("Unsupported input unit: %s" % (unit_in))

    freq_si = c / wavelength_si
    angFreq_si = (2 * pi) * freq_si
    angFreq_au = angFreq_si * si2au['ang_freq']
    #wavelength_au = wavelength_si * si2au['length']
    #freq_au = c / wavelength_au
    #angFreq_au = freq_au * (2 * pi)
    #angFreq_si = angFreq_au * au2si['ang_freq']
    
    if unit_out == 'au':
        return angFreq_au
    elif unit_out == 'si':
        return angFreq_si
    else:
        raise IOError("Unsupported output unit: %s" % (unit_out))

