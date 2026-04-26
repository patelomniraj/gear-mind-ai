@echo off
echo Training Worm Gear Model...
echo.
cd models
py train_worm_model.py
cd ..
echo.
echo Training complete! Press any key to exit...
pause
