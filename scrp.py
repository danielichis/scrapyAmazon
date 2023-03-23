from logging import exception
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import re
import locale
import pandas as pd
from datetime import datetime,date,timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

download_path=f"{os.getcwd()}/descargas_pdf"
with open("parametros.txt", mode="r") as f:
    lines=f.readlines()
d=lines[0]
pdfs_path=lines[1]
w='chromedriver'
options = webdriver.ChromeOptions() 
settings = {
    "recentDestinations": [{
        "id": "Save as PDF",
        "origin": "local",
        "account": ""
    }],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
}
prefs = {
    'printing.print_preview_sticky_settings.appState': json.dumps(settings),
    'savefile.default_directory':download_path
}
options.add_argument('--kiosk-printing')
options.add_experimental_option('prefs', prefs)
options.add_argument(f"user-data-dir={pdfs_path}")
w = webdriver.Chrome(executable_path=w, options=options)
wait = WebDriverWait(w, 30)
def pdfs_links():
    impr_button=w.find_element(By.XPATH,"//a[contains(., 'Ver o Imprimir Recibo')]")
    pdf_link=impr_button.get_attribute("href")
    return pdf_link
def traking_ids():
    try:
        button_tracking=w.find_element(By.XPATH,"//a[contains(., 'Rastrear paquete')]")
        w.get(button_tracking.get_attribute("href"))
        traking_id=wait.until(EC.visibility_of_element_located((By.XPATH,"//div[contains(text(), 'ID de rastreo:')]"))).text
        traking_id=re.findall(r"T?B?A?\d{12,}",traking_id)[0]
    except:
        traking_id="Sin Tranking"
    return "'"+str(traking_id)
def taxes():
    tax =w.find_element(By.XPATH,'//div[contains(., "Impuestos")]/following-sibling::div/span').text
    tax=re.findall(r"\d+\.\d+",tax)[0]
    return tax
def num_orders():
    num_order=w.find_element(By.XPATH,'//*[@id="orderDetails"]//span[@class="order-date-invoice-item"][2]').text
    num_order=re.findall(r"\d{3}-\d{7}-\d{7}",num_order)[0]
    return num_order
def date_order():
    date_orderd =w.find_element(By.XPATH,'//*[@id="orderDetails"]//span[@class="order-date-invoice-item"][1]').text
    date_orderd=datetime.strptime(date_orderd, 'Pedido el %d de %B de %Y').date()
    return date_orderd
def addresess():
    try:
        address=w.find_element(By.XPATH,"//li[@class='displayAddressLI displayAddressAddressLine1']").text
        if len(re.findall(r"8414 Nw 66th St",address,flags=re.I))>0:
            address="EF"
        elif len(re.findall(r"7806 NW 46TH ST",address,flags=re.I))>0:
            address="Alexim"
        elif len(re.findall(r"2868 NW 72ND AVE",address,flags=re.I))>0:
            address="JMC"
        else:
            address="otros"
    except:
        address="Sin courier"
    return address
def targets_digits():
    try:
        target_digits=w.find_element(By.XPATH,"//span[contains(text(),'****')]").text
        target_digits=re.findall(r"\d{4}",target_digits)[0]
    except:
        target_digits="sin tarjeta"
    return target_digits
    
def scrap_order_details(cuenta,d):
    orders_details=[]
    print("PAGINA CARGADA")
    butoon_ped=wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='nav-orders']/span[2]")))
    butoon_ped.click()
    
    locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))
    #headers=w.find_elements(By.XPATH,"//div[@class='a-box a-color-offset-background order-header']//div[@class='a-fixed-right-grid-inner']")
    pages=[page.get_attribute("href") for page in w.find_elements(By.XPATH,"//li[@class='a-normal' or @class='a-selected' ]/a")]
    from_date=date.today()+timedelta(days=-int(d))
    fin=False
    if len(pages)>0:
        n=len(pages)
    else:
        n=1
    print(f"numero de paginas : {len(pages)}" )
    for i in range(n):
        #page=w.find_elements(By.XPATH,"//li[@class='a-normal' or @class='a-selected' ]/a")[i].get_attribute("href")
        if n!=1:
            w.get(pages[i])
        print(f"En la pagina {i+1}")
        espera=wait.until(EC.visibility_of_element_located((By.XPATH,"//a[contains(text(),'Ver detalles del pedido')]")))
        orders_elements=w.find_elements(By.XPATH,"//a[contains(text(),'Ver detalles del pedido')]")
        orders=[order.get_attribute("href") for order in orders_elements]
        fechas_elements=w.find_elements(By.XPATH,"//div[contains(., 'Pedido realizado')]/following-sibling::div/span")
        fechas=[fecha.text for fecha in fechas_elements]
        #pedidos=w.find_elements(By.XPATH,"//div[@class='a-text-right a-fixed-right-grid-col a-col-right']/div[@class='a-row']/a[1]")
        for j in range(len(fechas)):
            try: 
                date_orederd=datetime.strptime(fechas[j], '%B %d, %Y').date()
            except:
                date_orederd=datetime.strptime(fechas[j], '%d de %B de %Y').date()
            #if j<=5:
            if from_date<=date_orederd:
                print(f"SE EXTRAE CON FECHA {date_orederd}")
                w.get(orders[j])
                target_digits=targets_digits()
                num_order=num_orders()
                address=addresess()
                tax =taxes()
                date_orderd =date_order()
                pdf_link=pdfs_links()
                traking_id=traking_ids()
                w.get(pdf_link)
                w.execute_script('window.print();')
                awb=""
                whe=""
                date_send=""
                date_refund=""
                orders_details.append([date_orderd,num_order,pdf_link,awb,traking_id,tax,whe,target_digits,date_send,date_refund,cuenta,address])
            else:
                fin=True
                #print(f"POR TERMINAR CON FECHA {date_orederd}")
                break
        if fin:
            break
    #print(orders_details)
    return orders_details

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
        orderf=scrap_order_details(cuenta,d)
        if orderf!=[]:
            orders_total_details.extend(orderf)
        w.get("https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F-%2Fes%2Fgp%2Fcss%2Forder-history%3Fref_%3Dnav_youraccount_switchacct&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&switch_account=picker&ignoreAuthState=1&_encoding=UTF8")
    #except Exception as e:
        #print(e)
        #print(f"ERROR NO DEFINIDO EN CUENTA: {cuenta}")
w.close()
df=pd.DataFrame(orders_total_details,columns=["Fecha de compra","Factura de amazon","link de factura","awb","Traking","Monto de Taxes","whe","Terminacion de tarjeta","Fecha de envio","Fecha de devolucion","Cuenta","Courier"])
df.to_csv("order_details.csv",index=False,sep=",")