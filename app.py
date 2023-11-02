import hashlib

from flask import Flask, render_template, url_for, request
import pymysql


app = Flask(__name__)

host = 'localhost'
user = 'root'
password = 'Zaza_2023!'
db = 'test123'
try:
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
except Exception as e:
    print(e)
res = []


@app.route('/search', methods=["GET"])
def found():
    global con
    no_found = 'По вашему запросу ничего не найдено.'
    element = request.args.get('name')
    res_list = []
    cur = con.cursor()
    if element is None:
        return render_template('search.html')
    else:
        if len(element) != 0:
            cur.execute(f"SELECT * FROM antiseptik WHERE nameA Like '%{element}%' LIMIT 100;")
            data = cur.fetchall()
            for i in data:
                res_list.append({'name': i[1], 'content': i[2], 'link': i[3]})
            if len(res_list) != 0:
                return render_template('search.html', data=res_list)
            else:
                return render_template('search.html', noSearch=no_found)
        else:
            no_found = 'По вашему запросу ничего не найдено.'
            return render_template('search.html', noSearch=no_found)


def giv_messag():
    global con
    messag_res = []
    cur1 = con.cursor()
    cur1.execute('SELECT id, messag, sender_name, sender_email FROM messages ORDER BY id DESC LIMIT 10;')
    data_mess = cur1.fetchall()
    if len(data_mess) != 0:
        for j in data_mess:
            messag_res.append({'id': j[0], 'messag': j[1], 'name': j[2], 'email': j[3]})
    cur1.close()
    return messag_res


res_mess = giv_messag()



@app.route('/admin', methods=["GET", "POST"])
def found_adm():
    global con, res_mess, res
    if request.method == "GET":
        no_found = 'По вашему запросу ничего не найдено.'
        element = request.args.get('name')
        tmp_res = []
        cur = con.cursor()

        if element is None:
            return render_template('admin.html')
        else:
            if len(element) != 0:
                cur.execute(f"SELECT * FROM antiseptik WHERE nameA Like '%{element}%' LIMIT 100;")
                data = cur.fetchall()
                for i in data:
                    tmp_res.append({'id': i[0], 'name': i[1], 'content': i[2], 'link': i[3]})
                if len(tmp_res) != 0:
                    res = tmp_res
                    return render_template('admin.html', data=tmp_res, messag=giv_messag())
                else:
                    res = tmp_res
                    return render_template('admin.html', noSearch=no_found, messag=giv_messag())
            else:
                res = tmp_res
                no_found = 'По вашему запросу ничего не найдено.'
                return render_template('admin.html', noSearch=no_found, messag=giv_messag())
    elif request.method == "POST":
        req = 'Не все поля заполнены.'
        name = request.form.get('name')
        link = request.form.get('link')
        messag = request.form.get('massag')
        cur3 = con.cursor()
        if name is None and link is None and messag is None:
            return render_template('admin.html')
        else:
            if len(name) != 0 and len(link) != 0 and len(messag) != 0:
                cur3.execute(
                    f"INSERT INTO antiseptik(nameA, link, descriptionA) VALUES('{name}', '{link}', '{messag}');")
                cur3.close()
                con.commit()
                req = 'Данные сохранены!'
                return render_template('admin.html', admin_req=req, messag=giv_messag())
            else:
                return render_template('admin.html', admin_req=req, messag=giv_messag())


def hash_password(password, salt):
    result = salt + password
    return hashlib.sha256(result.encode()).hexdigest()


@app.route('/autorysit', methods=["GET", "POST"])
def login_try():
    if request.method == "POST":
        global con, res_mess
        no_ent = 'Неверный пароль, попробуйте еще раз.'
        login = request.form.get('login')
        passw = request.form.get('passw')

        cur = con.cursor()
        cur.execute(f"SELECT lastname, passw FROM users WHERE email = '{login}';")
        data = cur.fetchall()
        if login is None and passw is None:
            return render_template('autorysit.html')
        else:
            if len(data) != 0:
                if len(login) != 0 and len(passw) != 0:
                    if data[0][1] == hash_password(passw, data[0][0]):
                        return render_template('admin.html', messag=giv_messag())
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
        print(count, k.get('email'))
        if count < 3:
            if k.get('email') == email:
                count += 1
        else:
            return False
    return True


@app.route('/', methods=["GET", "POST"])
def send_messag():
    if request.method == "POST":
        global con
        req = 'Не все поля заполнены.'
        name = request.form.get('name')
        email = request.form.get('email')
        messag = request.form.get('massag')
        cur2 = con.cursor()
        if name is None and email is None and messag is None:
            return render_template('index.html')
        else:
            if len(name) != 0 and len(email) != 0 and len(messag) != 0:
                if check_email(email, giv_messag()):
                    if len(messag) > 1000:
                        req = f'Слишком много текста - {len(messag)} символов! НЕ БОЛЕЕ 1000!'
                        return render_template('index.html', req1=req)
                    else:
                        cur2.execute(
                            f"INSERT INTO messages(sender_name, sender_email, messag) VALUES('{name}', '{email}', '{messag}');")
                        cur2.close()
                        con.commit()
                        req = 'Сообщение отправлено!'
                        return render_template('index.html', req1=req)
                else:
                    req = 'Специалист с вами свяжется, ожидайте. Сообщение заблокированно.'
                    return render_template('index.html', req1=req)
            else:
                return render_template('index.html', req1=req)
    else:
        return render_template('index.html')


@app.route('/delete/', methods=["POST"])
def delete():
    global res, con
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
    return render_template('admin.html', data=res, delete_item=messag_to_admin, messag=giv_messag())


@app.route('/del_messag/', methods=["POST"])
def delete_messag():
    global res, con
    tmp_list = giv_messag()
    cur4 = con.cursor()
    id_item = request.form.get('delete_messag')
    email_send = ''
    for i in tmp_list:
        if str(i.get('id')) == id_item:
            email_send = i.get('email')
            tmp_list.remove(i)
    cur4.execute(f"DELETE FROM messages WHERE id = {id_item};")
    cur4.close()
    con.commit()
    messag_to_admin = f'Сообщение от {email_send} - удалено.'
    return render_template('admin.html', data=res, admin_del_mess=messag_to_admin, messag=giv_messag())



if __name__ == "__main__":
    app.run(debug=True)