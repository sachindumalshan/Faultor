# Import library modules that need to get system information
import psutil
import platform
import os
import subprocess
import time
import logging

from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from RPLCD.i2c import CharLCD

DEVICE_ID = "RBPi0001"
interval = 1

checkmark = [0b00000,0b00001,0b00010,0b10100,0b01000,0b00000,0b0000,0b00000]
wrongmark = [0b00000,0b10001,0b01010,0b00100,0b01010,0b10001,0b0000,0b00000]

lcd = CharLCD('PCF8574',0x27)
lcd.create_char(0,checkmark)
lcd.create_char(1,wrongmark)
lcd.clear()

# Create a logger
logger = logging.getLogger('MyLoggger')
logger.setLevel(logging.DEBUG)

# Creates a TimedRotatingFileHandler
handler = TimedRotatingFileHandler(
	"my_logs.log",
	when="midnight",
	interval=1,
	backupCount=7)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

# Scale bytes to its proper format
# e.g: 1253656 => '1.20MB' ,1253656678 => '1.17GB'
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

# Boot Time
def boot_time():
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    logger.info(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}" )
    #print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

# Device Details
def device_detail():
    uname = platform.uname()
    logger.info(f"System: {uname.system}")
    logger.info(f"Device ID: {DEVICE_ID}")
    logger.info(f"Node Name: {uname.node}")
    logger.info(f"Machine: {uname.machine}")
    #print(f"System: {uname.system}")
    #print(f"Device ID: {DEVICE_ID}")
    #print(f"Node Name: {uname.node}")
    #print(f"Machine: {uname.machine}")

# Device cpu, disk, memory usage
def cdm_usage():
    # CPU information
    cpu_usage = float(psutil.cpu_percent())
    #print(f"Total CPU Usage: {psutil.cpu_percent()}%")
    if ((cpu_usage > 0) and (cpu_usage <= 50)):
        logger.info(f"CPU Usage: {cpu_usage}%")
    elif ((cpu_usage > 50) and (cpu_usage <= 85)):
        logger.warning(f"CPU Usage: {cpu_usage}%")
    else:
        logger.critical(f"CPU Usage: {cpu_usage}%")
    
    # Memory Information
    svmem = psutil.virtual_memory()
    #print(f"Total Memory Usage: {svmem.percent}%")
    if ((svmem.percent > 0) and (svmem.percent <= 60)):
        logger.info(f"Memory Usage: {svmem.percent}%")
    elif ((svmem.percent > 60) and (svmem.percent <= 85)):
        logger.warning(f"Memory Usage: {svmem.percent}%")
    else:
        logger.critical(f"Memory Usage: {svmem.percent}%")
    
    
    # Disk Information
    disk_info_root = psutil.disk_usage('/root')
    disk_info_boot = psutil.disk_usage('/boot')    
    #print(f"boot: {disk_info_boot.percent }%")
    #print(f"root: {disk_info_root.percent}%")
    
    # boot directory
    if ((disk_info_boot.percent > 0) and (disk_info_boot.percent <= 70)):
        logger.info(f"Boot disk usage: {disk_info_boot.percent}%")
    elif ((disk_info_boot.percent > 70) and (disk_info_boot.percent <= 90)):
        logger.warning(f"Boot disk usage: {disk_info_boot.percent}%")
    else:
        logger.critical(f"Boot disk usage: {disk_info_boot.percent}%")
    
    # root directory
    if ((disk_info_boot.percent > 0) and (disk_info_boot.percent <= 70)):
        logger.info(f"Root disk usage: {disk_info_boot.percent}%")
    elif ((disk_info_boot.percent > 70) and (disk_info_boot.percent <= 90)):
        logger.warning(f"Root disk usage: {disk_info_boot.percent}%")
    else:
        logger.critical(f"Root disk usage: {disk_info_boot.percent}%") 

def network_connectivity():
    # Ethernet connectivity information
    interfaces = psutil.net_if_stats()
    ethernet = interfaces.get('eth0')
    if ethernet and ethernet.isup:
        logger.info("Ethernet connected")
        #print("Ethernet connected")
    else:
        # WiFi connectivity information
        interfaces = psutil.net_if_stats()
        wifi = interfaces.get('wlan0')
        if wifi and wifi.isup:
            logger.info("WiFi connected")
            #print("Ethernet connected")
        else:
            logger.critical("Ethernet or WiFi not connected")
            #print("Ethernet or WiFi not connected")

    # Internet connectivity information
    hostname = '8.8.8.8'
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        logger.info("Internet connected")
        #print("Internet connected")
    else:
        logger.critical("Internet not connected")
        #print("Internet not connected")

# Check service file running or not
def check_service_status(service_name):
    try:
        result = subprocess.run(["systemctl","is-active",service_name],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
        )
        status = result.stdout.strip()
        if status == "active":
            logger.info(f"{service_name} is running")
            #print(f"{service_name} is running")
        else:
            logger.critical(f"{service_name} is NOT running")
            #print(f"{service_name} is NOT running")
    except Exception as e:
        logger.warning(f"Error checking status for {service_name}: {e}")
        #print(f"Error checking status for {service_name}: {e}")

# looping function
def run_continuously():
    while True:
        cdm_usage()
        network_connectivity()
        services = ["dummy_service1","dummy_service2"]
        for service in services:
            check_service_status(service)
        
        lcd.cursor_pos = (0,0)
        current_time = datetime.now()
        c_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        lcd.write_string(c_time)

        lcd.cursor_pos = (1,0)
        lcd.write_string(f"C:32% M:16% DR:13%")
        
        lcd.cursor_pos = (2,0)
        lcd.write_string(f"ETH:\x00 WiFi:\x01 INT:\x00")
        
        lcd.cursor_pos = (3,0)
        lcd.write_string(f"S1:\x00 S2:\x01 S3:\x00 S4:\x01")    

        time.sleep(interval)

# one time function
def run_once():
    boot_time()
    device_detail()
    lcd.cursor_pos = (0,4)
    lcd.write_string('Customizable')
    lcd.cursor_pos = (1,2)
    lcd.write_string('Error Indication')
    lcd.cursor_pos = (2,7)
    lcd.write_string('System')
    lcd.cursor_pos = (3,0)
    lcd.write_string('====================')
    time.sleep(5)
    lcd.clear()

def main():
    run_once()
    run_continuously()
    
main()
    
    
