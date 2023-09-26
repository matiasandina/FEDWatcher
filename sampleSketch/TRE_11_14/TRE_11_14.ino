/*
  Feeding experimentation device 3 (FED3)

  // 3 Timed free feeding

  This project is released under the terms of the Creative Commons - Attribution - ShareAlike 3.0 license:
  human readable: https://creativecommons.org/licenses/by-sa/3.0/
  legal wording: https://creativecommons.org/licenses/by-sa/3.0/legalcode
  Copyright (c) 2020 Lex Kravitz

*/

#include "FED3.h"                //Include the FED3 library 
String sketch = "TRE";          //Unique identifier text for each sketch
FED3 fed3 (sketch);              //Start the FED3 object

void setup() {
  fed3.begin();                                         //Setup the FED3 hardware
  fed3.DisplayPokes = false;                            //Customize the DisplayPokes option to 'false' to not display the poke indicators
  fed3.timeout = 3; //Set a timeout period (in seconds) after each pellet is taken

  fed3.timedStart = 11; // lights on 07:00, ZT4 = 11:00
  fed3.timedEnd =  14; // ZT7 = 14:00
  
  // Turn to true if you are using FEDWatcher
  fed3.setSerial(true);
  // set a 15 min timeout 
  //fed3.Timeout(15 * 60);
}

void loop() {
  ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //                                                                     Timed Feeding
  ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  fed3.sessiontype = "Timed";                         //The text in "sessiontype" will appear on the screen and in the logfile
  fed3.DisplayTimed = true;                           //Display timed feeding info
  fed3.UpdateDisplay();
  if (fed3.currentHour >= fed3.timedStart && fed3.currentHour < fed3.timedEnd) {
      fed3.Feed();
    }
  

  fed3.run();
}
