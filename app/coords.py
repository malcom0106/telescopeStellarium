import math
import re
import logging
from time import time, ctime, strftime, localtime

def hauteur(dec=0.0, lat=48.927171, H=0.0) :
    """Calcul de la Hauteur

    Args:
        dec (float): Declinaison en radian
        lat (float): Latitude 
        H (float): Angle Horaire de l'etoile en radian 

    Returns:
        float: Hauteur en radian
    """

    sinushauteur = math.sin(dec)*math.sin(lat) - math.cos(dec)*math.cos(lat)*math.cos(H)
    haut = math.asin(sinushauteur)
    return haut

def azimuth(dec=0.0, lat=48.927171, hau=0.0, H=0.0) : 
    cosazimuth = ( math.sin(dec) - math.sin(lat) * math.sin(hau) ) / ( math.cos(lat) * math.cos(hau) )

    sinazimuth = ( math.cos(dec) * math.sin (H) ) / math.cos(hau)

    if(sinazimuth > 0 ) : 
        return + math.acos(cosazimuth)
    else : 
        return - math.acos(cosazimuth)



def rad_2_hour(rads):
    """Des radians aux heures, avec jusqu'à six décimales de précision (float) 

    Args:
        rads (Float): Angle en radian

    Returns:
        Float: Angle en heures
    """
    h = round( (rads * 180)/(15 * math.pi), 6)
    if h > 24.0:
        h = h - 24.0
    if h < 0.0:
        h = 24.0 + h
    return h


def radStr_2_deg(rad):
    """Transforme des radians dans un format de chaîne en degrés (float)

    Args:
        rad (float): Angle en radian

    Returns:
        float: angle en degres
    """
    exp = re.compile(r'^(-?)[0-9]{1}\.[0-9]{4,8}')
    
    if(not exp.match(rad)):
        return None
    
    r = float(rad)
    if(r < 0):
        r = (2 * math.pi) - abs(r)
    
    return (r * 180) / math.pi

def rad_2_deg(rad):
    return (rad * 180) / math.pi

def rad_2_radStr(rad):
    """Transforme des radians en string

    Args:
        rad (float): Angle en Radian

    Returns:
        String: Angle en string
    """
    if(rad < 0.0): 
        return '%f' % rad
    else: 
        return '+%f' % rad
    

def radStr_2_degStr(r):
    """Transforme les radians en degrés, tous deux au format chaîne

    Args:
        r (float): Radians signés au format chaîne

    Returns:
        float: Degrés au format chaîne (ej: "DºM'S ''")
    """
    return deg_2_degStr(radStr_2_deg(r))


def degStr_2_rad(d):
    """Transforme les degrés au format chaîne en radians
# d = DºM'S '' => D + (M / 60) + (S / 60 ^ 2) degrés => D.dº

    Args:
        d (string): Degrés au format chaîne ("DºM'S ''" || "D.dº")

    Returns:
        float: Radians au format flottant
    """
    exp1 = re.compile('^-?[0-9]{,3}(º|ᵒ)[0-9]{,3}\'[0-9]{,3}([\']{2}|")$')
    exp2 = re.compile('^-?[0-9]{,3}\.[0-9]{,6}(º|ᵒ)$')

    if(not exp1.match(d) and not exp2.match(d)):
        logging.debug("Error parametro: %s" % d)
        return None
    elif(exp1.match(d)):
        d = d.replace('º','.').replace("''",'.').replace("'",'.')
        d_dic = d.split('.')
        d_deg = float(d_dic[0])
        d_min = float(d_dic[1])
        d_sec = float(d_dic[2])
        
        if(d_deg < 0):
            d_min = 0 - d_min
            d_sec = 0 - d_sec
    
        d_ndeg = (d_deg+(d_min/60)+(d_sec/(60**2)))
    else:
        d_ndeg = float(d.replace('º',''))
        if(d_ndeg < 0): 
            d_ndeg = 360 - abs(d_ndeg)

    return round((d_ndeg * math.pi) / 180, 6)


def degStr_2_radStr(d):
    """Transforme les degrés en radians, tous deux au format chaîne

    Args:
        d (string): Degrés au format chaîne ("DºM'S ''" || "D.dº")

    Returns:
        float: Radians signés au format chaîne
    """
    return rad_2_radStr(degStr_2_rad(d))


def deg_2_degStr(deg):
    """Transforme des degrés en string

    Args:
        deg (string): Angle en degré

    Returns:
        string: angle converti en string ("DºM'S''")
    """
    ndeg = math.floor(float(deg))
    
    nmins = (deg - ndeg) * 60
    mins = math.floor(nmins)
    secs = round( (nmins - mins) * 60 )
    
    return "%dº%d'%d''" % (ndeg, mins, secs)


