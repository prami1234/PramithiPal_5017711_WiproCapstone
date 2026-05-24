from selenium import webdriver
import time

driver = webdriver.Chrome()

driver.get("https://www.ixigo.com/buses")

driver.maximize_window()

time.sleep(5)

print("Ixigo Bus Page Opened")

driver.quit()