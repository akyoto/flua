#ifndef LANGBPC_HPP_
#define LANGBPC_HPP_

//Includes
#include "../Interface/PrgmLang.hpp"

namespace bpc
{
	//Const vars
	const String el = "\n";
	const String separator = ";---------------------------------------------------------------------------" + el;
	const String oneLineComment = ";" + el;
}

//CompileError
#undef CompileError
#undef CompileLog
#ifdef DEBUG
	#define CompileError(msg) cerr << "[" << lineCounter << "] " << msg << endl
	#define CompileLog(msg) cout << "[" << lineCounter << "] " << msg << endl
	#define CompileWarning(msg) cout << "[" << lineCounter << "] { * * * Warning * * * } " << msg << endl
#else
	#define CompileError(msg) //
	#define CompileLog(msg) //
	#define CompileWarning(msg) //
#endif

//TPrgmLangBPC
class TPrgmLangBPC: public TPrgmLang
{
	public:
		
		//TabLevel
		static String tabLevel;
		static bool isInline;
		static bool inClassTopLevel;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TPrgmLangBPC()
		{
			//Names
			names.Add("BPC");
			names.Add("bpc");
			names.Add("bp");
			names.Add("Blitzprog");
			names.Add("Blitzprog Code");
			names.Add("BPR");
			names.Add("bpr");
			
			//File extensions
			exts.Add("bpc");
		}
		
		//Destructor
		~TPrgmLangBPC()
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		//Init
		inline void Init(bool debug)
		{
			//Debug
			debugMode = debug;
			
			//Operators
			
			//Level 1
			Array<Operator> ops = new TArray<Operator>;
			ops->Add(new TOperator('.', "call"));
			opLevels.Add(ops);
			
			//Level 2
			ops = new TArray<Operator>;
			ops->Add(new TOperator('^', "pow"));
			opLevels.Add(ops);
			
			//Level 3
			ops = new TArray<Operator>;
			ops->Add(new TOperator('*', "multiply"));
			ops->Add(new TOperator('/', "divide"));
			ops->Add(new TOperator('%', "modulo"));	//Mod
			opLevels.Add(ops);
			
			//Level 4
			ops = new TArray<Operator>;
			ops->Add(new TOperator('+', "add"));
			ops->Add(new TOperator('-', "subtract"));
			opLevels.Add(ops);
			
			//Level 5
			ops = new TArray<Operator>;
			ops->Add(new TOperator("<<", "shift-left"));	//Shl
			ops->Add(new TOperator(">>", "shift-right"));	//Shr
			opLevels.Add(ops);
			
			//Level 6
			ops = new TArray<Operator>;
			ops->Add(new TOperator('>', "greater-than"));
			ops->Add(new TOperator('<', "lower-than"));
			ops->Add(new TOperator(">=", "greater-or-equal"));
			ops->Add(new TOperator("<=", "lower-or-equal"));
			opLevels.Add(ops);
			
			//Level 7
			ops = new TArray<Operator>;
			ops->Add(new TOperator('=', "equal"));
			ops->Add(new TOperator("<>", "not-equal"));
			opLevels.Add(ops);
			
			//Level 8
			ops = new TArray<Operator>;
			ops->Add(new TOperator("&&", "and"));	//And
			ops->Add(new TOperator("||", "or"));	//Or
			opLevels.Add(ops);
			
			//Level 9
			
			//TODO: Assignments in ParseLine?
			
			/*ops = new TArray<Operator>;
			ops->Add(new TOperator("+=", "assign-add"));
			ops->Add(new TOperator("-=", "assign-subtract"));
			ops->Add(new TOperator("*=", "assign-multiply"));
			ops->Add(new TOperator("/=", "assign-divide"));
			opLevels.Add(ops);*/
		}
		
		//ConvertToXML
		inline XMLNode ConvertToXML(const String &file)
		{
			//Basic nodes
			XMLNode root = CreateXMLNode("module");
			XMLNode header = CreateXMLNode("header");
			XMLNode code = CreateXMLNode("code");
			currentNode = code;
			
			AddNode(root, header);
			AddNode(root, code);
			
			//Read file
			CompileLog("Opening \"" << file << "\"...");
			FileReadStream stream = CreateFileReadStream(file);
			CompileLog("Opened.");
			
			//if(!stream)
			//	CompileError("Could not open \"" << file << "\"");
			
			String line;
			while(!stream->Eof())
			{
				//Count lines
				++lineCounter;
				
				//Debug
				CompileLog("ReadLine...");
				stream->ReadLine(line);
				
				//Debug
				CompileLog("ProcessLine...");
				ProcessLine(line);
				
				if(line.IsEmpty())
					continue;
				
				tmpNode = currentNode;
				
				//Debug
				CompileLog("Adding node...");
				
				AddNode(tmpNode, ParseLine(line));
			}
			
			//Debug: String pool
			if(debugMode && !stringPool.IsEmpty())
			{
				//Info
				CompileLog("String pool");
				
				//Create string pool
				XMLNode stringPoolNode = CreateXMLNode("strings");
				AddNode(header, stringPoolNode);
				
				for(size_t i = 0; i < stringPool.GetLength(); ++i)
				{
					CompileLog(i << ": " << stringPool[i]);
					
					//Create string node
					XMLNode node = CreateXMLNode("string");
					XMLNode translation = CreateXMLNode("translation");
					node->SetAttribute("id", String(i + 1));
					
					translation->SetAttribute("language", "english");
					translation->SetAttribute("string", stringPool[i]);
					
					AddNode(node, translation);
					AddNode(stringPoolNode, node);
				}
			}
			
			return root;
		}
		
