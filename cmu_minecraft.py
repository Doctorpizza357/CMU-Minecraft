import math
import time

# Lists used to store rendered shapes each frame
app.drawnShapes = []
app.allFaces = []

# Dictionary of placed blocks: keys = (x,y,z), values = block type string
app.blocks = {}
app.blockSize = 1

# Movement paremeters
app.moveSpeed = 0.2
app.verticalSpeed = 0.2
app.keysHeld = set()

# Grabity system and parameters (disabled in fly mode)
app.gravity = -0.05
app.jumpVelocity = 0.4
app.airDrag = 0.98
app.terminalVelocity = -0.92
app.yVelocity = 0
app.onGround = False
app.groundY = 0.5
app.flyMode = False
app.fallDistance = 0

# UI labels
app.modeLabel = Label("SURVIVAL MODE", 70,20, size = 14, bold = True, fill = 'black', visible = False)
app.coordLabel = Label("", 300,20,size = 14, bold = True, fill = 'black', visible = False)

# Hotbar setup
app.hotbarSize = 8
app.hotbar = [None] * app.hotbarSize
app.hotbarCounts = {}
app.selectedSlot = 0


# Health
app.maxHealth = 20
app.health = 20
app.maxHunger = 20
app.hunger = 20

# Inventory setup (3 rows * 8 columns)
app.inventoryCols = 8
app.inventoryRows = 3
app.inventorySize = app.inventoryCols * app.inventoryRows
app.inventory = [None] * app.inventorySize
app.inventoryCounts = {}

# Inventory UI state
app.inventoryOpen = False
app.inventoryGroup = None
app.inventorySlots = []
app.inventorySelectedIndex = None

app.chatMessages = []
app.chatCompactLines = 6
app.chatMaxLines = 6
app.chatGroup = None
app.chatBackground = None
app.chatExpanded = False
app.chatLabels = []

# Preload inventory items
app.inventory[0] = 'stone'
app.inventory[1] = 'dirt'
app.inventory[2] = 'grass'
app.inventory[3] = 'pickaxe'

app.inventoryCounts[0] = 5
app.inventoryCounts[1] = 37
app.inventoryCounts[2] = 62

# Item currently being dragged by the mouse
app.heldItem = None
app.heldItemIndex = None
app.heldItemCount = 1
app.heldPreview = None

app.useFaceCulling = True
app.useFaceCache = True
app.useCollisions = True
app.useSmoothLighting = False
app.useWireframe = False

app.playerWidth = 0.4
app.playerHeight = 1.8
app.playerEyeHeight = 1.5

app.FOV = 70
app.mouseSensitivity = 0.5
app.renderDistance = 8

# FPS Counter
app.fpsFrames = 0
app.fpsTime = time.time()
app.fpsLabel = Label("FPS: 0",app.width - 45, 40,size = 14,bold = True,fill = 'black',visible = False)

# Render distance for blocks
app.renderDistance = 16

# Place a test block
app.blocks[(0,1,0)] = 'stone'
#app.blocks[(1,1,0)] = 'stone'
#app.blocks[(-1,1,0)] = 'stone'
#app.blocks[(0,2,0)] = 'stone'
#app.blocks[(0,3,0)] = 'grass'


# Preview block placement position
app.previewPos = None

# Game state flags
app.gameStarted = False
app.pausing = False
app.f3Visible = True
app.isDead = False

# Cache for block faces (used to avoid recomputing projection)
# This is essentially a manual version of "geometry batching"
app.blockFaceCache = {}
app.cameraChanged = True

def isSolid(x,y,z):
    return (x,y,z) in app.blocks

def collidesAt(px,py,pz):
    w = app.playerWidth
    h = app.playerHeight
    
    feetY = py - app.playerEyeHeight
    headY = feetY + h
    playerMinX = px - w
    playerMaxX = px + w
    playerMinY = feetY
    playerMaxY = headY
    playerMinZ = pz - w
    playerMaxZ = pz + w
    
    if playerMinY < 0.5:
        return True
        
    minX = math.floor(playerMinX + 0.5)
    maxX = math.floor(playerMaxX + 0.5)
    minY = math.floor(playerMinY + 0.5)
    maxY = math.floor(playerMaxY + 0.5)
    minZ = math.floor(playerMinZ + 0.5)
    maxZ = math.floor(playerMaxZ + 0.5)
    
    for x in range(minX, maxX + 1):
        for y in range(minY, maxY + 1):
            for z in range(minZ,maxZ + 1):
                if not isSolid(x,y,z):
                    continue
                blockMinX = x - 0.5
                blockMaxX = x + 0.5
                blockMinY = y - 0.5
                blockMaxY = y + 0.5
                blockMinZ = z - 0.5
                blockMaxZ = z + 0.5
                
                overlapX = (playerMinX < blockMaxX) and (playerMaxX > blockMinX)
                overlapY = (playerMinY < blockMaxY) and (playerMaxY > blockMinY)
                overlapZ = (playerMinZ < blockMaxZ) and (playerMaxZ > blockMinZ)
                
                if overlapX and overlapY and overlapZ:
                    return True
    return False

def blockOverlapsPlayer(bx,by,bz):
    w = app.playerWidth
    h = app.playerHeight
    
    feetY = app.y - app.playerEyeHeight
    playerMinX = app.x - w
    playerMaxX = app.x + w
    playerMinY = feetY
    playerMaxY = feetY + h
    playerMinZ = app.z - w
    playerMaxZ = app.z + w
    
    blockMinX = bx - 0.5
    blockMaxX = bx + 0.5
    blockMinY = by - 0.5
    blockMaxY = by + 0.5
    blockMinZ = bz - 0.5
    blockMaxZ = bz + 0.5
    
    overlapX = (playerMinX < blockMaxX) and (playerMaxX > blockMinX)
    overlapY = (playerMinY < blockMaxY) and (playerMaxY > blockMinY)
    overlapZ = (playerMinZ < blockMaxZ) and (playerMaxZ > blockMinZ)
    
    return overlapX and overlapY and overlapZ


# ----------------------------------------------------
# createPauseMenu()
# ----------------------------------------------------
# PURPOSE:
# * Builds the pause menu UI overlay, includiing background dimming and buttons
# 
# FUNCTIONALITY:
# * Creates a Group() to hold all pause menu elements
# * Adds a semi-transparent dark background
# * Adds a Pause and Settings buttons
# * Adds buttons with attributes (isResume, isSettings) for click detection
#
# NOTES:
# * This function only constructs the UI; visibility is controlled elsewhere
# ----------------------------------------------------
def createPauseMenu():
    # Creates a semi-tranmsparent pause overlay with buttons
    app.pauseMenu = Group()
    app.pauseMenu.visible = False
    
    bg = Rect(0,0,app.width,app.height,fill = 'black',opacity = 60)
    title = Label("PAUSED", app.width / 2,app.height / 2 - 60,size = 36,bold = True,fill = 'white')
    
    # Resume button
    resumeBtn = Rect(app.width / 2 - 80,app.height / 2,160,50,fill = 'white',border = 'black',borderWidth = 3)
    resumeText = Label("RESUME",resumeBtn.centerX,resumeBtn.centerY,size = 22,bold = True)
    
    # Settings button
    settingsBtn = Rect(app.width / 2 - 80,app.height / 2 + 60,160,50,fill = 'white',border = 'black',borderWidth = 3)
    settingsText = Label("SETTINGS",settingsBtn.centerX,settingsBtn.centerY,size = 22,bold = True)
    
    # Tag buttons for click detection
    resumeBtn.isResume = True
    settingsBtn.isSettings = True
    
    app.pauseMenu.add(bg,title,resumeBtn,resumeText,settingsBtn,settingsText)

