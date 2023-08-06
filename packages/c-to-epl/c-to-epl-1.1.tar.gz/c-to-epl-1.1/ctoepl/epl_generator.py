#------------------------------------------------------------------------------
# pycparser: c_generator.py
#
# C code generator from pycparser AST nodes.
#
# Eli Bendersky [http://eli.thegreenplace.net]
# License: BSD
#------------------------------------------------------------------------------
from . import c_ast
import re
used_i = []
used_u = []
used_l = []
used_ul = []
used_f = []
used_d = []

assignments = []

current_fct = None;
class VariableMappings(object):

    def get_free(self, arr):
        for i in range(20000):
            if i in arr:
                continue
            return i;
        raise Exception("Memory exhausted, you are using to many int variables")

    def get_free_i(self):
        return self.get_free(used_i)
    def get_free_u(self):
        return self.get_free(used_u)
    def get_free_l(self):
        return self.get_free(used_l)
    def get_free_ul(self):
        return self.get_free(used_ul)
    def get_free_f(self):
        return self.get_free(used_f)
    def get_free_d(self):
        return self.get_free(used_d)

    def add_i(self, variable):
        f = self.get_free_i();
        self.mappings[variable] =['i', f]
        used_i.append(f)
        return "i["+str(f)+"]"

    def add_u(self, variable):
        f = self.get_free_u();
        self.mappings[variable] =['u', f]
        used_u.append(f)
        return "u["+str(f)+"]"

    def add_l(self, variable):
        f = self.get_free_l();
        self.mappings[variable] =['l', f]
        used_l.append(f)
        return "l["+str(f)+"]"

    def add_ul(self, variable):
        f = self.get_free_ul();
        self.mappings[variable] =['ul', f]
        used_ul.append(f)
        return "ul["+str(f)+"]"

    def add_d(self, variable):
        f = self.get_free_d();
        self.mappings[variable] =['d', f]
        used_d.append(f)
        return "d["+str(f)+"]"

    def add_f(self, variable):
        f = self.get_free_f();
        self.mappings[variable] =['f', f]
        used_f.append(f)
        return "f["+str(f)+"]"

    def addFuncArgs(self,function,arglist):
        self.funcargs[function] = arglist

    def getFuncArgs(self,function):
        return self.funcargs[function]


    def get(self, variable):
        if variable in self.mappings:
            return self.mappings[variable][0] + "[" + str(self.mappings[variable][1]) + "]"
        else:
            if self.prev==None:
                raise Exception("Unknown variable " + variable)
            else:
                return self.prev.get(variable)

    mappings = {}
    funcargs = {}
    prev = None