		//IsVarChar
		template <typename T>
		inline bool IsVarChar(T a) const
		{
			return isalnum(a) || a == '_';
		}
		
		//GetCleanExpr
		inline XMLNode GetCleanExpr(String expr)
		{
			//Debug
			CompileLog("GetCleanExpr");
			
			//Return text
			if(expr[0] != '(' && expr.GetLastChar() != ')')
			{
				return CreateXMLTextNode(expr.Trim());
			}
			
			//Remove unnecessary brackets
			if(expr.Find('(', 2) == String::npos)
			{
				while(expr[0] == '(' && expr[1] == '(' && expr[expr.GetLength()-1] == ')' && expr[expr.GetLength()-2] == ')')
				{
					expr.EraseLeft(1);
					expr.EraseRight(1);
				}
			}
			
			//Debug
			CompileLog("Parsing expression part: " << expr);
			
			//Create XML structure
			size_t counter = 0;
			for(size_t i = 1; i < expr.GetLength() - 1; ++i)
			{
				if(expr[i] == '(')
					++counter;
				if(expr[i] == ')')
					--counter;
				if(counter == 0)
				{
					//Found left operator
					while(IsVarChar(expr[++i]));
					
					//XML node (left operand)
					XMLNode term1, functerm1;
					
					//Function calls
					if(expr[i] == '(')
					{
						//Debug
						CompileLog("Found function call");
						
						//Use 'counter' (which is equal to zero) again
						counter = 1;
						while(++i < expr.GetLength() && counter != 0)	//TODO: Bounds check
						{
							if(expr[i] == ')')
								--counter;
							else if(expr[i] == '(')
								++counter;
						}
						
						//Error?
						if(counter != 0)
							CompileError("Expected ')'. Maybe you forgot one bracket.");
						
						//Save XML function call
						functerm1 = GetFunctionCall(expr.FromTo(1, i - 1));
					}
					
					--i;
					String left = expr.FromTo(1, i);
					CompileLog("Left expression: " << left);
					
					//Get operator sign
					while(expr[++i] != '(' && !IsVarChar(expr[i]));
					String op = expr.FromTo(1 + left.GetLength(), i - 1);
					CompileLog("Operator: " << op);
					
					String right = expr.FromTo(1 + left.GetLength() + op.GetLength(), expr.GetLength() - 2);
					CompileLog("Right expression: " << right);
					
					//XML node (right operand)
					XMLNode term2, functerm2;
					
					//Function calls (right)
					if(right[0] != '(' && right.GetLastChar() == ')')
					{
						//Debug
						CompileLog("Found function call");
						
						//Save XML function call
						functerm2 = GetFunctionCall(right);
					}
					
					//Find operator
					Operator opInst = GetOperator(op);
					if(!opInst)
						CompileError("Unknown operator: " << op);
					
					//Create nodes
					XMLNode node = CreateXMLNode(opInst->GetNodeName());
					term1 = CreateXMLNode("term");
					term2 = CreateXMLNode("term");
					
					//Structure
					AddNode(node, term1);
					AddNode(node, term2);
					
					//Left
					if(left[0] == '(')
						AddNode(term1, GetCleanExpr(left));				//Next expression (recursive)
					else if(functerm1)
						AddNode(term1, functerm1);						//Function call
					else
						AddNode(term1, CreateXMLTextNode(left));		//Operand itself (text)
					
					//Right
					if(right[0] == '(')
						AddNode(term2, GetCleanExpr(right));			//Next expression (recursive)
					else if(functerm2)
						AddNode(term2, functerm2);						//Function call
					else
						AddNode(term2, CreateXMLTextNode(right));		//Operand itself (text)
					
					return node;
				}
			}
			
			return CreateXMLTextNode(expr);
		}
		
