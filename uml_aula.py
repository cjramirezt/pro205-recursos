"""UML Aula 2.1: dibujos de clases editables con Matplotlib.

Uso: from uml_aula import DiagramaUML, dibujar_mapa
Las clases se ubican por columna y fila; el espacio crece con su contenido.
conectar() reúne tipo, multiplicidades y verbo en una sola instrucción.
Las posiciones entregadas evitan superponer cajas. Si agregas clases o
relaciones, revisa los recorridos: no es un motor universal de enrutamiento.
Se conservan clase(), herencia(), asociacion(), agregacion(), composicion()
y mostrar() de la versión anterior. Los tipos de relación no se infieren
del código Python: los elige y justifica quien diseña el modelo.
dibujar_mapa() dibuja el mapa de ciclo de vida de Tecnobox (Tarea 2B).
"""
__version__ = "2.1"
__all__ = ["DiagramaUML", "dibujar_mapa"]

import math
import io
import textwrap
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch


class DiagramaUML:
    def __init__(self, titulo="Diagrama UML", orientacion="horizontal"):
        if orientacion not in ("horizontal", "vertical"):
            raise ValueError("Usa orientación horizontal o vertical.")
        self.titulo = titulo
        self.orientacion = orientacion
        self.clases = []
        self.relaciones = []

    def clase(self, nombre, atributos=None, metodos=None, columna=None,
              fila=None, identificador=None):
        """Agrega una caja. [] deja vacío el compartimento.

        identificador es opcional: permite cambiar el nombre visible sin
        modificar las conexiones. Columna crece a la derecha; fila hacia abajo.
        """
        atributos = [] if atributos is None else atributos
        metodos = [] if metodos is None else metodos
        if not isinstance(atributos, list) or not isinstance(metodos, list):
            raise TypeError('Atributos y métodos deben ser listas: ["texto", "texto"].')
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Escribe un nombre de clase no vacío.")
        if any(not isinstance(x, str) for x in atributos + metodos):
            raise TypeError("Cada atributo y método debe ser un texto entre comillas.")
        clave = nombre if identificador is None else identificador
        if any(c["id"] == clave for c in self.clases):
            raise ValueError("Identificador repetido: " + str(clave))
        if any(c["nombre"] == nombre for c in self.clases):
            raise ValueError("Nombre de clase repetido: " + nombre)
        n = len(self.clases)
        columna = (n if self.orientacion == "horizontal" else 0) if columna is None else columna
        fila = (n if self.orientacion == "vertical" else 0) if fila is None else fila
        if any(type(v) is not int or v < 0 for v in (columna, fila)):
            raise ValueError("Columna y fila deben ser enteros mayores o iguales a cero.")
        if any((c["col"], c["fila"]) == (columna, fila) for c in self.clases):
            raise ValueError("Esa posición ya tiene una clase: cambia columna o fila.")
        self.clases.append(dict(id=clave, nombre=nombre, atributos=list(atributos),
                                metodos=list(metodos), col=columna, fila=fila))
        return self

    def conectar(self, origen, destino, tipo="asociacion",
                 multiplicidad_origen="", multiplicidad_destino="", verbo="",
                 salida=None, entrada=None, posicion_origen=0.5,
                 posicion_destino=0.5, ruta="recta", desplazamiento=-0.5):
        """Une dos clases por sus identificadores (o nombres si no usaste ID).

        Tipos: asociacion, agregacion, composicion, herencia, dependencia.
        Herencia: primero SUBCLASE, luego SUPERCLASE; sin multiplicidades.
        Agregación/composición: primero TODO, luego PARTE; rombo en el TODO.
        Las multiplicidades se escriben JUNTO al extremo indicado.
        verbo solo rotula la línea: no crea una dirección de navegación.

        Opciones de dibujo entregadas: salida/entrada (arriba, abajo,
        izquierda, derecha), ruta (recta, codo), posición de puerto 0..1.
        No hace falta modificarlas en las plantillas de la evaluación.
        """
        tipos = ("asociacion", "agregacion", "composicion", "herencia", "dependencia")
        if tipo not in tipos:
            raise ValueError("Tipo desconocido. Usa: " + ", ".join(tipos))
        ids = [c["id"] for c in self.clases]
        if origen not in ids or destino not in ids:
            raise ValueError("Agrega primero las clases. Revisa los identificadores de la conexión.")
        if origen == destino:
            raise ValueError("Esta ayuda no dibuja relaciones de una clase consigo misma.")
        if tipo in ("herencia", "dependencia") and (multiplicidad_origen or multiplicidad_destino):
            raise ValueError("Herencia y dependencia no llevan multiplicidades en esta notación.")
        lados = (None, "arriba", "abajo", "izquierda", "derecha")
        if salida not in lados or entrada not in lados:
            raise ValueError("Lado: arriba, abajo, izquierda o derecha.")
        if ruta not in ("recta", "codo"):
            raise ValueError("La ruta debe ser recta o codo.")
        if ruta == "codo" and (salida is None or entrada is None):
            raise ValueError("Para una ruta con codo indica salida y entrada.")
        if not 0 <= posicion_origen <= 1 or not 0 <= posicion_destino <= 1:
            raise ValueError("Las posiciones de puerto deben estar entre 0 y 1.")
        self.relaciones.append(dict(origen=origen, destino=destino, tipo=tipo,
            mo=str(multiplicidad_origen), md=str(multiplicidad_destino), verbo=verbo,
            salida=salida, entrada=entrada, po=posicion_origen, pd=posicion_destino,
            ruta=ruta, desplazamiento=desplazamiento))
        return self

    def herencia(self, subclase, superclase, **dibujo):
        return self.conectar(subclase, superclase, "herencia", **dibujo)

    def asociacion(self, origen, destino, multiplicidad_origen="",
                   multiplicidad_destino="", etiqueta="", **dibujo):
        return self.conectar(origen, destino, "asociacion", multiplicidad_origen,
                             multiplicidad_destino, etiqueta, **dibujo)

    def agregacion(self, todo, parte, multiplicidad_todo="",
                   multiplicidad_parte="", etiqueta="", **dibujo):
        return self.conectar(todo, parte, "agregacion", multiplicidad_todo,
                             multiplicidad_parte, etiqueta, **dibujo)

    def composicion(self, todo, parte, multiplicidad_todo="",
                    multiplicidad_parte="", etiqueta="", **dibujo):
        return self.conectar(todo, parte, "composicion", multiplicidad_todo,
                             multiplicidad_parte, etiqueta, **dibujo)

    def dependencia(self, usuario, recurso, etiqueta="", **dibujo):
        return self.conectar(usuario, recurso, "dependencia", verbo=etiqueta, **dibujo)

    def mostrar(self, archivo="diagrama", carpeta="diagramas", preliminar=False,
                mostrar=True):
        """Muestra y guarda PNG/PDF. preliminar=True muestra solo nombres.

        Devuelve un diccionario con las rutas exportadas. Puede ejecutarse de
        nuevo después de editar la celda que construye el diagrama completo.
        """
        if not self.clases:
            raise ValueError("Agrega al menos una clase antes de mostrar.")
        azul, fondo = "#18364D", "#E8F1F7"
        ancho, paso, cab = 6.6, 0.37, 0.65
        cajas = {}
        alturas = {}
        def envolver(lineas):
            return [trozo for texto in lineas for trozo in
                    (textwrap.wrap(texto, 46, subsequent_indent="  ",
                     break_long_words=True, break_on_hyphens=False) or [""])]
        for c in self.clases:
            a, m = envolver(c["atributos"]), envolver(c["metodos"])
            ha = 0 if preliminar else 0.26 + paso * max(2, len(a))
            hm = 0 if preliminar else 0.26 + paso * max(2, len(m))
            h = cab + ha + hm
            cajas[c["id"]] = dict(c=c, a=a, m=m, ha=ha, hm=hm, h=h)
            alturas[c["fila"]] = max(alturas.get(c["fila"], 0), h)
        centros_y = {}
        cursor = 0
        for fila in range(max(alturas) + 1):
            alto_fila = alturas.get(fila, cab + 2)
            centros_y[fila] = -(cursor + alto_fila/2)
            cursor += alto_fila + 2.5
        for b in cajas.values():
            b["x"] = b["c"]["col"] * (ancho + 3.6)
            b["y"] = centros_y[b["c"]["fila"]]
        xmin = min(b["x"] for b in cajas.values()) - ancho/2 - 0.55
        xmax = max(b["x"] for b in cajas.values()) + ancho/2 + 0.55
        ymin = min(b["y"]-b["h"]/2 for b in cajas.values()) - 0.55
        ymax = max(b["y"]+b["h"]/2 for b in cajas.values()) + 0.55
        fig, ax = plt.subplots(figsize=((xmax-xmin)*0.76, (ymax-ymin)*0.76+0.65))
        fig.patch.set_facecolor("white")
        ax.set(xlim=(xmin,xmax), ylim=(ymin,ymax), aspect="equal")
        ax.axis("off")
        ax.set_title(self.titulo, color=azul, fontsize=16, weight="bold", pad=20)

        def borde(b, otro, lado, p):
            x, y, h = b["x"], b["y"], b["h"]
            if lado == "arriba": return (x-ancho/2+p*ancho, y+h/2)
            if lado == "abajo": return (x-ancho/2+p*ancho, y-h/2)
            if lado == "izquierda": return (x-ancho/2, y+h/2-p*h)
            if lado == "derecha": return (x+ancho/2, y+h/2-p*h)
            dx, dy = otro["x"]-x, otro["y"]-y
            t = min(ancho/2/abs(dx) if dx else math.inf,
                    h/2/abs(dy) if dy else math.inf)
            return x+dx*t, y+dy*t

        def unidad(p,q):
            dx,dy=q[0]-p[0],q[1]-p[1]
            l=math.hypot(dx,dy)
            return dx/l,dy/l

        for r in self.relaciones:
            b0,b1=cajas[r["origen"]],cajas[r["destino"]]
            p0=borde(b0,b1,r["salida"],r["po"])
            p1=borde(b1,b0,r["entrada"],r["pd"])
            pts=[p0,p1]
            if r["ruta"] == "codo":
                vertical=("arriba","abajo")
                if r["salida"] in vertical and r["entrada"] in vertical:
                    y=(p0[1]+p1[1])/2
                    pts=[p0,(p0[0],y),(p1[0],y),p1]
                elif r["salida"] not in vertical and r["entrada"] not in vertical:
                    x=(p0[0]+p1[0])/2
                    pts=[p0,(x,p0[1]),(x,p1[1]),p1]
                elif r["salida"] in vertical: pts=[p0,(p0[0],p1[1]),p1]
                else: pts=[p0,(p1[0],p0[1]),p1]
            pts=[p for i,p in enumerate(pts) if i==0 or p!=pts[i-1]]
            u0=unidad(pts[0],pts[1]); u1=unidad(pts[-2],pts[-1])
            n0=(-u0[1],u0[0]); n1=(-u1[1],u1[0])
            linea=list(pts)
            if r["tipo"] == "herencia":
                base=(p1[0]-u1[0]*0.52,p1[1]-u1[1]*0.52)
                ax.add_patch(Polygon([p1,(base[0]+n1[0]*0.25,base[1]+n1[1]*0.25),
                    (base[0]-n1[0]*0.25,base[1]-n1[1]*0.25)],facecolor="white",
                    edgecolor=azul,lw=1.5,zorder=3))
                linea[-1]=base
            elif r["tipo"] in ("agregacion","composicion"):
                medio=(p0[0]+u0[0]*0.38,p0[1]+u0[1]*0.38)
                fin=(p0[0]+u0[0]*0.76,p0[1]+u0[1]*0.76)
                ax.add_patch(Polygon([p0,(medio[0]+n0[0]*0.21,medio[1]+n0[1]*0.21),fin,
                    (medio[0]-n0[0]*0.21,medio[1]-n0[1]*0.21)],
                    facecolor=azul if r["tipo"]=="composicion" else "white",
                    edgecolor=azul,lw=1.5,zorder=3))
                linea[0]=fin
            elif r["tipo"] == "dependencia":
                base=(p1[0]-u1[0]*0.46,p1[1]-u1[1]*0.46)
                ax.plot([base[0]+n1[0]*0.23,p1[0],base[0]-n1[0]*0.23],
                        [base[1]+n1[1]*0.23,p1[1],base[1]-n1[1]*0.23],color=azul,lw=1.5)
            ax.plot([p[0] for p in linea],[p[1] for p in linea],color=azul,lw=1.5,
                    linestyle="--" if r["tipo"]=="dependencia" else "-",zorder=1)
            fondo_texto=dict(facecolor="white",edgecolor="none",pad=1.4)
            for texto,p,u,n,dist in [(r["mo"],p0,u0,n0,1.3 if r["tipo"] in ("agregacion","composicion") else 1.1),
                                     (r["md"],p1,u1,n1,-1.1)]:
                if texto: ax.text(p[0]+u[0]*dist+n[0]*0.29,p[1]+u[1]*dist+n[1]*0.29,
                    texto,fontsize=11,color=azul,ha="center",va="center",bbox=fondo_texto,zorder=7)
            if r["verbo"]:
                segmentos=[math.dist(a,b) for a,b in zip(pts,pts[1:])]
                restante=sum(segmentos)/2
                for i,l in enumerate(segmentos):
                    if restante<=l:
                        u=unidad(pts[i],pts[i+1]); n=(-u[1],u[0])
                        mx=pts[i][0]+u[0]*restante+n[0]*r["desplazamiento"]
                        my=pts[i][1]+u[1]*restante+n[1]*r["desplazamiento"]
                        ax.text(mx,my,textwrap.fill(r["verbo"],18),ha="center",va="center",
                            fontsize=10.5,color=azul,bbox=fondo_texto,zorder=7)
                        break
                    restante-=l

        for b in cajas.values():
            c=b["c"]; x=b["x"]-ancho/2; top=b["y"]+b["h"]/2
            ax.add_patch(Rectangle((x,top-b["h"]),ancho,b["h"],facecolor="white",edgecolor=azul,lw=1.5,zorder=4))
            ax.add_patch(Rectangle((x,top-cab),ancho,cab,facecolor=fondo,edgecolor=azul,lw=1.4,zorder=5))
            ax.text(b["x"],top-cab/2,c["nombre"],fontsize=12,color=azul,
                    weight="bold",ha="center",va="center",zorder=6)
            if not preliminar:
                div=top-cab-b["ha"]
                ax.plot([x,x+ancho],[div,div],color=azul,lw=1,zorder=5)
                for lineas,y in [(b["a"],top-cab-0.34),(b["m"],div-0.34)]:
                    for i,texto in enumerate(lineas):
                        ax.text(x+0.17,y-i*paso,texto,fontsize=10,color=azul,
                                family="monospace",va="center",zorder=6)
        ruta=Path(archivo)
        if ruta.parent == Path("."): ruta=Path(carpeta)/ruta
        ruta.parent.mkdir(parents=True,exist_ok=True)
        rutas={ext:str(ruta.with_suffix('.'+ext)) for ext in ("png","pdf")}
        fig.tight_layout(pad=1.3)
        for ext,p in rutas.items():
            buffer=io.BytesIO()
            fig.savefig(buffer,format=ext,dpi=160,bbox_inches="tight")
            Path(p).write_bytes(buffer.getvalue())
        if mostrar: plt.show()
        plt.close(fig)
        return rutas


