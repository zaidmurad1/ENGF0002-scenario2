res = {
        "truthTableHeader": [],
        "truthTable": [[]]
    }

class Node:
    def __init__(self, operator=None, variable=None, left=None, right=None):
        self.operator = operator
        self.variable = variable
        self.left = left
        self.right = right

    def print_tree(self, level=0):
        if self.variable is not None:
            return " " * level + str(self.variable) + "\n"
        else:
            result = " " * level + str(self.operator) + "\n"
            if self.left:
                result += self.left.print_tree(level + 1)
            if self.right:
                result += self.right.print_tree(level + 1)
            return result

    def evaluate(self, values):
        if self.variable is not None:
            return values[self.variable]
        elif self.operator == '!':
            return not self.right.evaluate(values)
        elif self.operator == '&':
            return self.left.evaluate(values) and self.right.evaluate(values)
        elif self.operator == '|':
            return self.left.evaluate(values) or self.right.evaluate(values)
        elif self.operator == '-':
            return (not self.left.evaluate(values)) or self.right.evaluate(values)

def build_expression_tree(expression):
    expression = expression.replace(" ", "")

    operator, variable = find_operator(expression)

    if expression[0] == '!' and operator == ')' and expression.count('!') > 1:
        num = expression.count('!')
        if num % 2 == 0:
            # print(expression, "==>", expression.replace('!', ""))
            expression = expression.replace('!', "")

    if operator == '-':
        # if the operator == '->'
        return show_imply(expression, variable)
        # return Node(operator='|', left=build_expression_tree('!'+expression[:variable]), right=build_expression_tree(expression[variable+2:]))

    if expression[0] == '!' and expression[1] == '(' and expression[3] == ')':
        return Node(operator='!', right=build_expression_tree(expression[2:-1]))

    if expression[0] == '!' and operator == ')':
        operator2, variable2 = find_operator(expression[2:-1])
        return negation_disjunction(expression, expression[2:-1], operator2, variable2)
        # return Node(operator='!', right=build_expression_tree(expression[2:len(expression)-1]))

    if expression[0] == '!' and operator is None:
        return Node(operator='!', right=build_expression_tree(expression[1:]))

    if operator is None:
        return Node(variable=expression)

    if operator == ')':
        # if the whole expression is enclosed in brackets
        return build_expression_tree(expression[1:-1])

    return Node(operator=operator, left=build_expression_tree(expression[:variable]),
                right=build_expression_tree(expression[variable + 1:]))

def find_operator(expression):
    # find the outer operator
    brackets = 0
    if expression.find('(') == -1:
        if expression.find('-') != -1:
            return '-', expression.find('-')

    for i, char in enumerate(expression):
        if char == '(':
            brackets += 1
        elif char == ')':
            brackets -= 1
        elif brackets == 0 and char in ['&', '|', '-']:
            return char, i

    if brackets == 0 and expression[len(expression) - 1] == ')':
        return char, i

    return None, i

def get_variables(node):
    if node is None:
        return []
    if node.variable is not None:
        return node.variable
    left_variables = get_variables(node.left)
    right_variables = get_variables(node.right)
    return sorted(set(left_variables).union(right_variables))

def negation_disjunction(first_expression, expression, operator, variable):
    # changes the negation disjunction for a dnf style
    change = ''
    if operator == '&':
        change = '|'
    elif operator == '|':
        change = '&'
    # print(first_expression, "==>", '!' + expression[:variable], change, '!' + expression[variable + 1:])
    return Node(operator=change,
                left=build_expression_tree('!' + expression[:variable]),
                right=build_expression_tree('!' + expression[variable + 1:]))

def show_imply(expression, variable):
    # converts imply to bool operators
    # print(expression, "==>", '!' + expression[:variable], '|', expression[variable + 2:])
    if expression[:variable][0] == '(' and expression[:variable][-1] == ')':
        return Node(operator='|',
                    left=build_expression_tree('!' + expression[:variable]),
                    right=build_expression_tree(expression[variable + 2:]))
    return Node(operator='|',
                left=build_expression_tree('!' + '(' + expression[:variable] + ')'),
                right=build_expression_tree(expression[variable + 2:]))

