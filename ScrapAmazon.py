from logging import exception
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import json
import re
import locale
import pandas as pd
from datetime import datetime,date,timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from sys import platform
from utils.setWebdriver import configWebDriver
download_path=f"{os.getcwd()}/descargas_pdf"
with open("parametros.txt", mode="r") as f:
    lines=f.readlines()
dates=lines[0].strip()
w=configWebDriver()
wait = WebDriverWait(w, 3)
def pdfs_links():
    impr_button=w.find_element(By.XPATH,"//a[contains(., 'Ver o Imprimir Recibo')]")
    pdf_link=impr_button.get_attribute("href")
    return pdf_link
def traking_ids():
    try:
        button_tracking=w.find_element(By.XPATH,"//a[contains(., 'Rastrear paquete')]")
        w.get(button_tracking.get_attribute("href"))
        traking_id=wait.until(EC.visibility_of_element_located((By.XPATH,"//div[contains(text(), 'ID de rastreo:')]"))).text
        if len(traking_id)<20:
            traking_id="Sin Tranking"
        traking_id=re.findall(r"ID de rastreo:(.*)",traking_id)[0]  
    except:
        traking_id="Sin Tranking"
    return "'"+str(traking_id)
def shipment_Date(year):
    try:
        #wait for element
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"a[data-ref='ppx_pt2_dt_b_pt_detail']")))
        w.find_element(By.CSS_SELECTOR,"a[data-ref='ppx_pt2_dt_b_pt_detail']").click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"span[class='tracking-event-date']")))
        shipmentDate=w.find_element(By.CSS_SELECTOR,"span[class='tracking-event-date']").text.replace(", ",",")
        shipmentDate=f"{shipmentDate} de {year}"
        shipmentDate=datetime.strptime(shipmentDate, '%A,%d de %B de %Y').date() 
    except Exception as e:
        print(e)
        shipmentDate="-"
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div[class='pt-status-milestone'] div[class='pt-status-milestone-label active current-label']")))
        status=w.find_element(By.CSS_SELECTOR,"div[class='pt-status-milestone'] div[class='pt-status-milestone-label active current-label']").text
    except:
        status="Sin status"

    return shipmentDate,status
def billings():
    billsRows=w.find_elements(By.XPATH,"//h5[contains(text(),'Resumen del pedido')]/parent::div/div[@class='a-row']")
    billObj={}
    for row in billsRows:
        concept=row.find_element(By.XPATH,"./div[1]").text
        value=row.find_element(By.XPATH,"./div[2]").text
        billObj[concept]=value
    keysDiscount=list(billObj.keys())
    if "Buy any 4, Save 5%:" in keysDiscount :
        cuopon=billObj["Buy any 4, Save 5%:"]
    elif "Deal of the Day:" in keysDiscount:
        cuopon=billObj["Deal of the Day:"]
    elif "Your Coupon Savings:" in keysDiscount:
        cuopon=billObj["Your Coupon Savings:"]
    else:
        cuopon="0"
    return billObj,cuopon
def num_orders():
    num_order=w.find_element(By.XPATH,'//*[@id="orderDetails"]//span[@class="order-date-invoice-item"][2]').text
    num_order=re.findall(r"\d{3}-\d{7}-\d{7}",num_order)[0]
    return num_order

def date_order():
    date_orderd =w.find_element(By.XPATH,'//*[@id="orderDetails"]//span[@class="order-date-invoice-item"][1]').text
    date_orderd=datetime.strptime(date_orderd, 'Pedido el %d de %B de %Y').date()
    return date_orderd
def get_courier(adressName):
    try:
        if len(re.findall(r"8414 Nw 66th St",adressName,flags=re.I))>0:
            courier="EF"
        elif len(re.findall(r"7806 NW 46TH ST",adressName,flags=re.I))>0:
            courier="Alexim"
        elif len(re.findall(r"2868 NW 72ND AVE",adressName,flags=re.I))>0:
            courier="JMC"
        elif len(re.findall(r"1350 NW 121ST AVE",adressName,flags=re.I))>0:
            courier="MSL"
        else:
            courier="otros"
    except:
        courier="Sin courier"
    return courier
def list_adress():
    try:
        dirs=w.find_elements(By.CSS_SELECTOR,"ul[class='displayAddressUL'] li")
    except:
        dirs=[]
    if len(dirs)>0:
        dictAdress={
            "Shipping_Address_Name":dirs[0].text,
            "shipping_Address_Street1":dirs[1].text,
            "shipping_Address_City":dirs[2].text.split(",")[0],
            "shipping_Address_State":dirs[2].text.split(",")[1].strip().split(" ")[0],
            "shipping_Address_Zip":dirs[2].text.split(",")[1].strip().split(" ")[1]
        }
    else:
        dictAdress={
            "shipping_Address_Street1":"-",
            "shipping_Address_City":"-",
            "shipping_Address_State":"-",
            "shipping_Address_Zip":"-"
        }
    return dictAdress
