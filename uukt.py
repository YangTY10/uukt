from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import re, datetime

from selenium.webdriver import Chrome
import time

import pymysql

conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="rootroot", db="db_uukt", charset='utf8mb4')
cur = conn.cursor()

driver = Chrome("./chromedriver")


def nextpage(element):
    try:
        driver.find_element_by_class_name(element)
        return True
    except:
        return False


def price_element(box, element):
    try:
        soup.find(box, class_=element)
        return True
    except:
        return False


def rem_rdl_sp():
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')
    if '' in room_date_list:
        room_date_list.remove('')


location_list = ["south-beach", "kenting"]
for l in location_list:
    first_url = "http://uukt.com.tw/inn-list/%s/" % (l)
    driver.get(first_url)
    time.sleep(3)

    page = 0
    location = l
    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # url = "http://uukt.com.tw/inn-list/kenting/"
        # response = urlopen(url)
        # soup = BeautifulSoup(response)
        urls = soup.find_all("div", class_="brief")
        for u in urls:
            hotel_url = "http://uukt.com.tw" + u.find("a")["href"]
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            # print(hotel_url)
            req = requests.get(hotel_url)
            soup = BeautifulSoup(req.text, "html.parser")
            div = soup.find("div", class_="widget clearfix widget-contact-us")
            li_all = div.find_all("li")

            for i in range(len(li_all)):
                if "名稱：" in li_all[i].text:
                    name = li_all[i].text
                    name = re.sub(" ", "", name)
                    name = re.sub("\n", "", name)
                    name = re.sub("\u3000", " ", name)
                    name = re.sub("名稱：", "", name)

                elif "地址：" in li_all[i].text:
                    address = li_all[i].text
                    address = re.sub(" ", "", address)
                    address = re.sub("\n", "", address)
                    address = re.sub("地址：", "", address)
                    address = re.sub("(入住前請到大尖山飯店辦理入住登記)", "", address)
                    address = re.sub("看地圖", "", address)

                elif "聯絡電話：" in li_all[i].text:
                    phone = li_all[i].text
                    phone = re.sub(" ", "", phone)
                    phone = re.sub("-", "", phone)
                    phone = re.sub("\n", "", phone)
                    phone = re.sub("聯絡電話：", "", phone)
                    phone = re.sub("打電話", ",", phone)
                    phone = phone.split(",")
                    phone.remove("")
                    phone_list = []
                    for i in range(len(phone)):
                        pattern = re.compile(r"[\d]{9,10}")
                        match = pattern.match(phone[i])
                        if match:
                            match = match.group()
                            phone_list.append(match)
                        else:
                            pass
                    # print(phone_list)

                    phone_verify_list = []
                    for i in phone_list:
                        pattern1 = re.compile(r"^09\d{8}")
                        pattern2 = re.compile(r"^08\d{7}")
                        match = pattern1.match(i) or pattern2.match(i)
                        if match:
                            verify = "YES"
                            phone_verify_list.append(verify)
                        else:
                            verify = "NO"
                            phone_verify_list.append(verify)
                    if "YES" in phone_verify_list:
                        phone_verify = "Valid"
                    else:
                        phone_verify = "Invalid"
                    # print(phone_verify)

                elif "電子信箱：" in li_all[i].text:
                    email = li_all[i].text
                    email = re.sub(" ", "", email)
                    email = re.sub("\n", "", email)
                    email = re.sub("主旨請用本名及住宿日期,方便查看.", "", email)
                    email = re.sub("電子信箱：", "", email)

                    if re.match(r'^[0-9a-zA-Z_]{1}[0-9a-zA-Z_.]{0,19}@[0-9a-zA-Z.]{1,13}\.[com,net,com.tw]{1,6}$',
                                email):
                        email_verify = "Valid"
                    else:
                        email_verify = "Invalid"

                    if phone_verify == "Valid" and email_verify == "Valid":
                        phone_email_verify = 1
                    elif phone_verify == "Valid" and email_verify == "Invalid":
                        phone_email_verify = 2
                    elif phone_verify == "Invalid" and email_verify == "Valid":
                        phone_email_verify = 3
                    elif phone_verify == "Invalid" and email_verify == "Invalid":
                        phone_email_verify = 4

                    hotel_j = {"hotel_url": hotel_url, "hotel_name": name, "location": location, "address": address,
                               "phone": str(phone_list), "email": email, "crawler_date": date,
                               "verify_id": phone_email_verify}
                    print(hotel_j)
                    insertsql = "INSERT INTO db_uukt.hotel (hotel_url, hotel_name, location, address, phone, email, crawler_date, verify_id) \
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    value = (hotel_j["hotel_url"], hotel_j["hotel_name"], hotel_j["location"], hotel_j["address"],
                             hotel_j["phone"], hotel_j["email"], hotel_j["crawler_date"], hotel_j["verify_id"])
                    cur.execute(insertsql, value)
                    conn.commit()
                    print("(hotel) Insert to mysql successfully!!")

            price_wide = soup.find("div", class_="price-wide")
            if price_wide == None:
                room_j = {"room": None, "date": None, "price": "0"}
                print(room_j)
            else:
                room_date = price_wide.find_all("tr")
                room_date = room_date[0].text
                room_date = room_date.split("\n")
                room_date.remove("")
                room_date.remove('')
                del room_date[0]
                room_date_list = []
                for rd in room_date:
                    rd = rd.strip()
                    rd = re.sub("       ", "", rd)
                    room_date_list.append(rd)
                # print(room_date_list)

                room_price = price_wide.find_all("td", class_="price")
                room_price_list = []
                for p in room_price:
                    p = p.text.strip()
                    room_price_list.append(p)
                # print(room_price_list)

                room = price_wide.find_all("td")
                room_list = []
                for i in range(len(room_date_list) + 1,
                               int(len(room_price_list) / len(room_date_list) * (len(room_date_list) + 1) + 1),
                               len(room_date_list) + 1):
                    room[i].text
                    room_list.append(room[i].text)
                # print(room_list)

                rem_rdl_sp()

                if hotel_j["hotel_url"] == "http://uukt.com.tw/kenting/243":
                    del_list = [3, 5, 5, 5, 5, 8, 10, 10, 10, 10, 13, 15, 15, 15, 15, 18, 20, 20, 20, 20, 23, 25, 25,
                                25, 25]
                    for d in del_list:
                        del room_price_list[d]
                if hotel_j["hotel_url"] == "http://uukt.com.tw/kenting/81":
                    del_list = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
                    for d in del_list:
                        del room_price_list[d]

                if int(len(room_date_list) * len(room_list)) != len(room_price_list):
                    for r in room_price_list:
                        if '-' in room_price_list:
                            room_price_list.remove('-')
                        else:
                            pass
                else:
                    room_price_list1 = []
                    for i in room_price_list:
                        if i == "-":
                            i = re.sub("-", "0", i)
                            room_price_list1.append(i)
                        else:
                            room_price_list1.append(i)
                    room_price_list = room_price_list1

                k = 0
                for i in range(len(room_list)):
                    for j in range(len(room_date_list)):
                        room_j = {"room": room_list[i], "date": room_date_list[j], "price": room_price_list[k]}
                        k = k + 1
                        print(room_j)

                        insertsql = "INSERT INTO db_uukt.room (hotel_url, room_type, room_date, price)\
                                        VALUES (%s, %s, %s, %s)"
                        value = (hotel_j["hotel_url"], room_j["room"], room_j["date"], int(room_j["price"]))
                        cur.execute(insertsql, value)
                        conn.commit()
                        print("(room) Insert to mysql successfully!!")

                ### 加分題 ###
                room_price_list2 = []
                    for i in room_price_list:
                        i = int(i)
                        room_price_list2.append(i)
                
                cpp = [room_price_list2[i:i+len(room_date_list)] for i in range(0, len(room_price_list2), len(room_date_list))]
                    
                for i in range(len(room_list)):
                    
                    j = {"hotel_name": name, "room": room_list[i], "max_price": max(cpp[i]),
                        "min_price": min(cpp[i]), "price_count": len(cpp[0]) , "crawler_date": date}
                    print(j)
                    insertsql = "INSERT INTO db_uukt.plus (hotel_name, room_type, max_price, min_price, price_count, crawler_date)\
                                 VALUES (%s, %s, %s, %s, %s, %s)"
                    value = (j["hotel_name"], j["room"], j["max_price"], j["min_price"], j["price_count"], j["crawler_date"])
                    cur.execute(insertsql, value)
                    conn.commit()
                    print("(plus) Insert to mysql successfully!!")


        n = nextpage("J-paginationjs-next")
        if n == True:
            next_page = driver.find_element_by_class_name("J-paginationjs-next")
            next_page.click()
            page = page + 1
            time.sleep(5)
        else:
            break
conn.close()
driver.close()
