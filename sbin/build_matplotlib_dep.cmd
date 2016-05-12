@echo off
rem Build Matplotlib Dependencies

set INTERP="C:\\Python35-x64\python"
setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="C:\Program Files (x86)\CMake 2.8\bin\cmake.exe"
set INCLIB=%~dp0\matplotlib-1.2-build-dependencies
set BUILD=%~dp0\build

echo "INTERP: %INTERP%"
echo "INCLIB: %INCLIB%"
echo "BUILD: %BUILD%"

echo "Removing old build directories..."
rmdir /S /Q %INCLIB%
rmdir /S /Q %BUILD%

echo "Creating new build directories..."
mkdir %INCLIB%
mkdir %BUILD%

rem Helper Scripts
echo import sys, zipfile > unzip.py
echo with zipfile.ZipFile(sys.argv[1]) as zf: >> unzip.py
echo     zf.extractall(sys.argv[2]) >> unzip.py

echo import sys, tarfile > untar.py
echo with tarfile.open(sys.argv[1], 'r:gz') as tgz: >> untar.py
echo     tgz.extractall(sys.argv[2]) >> untar.py

echo import sys, os > fixproj.py
echo with open(sys.argv[1], 'r') as fd: >> fixproj.py
echo     content = '\n'.join(line.strip() for line in fd if line.strip()) >> fixproj.py
echo if len(sys.argv) == 3: >> fixproj.py
echo     content = content.replace('Win32', sys.argv[2]).replace('x64', sys.argv[2]) >> fixproj.py
echo with open(sys.argv[1], 'w') as fd: >> fixproj.py
echo     fd.write(content) >> fixproj.py

echo import sys, os, urllib.parse, urllib.request > fetch.py
echo name = urllib.parse.urlsplit(sys.argv[1])[2].split('/')[-1] >> fetch.py
echo if not os.path.exists(name): >> fetch.py
echo     print("Fetching", sys.argv[1]) >> fetch.py
echo     content = urllib.request.urlopen(sys.argv[1]).read() >> fetch.py
echo     with open(name, 'wb') as fd: >> fetch.py
echo         fd.write(content) >> fetch.py

rem Get freetype
echo "Downloading FreeType..."
%INTERP% fetch.py http://download.savannah.gnu.org/releases/freetype/ft261.zip
%INTERP% unzip.py ft261.zip %BUILD%
set FREETYPE=%BUILD%\freetype-2.6.1
echo "FreeType build directory"
ls %FREETYPE%
copy /Y /B ft261.zip %INCLIB%

rem Get zlib
%INTERP% fetch.py http://zlib.net/zlib128.zip
%INTERP% unzip.py zlib128.zip %BUILD%
set ZLIB=%BUILD%\zlib-1.2.8
copy /Y /B zlib128.zip %INCLIB%

rem Get libpng
%INTERP% fetch.py ftp://ftp.simplesystems.org/pub/libpng/png/src/libpng15/libpng-1.5.23.tar.gz
%INTERP% untar.py libpng-1.5.23.tar.gz %BUILD%
set LIBPNG=%BUILD%\libpng-1.5.14
copy /Y /B libpng-1.5.23.tar.gz %INCLIB%

rem Get tcl/tk
%INTERP% fetch.py http://skylineservers.dl.sourceforge.net/project/tcl/Tcl/8.6.4/tcl864-src.zip
%INTERP% unzip.py tcl864-src.zip %BUILD%
copy /Y /B tcl8513-src.zip %INCLIB%
%INTERP% fetch.py http://skylineservers.dl.sourceforge.net/project/tcl/Tcl/8.6.4/tk864-src.zip
%INTERP% unzip.py tk864-src.zip %BUILD%
copy /Y /B tk864-src.zip %INCLIB%

mkdir %INCLIB%\tcl85\include\X11
copy /Y /B %BUILD%\tcl8.6.4\generic\*.h %INCLIB%\tcl86\include\
copy /Y /B %BUILD%\tk8.6.4\generic\*.h %INCLIB%\tcl86\include\
copy /Y /B %BUILD%\tk8.6.4\xlib\X11\* %INCLIB%\tcl86\include\X11\

rem Build for VC 2008 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr90-x64
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build libpng
setlocal
set BUILDDIR=%LIBPNG%-build
rd /S /Q %BUILDDIR%
%CMAKE% -G"NMake Makefiles" -H%LIBPNG% -B%BUILDDIR% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DZLIB_INCLUDE_DIR=%INCLIB% ^
    -DZLIB_LIBRARY:FILEPATH=%INCLIB%\zlib.lib ^
    -DPNG_STATIC=ON ^
    -DPNG_SHARED=OFF
