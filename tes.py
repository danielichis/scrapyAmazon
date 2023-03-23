from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

with open("parametros.txt", mode="r") as f:
    lines=f.readlines()
profile_path=lines[1]
opt = webdriver.ChromeOptions() 
opt.add_argument(f"user-data-dir={profile_path}") #Path to your chrome profile
driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
driver.get("https://www.google.com/")
driver.get("https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F-%2Fes%2Fgp%2Fcss%2Forder-history%3Fref_%3Dnav_youraccount_switchacct&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&switch_account=picker&ignoreAuthState=1&_encoding=UTF8")
driver.get("https://www.youtube.com/")