def hourStr_2_rad(h):
    """Des heures au format chaîne en radians
        h = HhMmSs => H + (M / 60) + (S / 60 ^ 2) heures
        (heures * 15 * pi) / 180

    Args:
        h (string): Heures au format chaîne ("HhMmSSs")

    Returns:
        float: Radians au format flottant
    """
    exp = re.compile('^[0-9]{,3}h[0-9]{,3}m[0-9]{,3}s$')
    if(not exp.match(h)):
        logging.debug("Error in param: %s" % h)
        return None
    
    h = h.replace('h','.').replace("m",'.').replace("s",'.')
    h_dic = h.split('.')

    h_h = float(h_dic[0])
    h_m = float(h_dic[1])
    h_s = float(h_dic[2])

    nh = (h_h+(h_m/60)+(h_s/(60**2)))

    return round((nh * 15 * math.pi) / 180, 6)
    

def hour_2_hourStr(hours):
    """ Transforme les heures du format float au format chaîne

    Args:
        hours (Float): Heures au format flottant

    Returns:
        String: Heures au format chaîne ("HhMmSSs")
    """
    (h, m, s) = hour_min_sec(hours)
    return '%dh%dm%00.1fs' % (h, m, s)
    

def hour_min_sec(hours):
    """Des heures au format flottant à une liste avec le nombre d'heures, de minutes et de secondes

    Args:
        hours (float): Heures au format Float

    Returns:
        tuple: tuple (heure, minute, seconde)
    """
    h = math.floor(hours)
    
    hours_m = (hours - h)*60.0
    m = math.floor(hours_m)
    
    s = (hours_m - m)*60.0
    
    #Éviter les valeurs X.60
    if s >= 59.99:
        s = 0
        m += 1
    if m >= 60:
        m = 60-m
        h += 1
    
    return (h, m, s)
    
## From degrees in float format, to a list with number of degrees, minutes and seconds
#
# \param degs Degrees in float format
# \return List with (degrees, minutes, seconds)
def grad_min_sec(degs):
    """De degrés au format flottant, à une liste avec nombre de degrés, minutes et secondes

    Args:
        degs (float): Dégre en float

    Returns:
        tuple: tuple avec (degré, minute, seconde)
    """

    #Eviter les opération avec des négatifs
    to_neg = False
    if degs < 0:
        degs = math.fabs(degs)
        to_neg = True
    
    d = math.floor(degs)
    
    degs_m = (degs - d)*60.0
    m = math.floor(degs_m)
    
    s = (degs_m - m)*60.0
    
    #Eviter les valeurs .60
    if s >= 59.99:
        s = 0
        m += 1
    if m >= 60.0:
        m = 60.0-m
        d += 1
    
    if to_neg:
        d = -d
    
    return (d, m, s)


def eCoords2str(ra, dec, mtime):
    """Transforme les valeurs obtenues à partir de "Stellarium Telescope Protocol" en une liste avec chaque valeur au format chaîne ("HhMmSSs", "DºM'S ''", "HhMmSs")

    Args:
        ra (float): Ascension droite
        dec (float): Déclinaison
        mtime (float): Horodatage en microsecondes

    Returns:
        tuple: tuple avec (Ascension droite, déclinaison, heure) => ("HhMmSSs", "DºM'S ''", "HhMmSs")
    """

    ra_h = ra*12.0/2147483648
    dec_d = dec*90.0/1073741824
    time_s = math.floor(mtime / 1000000)
    
    return ('%dh%dm%00.0fs' % hour_min_sec(ra_h), '%dº%d\'%00.0f\'\'' % grad_min_sec(dec_d), strftime("%Hh%Mm%Ss", localtime(time_s)))
    

def toJ2000(ra, dec, mtime):
    """Transforme les coordonnées des radians au format de chaîne J2000 ("HhMmSSs / GºM'SS" à Fecha ")

    Args:
        ra (float): Ascension droite
        dec (float): Déclinaison 
        mtime (float): Horodatage en microsecondes

    Returns:
        string: Coordonnées équatoriales au format chaîne J2000
    """

# HhMmSs => H+(M/60)+(S/60^2) houres
# DºM'S'' => D+(M/60)+(S/60^2) degres
# heures vers radian: (hours * 15 * pi)/180
    
    ra_h = ra*12.0/2147483648
    (h1, m1, s1) = hour_min_sec(ra_h)
        
    dec_d = dec*90.0/1073741824
    (h2, m2, s2) = grad_min_sec(dec_d)

    time_s = math.floor(mtime / 1000000)  # Depuis microsecondes vers secondes (Unix timestamp)
    t = ctime(time_s)
            
    return '%dh%dm%00.0fs/%dº%d\'%00.1f\'\' at %s' % (h1, m1, s1, h2, m2, s2, t)
        

def rad_2_stellarium_protocol(ra, dec):
    """Transforme les coordonnées des radians au format "Stellarium Telescope Protocol"

    Args:
        ra (float): Ascension droite
        dec (float): Déclinaison 

    Returns:
        tuple: Tuple avec (Ascension droite, Déclinaison) au format "Stellarium Telescope Protocol"
    """

    ra_h = rad_2_hour(ra)
    
    dec_d = (dec * 180) / math.pi

    logging.debug("(hours, degrees): (%f, %f)" % (ra_h, dec_d))
    
    return (int(ra_h*(2147483648/12.0)), int(dec_d*(1073741824/90.0)))