from tkinter import *
import math
import re

# ---------- Main Window ----------
root = Tk()
root.title("Ultimate Scientific Calculator Pro")
root.geometry("750x800")
root.resizable(False, False)
root.configure(bg="#1E1E1E")

# ---------- Input Field ----------
entry = Entry(root, width=20, borderwidth=4, font=('Arial', 24), justify='right',
              bg="#2B2B2B", fg="#FFD700", insertbackground="#FFD700")
entry.grid(row=0, column=0, columnspan=6, pady=20, padx=10, sticky="ew")

# ---------- Memory Display ----------
memory_label = Label(root, text="M: 0", font=('Arial', 10), bg="#1E1E1E", fg="#888888")
memory_label.grid(row=1, column=0, columnspan=6, sticky="w", padx=15)

# ---------- Memory ----------
memory = 0


# ---------- Helper Functions ----------
def update_memory_display():
    memory_label.config(text=f"M: {memory:.6g}")


def click(value):
    if value == 'e^x':
        entry.insert(END, 'exp(')
    elif value == 'x²':
        entry.insert(END, '^2')
    elif value == 'x³':
        entry.insert(END, '^3')
    elif value == '10^x':
        entry.insert(END, '10^(')
    elif value == '1/x':
        current = entry.get()
        if current:
            entry.delete(0, END)
            entry.insert(0, f'1/({current})')
    elif value == '%':
        current = entry.get()
        if current:
            try:
                result = eval_expression(current) / 100
                entry.delete(0, END)
                entry.insert(0, format_result(result))
            except:
                entry.delete(0, END)
                entry.insert(0, "Error")
    else:
        entry.insert(END, str(value))


def clear():
    entry.delete(0, END)


def delete():
    current = entry.get()
    entry.delete(0, END)
    entry.insert(0, current[:-1])


def memory_clear():
    global memory
    memory = 0
    update_memory_display()


def memory_recall():
    entry.delete(0, END)
    entry.insert(0, format_result(memory))


def memory_add():
    global memory
    try:
        result = eval_expression(entry.get())
        memory += result
        update_memory_display()
    except:
        entry.delete(0, END)
        entry.insert(0, "Error")


def memory_subtract():
    global memory
    try:
        result = eval_expression(entry.get())
        memory -= result
        update_memory_display()
    except:
        entry.delete(0, END)
        entry.insert(0, "Error")


def format_result(result):
    """Format result to remove trailing zeros and handle scientific notation"""
    if isinstance(result, (int, float)):
        if isinstance(result, float):
            if abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                return f"{result:.6e}"
            elif result.is_integer():
                return str(int(result))
            else:
                formatted = f"{result:.10f}".rstrip('0').rstrip('.')
                return formatted
        return str(result)
    return str(result)


# ---------- Expression Evaluation ----------
def eval_expression(expr):
    """Safely evaluate mathematical expression"""
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty expression")

    # Replace constants
    expr = re.sub(r'(?<![a-zA-Z])π(?![a-zA-Z])', str(math.pi), expr)
    expr = re.sub(r'(?<![a-zA-Z])e(?![a-zA-Z])', str(math.e), expr)

    # Replace power operator
    expr = expr.replace("^", "**")

    # ---------- Factorial ----------
    def factorial_replacer(match):
        num_str = match.group(1)
        val = eval(num_str)
        if val < 0:
            raise ValueError("Negative factorial")
        if val > 170:
            raise ValueError("Factorial too large")
        return str(math.factorial(int(val)))

    expr = re.sub(r'\(([^()]+)\)!', factorial_replacer, expr)
    expr = re.sub(r'(\d+(?:\.\d+)?)!', factorial_replacer, expr)

    # ---------- Square Root ----------
    expr = re.sub(r'√\(([^)]+)\)', r'math.sqrt(\1)', expr)
    expr = re.sub(r'√(\d+(?:\.\d+)?)', r'math.sqrt(\1)', expr)

    # ---------- Exponential ----------
    expr = re.sub(r'\bexp\(', 'math.exp(', expr)

    # ---------- Logs ----------
    expr = re.sub(r'\bln\(', 'math.log(', expr)
    expr = re.sub(r'\blog10\(', 'math.log10(', expr)
    expr = re.sub(r'\blog\(', 'math.log10(', expr)

    # ---------- Trig Functions ----------
    expr = re.sub(r'\bsin\(([^)]+)\)', lambda m: f'math.sin(math.radians({m.group(1)}))', expr)
    expr = re.sub(r'\bcos\(([^)]+)\)', lambda m: f'math.cos(math.radians({m.group(1)}))', expr)
    expr = re.sub(r'\btan\(([^)]+)\)', lambda m: f'math.tan(math.radians({m.group(1)}))', expr)

    # ---------- Inverse Trig ----------
    expr = re.sub(r'\bcosec\(([^)]+)\)', lambda m: f'(1/math.sin(math.radians({m.group(1)})))', expr)
    expr = re.sub(r'\bsec\(([^)]+)\)', lambda m: f'(1/math.cos(math.radians({m.group(1)})))', expr)
    expr = re.sub(r'\bcot\(([^)]+)\)', lambda m: f'(1/math.tan(math.radians({m.group(1)})))', expr)

    try:
        result = eval(expr)
        if math.isnan(result):
            raise ValueError("Result undefined")
        if math.isinf(result):
            raise ValueError("Infinity result")
        return result
    except NameError:
        raise SyntaxError("Unknown function")
    except Exception as e:
        raise


