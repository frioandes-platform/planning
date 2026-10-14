from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
F='fonts/node_modules/@fontsource/inter-tight/files/inter-tight-latin-800-normal.woff'
font=TTFont(F); gs=font.getGlyphSet(); cmap=font.getBestCmap(); upm=font['head'].unitsPerEm
def word_paths(text, size, x0, base_y, tracking=0):
    """devuelve lista [(char, d)] con contornos ya posicionados"""
    s=size/upm; x=x0; out=[]
    for ch in text:
        gn=cmap[ord(ch)]
        pen=SVGPathPen(gs)
        tp=TransformPen(pen,(s,0,0,-s,x,base_y))
        gs[gn].draw(tp)
        out.append((ch,pen.getCommands()))
        x+=gs[gn].width*s+tracking
    return out, x
NAVY='#0A1F2E'; TEAL='#0D7894'; CYAN='#1FB5D6'; ICE='#F2F6F8'; WHITE='#FFFFFF'
def isotipo(x,y,k,ridge,dot):
    # cresta andina = traza de temperatura; punto = sensor en la cumbre. Caja 64x64 escalada por k
    pts=[(6,48),(20,30),(28,40),(42,12),(58,48)]
    p=' '.join(f'{x+a*k:.2f},{y+b*k:.2f}' for a,b in pts)
    cx,cy=x+42*k,y+12*k
    return (f'<polyline points="{p}" fill="none" stroke="{ridge}" stroke-width="{8.5*k:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{7*k:.2f}" fill="{dot}"/>')
def svg(w,h,body,title,bg=None):
    r=f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{r}{body}</svg>\n')
def logo(c_ridge,c_dot,c_frio,c_andes,pad=16):
    size=64; k=1.0
    # wordmark: tamaño tal que la altura de mayúscula (~0.727 em) quede ~ 38 u
    fs=52; base=48+pad  # linea base alineada con la base de la cresta
    frio,x1=word_paths('Frío',fs,pad+64+14,base,tracking=-0.5)
    andes,x2=word_paths('Andes',fs,x1-0.5,base,tracking=-0.5)
    w=x2+pad; h=64+2*pad
    body=isotipo(pad,pad,k,c_ridge,c_dot)
    body+=''.join(f'<path d="{d}" fill="{c_frio}"/>' for _,d in frio)
    body+=''.join(f'<path d="{d}" fill="{c_andes}"/>' for _,d in andes)
    return round(w),h,body
def write(name,w,h,body,title,bg=None):
    open(f'out/svg/{name}.svg','w').write(svg(w,h,body,title,bg))
# --- logo horizontal
w,h,b=logo(TEAL,CYAN,NAVY,TEAL); write('logo-principal',w,h,b,'FríoAndes logo principal')
w,h,b=logo(NAVY,NAVY,NAVY,NAVY); write('logo-una-tinta',w,h,b,'FríoAndes logo una tinta')
w,h,b=logo(ICE,CYAN,ICE,CYAN); write('logo-negativo',w,h,b,'FríoAndes logo negativo')
w,h,b=logo(WHITE,WHITE,WHITE,WHITE); write('logo-una-tinta-blanco',w,h,b,'FríoAndes logo una tinta en blanco')
# --- isotipo solo (caja 96 con margen)
def iso(r,d,bg=None,nm='',title=''):
    body=isotipo(16,16,1.0,r,d); write(nm,96,96,body,title,bg)
iso(TEAL,CYAN,nm='isotipo-principal',title='Isotipo FríoAndes')
iso(NAVY,NAVY,nm='isotipo-una-tinta',title='Isotipo FríoAndes una tinta')
iso(ICE,CYAN,nm='isotipo-negativo',title='Isotipo FríoAndes negativo')
# --- icono de app: cuadrado redondeado navy con isotipo negativo
body=f'<rect width="128" height="128" rx="28" fill="{NAVY}"/>'+isotipo(24,24,1.25,ICE,CYAN)
write('icono-app',128,128,body,'Icono FríoAndes')
print('ok')