def createSettingsMenu():
    app.settingsMenu = Group()
    app.settingsMenu.visible = False
    app.settingToggles = {}
    app.settingSliders = {}
    app.activeSettingSlider = None
    
    bg = Rect(0,0,app.width,app.height,fill='black',opacity=75)
    panel = Rect(app.width / 2- 175, 10, 350,380,fill='dimGray',border='white',borderWidth = 2)
    title = Label("SETTINGS",app.width/2,36,size=30,bold=True,fill='white')
    app.settingsMenu.add(bg,panel,title)
    
    def makeToggle(labelText,y,attrName):
        lbl = Label(labelText,panel.left + 20,y,size=16,fill='white',align='left')
        stateLabel = Label("",panel.left + 245,y,size=12,bold=True,fill='white')
        box = Rect(panel.right - 70, y-12,44,24,fill='lightGray',border='black',borderWidth = 2)
        box.isToggle = True
        box.toggleName = attrName
        box.state = getattr(app,attrName)
        
        
        knobColor = 'lawnGreen' if box.state else 'red'
        knob = Rect(box.left + (box.width - 20 if box.state else 0),y-12,20,24,fill=knobColor)
        knob.toggleKnob = True
        knob.parentToggle = box
        box.toggleKnob  = knob
        box.stateLabel = stateLabel
        app.settingToggles[attrName] = box
        
        app.settingsMenu.add(lbl,stateLabel,box,knob)
    
    def makeSlider(labelText, y, attrName, minVal, maxVal):
        lbl = Label(labelText,panel.left + 20,y,size=16,fill='white',align='left')
        valueLabel = Label("",panel.right - 27,y,size=13,bold = True,fill='yellow')
        bar = Rect(panel.left + 160,y-4,145,8,fill='white')
        bar.isSlider = True
        bar.sliderName = attrName
        bar.minVal = minVal
        bar.maxVal = maxVal
        bar.valueLabel = valueLabel
        
        cur = getattr(app,attrName)
        t = (cur - minVal) / (maxVal - minVal)
        knob = Circle(bar.left + t * bar.width, y,5,fill = 'yellow')
        knob.sliderKnob = True
        knob.parentSlider = bar
        bar.sliderKnob = knob
        app.settingSliders[attrName] = bar
        
        app.settingsMenu.add(lbl,valueLabel,bar,knob)
    
    
    makeToggle("Face Culling", 95, "useFaceCulling")
    makeToggle("Block Cache", 130, "useFaceCache")
    makeToggle("Collisions", 165, "useCollisions")
    makeToggle("Smooth Lighting", 200, "useSmoothLighting")
    makeToggle("Wireframe Mode", 235, "useWireframe")
    
    makeSlider("FOV", 285, "FOV", 30,110)
    makeSlider("Sensitivity", 320, "mouseSensitivity", 0.1,2.0)
    makeSlider("Render Distance", 355, "renderDistance",4,32)
    
    backBtn = Rect(title.centerX-50, title.bottom + 8,100,25,fill = 'white',border = 'black',borderWidth = 3)
    backBtn.isBack = True
    backText = Label("BACK",backBtn.centerX, backBtn.centerY,size = 18,bold = True)
    
    app.settingsMenu.add(backBtn,backText)
    syncSettingsUI()
    
# ----------------------------------------------------
# createStartMenu()
# ----------------------------------------------------
# PURPOSE:
# * Builds the game's start menu UI, including background image and start button
# 
# FUNCTIONALIITY:
# * Loads a background image 
# * Creates an invisible button overlay for starting the game
# * Groups all elements into app.startMenu
#
# NOTES:
# * The start button is invisible (opacity = 0) but clickable
# ----------------------------------------------------
def createStartMenu():
    app.startMenu = Group()
    
    # Image created using ChatGPT image generator
    bg = Image('cmu://444716/44961807/CMU+Minecraft+Start+Screen.png',0,0)
    bg.width = 400
    bg.height = 400
    startBtn = Rect(133, 304, 130,50,fill = 'white',opacity = 0)
    startBtn.isButton = True
    app.startMenu.add(bg,startBtn)

# ----------------------------------------------------
# createHeldPreview(mouseX,mousey)
# ----------------------------------------------------
# PURPOSE:
# * Creates a visible preview of the item currently being dragged by the mouse
#
# FUNCTIONALITY:
# * Removes any existing preview
# * If holding a pickaxe, draws a red X
# * If holding a block, draws a colered square
# * Adds the preview to the inventory UI layer
#
# NOTES:
# * This is purely a UI representation; it does not affect inventory logic
# ----------------------------------------------------
def createHeldPreview(mouseX, mouseY):
    destroyHeldPreview()
    
    item = app.heldItem
    if item is None:
        return
    
    if item == 'pickaxe':
        pickaxeImage = Image("cmu://444716/45237456/310-3109338_minecraft-pickaxe-diamond-fte-remixit-ftestickers-minecraft-diamond-removebg-preview.png",mouseX+4,mouseY+6,width=30,height=30)
        #l1 = Line(mouseX - 12, mouseY - 12, mouseX + 12, mouseY + 12, fill = 'red',lineWidth = 3)
        #l2 = Line(mouseX - 12,mouseY + 12,mouseX + 12,mouseY - 12,fill = 'red',lineWidth = 3)
        app.heldPreview = Group(pickaxeImage)
    else:
        app.heldPreview = Rect(mouseX - 12, mouseY - 12, 24, 24, fill = getBlockColor(item), border = 'black')
        
    app.heldPreview.centerX = mouseX
    app.heldPreview.centerY = mouseY
        
    app.inventoryGroup.add(app.heldPreview)
    app.heldPreview.toFront()
    
# ----------------------------------------------------
# destroyHeldPreview()
# ----------------------------------------------------
# PURPOSE:
# * Removes the current held-item preview from the screen
# 
# FUNCTIONALITY:
# * Hides and clears the preview objects
#
# NOTES:
# * Called whenever the held item changes or is dropped
# ----------------------------------------------------
def destroyHeldPreview():
    if app.heldPreview is not None:
        app.heldPreview.visible = False
        app.heldPreview = None

# ----------------------------------------------------
# handleHotbarClick(mouseX,mouseY,button)
# ----------------------------------------------------
# PURPOSE:
# * Handles clicking on hotbar slots, enabling drag-and-drop item movement
#
# FUNCTIONALITY:
# * If no item iis held, clicking a slot picks up its item
# * If an item is held, clicking a slot swaps the held item with the slot
# * Updates hotbar visibales and creates preview graphics
#
# NOTES:
# * This mirrors Minecraft style hotbar swapping behavior
# ----------------------------------------------------
def handleHotbarClick(mouseX, mouseY, button):
    for slot in app.hotbarSlots:
        if slot.hits(mouseX, mouseY):
            idx = slot.hotbarIndex
            item = app.hotbar[idx]

            if app.heldItem is None and item is not None:
                app.heldItem = item
                app.heldItemIndex = idx
                app.heldItemCount = app.hotbarCounts.get(idx,1)
                app.hotbar[idx] = None
                if idx in app.hotbarCounts:
                    del app.hotbarCounts[idx]
                updateHotbarContents()
                createHeldPreview(mouseX, mouseY)
                return
            
            if app.heldItem is not None:
                oldItem = app.hotbar[idx]
                oldCount = app.hotbarCounts.get(idx,1) if oldItem is not None else 1
                heldCount = app.heldItemCount if hasattr(app,'heldItemCount') else 1
                app.hotbar[idx], app.heldItem = app.heldItem, app.hotbar[idx]
                
                if app.hotbar[idx] is not None:
                    app.hotbarCounts[idx] = heldCount
                else:
                    if idx in app.hotbarCounts:
                        del app.hotbarCounts[idx]
                
                app.heldItemCount = oldCount if app.heldItem is not None else 1
                app.heldItemIndex = None
                destroyHeldPreview()
                updateHotbarContents()
                
                createHeldPreview(mouseX, mouseY)
                return
