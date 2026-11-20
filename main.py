from arithmetic import add
# Изменение для практической работы №4
import ast
import math
import tkinter as tk
from tkinter import messagebox


class Calculator:
    """Графический калькулятор с проверкой выражений и учетом приоритетов."""

    FUNCTIONS = {
        "sqrt": math.sqrt,
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "log": math.log10,
        "ln": math.log,
        "abs": abs,
        "factorial": math.factorial,
    }
    CONSTANTS = {"pi": math.pi, "e": math.e}

    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.resizable(False, False)
        self.expression = tk.StringVar()

        self.entry = tk.Entry(
            root, textvariable=self.expression, font=("Arial", 22),
            justify="right", width=22, bd=8, relief="groove"
        )
        self.entry.grid(row=0, column=0, columnspan=5, padx=8, pady=10)
        self.entry.focus_set()

        buttons = [
            ("7", "8", "9", "/", "C"),
            ("4", "5", "6", "*", "⌫"),
            ("1", "2", "3", "-", "("),
            ("0", ".", "=", "+", ")"),
            ("sqrt(", "sin(", "cos(", "tan(", "^"),
            ("log(", "ln(", "abs(", "pi", "e"),
        ]

        for r, row in enumerate(buttons, start=1):
            for c, label in enumerate(row):
                command = lambda value=label: self.press(value)
                tk.Button(
                    root, text=label, width=7, height=2,
                    font=("Arial", 12), command=command
                ).grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

        tk.Button(
            root, text="Вычислить", height=2, font=("Arial", 12, "bold"),
            command=self.calculate
        ).grid(row=7, column=0, columnspan=5, padx=5, pady=7, sticky="nsew")

        self.root.bind("<Return>", lambda event: self.calculate())
        self.root.bind("<Escape>", lambda event: self.clear())
        self.root.bind("<BackSpace>", lambda event: self.press("⌫"))
        self.root.bind("<Control-l>", lambda event: self.clear())

    def press(self, value):
        if value == "C":
            self.clear()
        elif value == "⌫":
            self.expression.set(self.expression.get()[:-1])
        elif value == "=":
            self.calculate()
        elif value == "^":
            self.expression.set(self.expression.get() + "**")
        else:
            self.expression.set(self.expression.get() + value)

    def clear(self):
        self.expression.set("")

    def safe_calculate(self, expression):
        """Разбирает выражение и разрешает только безопасные математические операции."""
        expression = expression.replace("^", "**")
        tree = ast.parse(expression, mode="eval")

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.BinOp):
                left, right = visit(node.left), visit(node.right)
                operations = {
                    ast.Add: lambda: left + right,
                    ast.Sub: lambda: left - right,
                    ast.Mult: lambda: left * right,
                    ast.Div: lambda: left / right,
                    ast.FloorDiv: lambda: left // right,
                    ast.Mod: lambda: left % right,
                    ast.Pow: lambda: left ** right,
                }
                operation = operations.get(type(node.op))
                if operation is None:
                    raise ValueError("Недопустимая операция")
                return operation()
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = visit(node.operand)
                return value if isinstance(node.op, ast.UAdd) else -value
            if isinstance(node, ast.Name):
                if node.id in self.CONSTANTS:
                    return self.CONSTANTS[node.id]
                raise ValueError("Неизвестная константа")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id
                if name not in self.FUNCTIONS or len(node.args) != 1 or node.keywords:
                    raise ValueError("Неизвестная функция или неверные аргументы")
                return self.FUNCTIONS[name](visit(node.args[0]))
            raise ValueError("Выражение содержит недопустимые элементы")

        result = visit(tree)
        if isinstance(result, complex) or not math.isfinite(float(result)):
            raise ValueError("Результат не является конечным числом")
        return result

    def calculate(self):
        source = self.expression.get().strip()
        if not source:
            messagebox.showwarning("Ввод данных", "Введите математическое выражение.")
            return
        try:
            result = self.safe_calculate(source)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression.set(str(result))
        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "Деление на ноль невозможно.")
        except (SyntaxError, ValueError, TypeError, OverflowError) as error:
            messagebox.showerror("Ошибка вычисления", f"Проверьте выражение.\n{error}")


if __name__ == "__main__":
    window = tk.Tk()
    app = Calculator(window)
    window.mainloop()
