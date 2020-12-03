from flask import Flask, redirect, url_for, render_template, request
import sympy
from sympy.abc import x
from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication_application, parse_expr, standard_transformations)
from sympy.solvers.solveset import substitution
from sympy.utilities.lambdify import implemented_function, lambdify
from matplotlib import pyplot as plt
import matplotlib.patches as polyplot
import matplotlib.pyplot as plt

# flask app init
plt.switch_backend('agg')
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Page functions
@app.after_request
def add_header(response):
    # funcion para que las imagenes de la grafica se actualicen
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check = 0, pre-check = 0, max-age = 0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route("/")
def homepage():
    # Homepage function calls home.html
    return render_template("index.html")

@app.route("/resultado", methods=["GET", "POST"])
def resultado():
    # Pagina de resultados, realiza la integracion, crea la grafica y llama a resultado.html
    metodo = request.form["metodo"]
    funcion = request.form["funcion"]
    limite_a = int(request.form["limite-a"])
    limite_b = int(request.form["limite-b"])
    valor_n = int(request.form["valor-n"])
    integral = 0
    metodo_utilizado = ""

    # elige el metoda para integrar
    if metodo == '1':
        integral = round(trapezoide(f(funcion), limite_a, limite_b, valor_n), 6)
        metodo_utilizado = "Trapezoide"
    elif metodo == '2':
        integral = round(simpson13(f(funcion), limite_a, limite_b, valor_n), 6)
        metodo_utilizado = "Simpson 1/3"
    elif metodo == '3':
        integral = round(simpson38(f(funcion), limite_a, limite_b, valor_n), 6)
        metodo_utilizado = "Simpson 3/8"
    else:
        integral = round(simpson13(f(funcion), limite_a, limite_b, valor_n), 6)
        metodo_utilizado = "Simpson 1/3"

    graficar(f(funcion), limite_a, limite_b, valor_n)
    return render_template('resultado.html', img="static/images/grafica.png", integral=integral, metodo=metodo_utilizado)


# U T I L I T Y  F U N C T I O N S
def f(str_func):
    # recibe un string y lo tranforma en una expresion
    transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
    parsed = parse_expr(str_func, evaluate=True, transformations=transformations)
    x = sympy.symbols('x')

    return lambdify(x, parsed, 'numpy')

def graficar(f, a, b, n):
    # recibe una funcion, limite a, limite b, y n, lo transforma en una grafica y guarda la imagen
    def fx(x):
        # funcion
        return f(x)
    # Los valores para X, Y y h
    dev_x = []
    dev_y = []
    h = (b - a) / n
    # Para agregar los valores de X y Y
    while a <= b:
        dev_x.append(a)
        dev_y.append(fx(a))
        a += h
    # Crear la tabla
    plt.plot(dev_x, dev_y, 'k', color='#492072', linewidth=0.5)
    plt.xlabel('x')
    plt.ylabel('y')
    # Pa' que se vea bonito
    plt.fill_between(dev_x, dev_y, color='#5c2296')
    ax = plt.gca()
    ax.set_facecolor('#201F23')
    plt.grid(True, linestyle='--', color='#424043', linewidth=0.5)
    # guarda la imagen de la grafica
    plt.savefig("static/images/grafica.png")


def trapezoide(f, a, b, n):
    # Codigo del metodo de trapezoide
    delta_x = (b - a) / n
    approx = f(a) + f(b)
    for i in range(1, n):
        k = a + i*delta_x
        approx = approx + 2 * f(k)
    approx = approx * delta_x/2
    return approx

def simpson13(f, a, b, n):
    # Codigo del metodo simpson 1/3
    delta_x = (b - a) / n
    approx = f(a) + f(b)
    for i in range(1, n):
        k = a + i*delta_x
        if i % 2 == 0:
            approx = approx + 2 * f(k)
        else:
            approx = approx + 4 * f(k)
    approx = approx * delta_x/3
    return approx

def simpson38(f, a, b, n):
    # Codigo del metodo simpson 3/8
    delta_x = (b - a) / n
    approx = f(a) + f(b)
    for i in range(1, n):
        k = a + i * delta_x
        if (i % 3 == 0):
            approx = approx + 2 * f(k)
        else:
            approx = approx + 3 * f(k)
    approx *= (3 * delta_x) / 8
    return approx

if __name__ == "__main__":
    app.run(debug=True)
