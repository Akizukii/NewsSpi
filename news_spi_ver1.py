# -*- coding: UTF-8 -*-

## 更新内容
#2020.01.03更新
# 取消selenium部分
# 修改为只爬取http://tz.cqut.edu.cn页面（因为该页面没有设置反爬，可以不使用无头浏览器减少资源消耗
# 弊端为若学校在1小时内更新内容超过40条则会出现漏爬的情况，考虑日常情况，这种情况基本不会发生
#====================================
# 2019.12.18
# 优化发件方式
# 添加了对超时报错的处理
# 使用新的scheduler
# 因学校网站更新202方式+js混淆修改cookie反爬，考虑逆向成本，改为使用chorme-headless+selenium方式爬取i

## 未来计划
# 与QQbot联动

import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

import sqlite3

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import os
import smtplib

# import schedule
from apscheduler.schedulers.blocking import BlockingScheduler

import time
from datetime import datetime

root_addr = 'http://tz.cqut.edu.cn/'
xxtz_link = 'http://tz.cqut.edu.cn/xxtz.htm'
bmtz_link = 'http://tz.cqut.edu.cn/bmtz.htm'

db_name = 'news.db'
userdb_path = '../mail_sys/server/app/user.db'

from_name = '雀巢1+2特浓'

user_filename = 'user_list.txt'

# conn = sqlite3.connect(db_name)
# cur = conn.cursor()

# def init_db(self):
# 		conn = sqlite3.connect(db_name)
# 		cur = conn.cursor()
# 		cur.execute(' CREATE TABLE IF NOT EXISTS news (news_title varchar(100) primary key, news_link varchar(100)) ')
# 		conn.commit()
# 		conn.close()

def init_db():
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	cur.execute(' CREATE TABLE IF NOT EXISTS news (news_title varchar(100) primary key, news_link varchar(100)) ')
	conn.commit()
	conn.close()

# news_block 为元组数据(news_title, news_link)
def insert_table(news_block_list):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	for news_block in news_block_list:
		cur.execute(' INSERT OR IGNORE INTO news VALUES (?, ?) ', (news_block[0], news_block[1]))
	conn.commit()
	conn.close()

def is_in_table(news_block):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	cur.execute("SELECT * FROM news WHERE news_title='%s'" % news_block[0])
	result = cur.fetchall()
	conn.close()
	return result

def get_news_list():
	r = requests.get(root_addr)
	bsObj = BeautifulSoup(r.content, 'lxml')

	# 学校通知列表拉取
	news_list = []
	temp = bsObj.find(id='zjtz')
	all_li = temp.find_all('li')
	for li in all_li:
		news_list.append([li.a['title'], root_addr+li.a['href']])
	
	# 部门通知列表拉去
	all_li = bsObj.find_all(id='bmtz')
	for li in all_li:
		news_list.append([li.div.div.a.text+li.a['title'], root_addr+li.a['href']])

	return news_list

# 获取需要更新的news的list
def get_update_list():
	update_list = []
	news_list = get_news_list()
	for news in news_list:
		if not is_in_table(news):
			update_list.append(news)
	return update_list

# def get_xxtz_update_list():
# 	return get_update_list(xxtz_link)

# def get_bmtz_update_list():
# 	return get_update_list(bmtz_link)

def make_email_content(update_list):
	title = '发现新闻网更新内容'+str(len(update_list)) + '条'
	content = '<p>内容如下：</p>\n'
	for news in update_list:
		temp = "<p><a href='{}'>{}</a></p>\n".format(news[1], news[0])
		content+=temp
	return title, content

def _format_addr(s):
	name, addr = parseaddr(s)
	return formataddr((Header(name, 'utf-8').encode(), addr))

# def email_notice(title, content):
# 	from_addr = 'akizuki@2016.cqut.edu.cn'
# 	password = 'jARMeSmiXaNx5dhZ'
# 	to_addr = '1151296369@qq.com'
# 	smtp_server = 'smtp.exmail.qq.com'

