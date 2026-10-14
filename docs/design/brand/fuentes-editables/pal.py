import numpy as np, itertools
def h2rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lin(c):
    c=c/255.0
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def lum(h):
    r,g,b=[lin(x) for x in h2rgb(h)]
    return 0.2126*r+0.7152*g+0.0722*b
def cr(a,b):
    la,lb=lum(a),lum(b)
    if la<lb: la,lb=lb,la
    return (la+0.05)/(lb+0.05)
# CVD (Machado 2009, severity 1.0), applied in linear RGB
M={'protan':np.array([[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]]),
   'deutan':np.array([[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]]),
   'tritan':np.array([[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]])}
def sim(h,kind):
    v=np.array([lin(x) for x in h2rgb(h)])
    if kind!='normal': v=np.clip(M[kind]@v,0,1)
    return v
def lab(v):
    # linear sRGB -> XYZ D65 -> Lab
    m=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
    xyz=m@v; xyz=xyz/np.array([0.95047,1.0,1.08883])
    f=lambda t: np.where(t>0.008856,np.cbrt(t),7.787*t+16/116)
    fx,fy,fz=f(xyz[0]),f(xyz[1]),f(xyz[2])
    return np.array([116*fy-16,500*(fx-fy),200*(fy-fz)])
def de(a,b,kind='normal'):
    return float(np.linalg.norm(lab(sim(a,kind))-lab(sim(b,kind))))
if __name__=='__main__':
    NAVY='#0A1F2E';NAVY2='#10304A';WHITE='#FFFFFF';BG='#F2F6F8'
    S={'normal':'#2BB673','advertencia':'#F5A524','excursion':'#FF5A3C','sin_senal':'#8D6BE3'}
    print("== estado como TEXTO/ICONO sobre superficies")
    print("%-12s %-8s | %-7s %-7s | %-7s %-7s | navy-on-fill white-on-fill"%("estado","hex","navy","navy2","bg","white"))
    for k,v in S.items():
        print("%-12s %-8s | %-7.2f %-7.2f | %-7.2f %-7.2f | %-7.2f %-7.2f"%(k,v,cr(v,NAVY),cr(v,NAVY2),cr(v,BG),cr(v,WHITE),cr(NAVY,v),cr(WHITE,v)))
    print("== marca")
    for n,h in {'cian #1FB5D6':'#1FB5D6','teal #0D7894':'#0D7894','gris #52646F':'#52646F','gris #A0AAB0':'#A0AAB0','navy2':NAVY2}.items():
        print("%-14s on navy %.2f | navy2 %.2f | bg %.2f | white %.2f"%(n,cr(h,NAVY),cr(h,NAVY2),cr(h,BG),cr(h,WHITE)))
    print("navy on cian",cr(NAVY,'#1FB5D6'),"white on navy",cr(WHITE,NAVY),"navy on bg",cr(NAVY,BG))
    print("== distinguibilidad de rellenos (dE Lab) entre pares, por tipo de vision")
    for kind in ['normal','protan','deutan','tritan']:
        row=[]
        for a,b in itertools.combinations(S,2):
            row.append("%s-%s %.0f"%(a[:4],b[:4],de(S[a],S[b],kind)))
        print(kind.ljust(7),' | '.join(row))
    print("== luminancia relativa de los rellenos")
    for k,v in S.items(): print(k, round(lum(v),3))
