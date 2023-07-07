from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from utils.setWebdriver import configWebDriver
download_path=f"{os.getcwd()}/descargas_pdf"
with open("parametros.txt", mode="r") as f:
    lines=f.readlines()
dates=lines[0].strip()
w=configWebDriver()
wait = WebDriverWait(w, 3)
homeUrl="https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F-%2Fes%2Fgp%2Fcss%2Forder-history%3Fref_%3Dnav_youraccount_switchacct&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&switch_account=picker&ignoreAuthState=1&_encoding=UTF8"
w.get(homeUrl)
cuentas=[cuenta.text for cuenta in wait.until(EC.visibility_of_all_elements_located((By.XPATH,"//div[contains(text(), '.com')]")))]
print(cuentas)
orders_total_details=[]
for cuenta in cuentas:
        account=wait.until(EC.visibility_of_element_located((By.XPATH,f"//div[contains(text(),'{cuenta}')]")))
        account.click()
        print(f"leyendo cuenta :{cuenta}")
        w.get(homeUrl)
w.close()

