@echo off
title Space Bioreactor Presentation Server
echo ========================================================
echo  ASTRO-BIOREACTOR & 2-AXIS CLINOSTAT 3D SHOWCASE
echo  Zher zhane Garysh turaly gylym - Zhambylkyzy Kausar
echo ========================================================
echo.
echo Starting local web server at http://localhost:8000 ...
start "" "http://localhost:8000"
python -m http.server 8000
pause
