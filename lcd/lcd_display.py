import time
from datetime import datetime
from RPLCD.i2c import CharLCD

checkmark = [0b00000,0b00001,0b00010,0b10100,0b01000,0b00000,0b0000,0b00000]
wrongmark = [0b00000,0b10001,0b01010,0b00100,0b01010,0b10001,0b0000,0b00000]

lcd = CharLCD('PCF8574',0x27)
lcd.create_char(0,checkmark)
lcd.create_char(1,wrongmark)
lcd.clear()

lcd.cursor_pos = (0,4)
lcd.write_string('Customizable')
lcd.cursor_pos = (1,2)
lcd.write_string('Error Indication')
lcd.cursor_pos = (2,7)
lcd.write_string('System')
lcd.cursor_pos = (3,0)
lcd.write_string('====================')
time.sleep(3)
lcd.clear()

while True:
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
    
    time.sleep(1)
    lcd.clear()

    
    

