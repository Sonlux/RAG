@echo off
REM Quick Start Script for PDF Metadata Extraction (Windows)
REM Usage: run_metadata_extraction.bat <input_directory> <output_csv>

if "%~1"=="" goto usage
if "%~2"=="" goto usage

set INPUT_DIR=%~1
set OUTPUT_CSV=%~2

echo ╔════════════════════════════════════════════════════╗
echo ║   PDF Metadata Extraction Tool                    ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo 📁 Input:  %INPUT_DIR%
echo 💾 Output: %OUTPUT_CSV%
echo.

REM Check if input directory exists
if not exist "%INPUT_DIR%" (
    echo ❌ Error: Directory '%INPUT_DIR%' not found!
    exit /b 1
)

echo 📊 Processing PDFs from %INPUT_DIR%...
echo.

REM Run the extraction
python cli_metadata_extractor.py -i "%INPUT_DIR%" -o "%OUTPUT_CSV%" --verbose

echo.
echo ✅ Extraction complete!
echo 📄 Results saved to: %OUTPUT_CSV%
echo.
echo To view the CSV:
echo   - Open in Excel
echo   - Or run: type "%OUTPUT_CSV%"
goto end

:usage
echo Usage: %~nx0 ^<input_directory^> ^<output_csv^>
echo.
echo Examples:
echo   %~nx0 .\documents metadata.csv
echo   %~nx0 D:\corporate_docs corporate_metadata.csv
exit /b 1

:end