def targets_digits():
    try:
        target_digits=w.find_element(By.XPATH,"//span[contains(text(),'****')]").text
        target_digits=re.findall(r"\d{4}",target_digits)[0]
    except:
        target_digits="sin tarjeta"
    return target_digits
def get_seller():
    try:
        sellBy=w.find_element(By.CSS_SELECTOR,"div[class='a-row'] span[class='a-size-small a-color-secondary']").text
        sellBy=re.findall(r"Vendido por: (.*)",sellBy)[0]
    except:
        sellBy="Sin seller"
    return sellBy
def get_status():
    try:
        status=w.find_element(By.XPATH,"//span[@class='a-color-secondary a-text-bold']/following-sibling::span").text
    except:
        status="Sin status"
    return status
def shiptment_status():
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div[class='pt-status-milestone'] div[class='pt-status-milestone-label active current-label']")))
        status=w.find_element(By.CSS_SELECTOR,"div[class='pt-status-milestone'] div[class='pt-status-milestone-label active current-label']").text
    except:
        status="Sin status"
    return status
def productsList():
    listProducts=w.find_elements(By.CSS_SELECTOR,"div.a-fixed-left-grid")
    productInfo=[]
    for product in listProducts:
        price=product.find_element(By.CSS_SELECTOR,"span[class='a-size-small a-color-price']").text
        condition=product.find_element(By.CSS_SELECTOR,"span[class='a-color-secondary']").text
        try:
            sellBy=product.find_element(By.XPATH,"//span[contains(text(),'Vendido por:')]").text
            sellBy=re.findall(r"Vendido por: (.*)",sellBy)[0]
            sellBy=sellBy.replace("¿Dudas sobre el producto? Pregunta al vendedor","")
        except:
            sellBy="Sin seller"
        try:
            quantity=product.find_element(By.CSS_SELECTOR,"span[class='item-view-qty']").text
        except:
            quantity=1
        name=product.find_element(By.CSS_SELECTOR,"div.a-fixed-left-grid div.a-row:first-child a").text
        link=product.find_element(By.CSS_SELECTOR,"div.a-fixed-left-grid div.a-row:first-child a").get_attribute("href")
        id=re.findall(r"/product/(.*)/ref",link)[0]
        productoObjeto={
            "name":name,
            "id":id,
            "price":price,
            "quantity":quantity,
            "condition":condition,
            "sellBy":sellBy
        }
        productInfo.append(productoObjeto)
    return productInfo
