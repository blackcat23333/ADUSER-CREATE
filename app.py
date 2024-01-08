from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_REPLACE, SUBTREE
from ldap3.core.exceptions import LDAPException
import logging
from flask import Flask, request, jsonify

logging.basicConfig(filename='create_ADUser.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def check_user_exists(server_url, admin_user, admin_password, emp_id):
    try:
        server = Server(server_url, get_info=ALL, use_ssl=True)
        conn = Connection(server, user=admin_user, password=admin_password, auto_bind=True)

        # 指定查询条件，这里是通过用户账号查找，修改base_dn的信息
        search_filter = f'(sAMAccountName={emp_id})'
        base_dn = "OU=xx,DC=xx,DC=xx"

        # 执行LDAP查询
        conn.search(search_base=base_dn, search_filter=search_filter, search_scope=SUBTREE)

        # 检查是否有匹配的用户
        if len(conn.entries) > 0:
            logging.info(f"用户 {emp_id} 存在于 {base_dn}")
            return True
        else:
            logging.info(f"用户 {emp_id} 不存在于 {base_dn}")
            return False

    except Exception as e:
        logging.error(f"发生错误：{e}")
        return False
    finally:
        # 关闭LDAP连接
        conn.unbind()

def createUser(server_url, admin_user, admin_password, emp_id, c_name):

    server = Server(server_url, get_info=ALL, use_ssl=True)
    conn = Connection(server, user=admin_user, password=admin_password, auto_bind=True)
    # 新用户信息
    new_user_cn = c_name
    new_user_dn = 'CN=' + new_user_cn + ',OU=xx,DC=xx,DC=xx'

    # 创建新用户
    entry = {
        'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
        'cn': new_user_cn,
        'sAMAccountName': emp_id,
        'userPrincipalName': emp_id + '@xx.xx',
        'displayName': new_user_cn,
        'userPassword': 'YOURPASSWORD',
       # 'userAccountControl': 512 ,  # 不使用字符串形式

    }


    try:
        # 尝试创建用户的代码
        result=conn.add(new_user_dn, attributes=entry)

        # 获取用户当前的userAccountControl值
        conn.search(new_user_dn, '(objectclass=*)', attributes=['userAccountControl'])
        current_user_account_control = conn.entries[0]['userAccountControl'].values
        # 移除ACCOUNTDISABLE标志位
        new_user_account_control = int(current_user_account_control[0]) & ~2
        # 更新用户的userAccountControl属性
        modify_dn = {'userAccountControl': [(MODIFY_REPLACE, [new_user_account_control])]}
        conn.modify(new_user_dn, modify_dn)

        # 添加用户到组（如果需要）修改group_dn：cn为组名
        group_dn = 'CN=xx,OU=xx,DC=xx,DC=xx'
        modify_dn = {'member': [(MODIFY_ADD, [new_user_dn])]}
        conn.modify(group_dn, modify_dn)

        # 修改用户属性示例（如果需要）
        #conn.modify(new_user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})


        print(result)
        if result==1:
            logging.info(f"创建新用户成功：工号为{emp_id},姓名为{c_name}")
            # 断开LDAP连接
            conn.unbind()
            return(1)
        else:
            logging.error(f"用户创建失败")
            conn.unbind()
            return ("用户创建失败")
    except LDAPException as e:
        logging.error(f"用户创建失败：{e}")
        # 断开LDAP连接
        conn.unbind()
        return(e)



app = Flask(__name__)

arr = {}  # 用于保存传输的数据

@app.route('/api/ADUser', methods=['POST'])

def transmit_api():
    payload = request.json  # 从请求中获取json数据

    emp_id = 'N'+payload.get('employee_id')

    c_name = payload.get('c_name')

    if any(value == "" or value is None for value in [emp_id, c_name]):
        response = {
            'code': '1',
            'message':"传输有空值"
        }
        return jsonify(response), 400

    # 将数据保存到字典中
    arr['user_no'] = emp_id
    arr['c_name'] = c_name

    # 打印保存的数据
    print("保存的数据：\n", arr)
    logging.info(f"接收的数据为：{arr}")

    ldap_server_url1 = 'ldap://AD服务器IP地址'    #用于ldap传输
    ldap_server_url2 = 'ldaps://AD服务器IP地址'   #用于ldaps传输
    ldap_admin_user = 'CN=Administrator,CN=xx,DC=xx,DC=xx'
    ldap_admin_password = 'YOURPASSWORD'
    check=check_user_exists(ldap_server_url1, ldap_admin_user, ldap_admin_password, emp_id)
    if check==0:
        result=createUser(ldap_server_url2, ldap_admin_user, ldap_admin_password, emp_id, c_name)
        if result==1:
            # 返回响应
            response = {
                'code': '0',
                'message': 'success'
            }
            return jsonify(response)
        else:
            response = {
                'code': '0',
                'message': result
            }
            return jsonify(response)
    else:
        response = {
            'code': '0',
            'message': "更新成功"
        }
        return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6300)
