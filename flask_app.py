import hashlib

from flask import Flask, render_template, url_for, request
import pymysql




app = Flask(__name__)

host = 'localhost'
user = 'root'
password = 'Zaza_2023!'
db = 'bibliodez'
res = []


@app.route('/search/', methods=["GET"])
def found():
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    no_found = 'По вашему запросу ничего не найдено.'
    element = request.args.get('name')
    res_list = []
    cur = con.cursor()
    if element is None:
        cur.close()
        return render_template('search.html')
    else:
        if len(element) != 0:
            cur.execute(f"SELECT * FROM antiseptik WHERE nameA Like '%{element}%' LIMIT 150;")
            data = cur.fetchall()
            for i in data:
                res_list.append({'name': i[1], 'link': i[2]})
            if len(res_list) != 0:
                cur.close()
                return render_template('search.html', data=res_list)
            else:
                cur.close()
                return render_template('search.html', noSearch=no_found)
        else:
            cur.close()
            return render_template('search.html', noSearch=no_found)


@app.route('/found/', methods=["GET"])
def found_index():
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    no_found = 'По вашему запросу ничего не найдено.'
    element = request.args.get('name')
    res_list = []
    cur = con.cursor()
    if element is None:
        cur.close()
        return render_template('index.html')
    else:
        if len(element) != 0:
            cur.execute(f"SELECT * FROM antiseptik WHERE nameA Like '%{element}%' LIMIT 150;")
            data = cur.fetchall()
            for i in data:
                res_list.append({'name': i[1], 'link': i[2]})
            if len(res_list) != 0:
                cur.close()
                return render_template('index.html', data=res_list)
            else:
                cur.close()
                return render_template('index.html', noSearch=no_found)
        else:
            cur.close()
            no_found = 'По вашему запросу ничего не найдено.'
            return render_template('index.html', noSearch=no_found)


@app.route('/admin', methods=["GET", "POST"])
def found_adm():
    global res
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    if request.method == "GET":
        no_found = 'По вашему запросу ничего не найдено.'
        element = request.args.get('name')
        tmp_res = []
        cur = con.cursor()

        if element is None:
            return render_template('admin.html')
        else:
            if len(element) != 0:
                cur.execute(f"SELECT * FROM antiseptik WHERE nameA Like '%{element}%' LIMIT 150;")
                data = cur.fetchall()
                for i in data:
                    tmp_res.append({'id': i[0], 'name': i[1], 'link': i[2]})
                if len(tmp_res) != 0:
                    res = tmp_res
                    cur.close()
                    return render_template('admin.html', data=tmp_res)
                else:
                    res = tmp_res
                    cur.close()
                    return render_template('admin.html', noSearch=no_found)
            else:
                res = tmp_res
                cur.close()
                no_found = 'По вашему запросу ничего не найдено.'
                return render_template('admin.html', noSearch=no_found)
    elif request.method == "POST":
        req = 'Не все поля заполнены.'
        name = request.form.get('name')
        link = request.form.get('link')
        cur3 = con.cursor()
        if name is None and link is None:
            return render_template('admin.html')
        else:
            if len(name) != 0 and len(link) != 0:
                cur3.execute(
                    f"INSERT INTO antiseptik(nameA, link) VALUES('{name}', '{link}');")
                cur3.close()
                con.commit()
                req = 'Данные сохранены!'
                return render_template('admin.html', admin_req=req)
            else:
                cur3.close()
                return render_template('admin.html', admin_req=req)


def hash_password(password, salt):
    result = salt + password
    return hashlib.sha256(result.encode()).hexdigest()


@app.route('/autorysit', methods=["GET", "POST"])
def login_try():
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    if request.method == "POST":
        no_ent = 'Неверный пароль, попробуйте еще раз.'
        login = request.form.get('login')
        passw = request.form.get('passw')

        cur = con.cursor()
        cur.execute(f"SELECT firstname, passw FROM users WHERE email = '{login}';")
        data = cur.fetchall()
        if login is None and passw is None:
            return render_template('autorysit.html')
        else:
            if len(data) != 0:
                if len(login) != 0 and len(passw) != 0:
                    if data[0][1] == hash_password(passw, data[0][0]):
                        cur.close()
                        return render_template('admin.html')
                    else:
                        return render_template('autorysit.html', noEnter=no_ent)
                else:
                    no_ent = 'Проверьте, все ли поля заполнены!'
                    return render_template('autorysit.html', noEnter=no_ent)
            else:
                no_ent = 'Логин (адрес эл.почты) отсутствует или указан неверно!'
                return render_template('autorysit.html', noEnter=no_ent)
    else:
        return render_template('autorysit.html')


def check_email(email, list_mess):
    count = 0
    for k in list_mess:
        if count < 3:
            if k.get('email') == email:
                count += 1
        else:
            return False
    return True


@app.route('/', methods=["GET", "POST"])
def send_messag():
    return render_template('index.html')


@app.route('/delete/', methods=["POST"])
def delete():
    global res
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    cur3 = con.cursor()
    id_item = request.form.get('delete')
    tmp_name = ''
    for i in res:
        if str(i.get('id')) == id_item:
            tmp_name = i.get('name')
            res.remove(i)
    cur3.execute(f"DELETE FROM antiseptik WHERE id = {id_item};")
    cur3.close()
    con.commit()
    messag_to_admin = f'Позиция {tmp_name} удалена.'
    return render_template('admin.html', data=res, delete_item=messag_to_admin)


@app.route('/giv/', methods=["POST"])
def giv():
    no_found = 'По вашему запросу ничего не найдено!'
    item = request.form.get('giv')
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    cur5 = con.cursor()
    tmp_res = []
    cur5.execute(f"SELECT * FROM antiseptik WHERE nameA Like '{item}%' LIMIT 150;")
    data = cur5.fetchall()
    for i in data:
        tmp_res.append({'name': i[1], 'link': i[2]})
    if len(tmp_res) != 0:
        cur5.close()
        return render_template('search.html', data=tmp_res)
    else:
        cur5.close()
        return render_template('search.html', noSearch=no_found)


if __name__ == '__main__':
    app.run(debug=True)