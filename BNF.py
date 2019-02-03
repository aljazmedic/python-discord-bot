#TODO BNF
#TODO Clap @ yourself
EXPR_SEP = ["(", ")"]
TERM_SEP = ["+", "-"]
FACT_SEP = ["*", "/"]
import sys

def tprint(*args, **kwargs):
	level = dict(kwargs).get("level", 0)
	if dict(kwargs).get("log", False):
		return
	bk = dict(kwargs).get("bk", False)
	#if bk:
	#	level-=1
	bk = "|->" if not bk else "%s<-"%args[-1]
	out = " ".join([str(x) for x in args])
	if level > 0:
		out = "|  "*(level-1) + bk+out

	print(out)

def tokenize(expression, delimer=None,
		sign_list=['(', ')', '*', '/', '+', '-']):
	if delimer:
		return expression.split(delimer)
	rt = []
	i = 0
	while i < len(expression):
		start_i = i
		i+=1
		if expression[start_i] in sign_list:
			rt.append(expression[start_i])
		else:
			while i < len(expression) and expression[i] not in sign_list:
				i+=1
			rt.append(expression[start_i:i])
	return rt

def get_next(expression, index=0,
	sign_list=['(', ')', '*', '/', '+', '-']):
	if len(expression) <= index:
		return None
	start_index = index
	stack_parenth = {"(":0,}
	ends = {")":"("}

	not_search_for_parenthasis = all([t not in stack_parenth.keys() for t in sign_list])

	if expression[start_index] in sign_list:
		return expression[start_index]
	if expression[start_index] in stack_parenth:
		stack_parenth[expression[start_index]]+=1
	index+=1

	if not_search_for_parenthasis:
		while index < len(expression) and \
		(sum(stack_parenth.values()) > 0 or expression[index] not in sign_list):
			if expression[index] in stack_parenth:
				stack_parenth[expression[index]]+=1
			elif expression[index] in ends:
				stack_parenth[ends[expression[index]]]-=1
			index+=1
	else:
		while index < len(expression) and expression[index] not in sign_list:
			index+=1

	#print("Finding", sign_list, not_search_for_parenthasis,expression[start_index:], expression[start_index:index])
	return expression[start_index:index]

def eval_expression(whole_expr, s=0, log=True, lvl=0):
	trm = get_next(whole_expr, s, sign_list=TERM_SEP)
	tprint("first term in", whole_expr[s:], "is", trm, log=log, level=lvl+1)
	rt = eval_term(trm, log=log, lvl=lvl+1)
	start = s + len(trm)

	operation = get_next(whole_expr, start, TERM_SEP)
	if operation:
		tprint("operation", operation, log=log, level=lvl+1, bk=True)
	if operation == None:
		#end of +/- chain
		return rt
	start+=1
	next_eval = whole_expr[start:]
	if next_eval == None:
		return None
	elif operation in TERM_SEP:
		next_e = eval_expression(whole_expr, start, log=log, lvl=lvl)
		if next_e:
			rt += next_e
			rt += [operation]
			tprint(rt, log=log, level=lvl, bk=True)
		return rt
	else:
		raise Exception("Not a valid expression", whole_expr)

def eval_term(whole_expr, s=0, log=True, lvl=0):
	fct = get_next(whole_expr, s, sign_list=FACT_SEP)
	tprint("first factor in", whole_expr[s:], "is", fct, log=log, level=lvl+1)
	rt = eval_factor(fct, log=log, lvl=lvl+1)
	start = s+len(fct)
	operation = get_next(whole_expr, start, sign_list=FACT_SEP)
	if operation:
		tprint("operation", operation, log=log, level=lvl+1, bk=True)
	if operation == None:
		#end of *// chain
		return rt
	start+=1

	next_trm = whole_expr[start:]
	if next_trm == None:
		return None
	elif operation in FACT_SEP:
		next_t = eval_term(whole_expr, start, log=log, lvl=lvl)
		if next_t:
			rt += next_t
			rt += [operation]
			tprint(rt, log=log, level=lvl, bk=True)
		return rt
	else:
		raise Exception("Not a valid term ", whole_expr)

def eval_factor(whole_expr, s=0, log=True, lvl=0):
	expr = get_next(whole_expr, s, EXPR_SEP)
	start = s + len(expr)
	try:
		r = [float(expr)]
		tprint("found a number", expr, log=log, level=lvl, bk=True)
		return r
	except:
		if expr == "(":
			expr = get_next(whole_expr, start, sign_list=EXPR_SEP)
			tprint("first expression in ", whole_expr[s:], "is", expr, log=log, level=lvl)
			rt = eval_expression(expr, log=log, lvl=lvl+1)
			start += len(expr) 
		if get_next(whole_expr, start, sign_list=EXPR_SEP) == ")":
			return rt
		else:
			tprint(") expected ", whole_expr[start:], log=log, level=lvl)
			raise Exception(") expected ", whole_expr, "@", start)

def postfix_calculator(input_array):
	table = {
		"+":lambda x, y: x+y,
		"-":lambda x, y: x-y,
		"*":lambda x, y: x*y,
		"/":lambda x, y: x/y if y != 0 else (None)
	}
	stack = []
	for e in input_array:
		if e in table:
			second = stack.pop()
			stack.append(table[e](stack.pop(), second))
		else:
			stack.append(e)
	return stack[0]

def eval_expression_complete(input_expression, log=False):
	ret = {}
	ret["post_fix"] = eval_expression(input_expression, log=log)
	ret["result"] = postfix_calculator(ret["post_fix"])
	return ret

if __name__ == '__main__':
	expression = sys.argv[1] #14
	print(tokenize(expression))
	postfix = eval_expression(expression)
	print(postfix_calculator(postfix))