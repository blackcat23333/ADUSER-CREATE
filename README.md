# ADUSER-CREATE

默认以docker部署，docker镜像仓库地址请自行修改，也可以直接运行app.py

功能：默认传输工号及姓名到指定服务器6300端口即可在AD服务器中自动创建用户

显示名称为姓名：c_name 账号为工号：emp_id

CN=xx,DC=xx,DC=xx 请自行修改 可以在AD服务器上powershell管理员状态下执行：Get-AdUser -Filter {SamAccountName -eq 'Administrator'} | Select-Object SamAccountName, DistinguishedName 查看AD域管理员及其cn\DC  如需查看其他用户明细信息 修改'Administrator'为其他用户显示名即可
