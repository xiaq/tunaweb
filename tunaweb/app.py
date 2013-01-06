# encoding=utf-8
import logging
from sys import exit
from cgi import escape
from random import randrange, choice
from string import printable
from StringIO import StringIO
from smtplib import SMTP
from email.mime.text import MIMEText

from flask import Flask, render_template, request
from flatland import Form
from flatland.out.markup import Generator
from jinja2 import Markup

from .widgets import OptionalText, RequiredText, RequiredEmail


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


class SignupForm(Form):
    name = RequiredText.using(label=u'姓名').with_properties(
        placeholder=u'尽量填写真实姓名')
    nick = OptionalText.using(label=u'常用 id').with_properties(
        placeholder=u'如果有的话')
    email = RequiredEmail.using(label=u'Email').with_properties(
        placeholder=u'会长会给你发欢迎邮件滴')
    mobile = OptionalText.using(label=u'手机号').with_properties(
        placeholder=u'不许乱写')
    dept = OptionalText.using(label=u'院系&年级').with_properties(
        placeholder=u'[例]计算机系九字班')
    address = OptionalText.using(label=u'住址').with_properties(
        placeholder=u'[例]Zj 10# 192A')
    student_id = OptionalText.using(label=u'学号').with_properties(
        placeholder=u'清华学生号')
    self_intro = OptionalText.using(label=u'自我介绍').with_properties(
        rows=7, placeholder=u'写点什么吧 ^.^')


# TODO make these configurable
FROM = 'signup-request@v.tuna.tsinghua.edu.cn'
TO = 'tuna-secrets@googlegroups.com'
SMTP_SERVER = 'smtp.tuna.tsinghua.edu.cn'
SIGNUP_SUCCEED_FLASH = u'\
报名成功，撒花~ 邮件已经发给 {0}，请静候佳音! :)'.format(TO)
MENTORS = [u'xiaqqaix@gmail.com', u'heroxbd@gmail.com', u'alick9188@gmail.com']
MENTOR_MSG = (u'---- 我是卖萌的分割线 ----\n'
              u'一只野生的 {0} 蹦出来了！\n'
              u'{1}，决定是你了！请速速前来迎新！\n')


def send_signup_form(form):
    name = form['name'].value
    content = StringIO()
    for e in ['name', 'nick', 'email', 'mobile', 'dept', 'address',
              'student_id', 'self_intro']:
        f = form[e]
        content.write(u'{0}: {1}\n'.format(f.label, f.value))
    mentor = choice(MENTORS)
    content.write(MENTOR_MSG.format(name, mentor))

    msg = MIMEText(content.getvalue().encode('utf-8'), _charset='utf-8')
    msg['From'] = FROM
    msg['To'] = TO
    msg['Cc'] = mentor
    msg['Subject'] = (u'来自 {0} 的加入请求'.format(name).encode('utf-8'))
    msg['Reply-To'] = form['email'].value.encode('utf-8')

    conn = SMTP(SMTP_SERVER)
    conn.set_debuglevel(1)
    conn.sendmail(FROM, [TO, mentor], msg.as_string())
    conn.quit()


@app.route('/get_involved', methods=['GET', 'POST'])
def get_involved():
    if request.method == 'POST':
        form = SignupForm.from_flat(request.form.items())
        if form.validate():
            send_signup_form(form)
            return render_template('get_involved.html',
                                   form=SignupForm.from_defaults(),
                                   flash=[SIGNUP_SUCCEED_FLASH],
                                   )
    else:
        form = SignupForm.from_defaults()
    return render_template('get_involved.html',
                           form=form,
                           )


@app.route('/about')
def about():
    return render_template('about.html')


def obfuscate(s, css_class='nospam', sparseness=5, rubbish_len=4,
              rubbish_range=printable):
    output = []
    for c in s:
        if c in '@-.':
            output.append('&#{0};'.format(ord(c)))
        else:
            output.append(escape(c))
        if randrange(0, sparseness) == 0:
            rubbish = [choice(rubbish_range) for j in xrange(rubbish_len)]
            output.append('<span class="{0}">{1}</span>'.format(
                escape(css_class, quote=True),
                escape(''.join(rubbish))))
    return Markup(''.join(output))

try:
    with open('config.py') as f:
        config_code = f.read()
except IOError:
    logging.error('config.py not found or cannot be read, exiting')
    exit(1)
else:
    g = {}
    try:
        exec(config_code, g)
    except:
        logging.exception('Error when evaluating config.py, exiting')
        exit(1)
    else:
        try:
            Config = g['Config']
        except KeyError:
            logging.critical(
                'No Config class defined in config.py, exiting')
            exit(1)
        try:
            config = Config()
        except:
            logging.exception(
                'Failed to initialize Config from config.py, exiting')
            exit(1)

config = Config()
app.config.from_object(config)

if not app.debug:
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(SMTP_SERVER,
                               'tunaweb-error@v.tuna.tsinghua.edu.cn',
                               TO, 'tunaweb error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

app.jinja_env.filters['obfuscate'] = obfuscate
app.jinja_env.globals.update(dict(
    gen=Generator(auto_domid=True, auto_for=True, auto_filter=True,
                  markup_wrapper=Markup)
))


def main():
    app.run(config.host, config.port)
