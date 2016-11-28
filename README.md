Flastocky
======
1. virtualenv setup & install python requirements
    source bin/activate
    pip install -r requirements/stock-dev2.txt

2. system envirment set
    ~/.bash_profile
        add:
            export MAIL_HOST="SMTP.163.com"
            export MAIL_FROM="example_name@163.com"
            export MAIL_TO="example_to@139.com"
            export MAIL_USERNAME="example"
            export MAIL_PASSWORD="example_passwd"
            export XUEQIU_USERNAME="xqexample"
            export XUEQIU_PASSWORDHASH="xqexamplehash"

    source ~/.bash_profile

3. sqlite3 db init
    cd flastocky/
    python manage.py shell
    db.create_all()

4. baseinfo initial
    python manage.py baseinfo_update

5. notify stocks set
    create a file app/stock/config.ini (there is an example :app/stock/config.ini.example)
    format:
    sh600999,0.1,18.4179309137,0.0,0.0,29.064
    sh600036,0.1,16.8595404919,0.0,0.0,15.651

    indacates: stock_id, notify_percent, price_save_now(auto set), (auto set), (auto_set), start_price

6. realtime stock price get
    python manage.py crawler

