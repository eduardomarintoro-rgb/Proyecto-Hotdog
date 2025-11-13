from rich import print
import random
from collections import Counter, defaultdict
import matplotlib.pyplot as plt


def simulacion_dia_de_ventas(app):
    """Función para simular un día de ventas en el puesto de hot dogs.

    Parámetros:
    - app: instancia de la clase App que contiene `hotdogs` y las listas de ingredientes

    El simulador modifica el `stock` en los objetos de ingredientes de la instancia `app`.
    """
    # Estadísticas
    clientes_cambiaron_opinion = 0
    clientes_no_pudieron_comprar = 0
    total_clients = random.randint(0, 200)
    total_hotdogs_sold = 0
    acompañantes_vendidos = 0
    hotdog_counter = Counter()
    hotdogs_que_causaron_salida = Counter()
    ingredientes_que_causaron_salida = Counter()

    if not hasattr(app, 'hotdogs') or len(app.hotdogs) == 0:
        print("[italic red]No hay hotdogs en el menú. Cargue el menú antes de simular.")
        return

    for i in range(total_clients):
        num_hotdogs = random.randint(0, 5)

        if num_hotdogs == 0:
            print(f"el cliente {i} cambió de opinión")
            clientes_cambiaron_opinion += 1
            continue

        # Construir la orden: lista de tuples (hotdog_obj, extra_acompañante_bool)
        orden = []
        for _ in range(num_hotdogs):
            hd = random.choice(app.hotdogs)
            extra_acompanante = random.choice([True, False])
            orden.append((hd, extra_acompanante))

        # Verificar inventario sin mutar: contamos requerimientos por objeto
        requeridos = defaultdict(int)
        for hd_obj, extra_ac in orden:
            # ingredientes principales
            requeridos[id(hd_obj.pan), 'pan', hd_obj.pan] += 1
            requeridos[id(hd_obj.salchicha), 'salchicha', hd_obj.salchicha] += 1
            # salsas y toppings: cada elemento de la lista consume una unidad
            for s in hd_obj.salsas:
                requeridos[id(s), 'salsa', s] += 1
            for t in hd_obj.toppings:
                requeridos[id(t), 'topping', t] += 1
            # acompañante incluido en el hotdog (combo)
            if hd_obj.acompañante is not None:
                requeridos[id(hd_obj.acompañante), 'acompañante', hd_obj.acompañante] += 1
            # acompañante extra (si el cliente lo compra)
            if extra_ac:
                # if hotdog already has acompañante object, we treat extra as another unidad of that same acompañante
                # if there is no acompañante in the hotdog, pick a random acompañante from app.acompañantes if available
                if hd_obj.acompañante is not None:
                    requeridos[id(hd_obj.acompañante), 'acompañante', hd_obj.acompañante] += 1
                else:
                    if hasattr(app, 'acompañantes') and len(app.acompañantes) > 0:
                        acomp_extra = random.choice(app.acompañantes)
                        requeridos[id(acomp_extra), 'acompañante', acomp_extra] += 1
                    else:
                        # no hay acompañantes en inventario; we'll register a requirement for None which will fail the check
                        requeridos[('none', i), 'acompañante', None] += 1

        # Ahora comprobar cada requerimiento
        faltante = None
        faltante_ingrediente = None
        for (_ident, _kind, obj), cantidad in list(requeridos.items()):
            # obj puede ser None en caso de no existir acompañantes
            if obj is None:
                faltante = True
                faltante_ingrediente = 'Acompañante (no disponible)'
                break
            stock = getattr(obj, 'stock', None)
            if stock is None:
                # Si no existe stock en el objeto, asumimos no disponible
                faltante = True
                faltante_ingrediente = getattr(obj, 'nombre', str(obj))
                break
            if stock < cantidad:
                faltante = True
                faltante_ingrediente = getattr(obj, 'nombre', str(obj))
                break

        if faltante:
            # El cliente se marcha sin llevarse nada.
            clientes_no_pudieron_comprar += 1
            # Para reporting, registrar qué hotdogs estaban en la orden (los que fallaron)
            # Tomamos el primer hotdog que contenía el ingrediente faltante
            hotdog_fallo = None
            for hd_obj, extra_ac in orden:
                # comprobar si el ingrediente faltante está entre sus componentes
                componentes = []
                componentes.append(hd_obj.pan)
                componentes.append(hd_obj.salchicha)
                componentes.extend(hd_obj.salsas)
                componentes.extend(hd_obj.toppings)
                if hd_obj.acompañante is not None:
                    componentes.append(hd_obj.acompañante)
                # si extra acompañante y hd_obj.acompañante is None, we don't know chosen acomp, so skip
                nombres_comp = [getattr(c, 'nombre', str(c)) for c in componentes if c is not None]
                if faltante_ingrediente in nombres_comp:
                    hotdog_fallo = hd_obj
                    break

            if hotdog_fallo is None:
                # fallback: pick first hd
                hotdog_fallo = orden[0][0]

            print(f"El cliente {i} no pudo comprar. HotDog: '{hotdog_fallo.nombre}' - Ingrediente faltante: {faltante_ingrediente}. Se marchó sin llevarse nada.")
            hotdogs_que_causaron_salida[hotdog_fallo.nombre] += 1
            ingredientes_que_causaron_salida[faltante_ingrediente] += 1
            continue

        # Si llegamos aquí, hay stock suficiente: descontar y confirmar venta
        # Aplicar decrementos
        for (_ident, _kind, obj), cantidad in list(requeridos.items()):
            # obj puede ser None sólo en caso de error anterior, pero lo evitamos
            if obj is None:
                continue
            # disminuir stock
            if hasattr(obj, 'stock'):
                obj.stock -= cantidad

        # Actualizar contadores de ventas
        total_hotdogs_sold += num_hotdogs
        # contar acompañantes vendidos: los incluidos en cada hotdog + extras
        for hd_obj, extra_ac in orden:
            if hd_obj.acompañante is not None:
                acompañantes_vendidos += 1
            if extra_ac:
                acompañantes_vendidos += 1
            hotdog_counter[hd_obj.nombre] += 1

        # Imprimir la lista de hot dogs que compró el cliente i
        lista_nombres = [hd_obj.nombre for hd_obj, _ in orden]
        print(f"Cliente {i} compró: {lista_nombres}")

    # Fin del día: reportar estadísticas
    promedio_hd_por_cliente = (total_hotdogs_sold / total_clients) if total_clients > 0 else 0

    print('\n[bold yellow]=== RESUMEN DEL DÍA SIMULADO ===')
    print(f"Total de clientes: {total_clients}")
    print(f"Clientes que cambiaron de opinión: {clientes_cambiaron_opinion}")
    print(f"Clientes que no pudieron comprar: {clientes_no_pudieron_comprar}")
    print(f"Total hot dogs vendidos: {total_hotdogs_sold}")
    print(f"Promedio de hot dogs por cliente: {promedio_hd_por_cliente:.2f}")
    most_sold = hotdog_counter.most_common(1)
    if most_sold:
        print(f"Hot dog más vendido: {most_sold[0][0]} (vendidos: {most_sold[0][1]})")
    else:
        print("Hot dog más vendido: Ninguno")

    if hotdogs_que_causaron_salida:
        print("Hot dogs que causaron que el cliente se marchara:")
        for nombre, c in hotdogs_que_causaron_salida.items():
            print(f" - {nombre}: {c} veces")
    else:
        print("Hot dogs que causaron que el cliente se marchara: Ninguno")

    if ingredientes_que_causaron_salida:
        print("Ingredientes que causaron que el cliente se marchara:")
        for nombre, c in ingredientes_que_causaron_salida.items():
            print(f" - {nombre}: {c} veces")
    else:
        print("Ingredientes que causaron que el cliente se marchara: Ninguno")

    print(f"Acompañantes vendidos (incluyendo combos): {acompañantes_vendidos}")

    # Guardar resultados en app para referencia posterior
    resultado = {
        'total_clients': total_clients,
        'clientes_cambiaron_opinion': clientes_cambiaron_opinion,
        'clientes_no_pudieron_comprar': clientes_no_pudieron_comprar,
        'total_hotdogs_sold': total_hotdogs_sold,
        'promedio_hd_por_cliente': promedio_hd_por_cliente,
        'hotdog_counter': dict(hotdog_counter),
        'hotdogs_que_causaron_salida': dict(hotdogs_que_causaron_salida),
        'ingredientes_que_causaron_salida': dict(ingredientes_que_causaron_salida),
        'acompañantes_vendidos': acompañantes_vendidos
    }
    if hasattr(app, 'resultados_simulaciones'):
        app.resultados_simulaciones.append(resultado)
    else:
        app.resultados_simulaciones = [resultado]