# ---------- Calculate ----------
def calculate():
    try:
        expr = entry.get()
        if not expr:
            return
        result = eval_expression(expr)
        entry.delete(0, END)
        entry.insert(0, format_result(result))
    except ZeroDivisionError:
        entry.delete(0, END)
        entry.insert(0, "Error: Div by 0")
    except ValueError as ve:
        entry.delete(0, END)
        entry.insert(0, "Error")
    except SyntaxError:
        entry.delete(0, END)
        entry.insert(0, "Syntax Error")
    except OverflowError:
        entry.delete(0, END)
        entry.insert(0, "Error: Overflow")
    except:
        entry.delete(0, END)
        entry.insert(0, "Error")


# ---------- Button Styles ----------
button_bg = "#333333"
button_fg = "#FFD700"
button_active = "#444444"

# ---------- Buttons ----------
buttons = [
    ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3), ('DEL', 2, 4), ('C', 2, 5),
    ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3), ('(', 3, 4), (')', 3, 5),
    ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3), ('^', 4, 4), ('%', 4, 5),
    ('0', 5, 0), ('.', 5, 1), ('+', 5, 2), ('√', 5, 3), ('x²', 5, 4), ('x³', 5, 5),
    ('sin', 6, 0), ('cos', 6, 1), ('tan', 6, 2), ('00', 6, 3), ('log', 6, 4), ('!', 6, 5),
    ('cosec', 7, 0), ('sec', 7, 1), ('cot', 7, 2), ('e^x', 7, 3), ('10^x', 7, 4), ('1/x', 7, 5),
    ('π', 8, 0), ('e', 8, 1), ('MC', 8, 2), ('MR', 8, 3), ('M+', 8, 4), ('M-', 8, 5),
    ('=', 9, 0)
]

# ---------- Create Buttons ----------
for (text, row, col) in buttons:
    if text == '=':
        Button(root, text=text, padx=15, pady=15, bg="#FFD700", fg="#1E1E1E",
               activebackground="#FFC300", font=('Arial', 14, 'bold'),
               command=calculate).grid(row=row, column=col, columnspan=6,
                                       sticky="nsew", padx=3, pady=3)
    elif text == 'C':
        Button(root, text=text, padx=15, pady=15, bg="#32CD32", fg="#FFFFFF",
               activebackground="#228B22", font=('Arial', 12, 'bold'),
               command=clear).grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
    elif text == 'DEL':
        Button(root, text=text, padx=15, pady=15, bg="#FF4500", fg="#FFFFFF",
               activebackground="#FF6347", font=('Arial', 10, 'bold'),
               command=delete).grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
    elif text in ['MC', 'MR', 'M+', 'M-']:
        if text == 'MC':
            cmd = memory_clear
        elif text == 'MR':
            cmd = memory_recall
        elif text == 'M+':
            cmd = memory_add
        else:
            cmd = memory_subtract
        Button(root, text=text, padx=15, pady=15, bg="#555555", fg="#FFFFFF",
               activebackground="#777777", font=('Arial', 10, 'bold'),
               command=cmd).grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
    else:
        Button(root, text=text, padx=15, pady=15, bg=button_bg, fg=button_fg,
               activebackground=button_active, font=('Arial', 11),
               command=lambda t=text: click(t)).grid(row=row, column=col,
                                                     sticky="nsew", padx=3, pady=3)

# ---------- Grid Configuration ----------
for i in range(10):
    root.grid_rowconfigure(i, weight=1)
for j in range(6):
    root.grid_columnconfigure(j, weight=1)

root.mainloop()
