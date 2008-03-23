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

#define Exec(cmd) Print(cmd); system(cmd)

//Main
void Main()
{
	//Get arguments
	int argc = GetCAppArgsCount();
	char **argv = GetCAppArgs();
	
	//Options
	bool compile = 0;
	bool run = 0;
	
	//Parse arguments
	String inputFile;
	String outputFile;
	String tmp;
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
		else if(FileExists(tmp))
		{
			inputFile = tmp;
		}
	}
	
	//Check arguments
	if(inputFile.IsEmpty())
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
	else
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
	Print("Done.");
	
	//Compile
	if(compile)
	{
		ms = MilliSecs();
		Print("Compile with g++...");
		
		//TODO: Optimize
		Exec("g++ " + outputFile + " -I ./lib/ -o " + ExtractDir(outputFile) + ExtractName(outputFile));	//TODO: Replace 'system' with CreateProcess
		Print("g++: " << MilliSecs() - ms << " ms");
	}
	
	//Run
	if(run)
	{
		Print("Run...\n");
		
		//TODO: Optimize
		Exec(ExtractDir(outputFile) + ExtractName(outputFile));												//TODO: Replace 'system' with CreateProcess
	}
}