def estadisticas_dia_ventas(app):
    """Imprime estadísticas guardadas de simulaciones anteriores (si las hay)."""
    if not hasattr(app, 'resultados_simulaciones') or len(app.resultados_simulaciones) == 0:
        print("No hay simulaciones previas almacenadas.")
        return

    # Mostrar la última simulación como antes
    ultima = app.resultados_simulaciones[-1]
    print('\n[bold yellow]=== ESTADÍSTICAS ÚLTIMA SIMULACIÓN ===')
    for k, v in ultima.items():
        if k == 'hotdog_counter' or k.endswith('_que_causaron_salida') or k == 'ingredientes_que_causaron_salida':
            print(f"{k}:")
            for a, b in v.items():
                print(f" - {a}: {b}")
        else:
            print(f"{k}: {v}")

    # Si hay 2 o más simulaciones, ofrecer módulo de estadísticas (gráficos)
    n = len(app.resultados_simulaciones)
    if n < 2:
        print('\n[italic]Se necesitan al menos 2 simulaciones para generar gráficas.\n')
        return

    # Seleccionar las claves numéricas estándar a graficar
    numeric_keys = [
        'total_clients',
        'clientes_cambiaron_opinion',
        'clientes_no_pudieron_comprar',
        'total_hotdogs_sold',
        'promedio_hd_por_cliente',
        'acompañantes_vendidos'
    ]

    # Construir series por día
    series = {k: [] for k in numeric_keys}
    for res in app.resultados_simulaciones:
        for k in numeric_keys:
            # Si falta alguna clave, usar 0 como fallback
            series[k].append(res.get(k, 0))

    # Preparar eje X y graficar fuera del bucle (ahora todas las series tienen longitud n)
    x = list(range(1, n + 1))
    plt.figure(figsize=(10, 6))

    # Dibujar cada serie
    for k in numeric_keys:
        plt.plot(x, series[k], marker='o', label=k)

    plt.title('Estadísticas por día de simulación')
    plt.xlabel('Día de simulación')
    plt.ylabel('Valor')
    plt.xticks(x)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()
    plt.tight_layout()

    # Mostrar la ventana de la gráfica
    plt.show()