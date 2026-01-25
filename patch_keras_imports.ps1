 = @(
    "OpenFace.py",
    "Facenet.py", 
    "VGGFace.py"
)

foreach ( in ) {
     = "C:\Users\arier\AppData\Local\Programs\Python\Python311\Lib\site-packages\deepface\basemodels\"
    
    if (Test-Path ) {
         = Get-Content  -Raw
         =  -replace "from keras\.layers\.core import", "from keras.layers import"
         =  -replace "import keras\.layers\.core", "import keras.layers"
        
        Set-Content -Path  -Value  -Encoding UTF8
        Write-Host "Patched: " -ForegroundColor Green
    } else {
        Write-Host "File not found: " -ForegroundColor Yellow
    }
}

Write-Host "All patches applied!" -ForegroundColor Green
