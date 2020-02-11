# MOC-35675 Dizz5

This is a program to use Xbox One Controller to remote control the LEGO EV3 Model **Dizz5** [MOC-35675](https://rebrickable.com/mocs/MOC-35675/hugbug/dizz5/).

The model has two motors and very large wheels.

The program consists of loop reading events from the XBox controller virtual device file and adjusting the motors. 
Use left thumb stick on the gamepad to move the model. Full left or full right spin the model. Full forward
followed by full backward (or the other way around) start spinning of the EV3 brick around wheel axis.

The right trigger reduces sensitivity of the X-axis, making steering easier - full press of the trigger
reduces steering sensitivity by 90%; lighter presses have lighter effect. Keep the trigger
pressed while using the left thumb stick.

# How to use

First you need to connect your Xbox One Controller to your EV3 brick.
The brick should be running LEGO MicroPython firmware image.

For instructions on how to connect the controller please see 
[Connecting Xbox One Controller to EV3 (EV3DEV or LEGO MicroPython)](https://github.com/hugbug/ev3/wiki/Connecting-Xbox-One-Controller-to-EV3-(EV3DEV-or-LEGO-MicroPython))

Once you have the controller connected upload the script to your EV3 brick and start it using EV3 brick file browser.

You can also use MS VS Code with LEGO MicroPython extension to upload the program to the brick.
Please refer to LEGO MicroPython documentation for details.

# How the program works

More details about the internals of the program can be found in article 
[Using Xbox One Controller with MicroPython on EV3](https://github.com/hugbug/ev3/wiki/Using-Xbox-One-Controller-with-MicroPython-on-EV3).