//Defines
#define BLITZPROG_MDA

//Includes
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/FileSystem/XML/XML.hpp>

//My includes
#include "Interface/PrgmLang.hpp"

//Languages
#include "Lang/LangCPP.hpp"
#include "Lang/LangBPC.hpp"

//TODO: Inline
#define Exec(cmd) Print(cmd); system(cmd)

//Main
void Main()
{
	//Version
	String version = "0.1.4";
	
	//Get arguments
	int argc = GetCAppArgsCount();
	char **argv = GetCAppArgs();
	
	//Options
	bool compile = 0;
	bool clean = 0;
	bool run = 0;
	
	//Parse arguments
	String tmp;
	String inputFile;
	String outputFile;
	for(int i = 1; i < argc; ++i)
	{
		tmp = argv[i];			//TODO: Optimise ("-")
		if(tmp == "-o")
		{
			outputFile = argv[++i];
			FixPath(outputFile);
			Print("Output file: " << outputFile);
		}
		else if(tmp == "-I")
		{
			
		}
		else if(tmp == "-d")
		{
			
		}
		else if(tmp == "-doc")
		{
			
		}
		else if(tmp == "-p")
		{
			
		}
		else if(tmp == "--clean")
		{
			clean = true;
		}
		else if(tmp == "--version")
		{
			Print("Blitzprog Compiler " << version);
		}
		else if(tmp == "--help")
		{
			Print("Blitzprog Compiler " << version);
		}
		else if(FileExists(tmp))
		{
			inputFile = tmp;
		}
	}
	
	//Check arguments
	if(inputFile.IsEmpty() && !clean)
	{
		Print("no input files" << endl << "Usage: bp in.bpc");
		End(1);
	}
	
	//System information
	#ifdef LINUX
		system("uname -a");
	#endif
	
	//Convert
	int ms = MilliSecs();
	if(inputFile.EndsWith(".bp"))
	{
		if(outputFile.IsEmpty())
		{
			outputFile = ExtractName(inputFile);
			outputFile += ".cpp";
			ConvertToLang(inputFile, outputFile);
			outputFile.AddLeft(ExtractDir(inputFile));	//TODO: Optimize
			compile = true;
			run = true;
		}
		else
		{
			ConvertToLang(inputFile, outputFile);
		}
	}
	else if(!inputFile.IsEmpty())
	{
		if(!outputFile.IsEmpty() && outputFile.Find('.') == String::npos)
		{
			ConvertToXML(inputFile, outputFile + ".bp");
			ConvertToLang(outputFile + ".bp", outputFile + ".cpp");
			outputFile += ".cpp";
			compile = true;
		}
		else
		{
			ConvertToXML(inputFile, outputFile);
		}
	}
	Print(MilliSecs() - ms << " ms");
	
	//Name of the binary file
	String exeFile = StripExt(outputFile);
	
	//Compile
	if(compile)
	{
		ms = MilliSecs();
		Print("Compile with g++...");
		
		//TODO: Optimize
		Exec("g++ " + outputFile + " -o " + exeFile);	//TODO: Replace 'system' with CreateProcess
		Print("g++: " << MilliSecs() - ms << " ms");
	}
	
	//Clean
	if(1)
	{
		ms = MilliSecs();
		String fileName;
		Dir currentDir = OpenDir(".");
		Print("TEST1");
		while(fileName = currentDir->GetNextVisibleFile())
		{
			Print(fileName);
		}
		Print("TEST2");
		Print("Clean: " << MilliSecs() - ms << " ms");
	}
	
	Print("Done.");
	
	//Run
	if(run)
	{
		Print("Run...\n");
		
		//TODO: Optimize
		Exec(exeFile);												//TODO: Replace 'system' with CreateProcess
	}
}