# 	msg = MIMEText(content, 'html', 'utf-8')
# 	msg['From'] = _format_addr('乳酪向日葵饼干 <%s>' % from_addr)
# 	msg['To'] = _format_addr('青菜 <%s>' % to_addr)
# 	msg['Subject'] = Header(title, 'utf-8').encode()

# 	try:	
# 		server = smtplib.SMTP_SSL(smtp_server, 465)
# 		server.ehlo()
# 		server.login(from_addr, password)
# 		server.sendmail(from_addr, [to_addr], msg.as_string())
# 		log('邮件成功发送')
# 	except smtplib.SMTPException:
# 		log('邮件发送失败')

# 	server.quit()

# def email_notice_dage(title, content):
# 	from_addr = 'akizuki@2016.cqut.edu.cn'
# 	password = 'jARMeSmiXaNx5dhZ'
# 	to_addr = '1878145728@qq.com'
# 	smtp_server = 'smtp.exmail.qq.com'

# 	msg = MIMEText(content, 'html', 'utf-8')
# 	msg['From'] = _format_addr('乳酪向日葵饼干 <%s>' % from_addr)
# 	msg['To'] = _format_addr('大哥 <%s>' % to_addr)
# 	msg['Subject'] = Header(title, 'utf-8').encode()

# 	try:	
# 		server = smtplib.SMTP_SSL(smtp_server, 465)
# 		server.ehlo()
# 		server.login(from_addr, password)
# 		server.sendmail(from_addr, [to_addr], msg.as_string())
# 		log('邮件成功发送(大哥)')
# 	except smtplib.SMTPException:
# 		log('邮件发送失败(大哥)')

# 	server.quit()

def get_users():
	with open(user_filename) as f:
		users = f.readlines()

	users = [user.strip('\n') for user in users]

	return users
	
def get_users_from_db():
	conn = sqlite3.connect(userdb_path)
	cur = conn.cursor()
	cur.execute(' select username from users where status=1 ')
	result = cur.fetchall()
	conn.close()
	return result
	

def email_notice_all(title, content):
	from_addr = ''
	password = ''
	smtp_server = 'smtp.exmail.qq.com'

	msg = MIMEText(content, 'html', 'utf-8')
	msg['From'] = _format_addr(from_name+' <%s>' % from_addr)
	msg['Subject'] = Header(title, 'utf-8').encode()

	# 旧方法，从txt里读取
	# users = get_users()
	
	# 新版，使用了sqlite3数据库
	users = []
	temp = get_users_from_db()
	for t in temp:
		users.append(t[0])
	

	try:	
		server = smtplib.SMTP_SSL(smtp_server, 465)
		server.ehlo()
		server.login(from_addr, password)
		server.sendmail(from_addr, users, msg.as_string())
		log('邮件成功发送')
	except smtplib.SMTPException:
		log('邮件发送失败')

	server.quit()


def looking_news():
	log('Looking_news...')
	# try:
	# 	xxtz = get_xxtz_update_list()
	# 	bmtz = get_bmtz_update_list()
	# except Timeout:
	# 	log('request timeout.')
	# xxtz = get_xxtz_update_list()
	# bmtz = get_bmtz_update_list()
	update_list = get_update_list()
	log('get {} news'.format(len(update_list)))
	if update_list:
		log('update_list...')
		insert_table(update_list)
		title, content = make_email_content(update_list)
		email_notice_all(title, content)

def log(content):
	now = datetime.now()
	temp = now.strftime('%Y %b %d %H:%M:%S')
	temp += '  ' + content
	print(temp)
	f = open('log.txt', 'a')
	f.write(temp+'\n')

if __name__ == '__main__':
	log('---------------------')
	log('Start running...')
	# 判断用户文件是否存在
	if not os.path.isfile(user_filename):
		with open(user_filename) as f:
			f.write('1151296369@qq.com\n')
			log('create user_list file...')
	else:
		log('user_list file exist...')

	init_db()
	log('db init...')

	scheduler = BlockingScheduler()

	scheduler.add_job(looking_news, 'cron', hour='*')
	log('scheduler init...')

	scheduler.start()
	# schedule.every().hour.do(looking_news)
	# while True:
	# 	schedule.run_pending()
	# 	time.sleep(10)