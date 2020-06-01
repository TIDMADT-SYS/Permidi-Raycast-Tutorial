import pygame, sys
from pygame.locals import *
import math

def load_image(image, darken, colorKey = None):
    ret = []
    if colorKey is not None:
        image.set_colorkey(colorKey)
    if darken:
        image.set_alpha(127)
    for i in range(image.get_width()):
        s = pygame.Surface((1, image.get_height())).convert()
        #s.fill((0,0,0))
        s.blit(image, (- i, 0))
        if colorKey is not None:
            s.set_colorkey(colorKey)
        ret.append(s)
    return ret

class gameWindow:
    def __init__(this, width, height, title):
        this.debug = False
        this.doDrawFloor = False
        this.doDrawBackground = False
        this.doDrawCeiling = False
        this.doDrawShadow = False
        this.width = width
        this.height = height
        this.frameRate = 24 

        # Remember that PROJECTIONPLANE = screen.  This demo assumes your screen is 320 pixels wide, 200 pixels high
        this.PROJECTIONPLANEWIDTH = 320
        this.PROJECTIONPLANEHEIGHT = 200

        # create the main and buffer canvas
        this.canvas = pygame.display.set_mode((this.width, this.height),)
        this.canvasBuffer = this.canvas.subsurface(0,0,this.PROJECTIONPLANEWIDTH, this.PROJECTIONPLANEHEIGHT)
        pygame.display.set_caption(title)

        #this.offscreenCanvas = pygame.surfarray.pixels2d()

        # size of tile (wall height)
        this.TILE_SIZE = 64
        this.WALL_HEIGHT = 64
        this.floorResolution = 2  # set to 1 for clearer floors, less performance

        # We use FOV of 60 degrees.  So we use this FOV basis of the table, taking into account
        # that we need to cast 320 rays (PROJECTIONPLANEWIDTH) within that 60 degree FOV.
        this.ANGLE60 = this.PROJECTIONPLANEWIDTH
        # You must make sure these values are integers because we're using loopup tables.
        this.ANGLE30 = math.floor(this.ANGLE60/2)
        this.ANGLE15 = math.floor(this.ANGLE30/2)
        this.ANGLE90 = math.floor(this.ANGLE30*3)
        this.ANGLE180 = math.floor(this.ANGLE90*2)
        this.ANGLE270 = math.floor(this.ANGLE90*3)
        this.ANGLE360 = math.floor(this.ANGLE60*6)
        this.ANGLE0 = 0
        this.ANGLE5 = math.floor(this.ANGLE30/6)
        this.ANGLE3 = math.floor(this.ANGLE30/10)
        this.ANGLE10 = math.floor(this.ANGLE5*2)
        this.ANGLE45 = math.floor(this.ANGLE15*3)

        # trigonometric tables (the ones with "I" such as ISiTable are "Inverse" table)
        this.fSinTable=[]
        this.fISinTable=[]
        this.fCosTable=[]
        this.fICosTable=[]
        this.fTanTable=[]
        this.fITanTable=[]
        this.fFishTable=[]
        this.fXStepTable=[]
        this.fYStepTable=[]

        # player's attributes
        this.fPlayerX = None
        this.fPlayerY = None
        this.fPlayerArc = None
        this.fPlayerDistanceToTheProjectionPlane = 277
        this.fPlayerHeight = this.WALL_HEIGHT//2
        this.fPlayerSpeed = this.TILE_SIZE//4
        this.fPlayerTurnSpeed = 20

        # the following variables are used to keep the player coordinate in the overhead map
        this.fPlayerMapX = None
        this.fPlayerMapY = None

        # Half of the screen height
        this.fProjectionPlaneYCenter = this.PROJECTIONPLANEHEIGHT/2

        # minimap vars
        this.fMinimapWidth = None

        this.animationFrameID = None

        this.fWallTextureCanvas = None
        this.fWallTexturePixels = None
        this.fBackgroundImageArc=0
	
        this.baseLightValue=180
        this.baseLightValueDelta=1
        this.fWallTextureBuffer = pygame.image.load("pics/walls/wood_wall.png").convert()
        this.fFloorTextureBuffer = pygame.image.load("pics/walls/colorstone.png").convert()
        this.fCeilingTextureBuffer = pygame.image.load("pics/walls/wood.png").convert()
        this.fBackgroundTextureBuffer = pygame.image.load("pics/bgr.png").convert()
        
        # map variables
        this.fMap=None
        this.MAP_WIDTH = 0
        this.MAP_HEIGHT = 0
        
        # scale of the minimap - in pixels
        this.fMinimapWidth=5

        # initialize cast tables
        this.init_tables()

    # toggle if show background
    def toggleBackground(this):
        this.doDrawBackground = not this.doDrawBackground
        #if doDrawBackground, make sure doDrawCeiling is off
        if this.doDrawBackground:
            this.doDrawCeiling = not this.doDrawBackground
            
    def toggleCeiling(this):
        this.doDrawCeiling = not this.doDrawCeiling
        #if doDrawCeiling, make sure doDrawBackground is off
        if this.doDrawCeiling:
            this.doDrawBackground = not this.doDrawCeiling

    # toggle if show background
    def toggleShadow(this):
        this.doDrawShadow = not this.doDrawShadow

    def drawBackground(this):
        if (this.doDrawBackground):
            # panoramic view, no ceiling