class EPLGenerator(object):
    """ Uses the same visitor pattern as c_ast.NodeVisitor, but modified to
        return a value from each visit method, using string accumulation in
        generic_visit.
    """
    def __init__(self):
        # Statements start with indentation of self.indent_level spaces, using
        # the _make_indent method
        #
        self.indent_level = 0

    def _make_indent(self):
        return ' ' * self.indent_level

    def visit(self, node, mappings = None):

        if mappings == None:
            raise Exception("YOU FORGOT THE MAPPING")

        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node, mappings)

    def generic_visit(self, node, mappings):
        #~ print('generic:', type(node))
        if node is None:
            return ''
        else:
            return ''.join(self.visit(c, mappings) for c_name, c in node.children())

    def visit_Constant(self, n, mappings):
        return n.value

    def visit_ID(self, n, mappings):
        res = n.name
        try:
            res = mappings.get(res)
        except Exception as e:
            pass
        return res

    def visit_Pragma(self, n, mappings):
        raise Exception('Pragma is not supported in ePL') 

    def visit_ArrayRef(self, n, mappings):
        arrref = self._parenthesize_unless_simple(n.name, mappings)
        gh = arrref + '[' + self.visit(n.subscript, mappings) + ']'
        return mappings.get(gh)

    def visit_StructRef(self, n, mappings):
        raise Exception('Structs is not supported in ePL')

    def visit_FuncCall(self, n, mappings):
        fref = self._parenthesize_unless_simple(n.name, mappings)
        argg=self.visit(n.args, mappings)

        arglist = [x.strip() for x in argg.split(",")]
        varlist = mappings.getFuncArgs(n.name.name)

        s = '';
        for i in range(len(arglist)):
            s += varlist[i] + ' = ' + arglist[i] + "; "

        return s + n.name.name + '()'

    def visit_UnaryOp(self, n, mappings):
        operand = self._parenthesize_unless_simple(n.expr, mappings)
        if n.op == 'p++':
            return '%s++' % operand
        elif n.op == 'p--':
            return '%s--' % operand
        elif n.op == 'sizeof':
            raise Exception("sizeof() is not supported in ePl")
        else:
            return '%s%s' % (n.op, operand)

    def visit_BinaryOp(self, n, mappings):
        lval_str = self._parenthesize_if(n.left,
                            lambda d: not self._is_simple_node(d), mappings)
        rval_str = self._parenthesize_if(n.right,
                            lambda d: not self._is_simple_node(d), mappings)
        return '%s %s %s' % (lval_str, n.op, rval_str)

    def visit_Assignment(self, n, mappings):
        varBB = self.visit(n.lvalue, mappings)
        if varBB not in assignments:
            assignments.append(varBB);
        if isinstance(n.rvalue, c_ast.FuncCall):
            fc = n.rvalue.name.name
            var = mappings.get(fc)

            rval_str = self._parenthesize_if(
                                n.rvalue,
                                lambda n: isinstance(n, c_ast.Assignment), mappings)
            return '%s; %s %s %s' % (rval_str,varBB, n.op, var)
        else:
            rval_str = self._parenthesize_if(
                                n.rvalue,
                                lambda n: isinstance(n, c_ast.Assignment), mappings)
            return '%s %s %s' % (varBB, n.op, rval_str)

    def visit_IdentifierType(self, n, mappings):
        return ' '.join(n.names)

    def _visit_expr(self, n, mappings):
        if isinstance(n, c_ast.InitList):
            return '{' + self.visit(n, mappings) + '}'
        elif isinstance(n, c_ast.ExprList):
            return '(' + self.visit(n, mappings) + ')'
        else:
            return self.visit(n, mappings)

    def visit_Decl(self, n, mappings, no_type=False):
        # no_type is used when a Decl is part of a DeclList, where the type is
        # explicitly only for the first declaration in a list.
        #

        if no_type:
            raise Exception("Declaration must be typed in ePL")

        s = self._generate_decl(n, mappings)

        if n.bitsize: raise Exception("Bitsize is not supported in ePL")
        if n.init:

            var = self._generate_decl(n, mappings)

            if var not in assignments:
                assignments.append(var);
            if isinstance(n.init, c_ast.FuncCall):
                fc = n.init.name.name
                var = mappings.get(fc)
                s = '%s; %s %s %s' % (self._visit_expr(n.init, mappings),var, '=', var)
            else:
                s = var + ' = ' + self._visit_expr(n.init, mappings)
        return s

    def visit_DeclList(self, n, mappings):
        s = self.visit(n.decls[0], mappings)
        if len(n.decls) > 1:
            s += ', ' + ', '.join(self.visit_Decl(decl, mappings, no_type=True)
                                    for decl in n.decls[1:])
        return s

    def visit_Typedef(self, n, mappings):
        raise Exception('Typedefs is not supported in ePL')

    def visit_Cast(self, n, mappings):
        s = '(' + self._generate_type(n.to_type, mappings) + ')'
        return s + ' ' + self._parenthesize_unless_simple(n.expr, mappings)

    def visit_ExprList(self, n, mappings):
        visited_subexprs = []
        for expr in n.exprs:
            visited_subexprs.append(self._visit_expr(expr, mappings))
        return ', '.join(visited_subexprs)

    def visit_InitList(self, n, mappings):
        visited_subexprs = []
        for expr in n.exprs:
            visited_subexprs.append(self._visit_expr(expr, mappings))
        return ', '.join(visited_subexprs)

    def visit_Enum(self, n, mappings):
        raise Exception('Enums is not supported in ePL')

    def visit_Enumerator(self, n, mappings):
        if not n.value:
            return '{indent}{name},\n'.format(
                indent=self._make_indent(),
                name=n.name,
            )
        else:
            return '{indent}{name} = {value},\n'.format(
                indent=self._make_indent(),
                name=n.name,
                value=self.visit(n.value),
            )

    def visit_FuncDef(self, n, mappings):
        global current_fct
        fg = VariableMappings()
        fg.prev = mappings
        decl = self.visit(n.decl, fg)
        nm = n.decl.name
        current_fct = nm;
        self.indent_level = 0
        body = self.visit(n.body,fg)
        if n.param_decls:
            raise Exception("Parameter declarations in functions are not supported in ePL")
        else:
            return decl + '\n' + body + '\n'

    def visit_FileAST(self, n, mappings):

        s = ''
        for ext in n.ext:
            if isinstance(ext, c_ast.FuncDef):
                s += self.visit(ext, mappings)
            elif isinstance(ext, c_ast.Pragma):
                s += self.visit(ext, mappings) + '\n'
            else:
                mp = self.visit(ext, mappings)
                if mp.strip()!="":
                    s += mp + ';\n'


        body = ""
        if len(used_i)>0: body+="array_int "+str(max(used_i)+1)+"\n"
        if len(used_u)>0: body+="array_uint "+str(max(used_u)+1)+"\n"
        if len(used_l)>0: body+="array_long "+str(max(used_l)+1)+"\n"
        if len(used_ul)>0: body+="array_ulong "+str(max(used_ul)+1)+"\n"
        if len(used_d)>0: body+="array_double "+str(max(used_d)+1)+"\n"
        if len(used_f)>0: body+="array_float "+str(max(used_f)+1)+"\n"


        return body+s

    def visit_Compound(self, n, mappings):
        s = self._make_indent() + '{\n'
        nmap = VariableMappings()
        nmap.prev = mappings
        self.indent_level += 2
        if n.block_items:
            s += ''.join(self._generate_stmt(stmt,nmap) for stmt in n.block_items)
        self.indent_level -= 2
        s += self._make_indent() + '}\n'
        return s

    def visit_CompoundLiteral(self, n, mappings):
        return '(' + self.visit(n.type,mappings) + '){' + self.visit(n.init,mappings) + '}'


    def visit_EmptyStatement(self, n, mappings):
        return ';'

    def visit_ParamList(self, n, mappings):
        return ', '.join(self.visit(param, mappings) for param in n.params)

    def visit_Return(self, n, mappings):
        global current_fct

        if current_fct=="main":
            if len(assignments)<4:
                raise Exception("You need to make at least 4 different assignments")
            return "verify_pow("+assignments[-1]+", "+assignments[-2]+", "+assignments[-3]+", "+assignments[-4]+"); verify_bty(" + self.visit(n.expr, mappings) + ");"
        else:
            current_slot = mappings.get(current_fct)
            s = current_slot + ' = '
            if n.expr: s += self.visit(n.expr, mappings)
            return s + ';'

    def visit_Break(self, n, mappings):
        return 'break;'

    def visit_Continue(self, n, mappings):
        return 'continue;'

    def visit_TernaryOp(self, n, mappings):
        raise Exception("No tenary operations allowed in ePL")

    def visit_If(self, n, mappings):
        s = 'if ('
        if n.cond: s += self.visit(n.cond, mappings)
        s += ')\n'
        s += self._generate_stmt(n.iftrue, mappings,add_indent=True)
        if n.iffalse:
            s += self._make_indent() + 'else\n'
            s += self._generate_stmt(n.iffalse, mappings, add_indent=True)
        return s

    def visit_For(self, n, mappings):

        jp = VariableMappings()
        jp.prev = mappings
        s = 'repeat ('
        m1 = ""
        m2=""
        m3=""
        if n.init: m1 = self.visit(n.init, jp)

        #s += ';'
        if n.cond: m2 = self.visit(n.cond, jp)
        #s += ';'
        if n.next: m3 = self.visit(n.next, jp)

        #s += ')\n'
        g0=re.search("(.\[[0-9]*\])( )*=( )*0",m1)
        g1=re.search(".\[[0-9]*\]( )*<(.*)",m2)
        if not g0:
            raise Exception("Wrong init: Only for loops of this type are allowed: for(int x=0;i<15;i++)")
        if not g1:
            raise Exception("Wrong cond: Only for loops of this type are allowed: for(int x=0;i<15;i++)")
        if not re.search(".\[[0-9]*\]( )*\+\+",m3):
            raise Exception("Wrong next: Only for loops of this type are allowed: for(int x=0;i<15;i++)")
        s += g0.group(1) + ", " + g1.group(2).strip() + ", 25000) " + self._generate_stmt(n.stmt, jp, add_indent=True)

        return s

    def visit_While(self, n, mappings):
        jp = VariableMappings()
        jp.prev = mappings

        x = jp.add_i("while_itermediary")

        s = 'repeat (' + x + ', 25000, 25000) { if(!(' + self.visit(n.cond, jp) + ")) break; "
        s += self._generate_stmt(n.stmt, jp, add_indent=True)
        s += self._make_indent()[0:-1] + " }";
        return s

    def visit_DoWhile(self, n, mappings):
        raise Exception("No Do-While allowed in ePL");

    def visit_Switch(self, n, mappings):
        raise Exception("No Switch allowed in ePL");

    def visit_Case(self, n, mappings):
        s = 'case ' + self.visit(n.expr) + ':\n'
        for stmt in n.stmts:
            s += self._generate_stmt(stmt, add_indent=True)
        return s

    def visit_Default(self, n, mappings):
        raise Exception("No default label allowed in ePL");

    def visit_Label(self, n, mappings):
        raise Exception("Labels are not supported in ePL")

    def visit_Goto(self, n, mappings):
        raise Exception("Goto is supported in ePL")

    def visit_EllipsisParam(self, n, mappings):
        raise Exception("No ellipsis params allowed in ePL");

    def visit_Struct(self, n, mappings):
        raise Exception("Structs and Enums are not supported in ePL")

    def visit_Typename(self, n, mappings):
        return self._generate_type(n.type, mappings)

    def visit_Union(self, n, mappings):
        raise Exception("Structs and Enums are not supported in ePL")

    def visit_NamedInitializer(self, n, mappings):
        s = ''
        for name in n.name:
            if isinstance(name, c_ast.ID):
                s += '.' + name.name
            elif isinstance(name, c_ast.Constant):
                s += '[' + name.value + ']'
        s += ' = ' + self._visit_expr(n.expr, mappings)
        return s

    def visit_FuncDecl(self, n, mappings):
        return self._generate_type(n, mappings)

   

    def _generate_enum_body(self, members):
        # `[:-2] + '\n'` removes the final `,` from the enumerator list
        return ''.join(self.visit(value) for value in members)[:-2] + '\n'

    def _generate_stmt(self, n, mappings, add_indent=False):
        """ Generation from a statement node. This method exists as a wrapper
            for individual visit_* methods to handle different treatment of
            some statements in this context.
        """
        typ = type(n)
        if add_indent: self.indent_level += 2
        indent = self._make_indent()
        if add_indent: self.indent_level -= 2

        if typ in (
                c_ast.Decl, c_ast.Assignment, c_ast.Cast, c_ast.UnaryOp,
                c_ast.BinaryOp, c_ast.TernaryOp, c_ast.FuncCall, c_ast.ArrayRef,
                c_ast.StructRef, c_ast.Constant, c_ast.ID, c_ast.Typedef,
                c_ast.ExprList):
            # These can also appear in an expression context so no semicolon
            # is added to them automatically
            #
            rtt=indent + self.visit(n, mappings)
            if rtt.strip()!="":
                return rtt + ';\n'
            else:
                return ''
        elif typ in (c_ast.Compound,):
            # No extra indentation required before the opening brace of a
            # compound - because it consists of multiple lines it has to
            # compute its own indentation.
        
            return self.visit(n, mappings)
        else:
            return indent + self.visit(n, mappings) + '\n'

    def _generate_decl(self, n, mappings):
        """ Generation from a Decl node.
        """
        s = ''
        if n.funcspec: raise Exception("Funcspec declaration not supported in ePL") # s = ' '.join(n.funcspec) + ' '
        if n.storage: raise Exception("Storage declaration not supported in ePL") #
        typ = self._generate_type(n.type, mappings)
        s += typ
        return s

    def _generate_type(self, n, mappings, modifiers=[]):
        """ Recursive generation from a type node. n is the type node.
            modifiers collects the PtrDecl, ArrayDecl and FuncDecl modifiers
            encountered on the way down to a TypeDecl, to allow proper
            generation from it.
        """
        typ = type(n)

        if typ == c_ast.TypeDecl:
            s = ''
            if n.quals: raise Exception("Declaration qualifiers are not allowed in ePL")

            nstr = n.declname if n.declname else ''
            typus = ' '.join(n.type.names)

            if typus=="int":
                pass
            elif typus=="unsigned int":
                pass
            elif typus=="long":
                pass
            elif typus=="unsigned long":
                pass
            elif typus=="double":
                pass
            elif typus=="float":
                pass
            else:
                raise Exception("Unsupported type '" + typus + "'")
            innervisit = self.visit(n.type, mappings)
            s += innervisit


            # Resolve modifiers.
            # Wrap in parens to distinguish pointer to array and pointer to
            # function syntax.
            #
            for i, modifier in enumerate(modifiers):
                if isinstance(modifier, c_ast.ArrayDecl):
                    if (i != 0 and isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                        nstr = '(' + nstr + ')'
                    nstr += '[' + self.visit(modifier.dim, mappings) + ']'
                elif isinstance(modifier, c_ast.FuncDecl):
                    if (i != 0 and isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                        nstr = '(' + nstr + ')'
                    nstr += '(' + self.visit(modifier.args, mappings) + ')'
                elif isinstance(modifier, c_ast.PtrDecl):
                    raise Exception("Pointer types are not supported in ePL")
            if nstr:
                s += ' ' + nstr
                isfunc = False
                if "(" in nstr:
                    # Dealing with function here
                    varlist = [x.strip() for x in nstr[nstr.find("(")+1:-1].split(",")]
                    nstr = nstr[0:nstr.find("(")].strip()
                    mappings.addFuncArgs(nstr, varlist)
                    isfunc = True

                if "[" in nstr:
                    base = nstr[0:nstr.find("[")].strip()
                    upperbount=int(nstr[nstr.find("[")+1:-1])
                    for x in range(upperbount):
                        if typus=="int":
                            s = mappings.add_i(base + "[" + str(x) + "]")
                        elif typus=="unsigned int":
                            s = mappings.add_u(base + "[" + str(x) + "]")    
                        elif typus=="long":
                            s = mappings.add_l(base + "[" + str(x) + "]")
                        elif typus=="unsigned long":
                            s = mappings.add_ul(base + "[" + str(x) + "]")
                        elif typus=="double":
                            s = mappings.add_d(base + "[" + str(x) + "]")
                        elif typus=="float":
                            s = mappings.add_f(base + "[" + str(x) + "]")
                    s = ''
                else:
                    if typus=="int":
                        s = mappings.add_i(nstr)
                    elif typus=="unsigned int":
                        s = mappings.add_u(nstr)    
                    elif typus=="long":
                        s = mappings.add_l(nstr)
                    elif typus=="unsigned long":
                        s = mappings.add_ul(nstr)
                    elif typus=="double":
                        s = mappings.add_d(nstr)
                    elif typus=="float":
                        s = mappings.add_f(nstr)

                if isfunc:
                    s = "function " + nstr

                            
                return s
        elif typ == c_ast.Decl:
            return self._generate_decl(n.type, mappings)
        elif typ == c_ast.Typename:
            return self._generate_type(n.type, mappings)
        elif typ == c_ast.IdentifierType:
            return ' '.join(n.names) + ' '
        elif typ in (c_ast.ArrayDecl, c_ast.PtrDecl, c_ast.FuncDecl):
            return self._generate_type(n.type, mappings, modifiers + [n])
        else:
            return self.visit(n, mappings)

    def _parenthesize_if(self, n, condition, mappings):
        """ Visits 'n' and returns its string representation, parenthesized
            if the condition function applied to the node returns True.
        """
        s = self._visit_expr(n, mappings)
        if condition(n):
            return '(' + s + ')'
        else:
            return s

    def _parenthesize_unless_simple(self, n, mappings):
        """ Common use case for _parenthesize_if
        """
        return self._parenthesize_if(n, lambda d: not self._is_simple_node(d), mappings)

    def _is_simple_node(self, n):
        """ Returns True for nodes that are "simple" - i.e. nodes that always
            have higher precedence than operators.
        """
        return isinstance(n, (c_ast.Constant, c_ast.ID, c_ast.ArrayRef,
                              c_ast.StructRef, c_ast.FuncCall))