# ----------------------------------------------------
# createHotbar()
# ----------------------------------------------------
# PURPOSE:
# * Constructs the hotbar UI at the bottom of the screen
#
# FUNCTIONALITY:
# * Creates a Group() to hold all hotbar slot rectangles
# * Computes layout so the hotbar is centered horizontally
# * Creates 8 slots (or app.hotbarSize slots) with borders
# * Stores slot references in app.hotbarSlots for click detection
#
# NOTES:
# * The hotbar only displays items; logic for selecting or swapping items
# is handled elsewhere (handleHotbarClick, upadteHotbarContents)
# ----------------------------------------------------
def createHotbar():
    app.hotbarGroup = Group()
    app.hotbarSlots = []
    
    slotSize = 40
    spacing = 8
    
    totalWidth = app.hotbarSize * slotSize + (app.hotbarSize - 1) * spacing
    startX = app.width / 2 - totalWidth / 2
    y = app.height - 60
    
    for i in range(app.hotbarSize):
        x = startX + i * (slotSize + spacing)
        
        slot = Rect(x,y,slotSize,slotSize, fill = 'lightGray', border = 'white', borderWidth = 2)
        slot.hotbarIndex = i
        countLabel = Label("",x+slotSize-8,y+slotSize-6,size=10,bold=True,fill='black',align='right')
        countLabel.hotbarSlot = i
        slot.countLabel = countLabel
        app.hotbarSlots.append(slot)
        app.hotbarGroup.add(slot,countLabel)
        
def createStatusUI():
    app.statusGroup = Group()
    app.healthIcons = []
    app.hungerIcons = []
    
    iconSize = 14
    spacing = 4
    count = 10
    y = app.height - 85
    
    totalWidth = count * (iconSize + spacing) - spacing
    
    leftStartX = app.width / 2 - totalWidth - 10
    rightStartX = app.width / 2 + 10
    
    for i in range(count):
        hx = leftStartX + i * (iconSize + spacing)
        healthBg = Rect(hx,y,iconSize,iconSize,fill='maroon',border='black',borderWidth=1)
        healthFill = Rect(hx + 2,y + 2,iconSize - 4,iconSize - 4,fill='red')
        app.healthIcons.append((healthBg,healthFill))
        app.statusGroup.add(healthBg,healthFill)
        
        fx = rightStartX + i * (iconSize + spacing)
        hungerBg = Rect(fx,y,iconSize,iconSize,fill='saddleBrown',border='black',borderWidth = 1)
        hungerFill = Rect(fx + 2, y + 2,iconSize - 4,iconSize - 4,fill='gold')
        app.hungerIcons.append((hungerBg,hungerFill))
        app.statusGroup.add(hungerBg,hungerFill)
        
    app.statusGroup.visible = False

def updateStatusUI():
    filledHealth = max(0,min(10,math.ceil(app.health / 2)))
    filledHunger = max(0,min(10,math.ceil(app.hunger / 2)))
    canShow = app.gameStarted
    
    for i,(_,fill) in enumerate(app.healthIcons):
        fill.visible = canShow and (i < filledHealth)
    
    for i,(_,fill) in enumerate(app.hungerIcons):
        fill.visible = canShow and (i < filledHunger)
        
def setStatusUIVisible(visible):
    app.statusGroup.visible = visible
    for shape in app.statusGroup.children:
        shape.visible = visible
    if visible:
        updateStatusUI()
        
def formatSettingValue(settingName,value):
    if settingName in ('FOV','renderDistance'):
        return str(int(rounded(value)))
    if settingName == 'mouseSensitivity':
        return f"{value:.2f}"
    return str(value)
    
def applySliderValue(slider,mouseX):
    t = max(0,min(1,(mouseX - slider.left) / slider.width))
    value = slider.minVal + t * (slider.maxVal - slider.minVal)
    
    if slider.sliderName in ('FOV','renderDistance'):
        value = int(rounded(value))
    elif slider.sliderName == 'mouseSensitivity':
        value = rounded(value * 100) / 100
        
    setattr(app,slider.sliderName,value)
    syncSettingsUI()
    
    if slider.sliderName in ('FOV','renderDistance'):
        app.cameraChanged = True
        app.blockFaceCache.clear()
        
def syncSettingsUI():
    if not hasattr(app,'settingToggles') or not hasattr(app,'settingSliders'):
        return
    
    for toggle in app.settingToggles.values():
        state = bool(getattr(app,toggle.toggleName))
        toggle.state = state
        toggle.fill = 'white' if state else 'lightGray'
        
        knob = toggle.toggleKnob
        knob.left = toggle.left + (toggle.width - knob.width if state else 0)
        knob.fill = 'lawnGreen' if state else 'red'
        toggle.stateLabel.value = 'ON' if state else 'OFF'
    
    for slider in app.settingSliders.values():
        cur = getattr(app,slider.sliderName)
        t = 0 if slider.maxVal == slider.minVal else (cur - slider.minVal) / (slider.maxVal - slider.minVal)
        t = max(0,min(1,t))
        slider.sliderKnob.centerX = slider.left + t * slider.width
        slider.valueLabel.value = formatSettingValue(slider.sliderName,cur)
    
def handleSettingsClick(mouseX,mouseY):
    app.settingsMenu.toFront()
    app.activeSettingSlider = None
    
    for shape in app.settingsMenu.children:
        if hasattr(shape,"isBack") and shape.hits(mouseX,mouseY):
            app.settingsMenu.visible = False
            app.pauseMenu.visible = True
            return
        
    for toggle in app.settingToggles.values():
        if toggle.hits(mouseX,mouseY) or toggle.toggleKnob.hits(mouseX,mouseY):
            newState = not getattr(app,toggle.toggleName)
            setattr(app,toggle.toggleName,newState)
            syncSettingsUI()
            
            if toggle.toggleName in ('useFaceCache','useFaceCulling','useSmoothLighting','useWireframe'):
                app.blockFaceCache.clear()
                app.cameraChanged = True
            return
        
    for slider in app.settingSliders.values():
        if slider.hits(mouseX,mouseY) or slider.sliderKnob.hits(mouseX,mouseY):
            app.activeSettingSlider = slider
            applySliderValue(slider,mouseX)
            return

def handleSettingsDrag(mouseX,mousey):
    if app.activeSettingSlider is not None:
        applySliderValue(app.activeSettingSlider,mouseX)

# ----------------------------------------------------
# createInventoryUI()
# ----------------------------------------------------
# PURPOSE:
# * Builds the full inventory UI window (background, title, slots)
#
# FUNCTIONALITY:
# * Creates a semi-transparent background panel
# * Ads a title label
# * Creates a grid of inventory slots (3 rows * 8 columns)
# * Stores slot references in app.inventorySlots for click detection
# * Initially hides the inventory (visible =  False)
#
# NOTES:
# * This function only builds the UI; item rendering is handled by
# updateInventoryContents()
# ----------------------------------------------------
def createInventoryUI():
    app.inventoryGroup = Group()
    app.inventorySlots = []
    
    slotSize = 40
    spacing = 6
    
    totalWidth = app.inventoryCols * slotSize + (app.inventoryCols - 1) * spacing
    totalHeight = app.inventoryRows * slotSize + (app.inventoryRows - 1) * spacing
    
    startX = app.width / 2 - totalWidth / 2
    startY = app.height / 2 - totalHeight / 2
    
    padX = 20
    padY = 40
    
    bg = Rect(startX - padX, startY - padY, totalWidth + padX * 2, totalHeight + padY * 2, fill = 'black',opacity = 60, border = 'white', borderWidth = 2)
    app.inventoryGroup.add(bg)
    
    title = Label("Inventory", bg.centerX, bg.top + 20, size = 18, bold = True, fill='white')
    app.inventoryGroup.add(title)
    
    for row in range(app.inventoryRows):
        for col in range(app.inventoryCols):
            x = startX + col * (slotSize + spacing)
            y = startY + row * (slotSize + spacing)
            
            slot = Rect(x,y,slotSize,slotSize,fill = 'gray', border = 'white',borderWidth = 2)
            slot.invIndex = row * app.inventoryCols + col
            
            countLabel = Label("",x+slotSize-8,y+slotSize-6,size=10,bold=True,fill='black',align='right')
            countLabel.invSlot = row * app.inventoryCols + col
            slot.countLabel = countLabel
            
            app.inventorySlots.append(slot)
            app.inventoryGroup.add(slot,countLabel)
            
    app.inventoryGroup.visible = False