		//GetExpr
		inline XMLNode GetExpr(String expr, void *expectType = Null)	//TODO: expectType
		{
			//Debug
			CompileLog("GetExpr");
			
			//Clean			//TODO: String version & optimize
			expr.Trim();
			
			//TODO: Recognize all unknown operators
			if(expr.Find("&&") != String::npos)
				CompileError("Use 'And' instead of '&&'");
			if(expr.Find("||") != String::npos)
				CompileError("Use 'Or' instead of '||'");
			if(expr.Find("%") != String::npos)
				CompileError("Use 'Mod' instead of '%'");
			if(expr.Find("<<") != String::npos)
				CompileError("Use 'Shl' instead of '<<'");
			if(expr.Find(">>") != String::npos)
				CompileError("Use 'Shr' instead of '>>'");
			
			//Replace
			expr.ReplaceStandalone("New", "New__");
			expr.ReplaceStandalone("And", "&&");
			expr.ReplaceStandalone("Or", "||");
			expr.ReplaceStandalone("Mod", "%");
			expr.ReplaceStandalone("Shl", "<<");
			expr.ReplaceStandalone("Shr", ">>");
			
			//Clean
			expr.EraseAll(" ");
			expr.EraseAll("\t");
			
			//'New' operator
			CompileLog("GetExpr: 'New'");
			size_t left = 0;
			size_t right = 0;
			
			while((left = expr.Find("New__", right)) != String::npos)	//TODO: Other whitespaces
			{
				right = left + 5;
				
				while(right < expr.GetLength() && IsVarChar(expr[right])) ++right;
				
				if(right >= expr.GetLength() || expr[right] != '(')
					expr.Insert("()", right);
			}
			
			//Debug
			CompileLog("Parsing " << expr);
			
			//Remove brackets
			if(expr[0] == '(' && expr[expr.GetLength()-1] == ')')
			{
				expr.EraseLeft(1);
				expr.EraseRight(1);
			}
			
			//Just to make sure everything works
			expr.Insert(" ", 0);
			expr += ' ';
			
			String sign;
			size_t found;
			size_t op;
			size_t offset;
			
			//For every operator level
			for(TArray<Array<Operator> >::const_iterator itl = opLevels.begin(); itl != opLevels.end(); ++itl)
			{
				TArray<int> array;
				
				//Find operators
				for(TArray<Operator>::const_iterator it = (*itl)->begin(); it != (*itl)->end(); ++it)
				{
					sign = (*it)->GetString();
					found = 1;
					while((found = expr.Find(sign, found)) != String::npos && (IsVarChar(expr[found + sign.GetLength()]) || expr[found + sign.GetLength()] == '(') && (IsVarChar(expr[found-1]) || expr[found-1] == ')'))
					{
						//Debug
						CompileLog("Found " << sign << " at position " << found);
						
						array.Add(found);
						found += sign.GetLength() + 1;
					}
				}
				
				//Empty?
				if(array.IsEmpty())
					continue;
				
				//Sort array
				array.Sort();
				
				offset = 0;
				
				//Edit string
				for(size_t i = 0; i < array.GetLength(); ++i)
				{
					op = array[i] + offset;
					
					//Get sign length
					right = op;
					while(!IsVarChar(expr[right]) && expr[right] != '(') ++right;
					sign = expr.FromTo(op, right - 1);
					right = op + sign.GetLength();
					
					//Left/Right
					left = op - 1;
					
					//Left operator
					while(IsVarChar(expr[left])) --left;
					while(IsVarChar(expr[right])) ++right;
					
					//Left ')'
					if(expr[left] == ')')
					{
						//Debug
						CompileLog("Found separate expression (left) at position: " << left);
						
						size_t counter = 1;
						while(--left >= 1 && counter != 0)	//TODO: Bounds check
						{
							if(expr[left] == '(')
								--counter;
							else if(expr[left] == ')')
								++counter;
						}
						
						//Debug
						CompileLog("Found separate expression end (left) at position: " << left + 1);
					}
					
					//Function calls left
					if(IsVarChar(expr[left]))
					{
						//Debug
						CompileLog("Found function call (left):");
						
						//Find previous operator
						while(IsVarChar(expr[left])) --left;
					}
					
					++left;
					
					//Right '('
					if(expr[right] == '(')
					{
						if(right != op + sign.GetLength())
						{
							//Debug
							CompileLog("Found function call (right): " << expr.FromTo(op + sign.GetLength(), right - 1));
						}
						
						//Debug
						CompileLog("Found separate expression (right) at position: " << right);
						
						size_t counter = 1;
						while(++right < expr.GetLength() - 1 && counter != 0)	//TODO: Bounds check
						{
							if(expr[right] == ')')
								--counter;
							else if(expr[right] == '(')
								++counter;
						}
						
						//Debug
						CompileLog("Found separate expression end (right) at position: " << right - 1);
					}
					
					//TODO: Function calls right
					
					--right;
					
					//Debug
					CompileLog(expr.FromTo(left, op - 1) << " | " << sign << " | " << expr.FromTo(op + 1, right));
					
					if(expr[left] != '(' || expr[right+1] != ')')
					{
						expr.Insert(")", right + 1);
						expr.Insert("(", left);
						offset += 2;
					}
					
					//Debug
					CompileLog("Expr:" << expr);
				}
			}
			
			//Expressions with no operators
			if(expr[1] != '(')
			{
				if(expr[expr.GetLength()-2] == ')')
					return GetFunctionCall(expr.Trim());		//Function call
				else
					return CreateXMLTextNode(expr.Trim());		//Other
			}
			
			return GetCleanExpr(expr.Trim());
		}
		
