# importing necessery libs 
import tkinter as tk
from tkinter import messagebox
from nltk import CFG
import nltk

# تشخیص نوع بازگشتی چپ یا راست از روی گرامر
def detect_recursion_type(rules):
    left_recursive = []
    right_recursive = []

    for var in rules:
        for rule in rules[var]:
            if rule and rule[0] == var:
                if var not in left_recursive:
                    left_recursive.append(var)
            if rule and rule[-1] == var:
                if var not in right_recursive:
                    right_recursive.append(var)

    return left_recursive, right_recursive

# پارس کردن گرامر بصورت عمقی
def parse_recursive(alephba, rules, start_symbol):
    if not alephba and not start_symbol:
        return True, []
    if not alephba or not start_symbol:
        return False, alephba

    for rule in rules[start_symbol]:
        remaining_alephba = alephba
        for symbol in rule:
            if symbol.islower():
                if remaining_alephba and remaining_alephba[0] == symbol:
                    remaining_alephba = remaining_alephba[1:]
                else:
                    break
            else:
                success, remaining_alephba = parse_recursive(remaining_alephba, rules, symbol)
                if not success:
                    break
        else:
            return True, remaining_alephba

    return False, alephba

def parse_iterative(alephba, rules, start_symbol):
    stack = [(start_symbol, alephba)]
    while stack:
        current_symbol, current_alephba = stack.pop()
        if not current_symbol and not current_alephba:
            return True, []
        if not current_alephba or not current_symbol:
            continue

        for rule in rules.get(current_symbol, []):
            remaining_alephba = current_alephba[:]
            temp_stack = []
            match = True
            for symbol in rule:
                if symbol.islower():
                    if remaining_alephba and remaining_alephba[0] == symbol:
                        remaining_alephba = remaining_alephba[1:]
                    else:
                        match = False
                        break
                else:
                    temp_stack.append((symbol, remaining_alephba))
            if match:
                if not remaining_alephba and not temp_stack:
                    return True, remaining_alephba
                stack.extend(temp_stack[::-1])

    return False, alephba

def parse(alephba, rules, start_symbol, left_recursive, right_recursive):
    if left_recursive and right_recursive:
        grammar_string = ""
        for var, productions in rules.items():
            for production in productions:
                grammar_string += f"{var} -> {' '.join(production)}\n"
        grammar = CFG.fromstring(grammar_string)
        parser = nltk.ChartParser(grammar)
        try:
            parses = list(parser.parse(alephba))
            if parses:
                return True, []
            else:
                return False, alephba
        except ValueError:
            return False, alephba
    elif left_recursive:
        return parse_iterative(alephba, rules, start_symbol)
    else:
        return parse_recursive(alephba, rules, start_symbol)

def check_grammar():
    grammar_input = grammar_entry.get("1.0", tk.END).strip()
    string_input = string_entry.get().strip()

    rules = {}
    for line in grammar_input.splitlines():
        left, right = line.split('->')
        left = left.strip()
        right = [r.strip().split() for r in right.strip().split('|')]
        if left in rules:
            rules[left].extend(right)
        else:
            rules[left] = right

    left_recursive, right_recursive = detect_recursion_type(rules)

    if left_recursive:
        recursion_info = f"Left-recursive non-terminals: {', '.join(left_recursive)}\n"
    else:
        recursion_info = "No left-recursive non-terminals detected.\n"

    if right_recursive:
        recursion_info += f"Right-recursive non-terminals: {', '.join(right_recursive)}"
    else:
        recursion_info += "No right-recursive non-terminals detected."

    success, remaining_alephba = parse(list(string_input), rules, 'S', left_recursive, right_recursive)

    if success and not remaining_alephba:
        result_label.config(text=f"The string '{string_input}' belongs to the language of the given grammar.", fg="green")
    else:
        result_label.config(text=f"The string '{string_input}' does NOT belong to the language of the given grammar.", fg="red")

    messagebox.showinfo("Recursion Detection", recursion_info)


window = tk.Tk()
window.title("Grammar Checker")

grammar_label = tk.Label(window, text="Enter the grammar (like this: 'S -> a S b' or 'S -> a b'):")
grammar_label.pack(pady=10)

grammar_entry = tk.Text(window, height=10, width=50)
grammar_entry.pack()

string_label = tk.Label(window, text="Enter the string to be parsed:")
string_label.pack(pady=10)

string_entry = tk.Entry(window, width=50)
string_entry.pack()

check_button = tk.Button(window, text="Check Grammar", command=check_grammar)
check_button.pack(pady=10)

result_label = tk.Label(window, text="", fg="black")
result_label.pack(pady=10)

window.mainloop()