def createChatUI():
    app.chatGroup = Group()
    app.chatLabels = []
    
    lineHeight = 16
    pad = 8
    boxWidth = 280
    
    x = app.modeLabel.left
    y = 40
    app.chatTextX = x
    
    availableHeight = app.height - y - 12
    maxLines = int((availableHeight - pad * 2) / lineHeight)
    boxHeight = app.chatMaxLines * lineHeight + pad * 2
    
    for i in range(app.chatMaxLines):
        lbl = Label("", x,y + i * lineHeight,size=12,fill='white',align='left')
        app.chatLabels.append(lbl)
        app.chatGroup.add(lbl)
        
    app.chatGroup.visible = False
    
def refreshChatUI():
    if app.chatGroup is None:
        return
    
    
    lineCount = app.chatMaxLines if app.chatExpanded else app.chatCompactLines
    recent = app.chatMessages[-lineCount:]
    
    for i,label in enumerate(app.chatLabels):
        label.left = app.chatTextX
        if i < len(recent):
            msg = recent[i].lstrip()
            label.value = msg
            label.fill = 'black'
            label.visible = True
        else:
            label.value = ""
            label.visible = False

def addChatMessage(text):
    app.chatMessages.append(text)
    if len(app.chatMessages) > 100:
        app.chatMessages = app.chatMessages[-100:]
    refreshChatUI()

def runChatCommand(rawCommand):
    parts = rawCommand.strip().split()
    if len(parts) == 0:
        return

    cmd = parts[0].lower()
    args = parts[1:]
    
    if cmd in ('tp','teleport'):
        if len(args) != 3:
            addChatMessage("Usage: /tp x y z")
            return
        try:
            x = float(args[0])
            y = float(args[1])
            z = float(args[2])
        except ValueError:
            addChatMessage("Teleport failed: coords must be numbers")
            return
        
        app.x = x
        app.y = y
        app.z = z
        app.cameraChanged = True
        addChatMessage(f"Teleported to {x:.2f} {y:.2f} {z:.2f}")
        return
    
    if cmd == 'help':
        addChatMessage("Commands: /tp x y z")
        return
        
    addChatMessage("Unknown command. Try /help")
    
def openChatInput():
    if not app.gameStarted or app.pausing:
        return
    
    app.chatExpanded = True
    refreshChatUI()
    redrawAll()
    text = app.getTextInput("Chat (use /help for commands)")
    app.chatExpanded = False
    refreshChatUI()
    if text is None:
        return
    text = text.strip()
    if text == "":
        return
    if text.startswith('/'):
        runChatCommand(text[1:])
    else:
        addChatMessage(f"<Player> {text}")

# ----------------------------------------------------
# getBlockColor(blockType)
# ----------------------------------------------------
# PURPOSE:
# * Maps a block type string to a display color
#
# FUNCTIONALITY:
# * Returns a color name based on block type
# * Defaults to white if block type is unknown
#
# NOTES:
# * Used for both hotbar previews and 3D block rendering
# ----------------------------------------------------
def getBlockColor(blockType):
    colors = {
        'stone': 'gray',
        'dirt': 'sienna',
        'grass': 'green'
    }
    return colors.get(blockType, 'white')
    
# ----------------------------------------------------
# updateHotbarHighlight()
# ----------------------------------------------------
# PURPOSE:
# * Visually highlights the currently selected hotbar slot
#
# FUNCTIONALITY:
# * Sets the selected slot borders to yellow and thicker
# * Resets all other slot borders to normal white
#
# NOTES:
# * Called whenever the user pressed number keys 1-8
# ----------------------------------------------------
def updateHotbarHighlight():
    for i in range(app.hotbarSize):
        if i == app.selectedSlot:
            app.hotbarSlots[i].border = 'yellow'
            app.hotbarSlots[i].borderWidth = 4
        else:
            app.hotbarSlots[i].border = 'white'
            app.hotbarSlots[i].borderWidth = 2

# ----------------------------------------------------
# updateHotbarContents()
# ----------------------------------------------------
# PURPOSE:
# * Updates the visual previews inside each hotbar slot
#
# FUNCTIONALITY:
# * Removes old preview
# * Draws a red X for pickaxes
# * Draws a colored square for blocks
# * Addds previews to the hotbar group so they under above the slots
#
# NOTES:
# * Called after swapping items or modifying hotbar contents
# ----------------------------------------------------
def updateHotbarContents():
    for i in range(app.hotbarSize):
        slot = app.hotbarSlots[i]
        
        if hasattr(slot, 'preview') and slot.preview is not None:
            slot.preview.visible = False
            slot.preview = None
        
        item = app.hotbar[i]
        
        if item is not None and i in app.hotbarCounts:
            count = int(app.hotbarCounts[i])
            if count > 1:
                slot.countLabel.value = f'x{count}'
            else:
                slot.countLabel.value = ''
        else:
            slot.countLabel.value = ''
        
        if item == 'pickaxe':
            pickaxeImage = Image("cmu://444716/45237456/310-3109338_minecraft-pickaxe-diamond-fte-remixit-ftestickers-minecraft-diamond-removebg-preview.png",slot.left+4,slot.top+6,width=30,height=30)
            #l1 = Line(slot.left + 8,slot.top + 8,slot.right - 8,slot.bottom - 8, fill = 'red',lineWidth = 3)
            #l2 = Line(slot.left + 8,slot.bottom - 8,slot.right - 8,slot.top + 8,fill = 'red',lineWidth = 3)
            slot.preview = Group(pickaxeImage)
            app.hotbarGroup.add(slot.preview)
        elif item is not None:
            preview = Rect(slot.centerX - 12, slot.centerY - 12, 24, 24, fill = getBlockColor(item), border = 'black')
        
            slot.preview = preview
            app.hotbarGroup.add(preview)
        
createHotbar()
createStatusUI()
updateHotbarHighlight()
createInventoryUI()
createStartMenu()
createPauseMenu()
createSettingsMenu()
createChatUI()

app.hotbar[0] = 'pickaxe'
app.hotbar[1] = 'stone'
app.hotbarCounts[1] = 64
updateHotbarContents()
updateStatusUI()
setStatusUIVisible(False)

# ----------------------------------------------------
# showInventory()
# ----------------------------------------------------
# PURPOSE:
# * Makes the inventory UI visible and ensures it renders above the other UI
#
# FUNCTIONALITY:
# * Shows the inventory group
# * Updates item previews
# * Brings inventory, hotbar, and labels to the front
#
# NOTES:
# * Called when the user presses 'E'
# ----------------------------------------------------
def showInventory():
    app.inventoryGroup.visible = True
    updateInventoryContents()
    app.inventoryGroup.toFront()
    app.statusGroup.toFront()
    app.hotbarGroup.toFront()
    app.coordLabel.toFront()
    app.modeLabel.toFront()
    
# ----------------------------------------------------
# hideInventory()
# ----------------------------------------------------
# PURPOSE:
# * hides the inventory UI and clears selection state
#
# FUNCTIONALITY:
# * Sets inventoryGroup.visible = False
# * Clears any selected inventory index
#
# NOTES:
# * Called when closing inventory (pressing 'E' with inventory open)
# ----------------------------------------------------
def hideInventory():
    app.inventoryGroup.visible = False
    app.inventorySelectedIndex = None

# ----------------------------------------------------
# updateInventoryContents()
# ----------------------------------------------------
# PURPOSE:
# * Updates the visual previews inside each inventory slot
#
# FUNCTIONALITY:
# * Removes old previews
# * Draws red X for pickaxes
# * Draws colored squares for blocks
# * Adds previews to the inventory group
#
# NOTES:
# * Called whenever inventory contents change or inventory is opened
# ----------------------------------------------------
def updateInventoryContents():
    for slot in app.inventorySlots:
        if hasattr(slot, 'preview') and slot.preview is not None:
            slot.preview.visible = False
            slot.preview = None
        
    for slot in app.inventorySlots:
        idx = slot.invIndex
        item = app.inventory[idx]
        
        if item is not None and idx in app.inventoryCounts:
            count = int(app.inventoryCounts[idx])
            if count > 1:
                slot.countLabel.value = f'x{count}'
            else:
                slot.countLabel.value = ''
        else:
            slot.countLabel.value = ''
            
        if item is None:
            continue
            
        if item == 'pickaxe':
            pickaxeImage = Image("cmu://444716/45237456/310-3109338_minecraft-pickaxe-diamond-fte-remixit-ftestickers-minecraft-diamond-removebg-preview.png",slot.left+4,slot.top+6,width=30,height=30)
            #l1 = Line(slot.left + 8,slot.top + 8,slot.right - 8,slot.bottom - 8, fill = 'red',lineWidth = 3)
            #l2 = Line(slot.left + 8,slot.bottom - 8,slot.right - 8,slot.top + 8,fill = 'red',lineWidth = 3)
            slot.preview = Group(pickaxeImage)
            app.inventoryGroup.add(slot.preview)
        else:
            preview = Rect(slot.centerX - 12, slot.centerY - 12, 24, 24, fill = getBlockColor(item), border = 'black')
            slot.preview = preview
            app.inventoryGroup.add(preview)
                