def dibujar_mapa(nodos, enlaces, archivo, titulo):
    """Nodos: (id, texto, columna, fila). Enlaces: (id_origen, id_destino, verbo)."""
    if not nodos:
        print('PENDIENTE: agrega los conceptos y sus conexiones.')
        return
    if len({n[0] for n in nodos}) != len(nodos):
        raise ValueError('Los identificadores de los nodos deben ser distintos.')
    cols = max(n[2] for n in nodos) + 1
    filas = max(n[3] for n in nodos) + 1
    fig, ax = plt.subplots(figsize=(cols*4.3, filas*2.7))
    ax.axis('off')
    puntos = {n[0]: (n[2]*4.8, -n[3]*3.1) for n in nodos}
    for origen, destino, verbo in enlaces:
        a, b = puntos[origen], puntos[destino]
        dx, dy = b[0]-a[0], b[1]-a[1]
        t = min([v for v in [1.85/abs(dx) if dx else 1e9,
                             .8/abs(dy) if dy else 1e9]])
        inicio = (a[0]+dx*t, a[1]+dy*t)
        fin = (b[0]-dx*t, b[1]-dy*t)
        ax.add_patch(FancyArrowPatch(inicio, fin, arrowstyle='->', mutation_scale=16,
                                    color='#17324d', lw=1.3))
        ax.text((a[0]+b[0])/2, (a[1]+b[1])/2+.13, verbo,
                ha='center', fontsize=9, bbox=dict(facecolor='white', edgecolor='none', pad=1))
    for ident, texto, col, fila in nodos:
        x, y = puntos[ident]
        ax.add_patch(Rectangle((x-1.85, y-.8), 3.7, 1.6,
                              facecolor='#edf4f9', edgecolor='#17324d', lw=1.4))
        ax.text(x, y, texto, ha='center', va='center', fontsize=10, linespacing=1.5)
    ax.set_xlim(-2.1, (cols-1)*4.8+2.1)
    ax.set_ylim(-(filas-1)*3.1-1.1, 1.3)
    ax.set_title(titulo, fontsize=14, weight='bold', color='#17324d', pad=16)
    fig.tight_layout()
    ruta = Path(archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(ruta)+'.png', dpi=160, bbox_inches='tight')
    fig.savefig(str(ruta)+'.pdf', bbox_inches='tight')
    plt.close(fig)
    from IPython.display import display, Image
    display(Image(filename=str(ruta)+'.png'))
    print('Archivos generados:', str(ruta)+'.png', 'y', str(ruta)+'.pdf')
