from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import time


def load_data():
    call.tableWidget.clearContents()
    connection = sqlite3.connect("database.db")
    cur = connection.cursor()
    sqlquery = "SELECT * FROM MEETS LIMIT 10"
    tablerow = 0
    call.tableWidget.setRowCount(10)
    for row in cur.execute(sqlquery):
        call.tableWidget.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(row[0]))
        call.tableWidget.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row[1]))
        call.tableWidget.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row[2]))
        call.tableWidget.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(row[3]))

        tablerow += 1


def delete_from_database(row_list):
    connection = sqlite3.connect("database.db")
    cur = connection.cursor()
    sqlquery = "DELETE FROM MEETS WHERE Name={} AND Url={} AND Start={} AND End={}".format(
        "'" + str(row_list[0]) + "'",
        "'" + str(row_list[1]) + "'",
        "'" + str(row_list[2]) + "'",
        "'" + str(row_list[3]) + "'")
    cur.execute(sqlquery)
    connection.commit()
    connection.close()
    load_data()


def delete_row():
    rows = call.tableWidget.selectedIndexes()
    for row in rows:
        row_list = (call.tableWidget.item(row.row(), 0).text(), call.tableWidget.item(row.row(), 1).text(),
                    call.tableWidget.item(row.row(), 2).text(), call.tableWidget.item(row.row(), 3).text())
        delete_from_database(row_list)


class automation:
    def __init__(self):
        self.driver = None
        self.opt = Options()
        self.opt.add_argument('--disable-blink-features=AutomationControlled')
        self.opt.add_argument('--start-maximized')
        self.opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        call.tableWidget.setColumnWidth(2, 200)
        call.tableWidget.setColumnWidth(3, 200)
        call.tableWidget.read_only = False
        load_data()

    def start(self, val, url):
        driver = webdriver.Chrome(options=self.opt,
                                  executable_path="C:\\Users\\Studio\\PycharmProjects\\Microsoft_team_automation"
                                                  "\\chromedriver.exe")
        driver.get(url)
        join = driver.find_element_by_xpath("//*[@id='buttonsbox']/button[2]")
        join.click()
        time.sleep(15)
        name = driver.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div['
            '2]/div/div/section/div[1]/div/div[1]/input')
        # name.send_keys('')
        name.send_keys(val)

        mic = driver.find_element_by_xpath("//*[@id='preJoinAudioButton']/div/button/span[1]")
        if mic.is_enabled():
            mic.click()

        cam = driver.find_element_by_xpath("//*[@id='page-content-wrapper']/div["
                                           "1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div["
                                           "2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]")
        if cam.is_enabled():
            cam.click()

        joinnow = driver.find_element_by_xpath(
            "//*[@id='page-content-wrapper']/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div["
            "2]/div/div/section/div[1]/div/div[2]/button")
        joinnow.click()
        self.driver = driver

    def stop(self):
        close = self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div/div[1]/div/calling-pre-join-screen/div/div/button")
        close.click()
        self.driver.close()


def start():
    name = call.lineEdit.text()
    url = call.lineEdit_2.text()
    auto.start(name, url)


def end():
    auto.stop()


def schedule():
    name = call.lineEdit.text()
    url = call.lineEdit_2.text()
    date_and_time1 = call.dateTimeEdit.dateTime().toPyDateTime()
    date_and_time2 = call.dateTimeEdit_2.dateTime().toPyDateTime()
    connection = sqlite3.connect("database.db")
    cur = connection.cursor()
    sqlquery = """INSERT INTO MEETS (Name,Url,Start,End) VALUES ({},{},{},{});""".format('"' + str(name) + '"',
                                                                                         '"' + str(url) + '"',
                                                                                         '"' + str(
                                                                                             date_and_time1) + '"',
                                                                                         '"' + str(
                                                                                             date_and_time2) + '"')
    cur.execute(sqlquery)
    connection.commit()
    connection.close()
    load_data()


def delete():
    delete_row()


def schedule_tasks():
    connection = sqlite3.connect("database.db")
    cur = connection.cursor()
    sqlquery = "SELECT * FROM MEETS LIMIT 10"
    for row in cur.execute(sqlquery):
        sched.add_job(auto.start, 'date', run_date=row[3], args=[row[0], row[1]])
        sched.add_job(auto.stop, 'date', run_date=row[3], args=[row[0], row[1]])


app = QtWidgets.QApplication([])
call = loadUi("micromeet.ui")
QtWidgets.QMainWindow.setWindowTitle(call, "Automate Microsoft Teams")
QtWidgets.QMainWindow.setWindowIcon(call, QtGui.QIcon('logo.png'))
auto = automation()

call.pushButton.clicked.connect(start)
call.pushButton_2.clicked.connect(end)
call.pushButton_3.clicked.connect(schedule)
call.pushButton_4.clicked.connect(delete)
call.show()

sched = BlockingScheduler()

app.exec()
schedule_tasks()
sched.start()