# ----------------------------------------------------
# snapToGrid(value, size =1)
# ----------------------------------------------------
# PURPOSE:
# * Snaps a floating-point value to the nearest grid coordinate
#
# FUNCTIONALITY:
# * Divides the value by grid size
# * Rounds to nearest integer
# * Multiplies back by grid size
#
# NOTES:
# * Useful for aligning block plcement to a voxel grid
# ----------------------------------------------------
def snapToGrid(value, size=1):
    return rounded(value / size) * size

# ----------------------------------------------------
# getViewRay()
# ----------------------------------------------------
# PURPOSE:
# * Computes the forward-facing direction vector of the camera based on 
# * horiztonal (yaw) and vertical (pitch) angles
#
# FUNCTIONALITY:
# * Converts yaw/pitch from degrees to radians
# * Uses spherical-to-cartesian conversion:
#   * dx = sin(yaw) * cos(pitch)
#   * dy = -sin(pitch)
#   * dz = cos(yaw) * cos(pitch)
#
# REFERENCES:
# * EULER Angles: https://en.wikipedia.org/wiki/Euler_angles
# * Spherical Coordinates: https://en.wikipedia.org/wiki/Spherical_coordinate_system
#
# NOTES:
# * Returned vector is normalized
# ----------------------------------------------------
def getViewRay():
    yaw = -math.radians(app.horizontalViewAngle)
    pitch = math.radians(app.verticalViewAngle)
    
    dx = math.sin(yaw) * math.cos(pitch)
    dy = -math.sin(pitch)
    dz = math.cos(yaw) * math.cos(pitch)
    
    return dx, dy, dz

# ----------------------------------------------------
# getTargetedBlock(maxDist = 6, step = 0.1)
# ----------------------------------------------------
# PURPOSE:
# * Performs a forward raycast to findd the first block the player is looking at
#
# FUNCTIONALITY:
# * Steps forward along the view ray in small increments
# * Converts each stepped position to voxel coordinates
# * Returns the first block encountered
#
# REFERENCES:
# * Ray Casting: https://en.wikipedia.org/wiki/Ray_casting
# * Voxel Traversal: https://en.wikipedia.org/wiki/Voxel#Ray_tracing
#
# NOTES:
# * This is a simple ray-march, not a DDA algorithm, but works well for short 
# distances and low block density
# ----------------------------------------------------
def getTargetedBlock(maxDist = 6, step = 0.1):
    dx, dy, dz = getViewRay()
    x = app.x
    y = app.y
    z = app.z
    dist = 0
    
    while dist < maxDist:
        x += dx * step
        y += dy * step
        z += dz * step
        dist += step
        
        gx = math.floor(x + 0.5)
        gy = math.floor(y + 0.5)
        gz = math.floor(z + 0.5)
        
        cell = (gx,gy,gz)
        if cell in app.blocks:
            return(gx,gy,gz,app.blocks[cell])
        
    return None

# ----------------------------------------------------
# getPlacementPosition(maxDist = 6, step = 0.1)
# ----------------------------------------------------
# PURPOSE:
# * Determines where a new block should be placedd when the player is looking
# at an existing block
#
# FUNCTIONALITY:
# * Ray-marches forward
# * Tracks the last empty cell before hitting a block or the floor plane
# * Returns that empty cell as the placement position
#
# NOTES:
# * This mimics Minecraft's block placement logic
# ----------------------------------------------------
def getPlacementPosition(maxDist = 6, step = 0.1):
    dx, dy, dz = getViewRay()
    x = app.x
    y = app.y 
    z = app.z
    dist = 0
    lastEmpty = None

    
    while dist < maxDist:
        x += dx * step
        y += dy * step
        z += dz * step
        dist += step
        
        gx = math.floor(x + 0.5)
        gy = math.floor(y + 0.5)
        gz = math.floor(z + 0.5)
        
        cell = (gx, gy, gz)
        
        
        if cell in app.blocks:
            return lastEmpty
        lastEmpty = cell
        
    floorY = 0.5
    if abs(dy) > 1e-6:
        t = (floorY - app.y) / dy
        if 0 < t < maxDist:
            fx = app.x + dx * t
            fz = app.z + dz * t
            gx = rounded(fx)
            gz = rounded(fz)
            return (gx,1,gz)

    return None

def onKeyPress(key):
    
    if key == 't':
        openChatInput()
        return
    
    app.keysHeld.add(key)
    
    if key == 'l' and app.gameStarted:
        app.f3Visible = not app.f3Visible

    if key == 'escape' and app.gameStarted:
        if app.settingsMenu.visible:
            app.settingsMenu.visible = False
            app.pauseMenu.visible = True
            app.activeSettingSlider = None
        else:
            app.pausing = not app.pausing
            app.pauseMenu.visible = app.pausing
    
    if key.isdigit():
        index = int(key) - 1
        if 0 <= index < app.hotbarSize:
            app.selectedSlot = index
            updateHotbarHighlight()
    
    if key == 'f':
        app.flyMode = not app.flyMode
        if app.flyMode:
            app.modeLabel.value = "CREATIVE MODE"
        else:
            app.modeLabel.value = 'SURVIVAL MODE'
        app.yVelocity = 0
        app.fallDistance = 0
    
    if key == 'space' and (not app.flyMode) and app.onGround:
        app.yVelocity = app.jumpVelocity
        app.onGround = False
        
    if key == 'e':
        app.inventoryOpen = not app.inventoryOpen
        if app.inventoryOpen:
            showInventory()
        else:
            hideInventory()

def onKeyRelease(key):
    if key in app.keysHeld:
        app.keysHeld.remove(key)

app.background = gradient('white','lightBlue',start = 'top')

app.verticalViewAngle = 0
app.horizontalViewAngle = 0

app.oldX = 0
app.oldY = 0

app.pivotX, app.pivotY, app.pivotZ = 0.5,0.75,0.5

app.x = 0.5
app.y = 2
app.z = -4

def drawFlatFloor():
    floorY = 0.5
    gridSize = 1
    renderDist = 8
    
    cx = int(app.x)
    cz = int(app.z)
    
    for gx in range(cx - renderDist, cx + renderDist):
        for gz in range(cz - renderDist, cz + renderDist):
            
            visualX = gx - 0.5
            visualZ = gz - 0.5
        
            corners = [
                (visualX,floorY,visualZ),
                (visualX + gridSize,floorY,visualZ),
                (visualX + gridSize,floorY,visualZ + gridSize),
                (visualX,floorY,visualZ + gridSize)
            ]
            
            face2D = []
            allInFront = True
            
            for p in corners:
                proj = convertTo2D(p)
                
                if proj is None:
                    allInFront = False
                    break
                face2D.append(proj)
            
            if allInFront:
                color = 'lightGreen' if (gx + gz) % 2 == 0 else 'forestGreen'
                
                depth = avgCameraZ(corners)
                app.allFaces.append((depth + 50,face2D,color,None))

