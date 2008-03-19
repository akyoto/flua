#include "FileSystem.hpp"

//GetNextFile
String TDirectory::GetNextFile()
{
	if(!dirHandle)
		return NullString;
	
	struct dirent *ent = readdir(dirHandle);
	if(ent == Null)
		return NullString;
	String tmp = ent->d_name;
	return tmp != "." && tmp != ".." ? tmp : GetNextFile();
}

//CopyFile
bool CopyFile(const String &from, const String &to)
{
	ifstream fromStream(from);
	if(!fromStream)
	{
		EngineLogError("Can't open file " << from);
		return false;
	}
	
	ofstream toStream(to);
	if(!toStream)
	{
		EngineLogError("Can't create file " << to);
		return false;
	}
	
	return toStream << fromStream.rdbuf();
}

//FileSize
off_t FileSize(const String &file)
{
	struct stat fileInfo;
	
	if(stat(file, &fileInfo) != 0)
	{
		EngineLogError("Can't get file info: " << strerror(errno));
		return 0;
	}
	
	return fileInfo.st_size;
}

//FileSize2
streampos FileSize2(const String &file)
{
	ifstream myStream(file, ios::in | ios::binary);
	if(!myStream)
	{
		EngineLogError("Can't open file " << file);
		return 0;
	}
	myStream.seekg(0, ios::end);
	return myStream.tellg();
}

//FileTime
time_t FileTime(const String &file)
{
	struct stat fileInfo;
	
	if(stat(file, &fileInfo) != 0)
	{
		EngineLogError("Cannot get file info: " << strerror(errno));
		return 0;
	}
	
	return fileInfo.st_mtime;
}

//PrintFile
void PrintFile(const String &url)
{
	String line;
	Stream stream = CreateFileReadStream(url);
	while(!stream->Eof())
	{
		stream->ReadLine(line);
		Print(line);
	}
}

//LoadDir
Array<String> LoadDir(const String &url, bool onlyVisibleFiles, bool skipDots)
{
	Array<String> dirArray = CreateArray<String>();
	DIR *dirHandle = opendir(url);
	
	if(!dirHandle)
		return dirArray;
	
	struct dirent *ent;
	
	if(skipDots && !onlyVisibleFiles)
	{
		String file;
		while((ent = readdir(dirHandle)) != Null)
		{
			if(
				(file = ent->d_name) == "."
#ifdef WIN32
				|| file == ".."
#endif
				)
				continue;
			dirArray->Add(file);
		}
	}
	else if(onlyVisibleFiles)
	{
		String file;
		while((ent = readdir(dirHandle)) != Null)
		{
			if((file = ent->d_name).GetFirstChar() == '.')
				continue;
			dirArray->Add(file);
		}
	}
	else //if(!skipDots && !onlyVisibleFiles)
	{
		while((ent = readdir(dirHandle)) != Null)
		{
			dirArray->Add(ent->d_name);
		}
	}
	
	closedir(dirHandle);
	return dirArray;
}