def build_truth_table(expression, variables):
    node = build_expression_tree(expression)
    n = len(variables)
    table = []
    for i in range(2 ** n):
        values = {}
        for j in range(n):
            # This generate all the combination of True and False of each variable
            values[variables[j]] = bool((i // 2 ** j) % 2)
        result = node.evaluate(values)
        row = [values[var] for var in variables] + [result]
        table.append(row)
    table_header = variables
    table_header.append(expression)
    res["truthTableHeader"] = table_header # TRUTH TABLE GEN RETURN
    res["truthTable"] = table # TRUTH TABLE GEN RETURN
    return table

def print_truth_table(expression, variables, table):
    header = ' | '.join(variables) + ' | ' + expression
    list = variables
    list.append(expression)
    print(header)
    print('-' * len(header))
    for row in table:
        row_str = ' | '.join(['1' if val else '0' for val in row])
        row_list = [True if val else False for val in row]
        print(row_str)

def canonical_DNF(variables, table):
    # Find all the rows with true result
    true_rows = [row[:-1] for row in table if row[-1]]
    CDNF = ' | '.join(
        ['(' + ' & '.join([var if val else '!' + var for var, val in zip(variables, row)]) + ')' for row in
            true_rows])
    # res["answer"] = CDNF # ANSWER GEN RETURN
    return CDNF

def is_DNF(receivedAnswer):
    isCorrect = False
    receivedAnswer = receivedAnswer.replace(" ", "")
    if receivedAnswer.find('->') != -1:
        return isCorrect
    brackets = 0
    alpha_num = 0
    not_num = 0
    alpha_counter = 0
    alpha_list = []
    for i, char in enumerate(receivedAnswer):
        if char == '(':
            brackets += 1
        elif char == ')':
            brackets -= 1
        if char.isalpha():
            if not_num != 0:
                not_num = 0
            alpha_counter += 1
            alpha_num += 1
        elif not char.isalpha():
            alpha_num -= 1
        if char == '!':
            not_num +=1
        if brackets == 0:
            alpha_list.append(alpha_counter)
            alpha_counter = 0
        elif alpha_num > 1 or brackets > 1 or not_num > 1:
            return isCorrect
        elif brackets == 0 and char == '&':
            return isCorrect
        elif brackets > 0 and char == '|':
            return isCorrect
    for n, i in enumerate(alpha_list):
        if n % 2 == 0 and i != alpha_list[0]:
            return isCorrect
    if brackets != 0:
        return isCorrect
    isCorrect = True
    return isCorrect

expression = "(p & q -> r) & (!p -> !q | r)" # truth table gen expression
# expression = "((p -> q) | (r -> !q)) & ((p & r) -> q)" # answer gen expression
node = build_expression_tree(expression)
# print(get_variables(node))
# print(node.print_tree())
# print(build_truth_table(expression, get_variables(node)))
print_truth_table(expression, get_variables(node), build_truth_table(expression, get_variables(node)))
print("Truth table in 2d array:", build_truth_table(expression, get_variables(node)))
print("Canonical DNF:", canonical_DNF(get_variables(node), build_truth_table(expression, get_variables(node))))

receivedAnswer = "(!p & !q & !r) | (!p & !q & r) | (!p & q & !r) | (!p & q & r) | (p & !q )"
print(is_DNF(receivedAnswer))
receivedAnswer2 = "(!p & !q & !r) | (!p & !q & r) | (!p & q & r) | (p & !q & !r) | (p & !q & r) | (p & q & r)"
print(is_DNF(receivedAnswer2))
receivedAnswer3 = "(!p & !q & !r) | (p & !q & r) | (p & q & r) | (!p & !q & r) | (p & !q & !r) | (!p & q & r)"
print(is_DNF(receivedAnswer3))