def handleInventoryClick(mouseX, mouseY, button):
    for slot in app.hotbarSlots:
        if slot.hits(mouseX, mouseY):
            handleHotbarClick(mouseX, mouseY, button)
            return
        
    for slot in app.inventorySlots:
        if slot.hits(mouseX, mouseY):
            idx = slot.invIndex
            item = app.inventory[idx]

            if app.heldItem is None and item is not None:
                app.heldItem = item
                app.heldItemIndex = idx
                app.heldItemCount = app.inventoryCounts.get(idx,1)
                if idx in app.inventoryCounts:
                    del app.inventoryCounts[idx]
                app.inventory[idx] = None
                updateInventoryContents()
                createHeldPreview(mouseX, mouseY)
                return
            
            if app.heldItem is not None:
                oldItem = app.inventory[idx]
                oldCount = app.inventoryCounts.get(idx,1) if oldItem is not None else 1
                heldCount = app.heldItemCount if hasattr(app,'heldItemCount') else 1
                app.inventory[idx], app.heldItem = app.heldItem, app.inventory[idx]
                if app.inventory[idx] is not None:
                    app.inventoryCounts[idx] = heldCount
                else:
                    if idx in app.inventoryCounts:
                        del app.inventoryCounts[idx]
                
                app.heldItemCount = oldCount if app.heldItem is not None else 1
                app.heldItemIndex = idx if app.heldItem is not None else 1
                destroyHeldPreview()
                updateInventoryContents()
                createHeldPreview(mouseX, mouseY)
                return
    if app.heldItem is not None:
        app.inventory[app.heldItemIndex] = app.heldItem
        app.inventoryCounts[app.heldItemIndex] = app.heldItemCount if hasattr(app,'heldItemCount') else 1
        app.heldItem = None
        app.heldItemIndex = None
        app.heldItemCount = 1
        destroyHeldPreview()
        updateInventoryContents()
        
    handleInventoryDrag(mouseX,mouseY)

def handleInventoryDrag(mouseX, mouseY):
    if app.heldPreview is not None:
        app.heldPreview.centerX = mouseX
        app.heldPreview.centerY = mouseY
        app.heldPreview.toFront()

def onMouseMove(mouseX, mouseY):
    if app.pausing and app.settingsMenu.visible and app.activeSettingSlider is not None:
        handleSettingsDrag(mouseX,mouseY)
        return
    
    if not app.gameStarted or app.pausing:
        return
    
    if app.inventoryOpen:
        handleInventoryDrag(mouseX, mouseY)
        return

def onMousePress(mouseX, mouseY, button):
    if app.pausing and app.settingsMenu.visible:
        handleSettingsClick(mouseX, mouseY)
        return
    if not app.gameStarted:
        for shape in app.startMenu.children:
            if hasattr(shape,'isButton') and shape.hits(mouseX, mouseY):
                app.gameStarted = True
                app.startMenu.visible = False
                setStatusUIVisible(True)
        return
    
    if app.pausing:
        for shape in app.pauseMenu.children:
            if hasattr(shape, 'isResume') and shape.hits(mouseX, mouseY):
                app.pausing = False
                app.pauseMenu.visible = False
            if hasattr(shape,'isSettings') and shape.hits(mouseX,mouseY):
                app.pauseMenu.visible = False
                app.settingsMenu.visible = True
                app.activeSettingSlider = None
                syncSettingsUI()
                app.settingsMenu.toFront()
                return
        return
    
    if app.inventoryOpen:
        handleInventoryClick(mouseX, mouseY, button)
        return
    app.oldX, app.oldY = mouseX, mouseY
    
    if button == 2:
        item = app.hotbar[app.selectedSlot]
        if item is None:
            return
        
        if item == 'pickaxe':
            target = getTargetedBlock()
            if target:
                x,y,z,_ = target
                if (x,y,z) in app.blocks:
                    brokenBlock = app.blocks[(x,y,z)]
                    del app.blocks[(x,y,z)]
                    app.blockFaceCache.clear()
                    
                    for i in range(app.hotbarSize):
                        if app.hotbar[i] == brokenBlock:
                            app.hotbarCounts[i] = app.hotbarCounts.get(i,1) + 1
                            updateHotbarContents()
                            return
                    
                    for i in range(app.inventorySize):
                        if app.inventory[i] == brokenBlock:
                            app.inventoryCounts[i] = app.inventoryCounts.get(i,1) + 1
                            updateInventoryContents()
                            updateHotbarContents()
                            return
                    
                    for i in range(app.inventorySize):
                        if app.inventory[i] is None:
                            app.inventory[i] = brokenBlock
                            app.inventoryCounts[i] = 1
                            updateInventoryContents()
                            updateHotbarContents()
                            return
                    
        elif item in ('stone','grass','dirt'):
            pos = getPlacementPosition()
            if pos:
                gx,gy,gz = pos
                if (gx,gy,gz) not in app.blocks and not blockOverlapsPlayer(gx,gy,gz):
                    app.blocks[(gx,gy,gz)] = item
                    app.blockFaceCache.clear()
                    
                    slotIdx = app.selectedSlot
                    if slotIdx in app.hotbarCounts:
                        app.hotbarCounts[slotIdx] -= 1
                        if app.hotbarCounts[slotIdx] <= 0:
                            app.hotbar[slotIdx] = None
                            del app.hotbarCounts[slotIdx]
                        updateHotbarContents()

def onMouseDrag(mouseX, mouseY):
    if app.pausing and app.settingsMenu.visible:
        handleSettingsDrag(mouseX,mouseY)
        return
    
    app.cameraChanged = True

    if not app.gameStarted or app.pausing:
        return
    if app.inventoryOpen:
            handleInventoryDrag(mouseX, mouseY)
            return
    xChange = mouseX - app.oldX
    yChange = mouseY - app.oldY
    
    # app.mouseSensitivity = 0.5
    app.horizontalViewAngle -= xChange * app.mouseSensitivity
    app.verticalViewAngle = max(-89, min(89,app.verticalViewAngle + yChange * app.mouseSensitivity))
    app.oldX, app.oldY = mouseX, mouseY

def onMouseRelease(mouseX,mouseY):
    app.activeSettingSlider = None
    
# ----------------------------------------------------
# isFaceExposed(bx,by,bz,normal)
# ----------------------------------------------------
# PURPOSE:
# * Determines whether a block face is exposed to air (i.e., not touching another block).
# this is the first step in face culling
#
# FUNCTIONALITY:
# * Computes the neighbor cell in the direction of the face normal.
# * If that neighbor cell does NOT contain a block, the face is exposed
#
# NOTES:
# * This is equivalent to Minecraft's "occlusion culling" for adjecent voxels
# ----------------------------------------------------
def isFaceExposed(bx,by,bz,normal):
    nx = bx + normal[0]
    ny = by + normal[1]
    nz = bz + normal[2]
    
    return (nx,ny,nz) not in app.blocks
    
# ----------------------------------------------------
# isFaceVisible(bx,by,bz,normal)
# ----------------------------------------------------
# PURPOSE:
# * Performs a back-face culling test: determines whether a face is oriented toward the camera
#
# FUNCTIONALITY:
# * Computes vector from block center to camera
# * Computes dot product with face normal
# * If dot > 0; face is facing the camera
#
# REFERENCES:
# * Back-face Culling: https://en.wikipedia.org/wiki/Back-face_culling
# * Dot Product: https://en.wikipedia.org/wiki/Dot_product
#
# NOTES:
# * Prevents rendering faces thatpoint away from the camera
# ----------------------------------------------------
def isFaceVisible(bx,by,bz,normal):
    nx,ny,nz = normal
    
    cx = app.x - bx
    cy = app.y - by
    cz = app.z - bz
    
    return (nx * cx + ny * cy + nz * cz) > 0
    
def moveCamera(mouseX, mouseY):
    xChange = mouseX - app.oldX
    yChange = mouseY - app.oldY
    
    app.oldX = mouseX
    app.oldY = mouseY
    
    maxChange = 10
    xChange = max(-maxChange, min(maxChange, xChange))
    
    app.horizontalViewAngle += xChange
    
    app.horizontalViewAngle %= 360
        
    dx = app.x - app.pivotX
    dy = app.y - app.pivotY
    dz = app.z - app.pivotZ
    
    dist = 5
    
    angleRad = math.radians(app.horizontalViewAngle)
    
    app.x = app.pivotX + dist * math.sin(angleRad)
    app.z = app.pivotZ + dist * math.cos(angleRad)

