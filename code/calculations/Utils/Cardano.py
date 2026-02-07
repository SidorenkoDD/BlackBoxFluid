import cmath
import math


def cbrt(z: complex | float):
    r = abs(z)
    phi = cmath.phase(z)
    res = [math.cbrt(r) * complex(math.cos((phi + 2 * math.pi * k) / 3), math.sin((phi + 2 * math.pi * k) / 3)) for k in
           range(3)]
    return [normalize(_) for _ in res]


def normalize(z: complex, eps: float = 1e-10):
    if abs(z.imag) < eps:
        return float(z.real)
    return z


def cubic_roots_cardano(a: float, b: float, c: float, d: float, only_real_roots: bool = False):
    """
    Решает кубическое уравнение a*x^3 + b*x^2 + c*x + d = 0 по методу Кардано.
    Если значение only_real_roots = True - вернет только вещественные корни (если уравнение имеет три корня, первый
    из которых вещественный, а остальные мнимые, вернется три первых вещественных корня)
    """

    if a == 0.0:
        raise TypeError('Аргумент a = 0.0, это не кубическое уравнение')

    # Нормировка
    A = b / a
    B = c / a
    C = d / a

    # Приведенное кубическое уравнение: y^3 + p y + q = 0, x = y - A/3
    p = B - A * A / 3.0
    q = 2.0 * A * A * A / 27.0 - A * B / 3.0 + C

    Q = (q / 2.0) ** 2 + (p / 3.0) ** 3

    if Q >= 0:
        sqrt_delta = math.sqrt(Q)
        alpha = math.cbrt(-q / 2.0 + sqrt_delta)
        beta = math.cbrt(-q / 2.0 - sqrt_delta)

    else:
        sqrt_delta = cmath.sqrt(Q)
        alpha_cbrts = cbrt(-q / 2.0 + sqrt_delta)
        beta_cbrts = cbrt(-q / 2.0 - sqrt_delta)

        alpha, beta, flag = None, None, False
        for alpha in alpha_cbrts:
            for beta in beta_cbrts:
                if abs(normalize(alpha * beta) + p / 3.0) < 1e-10:
                    flag = True
                    break
            if flag:
                break

    if any(_ is None for _ in [alpha, beta]):
        raise ValueError('Не найдено подходящих значений alpha и beta в методе Кардано')

    omega = complex(-0.5, math.sqrt(3) / 2.0)
    omega2 = complex(-0.5, -math.sqrt(3) / 2.0)

    y1 = alpha + beta
    y2 = omega * alpha + omega2 * beta
    y3 = omega2 * alpha + omega * beta

    shift = A / 3.0
    roots = [y1 - shift, y2 - shift, y3 - shift]
    roots = list(normalize(r) for r in roots)

    if only_real_roots:
        real_roots = list(filter(lambda z: isinstance(z, (int, float)), roots))
        if len(real_roots) == 1:
            roots = real_roots * 3
        else:
            roots = real_roots

    return roots


if __name__ == '__main__':
    import time

    start = time.perf_counter()
    res = cubic_roots_cardano(1, -1, 1, -1, only_real_roots=True)
    end = time.perf_counter()

    print(f'Корни: {res}\nВремя расчета: {(end - start) * 1e6} ms')