		//ParseLine
		inline XMLNode ParseLine(String expr)
		{
			//Debug
			CompileLog("ParseLine: " << expr);
			
			//Find keyword
			size_t i = 0;
			while(i < expr.GetLength() && IsVarChar(expr[i])) ++i;
			
			//Debug
			CompileLog("Extracting left expression");
			
			String exprLeft = expr.Left(i);
			
			//Debug
			CompileLog("Found left expression (ParseLine, " << i << ")");
			
			size_t iNext = i;
			
			//Get char
			while(iNext < expr.GetLength() && IsWhitespace(expr[iNext])) ++iNext;
			
			//Assignment
			if(iNext < expr.GetLength() && expr[iNext] == '=')
				return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 1));
			
			//Function call?
			if(iNext < expr.GetLength() && expr[iNext] == '(')
			{
				//Debug
				CompileLog("Function call (ParseLine): " << expr);
				
				//Find =
				size_t counter = 1;
				while(++iNext < expr.GetLength() && (expr[iNext] != '=' || counter != 0))
				{
					if(expr[iNext] == ')')
						--counter;
					else if(expr[iNext] == '(')
						++counter;
				}
				
				//Debug
				CompileLog("Part: " << expr.Left(iNext));
				
				//XML
				if(iNext < expr.GetLength() && expr[iNext] == '=')
					return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 1));
				else
					return GetExpr(expr.Left(iNext));
			}
			
			//Object call/var?
			if(iNext < expr.GetLength() && expr[iNext] == '.')
			{
				//Debug
				CompileLog("Object call/var: " << expr);
				CompileLog("Object: " << expr.Left(iNext));
				
				//Find =
				size_t counter = 0;
				String exprTwoChars = expr.Mid(iNext + 1, 2);
				while(++iNext < expr.GetLength() && ((expr[iNext] != '=' && exprTwoChars != "/=" && exprTwoChars != "*=" && exprTwoChars != "+=" && exprTwoChars != "-=") || counter != 0))
				{
					if(expr[iNext] == ')')
						--counter;
					else if(expr[iNext] == '(')
						++counter;
					exprTwoChars = expr.Mid(iNext + 1, 2);
				}
				
				//Debug
				CompileLog("Part: " << expr.Left(iNext));
				
				//XML
				if(expr[iNext] == '=')
					return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 1));
				else if(exprTwoChars == "+=")
					return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 2), "assign-add");
				else if(exprTwoChars == "-=")
					return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 2), "assign-subtract");
				else if(exprTwoChars == "*=")
					return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 2), "assign-multiply");
				else if(exprTwoChars == "/=")
					return GetAssignment(expr.Left(iNext), expr.Mid(iNext + 2), "assign-divide");
				else
					return GetExpr(expr.Left(iNext));
			}
			
			//Get char
			while(iNext < expr.GetLength() && IsWhitespace(expr[iNext])) ++iNext;
			
			char chr = iNext < expr.GetLength() ? expr[iNext] : ' ';
			
			//Type of command
			switch(chr)
			{
				case '(':
					//TODO: Check this, too (FunctionExists)
					return GetFunctionCall(expr);
					
				case '=':
					//TODO: Assignments
					return CreateXMLTextNode(expr);
					
				default:
					
					//TODO: Check for bugs
					if(exprLeft == "End")
						exprLeft = expr;
					
					//If
					if(exprLeft == "If")
					{
						XMLNode block = CreateXMLNode("if-block");
						XMLNode ifNode = CreateXMLNode("if");
						XMLNode condition = CreateXMLNode("condition");
						XMLNode code = CreateXMLNode("code");
						
						AddNode(block, ifNode);
						AddNode(ifNode, condition);
						AddNode(ifNode, code);
						
						size_t then = expr.Find("Then", i);	//TODO: Strings
						
						//Multi-Line-If
						if(then == String::npos)
						{
							//Find errors
							if(expr.GetLength() == 2)
								CompileError("Expected condition. Maybe you forgot to specify a condition for the 'If' block.");
							
							AddNode(condition, GetExpr(expr.FromTo(i+1, then)));
							
							currentNode = code;
							return block;
						}
						else	//Single-Line-If
						{
							AddNode(condition, GetExpr(expr.FromTo(i+1, then - 1)));
							AddNode(code, GetExpr(expr.Mid(then + 5)));
							return block;
						}
					}
					
					//End If
					if(exprLeft == "EndIf" || expr == "End If")
					{
						currentNode = currentNode->GetParent()->GetParent()->GetParent();	//code->if->if-block->parent
						return Null;
					}
					
					//Return
					if(exprLeft == "Return")
					{
						if(!inSubProgram)
							CompileError("'Return' can only be used in functions/methods/operators/casts");
						
						XMLNode node = CreateXMLNode("return");
						if(expr.GetLength() != 6)											//Argument
							AddNode(node, GetExpr(expr.Mid(i+1)));
						return node;
					}
					
					//New
					if(exprLeft == "New")
					{
						return GetConstructorExpr(expr.Mid(i+1));
					}
					
					//Delete
					if(exprLeft == "Delete")
					{
						XMLNode node = CreateXMLNode("delete");
						AddNode(node, GetExpr(expr.Mid(i+1)));
						return node;
					}
					
					//Method
					if(exprLeft == "Method" || exprLeft == "Operator" || exprLeft == "Function")
					{
						//Functions
						bool isFunction = false;
						if(exprLeft == "Function")
							isFunction = true;
						
						inSubProgram = true;
						
						//Find char positions
						size_t dp = expr.Find(':', i);
						size_t br = expr.Find('(', i);
						size_t toChar;
						
						if(dp != String::npos && dp < br)
							toChar = dp;
						else
							toChar = br;
						
						//Name of the method
						String methName = expr.Mid(i, toChar - i).Trim();
						
						if(!isFunction)
							CompileLog("Found method: " << currentClass->GetAttribute("name") << "." << methName);
						else
							CompileLog("Found function: " << methName);
						
						XMLNode node;
						if(methName == "New")
						{
							if(isFunction)
								CompileError("Invalid function name: 'New'");
							
							node = CreateXMLNode("constructor");
						}
						else if(methName == "Delete")
						{
							if(isFunction)
								CompileError("Invalid function name: 'Delete'");
							
							node = CreateXMLNode("destructor");
						}
						else if(exprLeft == "Method")
						{
							node = CreateXMLNode("method");
							node->SetAttribute("name", methName);
							
							if(toChar == dp)
							{
								AddNode(node, GetType(expr.FromTo(toChar + 1, br - 1).Trim()));	//Return type
							}
						}
						else if(exprLeft == "Operator")
						{
							node = CreateXMLNode("operator");
							node->SetAttribute("name", methName);
							
							if(toChar == dp)
							{
								AddNode(node, GetType(expr.FromTo(toChar + 1, br - 1).Trim()));	//Return type
							}
						}
						else if(isFunction)
						{
							node = CreateXMLNode("function");
							node->SetAttribute("name", methName);
							
							if(toChar == dp)
							{
								AddNode(node, GetType(expr.FromTo(toChar + 1, br - 1).Trim()));	//Return type
							}
						}
						
						//Function arguments
						String args = expr.FromTo(br + 1, expr.FindLast(')') - 1);
						if(!args.IsEmpty())
						{
							if(methName == "Delete")
								CompileError("Destructor must not have any function arguments");
							
							AddNode(node, GetParameters(args, CreateXMLNode("parameters")));
						}
						
						//Nodes
						//XMLNode parameters = CreateXMLNode("parameters");
						XMLNode methodCode = CreateXMLNode("code");
						//AddNode(node, parameters);
						AddNode(node, methodCode);
						
						if(isFunction)
						{
							//Set current node
							currentNode = methodCode;
							
							functions.Add(node);
							return node;
						}
						else
						{
							//Add method node
							AddNode(currentClassVisibility->Find("methods"), node);
							
							//if(!inFuncTemplate)												//TODO: Check this - Is that right?
							//	AddNode(currentClassVisibility->Find("methods"), node);	//TODO: Error handling
							//else
							//	AddNode(currentNode, node);
							
							//Set current node
							currentNode = methodCode;
							
							return Null;	//Because 'Method' must add itself to the method tree
						}
					}
					
					//End Method
					if(exprLeft == "EndMethod" || exprLeft == "End Method")
					{
						currentNode = currentClassVisibility;	//code->method->methods->public
						//if(inTemplate)
						//	inTemplate--;
						inSubProgram = false;
						return Null;
					}
					
					//End Function
					if(exprLeft == "EndFunction" || exprLeft == "End Function")
					{
						currentNode = currentNode->GetParent()->GetParent();	//code->function->parent
						inSubProgram = false;
						return Null;
					}
					
					//Type
					if(exprLeft == "Type")
					{
						if(inSubProgram || inClass)
							CompileError("'Type' declaration can neither be used in expressions nor functions and it cannot be used inside a type defintion");
						
						inClass = true;
						
						XMLNode node = CreateXMLNode("class");
						
						XMLNode p[3];
						p[0] = CreateXMLNode("public");
						p[1] = CreateXMLNode("protected");
						p[2] = CreateXMLNode("private");
						
						for(int i=0; i < 3; ++i)
						{
							AddNode(p[i], CreateXMLNode("definitions"));
							AddNode(p[i], CreateXMLNode("vars"));
							AddNode(p[i], CreateXMLNode("methods"));
							AddNode(p[i], CreateXMLNode("operators"));
							AddNode(p[i], CreateXMLNode("casts"));
							AddNode(node, p[i]);
						}
						
						node->SetAttribute("name", expr.Mid(5).Trim());	//TODO: Extends
						currentNode = currentClassVisibility = p[0];		//Public node
						
						return currentClass = node;
					}
					
					//End Type
					if(exprLeft == "EndType" || exprLeft == "End Type")
					{
						if(inSubProgram || !inClass)
							CompileError("'End Type' can neither be used in expressions nor functions");
						
						if(inClassTemplate)
						{
							currentNode = currentNode->GetParent()->GetParent()->GetParent()->GetParent();		//public->class->code->template->parent
							inClassTemplate = false;
						}
						else
						{
							currentNode = currentNode->GetParent()->GetParent();		//public->class->parent
						}
						
						inClass = false;
						return Null;
					}
					
					//Public
					if(exprLeft == "Public")
					{
						if(!inClass)
							CompileError("'Public' can only be used in type defintions");
						
						currentNode = currentClass->Find("public");
						return Null;
					}
					
					//Protected
					if(exprLeft == "Protected")
					{
						if(!inClass)
							CompileError("'Protected' can only be used in type defintions");
						
						currentNode = currentClass->Find("protected");
						return Null;
					}
					
					//Private
					if(exprLeft == "Private")
					{
						if(!inClass)
							CompileError("'Private' can only be used in type defintions");
						
						currentNode = currentClass->Find("private");
						return Null;
					}
					
					//Template
					if(exprLeft == "Template")
					{
						size_t foundLeft = expr.Find('<');
						if(foundLeft == String::npos)
							CompileError("Expected '<'. Usage: 'Template <T:Type>'");
						
						size_t foundRight = expr.Find('>');
						if(foundRight == String::npos)
							CompileError("Expected '>'. Usage: 'Template <T:Type>'");
						
						XMLNode node = CreateXMLNode("template");
						XMLNode params = GetParameters(expr.FromTo(foundLeft + 1, foundRight - 1), CreateXMLNode("parameters"));
						XMLNode code = CreateXMLNode("code");
						
						AddNode(node, params);
						AddNode(node, code);
						
						currentNode = code;
						
						lastTemplate = node;
						
						if(!inClass)
						{
							return node;
						}
						else
						{
							AddNode(currentClassVisibility->Find("methods"), node);
							return Null;
						}
					}
					
					//Local
					if(exprLeft == "Local")
					{
						if(inClass && !inSubProgram)	//TODO: For loop
							CompileError("'Local' variable declaration can neither be used in expressions nor types");
						
						//If there is nothing more than 'Local'
						if(expr.GetLength() == 5)
							CompileError("You forgot to specify the name of the variable. 'Local' is used for variable declarations. Example: 'Local x:Int'");
						
						XMLNode node = GetParameters(expr.Mid(i+1), CreateXMLNode("local"));
						return node;
					}
					
					//Global
					if(exprLeft == "Global")
					{
						//If there is nothing more than 'Global'
						if(expr.GetLength() == 6)
							CompileError("You forgot to specify the name of the variable. 'Global' is used for variable declarations. Example: 'Global x:Int'");
						
						XMLNode node = GetParameters(expr.Mid(i+1), CreateXMLNode("global"));
						return node;
					}
					
					//Field
					if(exprLeft == "Field")
					{
						if(inSubProgram || !inClass)
							CompileError("'Field' variable declaration can neither be used in expressions nor functions and has to be used inside a type definition");
						
						//If there is nothing more than 'Field'
						if(expr.GetLength() == 5)
							CompileError("You forgot to specify the name of the variable. 'Field' is used for the declaration of class variables. Example: 'Field x:Int'");
						
						GetParameters(expr.Mid(i+1), currentClassVisibility->Find("vars"));
						return Null;
					}
					
					//Define
					if(exprLeft == "Define")
					{
						size_t found = expr.Find('=');
						
						if(found == String::npos)
							CompileError("You have forgotten the '='. Use it to define your term by using 'Define A = B'");
						
						XMLNode node = CreateXMLNode("define");
						XMLNode term = CreateXMLNode("term");
						XMLNode alias = CreateXMLNode("alias");
						
						AddNode(term, GetExpr(expr.FromTo(i+1, found-1)));
						AddNode(alias, GetExpr(expr.Mid(found+1)));
						
						AddNode(node, term);
						AddNode(node, alias);
						
						if(inClass)
						{
							AddNode(currentClassVisibility->Find("definitions"), node);
							return Null;
						}
						else
						{
							return node;
						}
					}
					
					//While
					if(exprLeft == "While")
					{
						XMLNode node = CreateXMLNode("while");
						XMLNode condition = CreateXMLNode("condition");
						XMLNode code = CreateXMLNode("code");
						
						AddNode(node, condition);
						AddNode(condition, GetExpr(expr.Mid(i + 1)));
						AddNode(node, code);
						
						currentNode = code;
						inWhile = true;
						
						return node;
					}
					
					//Wend
					if(exprLeft == "Wend")
					{
						if(!inWhile)
							CompileError("'Wend' can only be used at the end of a 'While/Wend' block. Maybe you have forgotten the 'While' keyword.");
						
						currentNode = currentNode->GetParent()->GetParent();	//code->while->parent
						inWhile = false;
						
						return Null;
					}
					
					//Repeat
					if(exprLeft == "Repeat")
					{
						XMLNode node = CreateXMLNode("repeat");
						XMLNode code = CreateXMLNode("code");
						
						AddNode(node, code);
						
						currentNode = code;
						inRepeat = true;
						
						return node;
					}
					
					//Until
					if(exprLeft == "Until")
					{
						if(!inRepeat)
							CompileError("'Until' can only be used at the end of a 'Repeat/Until' block. Maybe you have forgotten the 'Repeat' keyword.");
						
						XMLNode condition = CreateXMLNode("until");
						AddNode(condition, GetExpr(expr.Mid(i + 1)));
						AddNode(currentNode->GetParent(), condition);
						
						currentNode = currentNode->GetParent()->GetParent();	//code->repeat->parent
						inRepeat = false;
						
						return Null;
					}
					
					//Select
					if(exprLeft == "Select")
					{
						currentNode = CreateXMLNode("select");
						XMLNode term = CreateXMLNode("term");
						
						AddNode(term, GetExpr(expr.Mid(i + 1)));
						AddNode(currentNode, term);
						
						inSelect = true;
						
						return currentNode;
					}
					
					//Case
					if(exprLeft == "Case")
					{
						if(!inSelect)
							CompileError("'Case' can only be used in a 'Select' block. Maybe you have forgotten the 'Select' keyword.");
						
						//After some case blocks
						if(currentNode->GetParent()->GetName() == "case")				//code->case
						{
							XMLNode node = CreateXMLNode("case");
							XMLNode code = CreateXMLNode("code");
							
							GetCallParameters(expr.Mid(i + 1), node, false, "value");
							AddNode(node, code);
							
							AddNode(currentNode->GetParent()->GetParent(), node);		//code->case->select
							currentNode = code;
							return Null;
						}
						else if(currentNode->GetName() == "select")		//First case
						{
							XMLNode node = CreateXMLNode("case");
							currentNode = CreateXMLNode("code");
							
							GetCallParameters(expr.Mid(i + 1), node, false, "value");
							AddNode(node, currentNode);
							
							return node;
						}
						else
						{
							CompileError("'Case' can only be used in a 'Select' block.");
						}
					}
					
					//Default
					if(exprLeft == "Default")
					{
						if(!inSelect)
							CompileError("'Default' can only be used in a 'Select' block. Maybe you have forgotten the 'Select' keyword.");
						
						//After some case blocks
						if(currentNode->GetParent()->GetName() == "case")			//code->case
						{
							XMLNode node = CreateXMLNode("default");
							XMLNode code = CreateXMLNode("code");
							
							AddNode(node, code);
							
							AddNode(currentNode->GetParent()->GetParent(), node);		//code->case->select
							currentNode = code;
							return Null;
						}
						else if(currentNode->GetName() == "select")		//First case
						{
							XMLNode node = CreateXMLNode("default");
							currentNode = CreateXMLNode("code");
							
							AddNode(node, currentNode);
							
							return node;
						}
						else
						{
							CompileError("'Default' can only be used in a 'Select' block.");
						}
					}
					
					//End Select
					if(exprLeft == "EndSelect" || exprLeft == "End Select")
					{
						if(!inSelect)
							CompileError("'End Select' can only be used at the end of a 'Select' block. Maybe you have forgotten the 'Select' keyword.");
						
						if(currentNode->GetName() == "select")
						{
							CompileWarning("You haven't specified any possible cases for the 'Select' block.");
							currentNode = currentNode->GetParent();								//select->parent
						}
						else
						{
							currentNode = currentNode->GetParent()->GetParent()->GetParent();	//code->case->select->parent
						}
						
						inSelect = false;
						return Null;
					}
					
					//Import
					if(exprLeft == "Import")
					{
						String module = expr.Mid(i + 1);
						
						if(module.IsSurroundedBy('"'))
						{
							module = module.Mid(1, module.GetLength() - 2);			//TODO: Cut function
							delete ::ConvertToXML(module, "", new TPrgmLangBPC);	//Not easy to understand...	//TODO: Multithreading
						}
						
						XMLNode node = CreateXMLNode("import");
						AddNode(node, CreateXMLTextNode(module));
						return node;
					}
			}
			
			//Check
			if(!FunctionExists(exprLeft))
			{
				CompileWarning("Unknown command: '" << exprLeft << "'");
			}
			
			/*
			//Function call
			if(FunctionExists(exprLeft))
			{
				return GetFunctionCall(exprLeft + "(" + expr.Mid(i + 1) + ")");
			}
			else
			{
				//Error
				CompileError("Unknown command: '" << expr << "' ('" << exprLeft << "', '" << expr[iNext] << "')");
				
				return CreateXMLTextNode(expr);
			}
			*/
			
			//Don't check whether the function really exists - that's the task of the XML interpreter
			return GetFunctionCall(exprLeft + "(" + expr.Mid(i + 1) + ")");
		}
		
		//GetConstructorExpr
		inline XMLNode GetConstructorExpr(const String &expr)
		{
			XMLNode node = CreateXMLNode("new");
			size_t br = expr.Find('(');
			
			XMLNode type = CreateXMLNode("type");
			AddNode(node, type);
			AddNode(type, CreateXMLTextNode(expr.Left(br)));
			
			if(br != String::npos)
			{
				XMLNode parameters = CreateXMLNode("parameters");
				AddNode(node, GetCallParameters(expr.FromTo(br + 1, expr.GetLength() - 3), parameters));
			}
			
			return node;
		}
		
		//GetAssignment
		inline XMLNode GetAssignment(const String &lValue, const String &rValue, const String &nodeName = "assign")
		{
			//Nodes
			XMLNode assign = CreateXMLNode(nodeName);
			XMLNode var = CreateXMLNode("var");
			XMLNode value = CreateXMLNode("value");
			
			//Structure
			AddNode(assign, var);
			AddNode(assign, value);
			
			//Assignment
			AddNode(var, GetExpr(lValue));
			AddNode(value, GetExpr(rValue));
			
			return assign;
		}
		
		//GetCallParameters
		inline XMLNode GetCallParameters(String expr, XMLNode node, bool clean = false, String parameterName = "parameter")
		{
			if(expr.IsEmpty())
				return Null;
			
			expr += ',';
			size_t i = 0;
			size_t lastIndex = 0;
			size_t counter = 0;
			
			do
			{
				//Iterate (every char)
				while(i < expr.GetLength() && (expr[i] != ',' || counter != 0))
				{
					if(expr[i] == ')')
						--counter;
					else if(expr[i] == '(')
						++counter;
					++i;
				}
				
				//Error
				if(counter != 0)
					CompileError("Expected ')'. Maybe you forgot one bracket.");
				
				XMLNode parameter = CreateXMLNode(parameterName);
				
				if(clean)
					AddNode(parameter, GetCleanExpr(expr.FromTo(lastIndex, i-1)));
				else
					AddNode(parameter, GetExpr(expr.FromTo(lastIndex, i-1)));
				
				AddNode(node, parameter);
				
				lastIndex = ++i;
				
			} while(i < expr.GetLength());
			
			return node;
		}
		
		//GetParameters
		inline XMLNode GetParameters(String expr, XMLNode node, bool isFunctionCall = false)
		{
			String typeDecl;
			String varName;
			expr += ',';
			size_t foundTypeDeclarator;
			size_t equalSign;
			size_t i = 0;
			size_t lastIndex = 0;
			size_t counter = 0;
			
			do
			{
				//Iterate (every char)
				while(i < expr.GetLength() && (expr[i] != ',' || counter != 0))
				{
					if(expr[i] == ')')
						--counter;
					else if(expr[i] == '(')
						++counter;
					++i;
				}
				
				//Error
				if(counter != 0)
					CompileError("Expected ')'. Maybe you forgot one bracket.");
				
				typeDecl = expr.FromTo(lastIndex, i-1);
				CompileLog("Parameter: " << typeDecl);
				foundTypeDeclarator = typeDecl.Find(':');
				
				if(isFunctionCall)
				{
					//Debug
					CompileLog("GetParameters: " << expr);
					
					//Create node
					XMLNode param = CreateXMLNode("parameter");
					
					//Structure
					AddNode(param, GetCleanExpr(typeDecl));
					AddNode(node, param);
				}
				else /*if(foundTypeDeclarator != String::npos)*/
				{
					XMLNode var = CreateXMLNode("var");
					XMLNode value;
					
					equalSign = typeDecl.Find('=');
					if(equalSign != String::npos)
					{
						value = CreateXMLNode("value");
						AddNode(value, GetExpr(typeDecl.Mid(equalSign + 1)));
					}
					
					if(foundTypeDeclarator != String::npos)
					{
						AddNode(var, GetType(typeDecl.FromTo(foundTypeDeclarator + 1, equalSign - 1)));
						varName = typeDecl.Left(foundTypeDeclarator);
					}
					else
					{
						varName = typeDecl.Left(equalSign).Trim();
					}
						
					if(varName.Left(5) == "Const" && IsWhitespace(varName[5]))
					{
						varName.EraseLeft(6);
						var->SetAttribute("const", "true");
					}
					var->SetAttribute("name", varName.Trim());
					
					AddNode(var, value);
					AddNode(node, var);
				}
				/*else
				{
					CompileError("You have to specify the type of the variable '" << typeDecl << "'");
				}*/
				
				lastIndex = ++i;
				
			} while(i < expr.GetLength());
			
			return node;
		}
		
		//GetType
		inline XMLNode GetType(String typeStr)
		{
			XMLNode type = CreateXMLNode("type");
			if(typeStr.StartsWith("Ref<"))	//TODO: Enable whitespaces
			{
				type->SetAttribute("callby", "reference");
				typeStr = typeStr.FromTo(4, typeStr.FindLast('>') - 1);
			}
			while(typeStr.StartsWith("Ptr<"))	//TODO: Enable whitespaces
			{
				type->SetAttribute("pointer", type->GetAttribute("pointer").ToInt() + 1);
				typeStr = typeStr.FromTo(4, typeStr.FindLast('>') - 1);
			}
			AddNode(type, CreateXMLTextNode(typeStr.Trim()));
			return type;
		}
		
		//GetFunction
		inline XMLNode GetFunctionCall(const String &expr)
		{
			//Debug
			CompileLog("FunctionCall: " << expr);
			
			//'New' operator
			if(expr.StartsWith("New__"))
			{
				XMLNode node = CreateXMLNode("new");
				XMLNode type = CreateXMLNode("type");
				
				AddNode(node, type);
				
				size_t found = expr.Find('(');
				AddNode(type, CreateXMLTextNode(expr.FromTo(5, found - 1)));
				
				GetCallParameters(expr.FromTo(found + 1, expr.GetLength() - 2), node);
				
				return node;
			}
			
			//Create nodes
			XMLNode node = CreateXMLNode("call");
			//XMLNode from = CreateXMLNode("from");
			XMLNode function = CreateXMLNode("function");
			
			//Structure
			//AddNode(node, from);
			AddNode(node, function);
			
			//Function name
			size_t bracket = expr.Find('(');
			AddNode(function, CreateXMLTextNode(expr.Left(bracket).Trim()));
			
			//Parameters
			String params = expr.FromTo(bracket + 1, expr.GetLength() - 2);
			if(!params.Trim().IsEmpty())
				GetCallParameters(params, node);	//GetParameters(params, node, true);
			
			return node;
		}
		
		//RemoveComment
		inline void RemoveComment(String &line, size_t found)
		{
			String comment = line.Mid(found + 1);
			String commentTrimmed = comment;
			commentTrimmed.Trim();
			
			//ToDo-Entry
			if(commentTrimmed.StartsWith("TODO"))
			{
				XMLNode todoNode = CreateXMLNode("todo");
				todoNode->SetAttribute("string", commentTrimmed.Mid(5));	//TODO: Whitespaces and other character types
				AddNode(currentNode, todoNode);
			}
			else	//Normal comment
			{
				XMLNode commentNode = CreateXMLNode("comment");
				commentNode->SetAttribute("string", comment);
				AddNode(currentNode, commentNode);
			}
			line = line.Left(found);							//TODO: Optimization: line.EraseFrom(found);
		}
		
		//RemoveComments
		inline void RemoveComments(String &line)
		{
			//line = line.Until(';');
			
			size_t found = line.Find(';');
			if(found != String::npos)
			{
				RemoveComment(line, found);
			}
		}
		
		//ReplaceStrings
		inline void ReplaceStrings(String &line)
		{
			if(line.StartsWith("Import "))					//TODO: Whitespaces
				return;
			
			size_t found = 0;
			size_t found2;
			size_t foundSingleLineComment = 0;
			String stringId;
			
			while((found = line.Find('\"', found)) != String::npos)	//TODO: Strings
			{
				//Find comment
				foundSingleLineComment = line.Find(';', foundSingleLineComment);
				
				//The String is in the comment
				if(found > foundSingleLineComment)
				{
					RemoveComment(line, foundSingleLineComment);
					return;
				}
				
				found2 = line.Find("\"", found + 1);
				if(found2 == String::npos)							//TODO: Multiline-Strings
					CompileError("Expected '\"'. Multiline-Strings are not enabled.");
				stringPool.Add(line.FromTo(found + 1, found2 - 1));
				
				//Modifying string...
				line.Erase(found, found2 - found + 1);
				stringId = String(stringPool.GetLength());
				line.Insert(stringId, found);
				line.Insert("Str__", found);
				
				//Now 'found2' is not valid so we can't use 'found = found2 + 1'. found += Len("Str__") + Len("5")
				found += 5 + stringId.GetLength();
				foundSingleLineComment = found;
			}
		}
		
		//ProcessLine
		inline void ProcessLine(String &line)
		{
			//Strings and comments with strings
			ReplaceStrings(line);
			
			//Comments
			RemoveComments(line);
			
			//Trim
			line.Trim();
		}
		
		//FunctionExists
		inline bool FunctionExists(const String &funcName)
		{
			//TODO: Optimize
			for(TArray<XMLNode>::iterator it = functions.begin(); it != functions.end(); ++it)
			{
				if(funcName == (*it)->GetAttribute("name"))
					return 1;
			}
			return 0;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//GetName
		inline String GetName() const
		{
			return "Blitzprog Code";
		}
		
		//GetHeader
		inline String GetHeader(XMLNode header)
		{
			return "";
		}
		
		//GetExpr
		inline String GetExpr(XMLNode node)
		{
			return "";
		}
		
	protected:
		
		XMLNode tmpNode;
		XMLNode currentNode;
		XMLNode currentClass;
		XMLNode currentClassVisibility;
		XMLNode lastTemplate;
		TArray<String> stringPool;
		size_t lineCounter;
		bool inClassTemplate;
		//bool inFuncTemplate;
		//bool inFunc;
		bool inClass;
		bool inSelect;
		bool inWhile;
		bool inRepeat;
		bool inSubProgram;
		bool debugMode;
};

//Instance
#ifdef BLITZPROG_MDA
	TPrgmLangBPC instanceBPC;
	String TPrgmLangBPC::tabLevel;
	bool TPrgmLangBPC::isInline;
	bool TPrgmLangBPC::inClassTopLevel;
#endif

#endif /*LANGBPC_HPP_*/