# ----------------------------------------------------
# convertTo2D(point, ignoreZ = False)
# ----------------------------------------------------
# PURPOSE:
# * Converts a 3D world coordinate into a 2D screen coordinate using:
#   * Camera translation
#   * Yaw rotation
#   * Pitching rotation
#   * Perspective projection
#
# FUNCTIONALITY:
# 1. Translate point into camera space
# 2. Apply yaw rotation (around Y-axis)
# 3. Apply pitch rotation (around X-axis)
# 4. Perform perspective projection:
#   * screenX = (x / z) * focalLength + centerX
#   * screenY = (x / z) * focalLength + centerY
#
# REFERENCES:
# * Rotation Matrices: https://en.wikipedia.org/wiki/Rotation_matrix
# * Perspective Projection: https://en.wikipedia/org/wiki/3D_projection#Perspective_projection
# * Camera Transform: https://en.wikipedia.org/wiki/Camera_matrix
#
# NOTES:
# * If ignoreZ = True, points behind the camrea are clamed instead of discarded
# ----------------------------------------------------
def convertTo2D(point, ignoreZ = False):
    aX, aY, aZ = point
    
    dx = aX - app.x
    dy = aY - app.y
    dz = aZ - app.z
    
    yaw = -math.radians(app.horizontalViewAngle)
    
    rx = dx * math.cos(yaw) - dz * math.sin(yaw)
    rz = dx * math.sin(yaw) + dz * math.cos(yaw)
    ry = dy
    
    pitch = math.radians(app.verticalViewAngle)
    
    ry_final = ry * math.cos(pitch) + rz * math.sin(pitch)
    rz_final = -ry * math.sin(pitch) + rz * math.cos(pitch)
    rx_final = rx
    
    z_final = rz_final
    
    if ignoreZ:
        z_final = max(z_final, 0.05)
    else:
        if z_final <= 0.05:
            return None
    
    # focalLength = 220
    fov = max(30,min(110,app.FOV))
    focalLength = (app.width / 2) / math.tan(math.radians(fov / 2))
    screenX = (rx_final * focalLength / z_final) + app.width / 2
    screenY = (-ry_final * focalLength / z_final) + app.height / 2
    
    return (screenX, screenY)

# ----------------------------------------------------
# draw3DLine(p1, p2, color = 'lightgray', width = 1, forceDraw = False)
# ----------------------------------------------------
# PURPOSE:
# * Draws a 3D line segment by projecting both endpoints into 2D
#
# FUNCTIONALITY:
# * Converts both endpoints using convertTo2D()
# * If both project successfully, draws 2D line
# * If forceDraw = True, attempts to clamp points behind camera
#
# NOTES:
# * Used for drawing the floor grid and debugging visuals
# ----------------------------------------------------
def draw3DLine(p1, p2, color = 'lightGray', width = 1):
    a = convertTo2D(p1, ignoreZ = True)
    b = convertTo2D(p2, ignoreZ = True)
    
    if a is not None and b is not None:
        app.drawnShapes.append(Line(*a, *b, fill=color, lineWidth = width))

# ----------------------------------------------------
# drawFloorGrid()
# ----------------------------------------------------
# PURPOSE:
# * Renders a simple 3D grid on the ground plane for orientation
#
# FUNCTIONALITY
# * Draws horizontal and vertical grid lines
# * Uses draw3DLine() for projection
#
# NOTES:
# * Helps the player understand depth and orientation in empty worlds
# ----------------------------------------------------
def drawFloorGrid():
    size = 10
    spacing = 1
    
    for i in range(-size, size + 1, spacing):
        color = 'gray' if i == 0 else 'lightGray'
        
        draw3DLine((-size, -2,i), (size, -2, i), color)
        draw3DLine((i, -2, -size), (i, -2, size), color)
  
# ----------------------------------------------------
# drawCrosshair()
# ----------------------------------------------------
# PURPOSE:
# * Draws a simple 2D crosshair at the center of the screen
#
# FUNCTIONALITY:
# * Draws horizontal and vertical lines
#
# NOTES:
# Purely UI; does not interact with 3D world
# ----------------------------------------------------
def drawCrosshair():
    cx = app.width / 2
    cy = app.height / 2
    size = 10
    
    h = Line(cx - size, cy, cx + size, cy, fill = 'black', lineWidth = 2)
    v = Line(cx, cy - size, cx, cy + size, fill = 'black', lineWidth = 2)
    
    app.drawnShapes.extend([h,v])
    
# ----------------------------------------------------
# avgCameraZ(points)
# ----------------------------------------------------
# PURPOSE:
# * Computes the average depth (distance along camera forward axis) of a face
#
# FUNCTIONALITY:
# * Transforms each point into camera space
# * extracts the Z component after yaw/pitch rotation
# * Averages the values
#
# NOTES:
# * Painter's Algorithm: https://en.wikipedia.org/wiki/Painter%27s_algorithm
# ----------------------------------------------------
def avgCameraZ(points):
    total = 0
    for x,y,z in points:
        dx = x - app.x
        dy = y - app.y
        dz = z - app.z
        
        yaw = -math.radians(app.horizontalViewAngle)
        rz = dx * math.sin(yaw) + dz * math.cos(yaw)
        
        pitch = math.radians(app.verticalViewAngle)
        rz = -dy * math.sin(pitch) + rz * math.cos(pitch)
        
        total += rz
    return total / len(points)
    
# ----------------------------------------------------
# isBlockInFront(bx,by,bz)
# ----------------------------------------------------
# PURPOSE:
# * Determines whether a block is in front of the camera (positive dot product)
#
# FUNCTIONALITY:
# * Computes camera forward vector
# * Computes vector from camera to block
# * Uses dot product:
#   * dot = forward * toBlock
# * If dot > 0; block is in front
#
# REFERENCES:
# * Dot Product: https://en.wikipedia.org/wiki/Dot_product
# * Back-face Culling: https://en.wikipedia.org/wiki/Back-face_culling
#
# NOTES:
# * Used to skip rendering blocks behind the player
# ----------------------------------------------------
def isBlockInFront(bx,by,bz):
    yaw = -math.radians(app.horizontalViewAngle)
    pitch = math.radians(app.verticalViewAngle)
    
    fx = math.sin(yaw) * math.cos(pitch)
    fy = -math.sin(pitch)
    fz = math.cos(yaw) * math.cos(pitch)
    
    vx = bx - app.x
    vy = by - app.y
    vz = bz - app.z
    
    return (fx * vx + fy * vy + fz * vz) > 0

