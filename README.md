# Permidi-Raycast-Tutorial
This is a Python implementation of the Permidi Ray-Casting Tutorial

The originals can be found here:
https://permadi.com/1996/05/ray-casting-tutorial-table-of-contents/
https://github.com/permadi-com/ray-cast/tree/master/

Notes on my implementation
To increase speed, floorResolution is set to 2. This effects both floor
and ceiling tiles, but not panoramic background. To render clearer 
floors and ceilings, set this to 1 in gameWindow.py on line 45

There are 4 toggles which control displaying the floors, ceilings, background
and shadow effects. They can be set in main.py on lines 46 through
49. If you set for ceilings, it makes sure background is off. If 
you set for background, it makes sure ceiling is off. If none of them
are set, it only shows walls

I haven't "cleaned up" the code, there is a lot of commented out code
from stuff where I was working on the python translation, or where
I was laying the groundwork for where I wanted to go with the code.
Some of it may be useful for where you want to take the code

Also, the "drawing" of the walls, floors, ceiling and background go to
a subscreen called canvasBuffer. I did this because if you draw them 
all directly to canvas (the main screen) then the walls (when up close)
break out of the 300x200 "projected plane". By putting them on the 
subscreen, it is an easy way to keep it nice and neat

I kept with the original code and put the "minimap" off to the side. 
The minimap was invaluable in debugging the code, as I could see where
rays that were cast went off where they shouldn't

I also changed part of the movement logic. This is in main.py between
lines 122 and 135. The logic of the original was when you pressed a 
key, it "moved" you, then checked to see if you could be there, and
if not, moved you back. My code takes the user input, looks to see if 
you CAN move, and only then does it move you.

Finally, I changed the refresh rate. In the original code, it redrew
the screen every cycle. I changed it so that it only redraws when you 
move. This is just a performance thing, I found it useless to constantly
redraw when you were redrawing the exact same thing.

I don't plan on making any further releases on this, it is purely a
translation of the Permidi code, and baring any bugs I haven't seen,
this is that. I did it entirely to learn about raycasting, and along 
with the other two repositories I have on GitHub (Pygame-FPS and 
simle-raycast) was my effort to learn about raycast engines

For the record, I have been working with raycasting and Python for about
2 weeks now... seriously... 2 weeks ago I knew nothing about either. 
I have, however, been programming in C/C++ and other programming languages
for about 40 years. This was all done during the great covid Pandemic of 
2020 and represents what happens when programmers get bored :)