#            background_col = math.floor(this.fPlayerArc *  0.01667)
##context.drawImage(img, sx, sy, swidth, sheight, x, y, width, height)
##subsurface(Rect) -> Surface
            back_column = this.fBackgroundTextureBuffer.subsurface(0, 0, this.PROJECTIONPLANEWIDTH-this.fBackgroundImageArc, this.PROJECTIONPLANEHEIGHT)
            #print("trying to get pixel at " , background_col , " " , ceil_row)
            #top_column=this.fBackgroundTextureBuffer.subsurface(background_col,ceil_row,PROJECTIONPLANEWIDTH,PROJECTIONPLANEWIDTH)
            this.canvasBuffer.blit(back_column,(this.fBackgroundImageArc,0))
                                                                   
            
    # toggle if show floor
    def toggleFloor(this):
        this.doDrawFloor = not this.doDrawFloor

    # check to see if the space ahead of the player is blocked
    def isBlocked(this):
        #first, figure out what the grid space in front of player is
        check_x = math.floor(this.fPlayerX/this.TILE_SIZE)
        check_y = math.floor(this.fPlayerY/this.TILE_SIZE)

        if this.fPlayerArc == this.ANGLE0:
            check_x+=1
        elif this.fPlayerArc == this.ANGLE90:
            check_y+=1
        elif this.fPlayerArc == this.ANGLE180:
            check_x-=1
        else:
            check_y-=1
        
        # Return true if the map block is not 0,
        # i.e. if there is a blocking wall.
        return (this.fMap[check_y][check_x] != 0);
        
    def loadMapSegment(this, inMap):
        this.fMap=inMap
        this.MAP_WIDTH = len(this.fMap[0])
        this.MAP_HEIGHT = len(this.fMap)
        print("MAP_WIDTH " , this.MAP_WIDTH)
        print("MAP_HEIGHT " , this.MAP_HEIGHT)

    def drawOverheadMap(this):
        GREY=(245, 245, 245)
        BLUE=(153, 217, 234)
        RED =(233,150,122)
        BLACK=pygame.color.THECOLORS["black"]

        for r in range(0, this.MAP_HEIGHT):
            for c in range(0, this.MAP_WIDTH):
                if this.fMap[r][c] != 0:
                    pygame.draw.rect(this.canvas, GREY, (this.PROJECTIONPLANEWIDTH + (c * this.fMinimapWidth), r * this.fMinimapWidth, this.fMinimapWidth, this.fMinimapWidth), 0)
                else:
                    pygame.draw.rect(this.canvas, BLACK, (this.PROJECTIONPLANEWIDTH + (c * this.fMinimapWidth), r * this.fMinimapWidth, this.fMinimapWidth, this.fMinimapWidth), 0)

    def placePlayer(this, x: int, y: int, angle: int):
        this.fPlayerX = x
        this.fPlayerY = y
        this.fPlayerArc = angle
        print(type(this.fMinimapWidth))
        this.fPlayerMapX=this.PROJECTIONPLANEWIDTH+((this.fPlayerX/this.TILE_SIZE) * this.fMinimapWidth);
        this.fPlayerMapY=((this.fPlayerY/this.TILE_SIZE) * this.fMinimapWidth);
        print("player placed on map at (" , this.fPlayerX, ", " , this.fPlayerY, ") angle " , this.fPlayerArc)        
        print("minimap position (" , this.fPlayerMapX, ", " , this.fPlayerMapY, ")")        

    def movePlayer(this):
        #print("in move")
        if this.fPlayerArc == this.ANGLE0:
            x_move = this.fPlayerSpeed
            y_move = 0
        elif this.fPlayerArc == this.ANGLE90:
            x_move = 0
            y_move = this.fPlayerSpeed
        elif this.fPlayerArc == this.ANGLE180:
            x_move = -this.fPlayerSpeed
            y_move = 0
        elif this.fPlayerArc == this.ANGLE270:
            x_move = 0
            y_move = -this.fPlayerSpeed
        else:
            print("unknown move direction (" , this.fPlayerArc , ")")
            pygame.quit()
            sys.exit()

        this.fPlayerX+=x_move
        this.fPlayerY+=y_move
        this.fPlayerX = round(this.fPlayerX, 2);
        this.fPlayerY = round(this.fPlayerY, 2);
        this.fPlayerMapX=this.PROJECTIONPLANEWIDTH+((this.fPlayerX/this.TILE_SIZE) * this.fMinimapWidth);
        this.fPlayerMapY=((this.fPlayerY/this.TILE_SIZE) * this.fMinimapWidth);

    def init_tables(this):
        radian = None
        this.fSinTable = [None] * int(this.ANGLE360+1)
        this.fISinTable = [None] * int(this.ANGLE360+1)
        this.fCosTable = [None] * int(this.ANGLE360+1)
        this.fICosTable = [None] *int(this.ANGLE360+1)
        this.fTanTable = [None] *int(this.ANGLE360+1)
        this.fITanTable = [None] *int(this.ANGLE360+1)
        this.fFishTable = [None] *int(this.ANGLE360+1)
        this.fXStepTable = [None] *int(this.ANGLE360+1)
        this.fYStepTable = [None] *int(this.ANGLE360+1)

        i = 0
        while (i <= this.ANGLE360):
            # Populate tables with their radian values.
            # (The addition of 0.0001 is a kludge to avoid divisions by 0. Removing it will produce unwanted holes in the wall when a ray is at 0, 90, 180, or 270 degree angles)
            radian = this.arcToRad(i) + (0.0001);
            this.fSinTable[i]=math.sin(radian);
            this.fISinTable[i]=(1.0/(this.fSinTable[i]));
            this.fCosTable[i]=math.cos(radian);
            this.fICosTable[i]=(1.0/(this.fCosTable[i]));
            this.fTanTable[i]=math.tan(radian);
            this.fITanTable[i]=(1.0/this.fTanTable[i]);

            # Next we crate a table to speed up wall lookups.
            # 
            #  You can see that the distance between walls are the same
            #  if we know the angle
            #  _____|_/next xi______________
            #       |
            #  ____/|next xi_________   slope = tan = height / dist between xi's
            #     / |
            #  __/__|_________  dist between xi = height/tan where height=tile size
            # old xi|
            #                  distance between xi = x_step[view_angle];
            # Facing LEFT
            if i>=this.ANGLE90 and i<this.ANGLE270:
                this.fXStepTable[i] = (this.TILE_SIZE/this.fTanTable[i]);
                if (this.fXStepTable[i]>0):
                    this.fXStepTable[i]=-this.fXStepTable[i];
            # facing RIGHT
            else:
                this.fXStepTable[i] = (this.TILE_SIZE/this.fTanTable[i]);
                if (this.fXStepTable[i]<0):
                    this.fXStepTable[i]=-this.fXStepTable[i];

            # FACING DOWN
            if (i>=this.ANGLE0 and i<this.ANGLE180):
                this.fYStepTable[i] = (this.TILE_SIZE*this.fTanTable[i])
                if (this.fYStepTable[i]<0):
                        this.fYStepTable[i]=-this.fYStepTable[i]
            else:
                this.fYStepTable[i] = (this.TILE_SIZE*this.fTanTable[i]);
                if (this.fYStepTable[i]>0):
                    this.fYStepTable[i]=-this.fYStepTable[i];
        
            i += 1
            # end of for loop
            
        # Create table for fixing FISHBOWL distortion
        i = -this.ANGLE30
        while i <= this.ANGLE30:
            radian = this.arcToRad(i);
            # we don't have negative angle, so make it start at 0
            # this will give range from column 0 to 319 (PROJECTONPLANEWIDTH) since we only will need to use those range
            this.fFishTable[i+this.ANGLE30] = (1.0/math.cos(radian));
            i += 1
        
        print("tables init")

    def arcToRad(this, arcAngle):
        return (arcAngle*math.pi)/this.ANGLE180

    def newDrawWallSliceRectangleTinted(this, castColumn, topOfWall, bottomOfWall, xOffset, darkenVal):
        if int(bottomOfWall-topOfWall)+1<0:
            return
        column=this.fWallTextureBuffer.subsurface(xOffset,0,1,this.TILE_SIZE)
        height = int(bottomOfWall-topOfWall)+1
        column = pygame.transform.scale(column, (1, height))

        if this.doDrawShadow:
            black_img = pygame.Surface(column.get_rect().size)
            darkness = int(255 * darkenVal)
            black_img.fill([darkness] * 3)
            column.blit(black_img, (0, 0),
                            special_flags=pygame.BLEND_RGB_MULT)

        this.canvasBuffer.blit(column,(castColumn,topOfWall))

        
    def clearScreen(this):
        this.canvas.fill((0,0,0))
        this.canvasBuffer.fill((0,0,0))

    def raycast(this):
        verticalGrid = None # horizotal or vertical coordinate of intersection
        horizontalGrid = None # theoritically, this will be multiple of TILE_SIZE
                                                         # , but some trick did here might cause
                                                         # the values off by 1
        distToNextVerticalGrid = None # how far to the next bound (this is multiple of
        distToNextHorizontalGrid = None # tile size)
        xIntersection = None  # x and y intersections
        yIntersection = None
        distToNextXIntersection = None
        distToNextYIntersection = None

        xGridIndex = None        # the current cell that the ray is in
        yGridIndex = None

        distToVerticalGridBeingHit = None      # the distance of the x and y ray intersections from
        distToHorizontalGridBeingHit = None      # the viewpoint

        castArc = None
        castColumn = None

        castArc = this.fPlayerArc
        # field of view is 60 degree with the point of view (player's direction in the middle)
        # 30  30
        #    ^
        #  \ | /
        #   \|/
        #    v
        # we will trace the rays starting from the leftmost ray
        castArc-=this.ANGLE30
        # wrap around if necessary
        if (castArc < 0):
            castArc+=this.ANGLE360
        
        for castColumn in range(0, this.PROJECTIONPLANEWIDTH):
            if this.debug:
                print("casting castArc " , castArc , " castColumn " , castColumn)
            # Ray is facing down
            if castArc > this.ANGLE0 and castArc < this.ANGLE180:
                # truncuate then add to get the coordinate of the FIRST grid (horizontal
                # wall) that is in front of the player (this is in pixel unit)
                # ROUNDED DOWN
                horizontalGrid = math.floor(this.fPlayerY/this.TILE_SIZE)*this.TILE_SIZE  + this.TILE_SIZE;

                # compute distance to the next horizontal wall
                distToNextHorizontalGrid = this.TILE_SIZE;

                xtemp = this.fITanTable[castArc]*(horizontalGrid-this.fPlayerY);
                # we can get the vertical distance to that wall by
                # (horizontalGrid-playerY)
                # we can get the horizontal distance to that wall by
                # 1/tan(arc)*verticalDistance
                # find the x interception to that wall
                xIntersection = xtemp + this.fPlayerX;
                if this.debug:
                    print("down ray - castArc=" , castArc , " in CHECKPOINT A, horizontalGrid=" , horizontalGrid , " distToNextHorizontalGrid=" , distToNextHorizontalGrid , " xtemp=" , xtemp , " xIntersection=" , xIntersection)
            # Else, the ray is facing up
            else:
                horizontalGrid = math.floor(this.fPlayerY/this.TILE_SIZE)*this.TILE_SIZE
                distToNextHorizontalGrid = -this.TILE_SIZE;

                xtemp = this.fITanTable[castArc]*(horizontalGrid - this.fPlayerY);
                xIntersection = xtemp + this.fPlayerX;

                horizontalGrid-=1
                if this.debug:
                    print("up ray - castArc=" , castArc , " in CHECKPOINT A, horizontalGrid=" , horizontalGrid , " distToNextHorizontalGrid=" , distToNextHorizontalGrid , " xtemp=" , xtemp , " xIntersection=" , xIntersection)

            # LOOK FOR HORIZONTAL WALL

            # If ray is directly facing right or left, then ignore it 
            if castArc==this.ANGLE0 or castArc==this.ANGLE180:
                distToHorizontalGridBeingHit=sys.maxsize;
            # else, move the ray until it hits a horizontal wall
            else:
                distToNextXIntersection = this.fXStepTable[castArc]
                while (True):
                    xGridIndex = math.floor(xIntersection/this.TILE_SIZE)
                    yGridIndex = math.floor(horizontalGrid/this.TILE_SIZE)
                    mapIndex=math.floor(yGridIndex*this.MAP_WIDTH+xGridIndex)
                    if this.debug:
                        print("this.fPlayerY="+this.fPlayerY+" this.fPlayerX="+this.fPlayerX+" castColumn="+castColumn+" castArc="+castArc+" xIntersection="+xIntersection+" horizontalGrid="+horizontalGrid+" xGridIndex="+xGridIndex+" yGridIndex="+yGridIndex+" mapIndex="+mapIndex)
                        print("this.fITanTable="+this.fITanTable[castArc])

                    # If we've looked as far as outside the map range, then bail out
                    if xGridIndex>=this.MAP_WIDTH or yGridIndex>=this.MAP_HEIGHT or xGridIndex<0 or yGridIndex<0:
                        distToHorizontalGridBeingHit = sys.maxsize
                        break
                    # If the grid is not an Opening, then stop
                    elif this.fMap[yGridIndex][xGridIndex] > 0:
                        distToHorizontalGridBeingHit  = (xIntersection-this.fPlayerX)*this.fICosTable[castArc]
                        break
                    # Else, keep looking.  At this point, the ray is not blocked, extend the ray to the next grid
                    else:
                        xIntersection += distToNextXIntersection
                        horizontalGrid += distToNextHorizontalGrid

            # FOLLOW X RAY
            if castArc < this.ANGLE90 or castArc > this.ANGLE270:
                verticalGrid = this.TILE_SIZE + math.floor(this.fPlayerX/this.TILE_SIZE)*this.TILE_SIZE
                distToNextVerticalGrid = this.TILE_SIZE

                ytemp = this.fTanTable[castArc]*(verticalGrid - this.fPlayerX)
                yIntersection = ytemp + this.fPlayerY
                if this.debug:
                    print("castArc=" , castArc , " in CHECKPOINT C, horizontalGrid=" , horizontalGrid , " distToNextHorizontalGrid=" , distToNextHorizontalGrid , " ytemp=" , ytemp , " yIntersection=" , yIntersection)				
            # RAY FACING LEFT
            else:
                verticalGrid = math.floor(this.fPlayerX/this.TILE_SIZE)*this.TILE_SIZE
                distToNextVerticalGrid = -this.TILE_SIZE

                ytemp = this.fTanTable[castArc]*(verticalGrid - this.fPlayerX)
                yIntersection = ytemp + this.fPlayerY

                verticalGrid-=1
                if this.debug:
                    print("castArc=" , castArc , " in CHECKPOINT D, horizontalGrid=" , horizontalGrid , " distToNextHorizontalGrid=" , distToNextHorizontalGrid , " ytemp=" , ytemp , " yIntersection=" , yIntersection)					

            # LOOK FOR VERTICAL WALL
            if castArc==this.ANGLE90 or castArc==this.ANGLE270:
                distToVerticalGridBeingHit = sys.maxsize
            else:
                distToNextYIntersection = this.fYStepTable[castArc]
                while (True):
                    # compute current map position to inspect
                    xGridIndex = math.floor(verticalGrid/this.TILE_SIZE)
                    yGridIndex = math.floor(yIntersection/this.TILE_SIZE)

                    mapIndex=math.floor(yGridIndex*this.MAP_WIDTH+xGridIndex)

                    if this.debug:
                        print("this.fPlayerY=" , this.fPlayerY , " this.fPlayerX=" , this.fPlayerX , " castColumn=" , castColumn , " castArc=" , castArc , " xIntersection=" , xIntersection , " horizontalGrid=" , horizontalGrid , " xGridIndex=" , xGridIndex , " yGridIndex=" , yGridIndex , " mapIndex=" , mapIndex)
                        print("this.fITanTable=" , this.fITanTable[castArc])

                    if xGridIndex>=this.MAP_WIDTH or yGridIndex>=this.MAP_HEIGHT or xGridIndex<0 or yGridIndex<0:
                        distToVerticalGridBeingHit = sys.maxsize
                        break
                    elif this.fMap[yGridIndex][xGridIndex] > 0:
                        distToVerticalGridBeingHit =(yIntersection-this.fPlayerY)*this.fISinTable[castArc]
                        break
                    else:
                        yIntersection += distToNextYIntersection
                        verticalGrid += distToNextVerticalGrid

            # DRAW THE WALL SLICE
            scaleFactor = None
            dist = None
            xOffset = None
            topOfWall = None    # used to compute the top and bottom of the sliver that
            bottomOfWall = None # will be the staring point of floor and ceiling
                                # determine which ray strikes a closer wall.
                                # if yray distance to the wall is closer, the yDistance will be shorter than
                                # the xDistance
            isVerticalHit=False
            distortedDistance=0
            bottomOfWall = None
            topOfWall = None
            if (distToHorizontalGridBeingHit < distToVerticalGridBeingHit):
                # the next function call (drawRayOnMap()) is not a part of raycating rendering part, 
                # it just draws the ray on the overhead map to illustrate the raycasting process
                this.drawRayOnOverheadMap(xIntersection, horizontalGrid);
                dist=distToHorizontalGridBeingHit/this.fFishTable[castColumn];

                distortedDistance=dist
                if dist <= 0:
                    dist = .1
                ratio = this.fPlayerDistanceToTheProjectionPlane/dist
                bottomOfWall = (ratio * this.fPlayerHeight + this.fProjectionPlaneYCenter)
                scale = (this.fPlayerDistanceToTheProjectionPlane*this.WALL_HEIGHT/dist)	
                topOfWall = bottomOfWall - scale

                xOffset=xIntersection%this.TILE_SIZE
                if this.debug:			
                    print("castColumn=" , castColumn , " using distToHorizontalGridBeingHit");
            # else, we use xray instead (meaning the vertical wall is closer than
            #   the horizontal wall)
            else:
                isVerticalHit=True;
                # the next function call (drawRayOnMap()) is not a part of raycating rendering part, 
                # it just draws the ray on the overhead map to illustrate the raycasting process
                this.drawRayOnOverheadMap(verticalGrid, yIntersection);
                dist=distToVerticalGridBeingHit/this.fFishTable[castColumn];

                xOffset=yIntersection%this.TILE_SIZE

                if dist <= 0:
                    dist = .1
                ratio = this.fPlayerDistanceToTheProjectionPlane/dist
                bottomOfWall = (ratio * this.fPlayerHeight + this.fProjectionPlaneYCenter)
                scale = (this.fPlayerDistanceToTheProjectionPlane*this.WALL_HEIGHT/dist)	
                topOfWall = bottomOfWall - scale
                                
                if this.debug:				
                    print("castColumn=" , castColumn , " using distToVerticalGridBeingHit");

            if this.debug:
                print("castColumn=" , castColumn , " distance=" , dist);

            # Add simple shading so that farther wall slices appear darker.
            # use arbitrary value of the farthest distance.  
            dist=math.floor(dist)
            if (dist <= 0):
                dist = .1

            # Trick to give different shades between vertical and horizontal (you could also use different textures for each if you wish to)
            if (isVerticalHit):
                darkenVal = this.baseLightValue/(dist)
            else:
                darkenVal = (this.baseLightValue-80)/(dist)

            if darkenVal > 1:
                darkenVal = 1
            this.newDrawWallSliceRectangleTinted(castColumn, topOfWall, bottomOfWall, xOffset, darkenVal)

            projectionPlaneCenterY=this.fProjectionPlaneYCenter
            lastBottomOfWall = math.floor(bottomOfWall)
            lastTopOfWall = math.floor(topOfWall)

            if this.doDrawFloor:
                #*************
                # FLOOR CASTING at the simplest!  Try to find ways to optimize this, you can do it!
                #*************
                if (this.fFloorTextureBuffer!=None):
                    # find the first bit so we can just add the width to get the
                    # next row (of the same column)
                    #targetIndex=lastBottomOfWall*(this.offscreenCanvasPixels.width*bytesPerPixel)+(bytesPerPixel*castColumn)
                    for row in range(lastBottomOfWall,this.PROJECTIONPLANEHEIGHT, this.floorResolution):
                        straightDistance=(this.fPlayerHeight)/(row-projectionPlaneCenterY)*this.fPlayerDistanceToTheProjectionPlane
                        
                        actualDistance=straightDistance*(this.fFishTable[castColumn])

                        yEnd = math.floor(actualDistance * this.fSinTable[castArc])
                        xEnd = math.floor(actualDistance * this.fCosTable[castArc])

                        # Translate relative to viewer coordinates:
                        xEnd+=this.fPlayerX
                        yEnd+=this.fPlayerY

                        
                        # Get the tile intersected by ray:
                        cellX = math.floor(xEnd / this.TILE_SIZE)
                        cellY = math.floor(yEnd / this.TILE_SIZE)
                        #console.log("cellX="+cellX+" cellY="+cellY);

                        
                        #Make sure the tile is within our map
                        if ((cellX<this.MAP_WIDTH) and (cellY<this.MAP_HEIGHT) and cellX>=0 and cellY>=0):