copy /Y /B %BUILDDIR%\pnglibconf.h %INCLIB%
copy /Y /B %LIBPNG%\png.h %INCLIB%
copy /Y /B %LIBPNG%\pngconf.h %INCLIB%
cd %BUILDDIR%
nmake -f Makefile
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B libpng15_static.lib %INCLIB%\png.lib
endlocal

rem Build freetype
setlocal
%INTERP% %~dp0\fixproj.py %FREETYPE%\builds\win32\vc2008\freetype.sln x64
%INTERP% %~dp0\fixproj.py %FREETYPE%\builds\win32\vc2008\freetype.vcproj x64
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\win32\vc2008\freetype.sln /t:Clean;Build /p:Configuration="LIB Release";Platform=x64
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2008 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2008\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

rem Build for VC 2008 32 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x86 /xp
set INCLIB=%INCLIB%\msvcr90-x32
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build libpng
setlocal
set BUILDDIR=%LIBPNG%-build
rd /S /Q %BUILDDIR%
%CMAKE% -G"NMake Makefiles" -H%LIBPNG% -B%BUILDDIR% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DZLIB_INCLUDE_DIR=%INCLIB% ^
    -DZLIB_LIBRARY:FILEPATH=%INCLIB%\zlib.lib ^
    -DPNG_STATIC=ON ^
    -DPNG_SHARED=OFF
copy /Y /B %BUILDDIR%\pnglibconf.h %INCLIB%
copy /Y /B %LIBPNG%\png.h %INCLIB%
copy /Y /B %LIBPNG%\pngconf.h %INCLIB%
cd %BUILDDIR%
nmake -f Makefile
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B libpng15_static.lib %INCLIB%\png.lib
endlocal

rem Build freetype
setlocal
%~dp0\fixproj.py %FREETYPE%\builds\win32\vc2008\freetype.sln Win32
%~dp0\fixproj.py %FREETYPE%\builds\win32\vc2008\freetype.vcproj Win32
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\win32\vc2008\freetype.sln /t:Clean;Build /p:Configuration="LIB Release";Platform=Win32
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2008 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2008\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

rem Build for VC 2010 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr100-x64
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build libpng
setlocal
set BUILDDIR=%LIBPNG%-build
rd /S /Q %BUILDDIR%
%CMAKE% -G"NMake Makefiles" -H%LIBPNG% -B%BUILDDIR% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DZLIB_INCLUDE_DIR=%INCLIB% ^
    -DZLIB_LIBRARY:FILEPATH=%INCLIB%\zlib.lib ^
    -DPNG_STATIC=ON ^
    -DPNG_SHARED=OFF
copy /Y /B %BUILDDIR%\pnglibconf.h %INCLIB%
copy /Y /B %LIBPNG%\png.h %INCLIB%
copy /Y /B %LIBPNG%\pngconf.h %INCLIB%
cd %BUILDDIR%
nmake -f Makefile
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B libpng15_static.lib %INCLIB%\png.lib
endlocal

rem Build freetype
setlocal
%INTERP% %~dp0\fixproj.py %FREETYPE%\builds\win32\vc2010\freetype.sln x64
%INTERP% %~dp0\fixproj.py %FREETYPE%\builds\win32\vc2010\freetype.vcxproj x64
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\win32\vc2010\freetype.sln /t:Clean;Build /p:Configuration="Release";Platform=x64
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2010 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2010\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

rem Build for VC 2010 32 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x86 /xp
set INCLIB=%INCLIB%\msvcr100-x32
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build libpng
setlocal
set BUILDDIR=%LIBPNG%-build
rd /S /Q %BUILDDIR%
%CMAKE% -G"NMake Makefiles" -H%LIBPNG% -B%BUILDDIR% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DZLIB_INCLUDE_DIR=%INCLIB% ^
    -DZLIB_LIBRARY:FILEPATH=%INCLIB%\zlib.lib ^
    -DPNG_STATIC=ON ^
    -DPNG_SHARED=OFF
copy /Y /B %BUILDDIR%\pnglibconf.h %INCLIB%
copy /Y /B %LIBPNG%\png.h %INCLIB%
copy /Y /B %LIBPNG%\pngconf.h %INCLIB%
cd %BUILDDIR%
nmake -f Makefile
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B libpng15_static.lib %INCLIB%\png.lib
endlocal

rem Build freetype
setlocal
%~dp0\fixproj.py %FREETYPE%\builds\win32\vc2010\freetype.sln Win32
%~dp0\fixproj.py %FREETYPE%\builds\win32\vc2010\freetype.vcxproj Win32
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\win32\vc2010\freetype.sln /t:Clean;Build /p:Configuration="Release";Platform=Win32
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2010 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2010\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

endlocal
