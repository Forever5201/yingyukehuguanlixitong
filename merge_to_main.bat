@echo off
echo 正在切换到main分支...
git checkout main

echo 正在合并cursor/familiarize-with-project-code-bdf1分支...
git merge cursor/familiarize-with-project-code-bdf1

echo 正在推送到远程main分支...
git push origin main

echo 正在切换回cursor/familiarize-with-project-code-bdf1分支...
git checkout cursor/familiarize-with-project-code-bdf1

echo 操作完成！
pause