#                        if (1 == 1):
                            # Find offset of tile and column in texture
                            tileRow = math.floor(yEnd % this.TILE_SIZE);
                            tileColumn = math.floor(xEnd % this.TILE_SIZE);
                            ceil_row = this.PROJECTIONPLANEHEIGHT - row
##                            this.canvas.blit(this.fFloorTextureBuffer,(castColumn,lastBottomOfWall),(tileColumn,tileRow,this.floorResolution,this.floorResolution))

                            column=this.fFloorTextureBuffer.subsurface(tileColumn,tileRow,1,1)
                            this.canvasBuffer.blit(column,(castColumn,row))
                            if this.doDrawCeiling:
                                top_column=this.fCeilingTextureBuffer.subsurface(tileColumn,tileRow,1,1)
                                this.canvasBuffer.blit(top_column,(castColumn,ceil_row))
##                                this.canvas.blit(this.fCeilingTextureBuffer,(castColumn,lastTopOfWall),(tileColumn,ceil_row,this.floorResolution,this.floorResolution))
##                            elif this.doDrawBackground:
##                                # panoramic view, no ceiling
##                                ceil_row = this.PROJECTIONPLANEHEIGHT - row
##                                background_col = this.fPlayerArc + castColumn
##                                #print("trying to get pixel at " , background_col , " " , ceil_row)
##                                top_column=this.fBackgroundTextureBuffer.subsurface(background_col,ceil_row,1,1)
##                                this.canvas.blit(this.fFloorTextureBuffer,(castColumn,row),(background_col,ceil_row,this.floorResolution,this.floorResolution))

                            # blit the top, be it ceiling or background
                            #this.canvas.blit(top_column,(castColumn,ceil_row))

                        lastBottomOfWall += this.floorResolution
                        lastTopOfWall -= this.floorResolution
            
            # TRACE THE NEXT RAY
            castArc+=1
            if (castArc>=this.ANGLE360):
                    castArc-=this.ANGLE360
                    
    #*******************************************************************#
    #* Draw ray on the overhead map (for illustartion purpose)
    #* This is not part of the ray-casting process
    #*******************************************************************#
    def drawRayOnOverheadMap(this, x, y):
        #console.log("drawRayOnOverheadMap x="+y+" y="+y);
        # draw line from the player position to the position where the ray
        # intersect with wall
        BLUE=(153, 217, 234)

        start_pos = [this.fPlayerMapX, this.fPlayerMapY]
        end_pos = [this.PROJECTIONPLANEWIDTH+((x*this.fMinimapWidth)/this.TILE_SIZE), (y*this.fMinimapWidth)/this.TILE_SIZE]
        pygame.draw.line(this.canvas, BLUE, start_pos, end_pos, 1)    