# ----------------------------------------------------
# drawBlock(x,y,z,width = 1, height = 1, depth = 1, color= 'red', borderColor = 'black', centerDot = False, wireframe = False)
# ----------------------------------------------------
# PURPOSE:
# * Renders a single voxel block at world coordinate (x,y,z)
#
# FUNCTIONALITY:
# * 1. **Face Caching**
#    - If the camera hasn't moved, reuse previously projected faces.
#    - This dramatically improves performance
#
# * 2. **Corner Construction**
#    - Computes all 8 corners of the cube in 3D space
#
# * 3. **Face Definitions**
#    - Defines each face by its corner indices and its outward normal
#
# * 4. **Visibility Tests**
#    - Face exposure test (adjacent block occlusion)
#    - Back-face culling (normal dot camera vector)
#    - Block-in-front test (skip blocks behind camera)
#
# * 5. **Projection**
#    - Converts each 3D corner to 2D using convertTo2D()
#    - Drops faces with invalid projections
#
# * 6. **Depth Sorting**
#    - Computes average camera-space Z for each face
#    - Stores facesin app.allFaces for global sorting
#
# * 7. **Wireframe Mode**
#    - Used for block placement preview
#
# REFERENCES:
# * Painters Algorithm: https://en.wikipedia.org/wiki/Painters%27s_algorithm
# * Back-face Culling: https://en.wikipedia.org/wiki/Back-face_culling
# * 3D Projection: https://en.wikipedia.org/wiki/3D_projection
#
# NOTES:
# * This it the main part of the voxel renderer. Every block on screen goes
# this pipeline
# ----------------------------------------------------
def drawBlock(x,y,z,width = 1,height = 1,depth = 1,color = 'red',borderColor = 'black',centerDot = False, wireframe = False):
    if app.useFaceCache and (not app.cameraChanged) and (x,y,z) in app.blockFaceCache:
        cachedFaces = app.blockFaceCache[(x,y,z)]
        for face in cachedFaces:
            app.allFaces.append(face)
        return
    
    center = (x,y,z)
    
    blockType = app.blocks.get((x,y,z))
    
    color = getBlockColor(blockType)

    halfW = width / 2
    halfH = height / 2
    halfD = depth / 2
    
    faces = [
        ([0,1,2,3],(0,0,-1)),
        ([5,4,7,6],(0,0,1)),
        ([0,4,7,3],(-1,0,0)),
        ([1,5,6,2,],(1,0,0)),
        ([0,1,5,4],(0,-1,0)),
        ([3,2,6,7],(0,1,0)),
    ]
    
    corners = [
        (center[0] - halfW, center[1] - halfH, center[2] - halfD),
        (center[0] + halfW, center[1] - halfH, center[2] - halfD),
        (center[0] + halfW, center[1] + halfH, center[2] - halfD),
        (center[0] - halfW, center[1] + halfH, center[2] - halfD),
        (center[0] - halfW, center[1] - halfH, center[2] + halfD),
        (center[0] + halfW, center[1] - halfH, center[2] + halfD),
        (center[0] + halfW, center[1] + halfH, center[2] + halfD),
        (center[0] - halfW, center[1] + halfH, center[2] + halfD),
    ]
    
    faceDrawList = []

    
    projPoints = [convertTo2D(p) for p in corners]
    if sum(1 for p in projPoints if p is None) > 6:
        return
    
    for faceIndices, normal in faces:
        if app.useFaceCulling and (not isFaceExposed(x,y,z,normal)):
            continue
        
        if app.useFaceCulling and (not isFaceVisible(x,y,z,normal)):
            continue
        
        if not isBlockInFront(x,y,z):
            continue
        
        face3D = [corners[i] for i in faceIndices]
        face2D = []
        
        all_valid = True
        for px,py,pz in face3D:
            proj = convertTo2D((px,py,pz))
            if proj is None:
                all_valid = False
                break
            face2D.append(proj)
            
        if not all_valid:
            continue
        
        depth = avgCameraZ(face3D)
        faceDrawList.append((depth,face2D))
        
    faceDrawList.sort(key = lambda pair: pair[0],reverse = True)
    
    if not wireframe:
        faceData = []
        
        for depth,pts in faceDrawList:
            data = (depth,pts,color,borderColor)
            app.allFaces.append(data)
            faceData.append(data)
        
        if app.useFaceCache:
            app.blockFaceCache[(x,y,z)] = faceData
            
    if centerDot:
        centerProj = convertTo2D((x,y,z))
        if centerProj:
            dot = Circle(centerProj[0],centerProj[1],6,fill = 'black')
            app.drawnShapes.append(dot)

def redrawAll():
    setStatusUIVisible(app.gameStarted)
    if app.settingsMenu.visible:
        app.settingsMenu.toFront()
    app.fpsFrames += 1
    now = time.time()
    if now - app.fpsTime >= 1:
        app.fpsLabel.value = f"FPS: {app.fpsFrames}"
        app.fpsFrames = 0
        app.fpsTime = now
    
    app.allFaces = []
    for shape in app.drawnShapes:
        shape.visible = False
    app.drawnShapes = []

    #drawFloorGrid()
    drawFlatFloor()

    for (bx, by, bz), blockType in app.blocks.items():
        if max(abs(bx - app.x),abs(by - app.y),abs(bz - app.z)) > app.renderDistance:
            continue
        drawBlock(bx, by, bz, width = app.blockSize, height = app.blockSize, depth = app.blockSize, color = getBlockColor(blockType))
    
    app.allFaces.sort(key = lambda x:x[0], reverse = True)
    
    for _, pts, color, borderColor in app.allFaces:
        polyOpacity = 20 if app.useWireframe else 100
        polyBorder = borderColor
        poly = Polygon(
            *[coord for pt in pts for coord in pt],
            fill=color,
            border=polyBorder,
            borderWidth=2,
            opacity=polyOpacity
        )
        app.drawnShapes.append(poly)
        
    if app.previewPos is not None:
        x,y,z,item = app.previewPos
        
        drawBlock(x,y,z,width = app.blockSize, height = app.blockSize, depth = app.blockSize,borderColor = 'white',wireframe = True)
    
    drawCrosshair()
    app.coordLabel.toFront()
    app.modeLabel.toFront()
    app.fpsLabel.toFront()
    app.statusGroup.toFront()
    app.hotbarGroup.toFront()
    if app.inventoryGroup:
        app.inventoryGroup.toFront()
    if app.chatGroup:
        app.chatGroup.visible = app.gameStarted
        refreshChatUI()
        app.chatGroup.toFront()
    if app.pauseMenu:
        app.pauseMenu.toFront()
        
    app.cameraChanged = False
    app.settingsMenu.toFront()
    
def moveWithCollisions(dx,dy,dz):
    if not app.useCollisions:
        app.x += dx
        app.y += dy
        app.z += dz
        return
    
    if not collidesAt(app.x + dx, app.y, app.z):
        app.x += dx
        
    if not collidesAt(app.x,app.y,app.z + dz):
        app.z += dz
        
    newY = app.y +  dy
    if not collidesAt(app.x,newY,app.z):
        app.y = newY
        app.onGround = False
    else:
        if dy < 0:
            app.onGround = True
        app.yVelocity = 0
    
def onStep():
    oldX = app.x
    oldY = app.y
    oldZ = app.z
    
    oldYaw = app.horizontalViewAngle
    oldPitch = app.verticalViewAngle
    if not app.gameStarted:
        setStatusUIVisible(False)
        return
    if app.pausing:
        redrawAll()
        return
    if app.inventoryOpen:
        redrawAll()
        return
    item = app.hotbar[app.selectedSlot]
    if item is not None:
        app.previewPos = getTargetedBlock()

    angle = -math.radians(app.horizontalViewAngle)
    
    forwardX = math.sin(angle)
    forwardZ = math.cos(angle)
    
    rightX = math.sin(angle + math.pi / 2)
    rightZ = math.cos(angle + math.pi / 2)
    
    dx = 0
    dy = 0
    dz = 0
    
    if 'w' in app.keysHeld:
        dx += forwardX * app.moveSpeed
        dz += forwardZ * app.moveSpeed
    if 's' in app.keysHeld:
        dx -= forwardX * app.moveSpeed
        dz -= forwardZ * app.moveSpeed
    if 'a' in app.keysHeld:
        dx -= rightX * app.moveSpeed
        dz -= rightZ * app.moveSpeed
    if 'd' in app.keysHeld:
        dx += rightX * app.moveSpeed
        dz += rightZ * app.moveSpeed
    
    if app.flyMode:
        if 'space' in app.keysHeld:
            dy += app.verticalSpeed
        if 'q' in app.keysHeld:
            dy -= app.verticalSpeed
    else:
        app.cameraChanged = True
        app.yVelocity += app.gravity
        app.yVelocity *= app.airDrag
        if app.yVelocity < app.terminalVelocity:
            app.yVelocity = app.terminalVelocity
        dy += app.yVelocity

    prevOnGround = app.onGround

    moveWithCollisions(dx,dy,dz)
    
    actualDy = app.y - oldY
    
    if (not app.flyMode) and app.useCollisions:
        if app.onGround:
            if (not prevOnGround) and app.fallDistance > 3:
                fallDamage = math.ceil(app.fallDistance - 3)
                app.health = max(0,app.health - fallDamage)
            app.fallDistance = 0
        elif actualDy < 0:
            app.fallDistance += -actualDy
    else:
        app.fallDistance = 0

    if any(k in app.keysHeld for k in ('w','a','s','d','space','q')):
        app.cameraChanged = True
        
    app.coordLabel.value = f"X: {app.x:.2f}  Y: {app.y:.2f}  Z: {app.z:.2f}"
    
    if (app.f3Visible):
        app.fpsLabel.visible = True
        app.coordLabel.visible = True
        app.modeLabel.visible = True
    else:
        app.fpsLabel.visible = False
        app.coordLabel.visible = False
        app.modeLabel.visible = False
    
    redrawAll()
    
    

    