def scrap_order_details(cuenta,dates):
    dateFrom=datetime.strptime(dates.split("-")[0],"%d/%m/%Y").date()
    dateTo=datetime.strptime(dates.split("-")[1],"%d/%m/%Y").date()
    print(dateFrom,dateTo)
    orders_details=[]
    print("PAGINA CARGADA")
    butoon_ped=wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='nav-orders']/span[2]")))
    butoon_ped.click()
    with open("parametros.txt","r") as f:
        lines=f.readlines()
    if int(lines[3])>0:
        w.find_element(By.XPATH,"//span[contains(text(),'Últimos 3 meses')]").click()
        w.find_element(By.XPATH,f"//a[@id='time-filter_{int(lines[3])}']").click()
        w.implicitly_wait(4)
    locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))
    #headers=w.find_elements(By.XPATH,"//div[@class='a-box a-color-offset-background order-header']//div[@class='a-fixed-right-grid-inner']")
    pages=[page.get_attribute("href") for page in w.find_elements(By.XPATH,"//li[@class='a-normal' or @class='a-selected' ]/a")]
    #from_date=date.today()+timedelta(days=-int(d))
    z=1
    fin=False
    while len(w.find_elements(By.XPATH,"//li[@class='a-disabled a-last']"))==0:
        print(f"En la pagina {z}")
        z+=1
        espera=wait.until(EC.visibility_of_element_located((By.XPATH,"//a[contains(text(),'Ver detalles del pedido')]|//a[contains(text(),'View order details')]")))
        orders_elements=w.find_elements(By.XPATH,"//a[contains(text(),'Ver detalles del pedido')]|//a[contains(text(),'View order details')]")
        orders=[order.get_attribute("href") for order in orders_elements]
        fechas_elements=w.find_elements(By.XPATH,"//div[contains(., 'Pedido realizado')]/following-sibling::div/span")
        fechas=[fecha.text for fecha in fechas_elements if len(fecha.text)>0]
        for j in range(len(fechas)):
            scraped=False
            try: 
                date_orederd=datetime.strptime(fechas[j], '%B %d, %Y').date()
            except:
                date_orederd=datetime.strptime(fechas[j], '%d de %B de %Y').date()
            #if j<=5:
            print(f"-----------Pedido con fecha {date_orederd}")
            if dateFrom<=date_orederd and date_orederd<=dateTo:
                print(f"SE EXTRAE CON FECHA {date_orederd}")
                w.get(orders[j])
                target_digits=targets_digits()
                num_order=num_orders()
                print(f"-------NUMERO DE ORDEN {num_order}")
                listAddress=list_adress()
                address_name=listAddress["Shipping_Address_Name"]
                address_street1=listAddress["shipping_Address_Street1"]
                courier=get_courier(address_street1)
                address_city=listAddress["shipping_Address_City"]
                address_state=listAddress["shipping_Address_State"]
                address_zip=listAddress["shipping_Address_Zip"]
                billinInfo,cuopon =billings()
                listProducts=productsList()
                date_orderd =date_order()
                pdf_link=pdfs_links()
                traking_id=traking_ids()
                date_send,sendStatus=shipment_Date(date_orderd.year)
                w.get(pdf_link)
                w.execute_script('window.print();')
                awb=""
                whe=""
                date_refund=""
                scraped=True
                for p in listProducts:
                    dictrow={
                        "Order Date":date_orderd,
                        "Order ID":num_order,
                        "Tittle":p["name"],
                        "Category":"",
                        "ASIN/ISBN":p["id"],
                        "UNSPSC Code":"",
                        "Website":"Amazon.com",
                        "Release Date":"",
                        "Condition":p["condition"],
                        "Seller":p["sellBy"],
                        "Seller Credentials":"",
                        "Quantity":1,
                        "Purchase Price Per Unit":p["price"],
                        "Payment Instrument Type":target_digits,
                        "Purchase Order Number":"",
                        "PO Line Number":"",
                        "Ordering Customer Email":cuenta,
                        "Shipment Date":date_send,
                        "address_name":address_name,
                        "address_street1":address_street1,
                        "address_city":address_city,
                        "address_state":address_state,
                        "address_zip":address_zip,
                        "Order Status":sendStatus,
                        "Courier":courier,
                        "traking_id":traking_id,
                        "item Subtotal":billinInfo["Productos:"],
                        "Taxes":billinInfo["Impuestos:"],
                        "Shipping cost $":billinInfo["Envío:"],
                        "Cupon $":cuopon,
                        "Grand Total $":billinInfo["Total (I.V.A. Incluido):"],
                        
                    }
                    orders_details.append(dictrow)
            else:
                if dateFrom>date_orederd:
                    fin=True
                    #print(f"POR TERMINAR CON FECHA {date_orederd}")
                    break
        if fin:
            break
        if scraped:
            previusUrl=f"https://www.amazon.com/-/es/gp/your-account/order-history/ref=ppx_yo_dt_b_pagination_{z-2}_{z-1}?ie=UTF8&orderFilter=year-2023&search=&startIndex={(z-2)*10}"
            w.get(previusUrl)
        w.find_element(By.XPATH,"//a[text()='Siguiente']").click()
        
    return orders_details

    
    
    #print(orders_details)
    

w.get("https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F-%2Fes%2Fgp%2Fcss%2Forder-history%3Fref_%3Dnav_youraccount_switchacct&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&switch_account=picker&ignoreAuthState=1&_encoding=UTF8")
cuentas=[cuenta.text for cuenta in wait.until(EC.visibility_of_all_elements_located((By.XPATH,"//div[contains(text(), '.com')]")))]
print(cuentas)
orders_total_details=[]

for cuenta in cuentas:
    #try:
        account=wait.until(EC.visibility_of_element_located((By.XPATH,f"//div[contains(text(),'{cuenta}')]")))
        time.sleep(2)
        account.click()
        print(f"leyendo cuenta :{cuenta}")
        orderf=scrap_order_details(cuenta,dates)
        if orderf!=[]:
            orders_total_details.extend(orderf)
        w.get("https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F-%2Fes%2Fgp%2Fcss%2Forder-history%3Fref_%3Dnav_youraccount_switchacct&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&switch_account=picker&ignoreAuthState=1&_encoding=UTF8")
    #except Exception as e:
        #print(e)
        print(f"ERROR NO DEFINIDO EN CUENTA: {cuenta}")
w.close()
df=pd.DataFrame(orders_total_details)
df.to_csv("order_details.csv",index=False,sep=",")


