# Class for having regions on the screen for a select purpose
class Region:
    def __init__(self,name,position,size):
        self.__name = name
        self.__position = position
        self.__size = size
    
    # Getter methods
    def GetName(self):
        return self.__name
    def GetPosition(self):
        return self.__position
    def GetSize(self):
        return self.__size

# Region to hold a button panel
class ButtonRegion(Region):
    def __init__(self,name,position,size,buttons):
        super().__init__(name,position,size)
        self.__buttons = buttons
    
    # Getter methods
    def Get_Buttons(self):
        return self.__buttons

# Region to hold the console
class ConsoleRegion(Region):
    def __init__(self,name,position,size):
        super().__init__(name,position,size)
        
    # Getter methods

class PathfindingRegion(Region):
    def __init__(self,name,position,size):
        super().__init__(name,position,size)
    
    # Getter methods

class NavbarRegion(Region):
    def __init__(self,name,position,size,navbarText,textPadding):
        super().__init__(name,position,size)
        self.__navbarText = navbarText
        self.__textPadding = textPadding
    
    # Getter methods
    def GetNavbarText(self):
        return self.__navbarText
    
    def GetNavbarTextPadding(self):
        return self.__textPadding

# Basic button class
class Button:
    def __init__(self,name,position,size,region,isActive):
        self.__name = name
        self.__size = size
        self.__position = position
        self.__region = region
        self.__isActive = isActive
    
    # Getter methods
    def GetButtonTextPosition(self,font):
        img = font.render(self.GetName(), False, "White")
        inheritedButtonPosition = self.GetInheritedPosition()
        textPositionX = inheritedButtonPosition[0] + self.GetSize()[0]//2 - img.get_rect().width//2
        textPositionY = inheritedButtonPosition[1] + self.GetSize()[1]//2 - img.get_rect().height//2
        
        return [textPositionX,textPositionY]
    
    def GetName(self):
        return self.__name
    
    def GetSize(self):
        return self.__size
    
    def GetPosition(self):
        return self.__position
    
    def GetRegion(self):
        return self.__region
    
    def GetInheritedPosition(self):
        return [self.GetPosition()[0]+self.GetRegion().GetPosition()[0],self.GetPosition()[1]+self.GetRegion().GetPosition()[1]]
    
    def GetActive(self):
        return self.__isActive
    
    # Other methods
    def GetClicked(self, clickCoords):
        if clickCoords[0] < self.GetInheritedPosition()[0]+self.GetSize()[0] and clickCoords[0] > self.GetInheritedPosition()[0]:
            if clickCoords[1] < self.GetInheritedPosition()[1]+self.GetSize()[1] and clickCoords[1] > self.GetInheritedPosition()[1]:
                self.ButtonClicked()
                return True
            else:
                return False
        else:
            return False
        
    def ButtonClicked(self):
        pass

class StartButton(Button):
    def __init__(self,name,position,size,region,isActive):
        super().__init__(name,position,size,region,isActive)
    
    def ButtonClicked(self):
        super().ButtonClicked()

class ResetButton(Button):
    def __init__(self,name,position,size,region,isActive):
        super().__init__(name,position,size,region,isActive)
        
    def ButtonClicked(self):
        super().ButtonClicked()
        
class ChangePathfindingButton(Button):
    def __init__(self,name,position,size,region,isActive):
        super().__init__(name,position,size,region,isActive)
        
    def ButtonClicked(self):
        super().ButtonClicked()
        
class ChangeConsoleButton(Button):
    def __init__(self,name,position,size,region,isActive):
        super().__init__(name,position,size,region,isActive)
        
    def ButtonClicked(self):
        super().ButtonClicked()
        
class NextMapButton(Button):
    def __init__(self,name,position,size,region,isActive,maps):
        super().__init__(name,position,size,region,isActive)
        self.__maps = maps
        self.__currentMapIndex = 0
        
    def GetMaps(self):
        return self.__maps
    
    def GetMapIndex(self):
        return self.__currentMapIndex
    
    def GetCurrentMap(self):
        return self.GetMaps()[self.GetMapIndex()]
        
    def ButtonClicked(self):
        super().ButtonClicked()
        self.__currentMapIndex += 1
        if self.__currentMapIndex == len(self.GetMaps()):
            self.__currentMapIndex = 0   
        
class PauseButton(Button):
    def __init__(self,name,position,size,region,isActive):
        super().__init__(name,position,size,region,isActive)
        
    def ButtonClicked(self):
        super().ButtonClicked()
        
class NextStepButton(Button):
    def __init__(self,name,position,size,region,isActive):
        super().__init__(name,position,size,region,isActive)
        
    def ButtonClicked(self):
        super().ButtonClicked()
