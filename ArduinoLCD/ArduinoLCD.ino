/*
 * LCD RS pin to digital pin 2
 * LCD Enable pin to digital pin 3
 * LCD D0 pin to digital pin 4
 * LCD D1 pin to digital pin 5
 * LCD D2 pin to digital pin 6
 * LCD D3 pin to digital pin 7
 * LCD D4 pin to digital pin 8
 * LCD D5 pin to digital pin 9
 * LCD D6 pin to digital pin 10
 * LCD D7 pin to digital pin 11
 * LCD R/W pin to ground*/

// include the library code:
#include <LiquidCrystal.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(2,3,4,5,6,7,8,9,10,11);

byte image[2][16][8] = {};

int wr = 4, clr = 0;
struct
{
  uint8_t data[6];
  uint8_t count;
  uint8_t row, col, pixels[8];
}lcd_char;

void setup() {
  Serial.begin(115200);
  lcd.begin(16, 2);
  lcd_char.count = 0;
}

void update_row(int row)
{
  byte cc = ((clr*2) & 0x07) + row; // custom character index
  
  lcd.createChar(cc, image[row][wr]);
  
  lcd.setCursor(clr, row);
  lcd.print(' ');
  lcd.setCursor(wr, row);
  lcd.write(cc);
}

void loop() {
  update_row(0);
  update_row(1);

  wr = (wr + 1) & 0x0F;
  clr = (clr + 1) & 0x0F;
  delay(1);
  
}

void serialEvent() {
  int i;
  while (Serial.available()) {
    lcd_char.data[lcd_char.count++] = Serial.read();
    
    switch(lcd_char.count)
    {
      case 1:
        lcd_char.col = lcd_char.data[0] >> 4;
        lcd_char.row = (lcd_char.data[0] >> 3) & 0x01;
        break;
      case 2:
        lcd_char.pixels[0] = ((lcd_char.data[0] & 0x07) << 2) | (lcd_char.data[1] >> 6);
        lcd_char.pixels[1] = (lcd_char.data[1] >> 1) & 0x1F;
        break;
      case 3:
        lcd_char.pixels[2] = ((lcd_char.data[1] & 0x01) << 4) | (lcd_char.data[2] >> 4);
        break;
      case 4:
        lcd_char.pixels[3] = ((lcd_char.data[2] & 0x0F) << 1) | (lcd_char.data[3] >> 7);
        lcd_char.pixels[4] = (lcd_char.data[3] >> 2) & 0x1F;
        break;
      case 5:
        lcd_char.pixels[5] = ((lcd_char.data[3] & 0x03) << 3) | (lcd_char.data[4] >> 5);
        lcd_char.pixels[6] = lcd_char.data[4] & 0x1F;
        break;
      case 6:
        lcd_char.pixels[7] = lcd_char.data[5] >> 3;
        lcd_char.count = 0;
        
        for(i = 0; i < 8; ++i)
          image[lcd_char.row][lcd_char.col][i] = lcd_char.pixels[i];
        break;
    }
  }
}



