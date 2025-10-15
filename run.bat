@echo off
REM 快速运行脚本：将参数透传给 Python 入口
python %~dp0arithmetic_generator.py %*
IF %ERRORLEVEL% NEQ 0 (
  echo 使用示例：
  echo  生成題目：run.bat -r 10 -n 20
  echo  判題：run.bat -e Exercises.txt -a Answers.txt
)