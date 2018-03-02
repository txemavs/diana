#!/usr/bin/python
# -*- coding: cp1252 -*-

import os
import wx
import time
import random
import images

HOME = os.getcwd()
TITLE = 'Diana - ejemplo DC wxpython'


class TargetWindow(wx.Window):
    def __init__(self, parent):
        self.win = parent
        #self.image = wx.Image(os.path.join(HOME,'target.png'), wx.BITMAP_TYPE_PNG)
        self.image = images.gettargetImage()
        #self.mask = wx.Image(os.path.join(HOME,'mask.png'), wx.BITMAP_TYPE_PNG)
        self.mask = images.getmaskImage()
        self.aspect = self.image.GetWidth()/float(self.image.GetHeight())
        self.color="RED"
        self.click = 0
        self.score = 0
        self.time = 0
        self.lastPos = None
        self.shoots = []
        
        wx.Window.__init__(self, parent, -1, size=(200,200), style=wx.SIMPLE_BORDER)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_LEFT_DOWN(self, self.OnLeftClick)
        wx.EVT_LEFT_UP(self, self.OnLeftClickEnd)
        wx.EVT_MOTION(self, self.OnMotion)
        try:
            self.shoot = wx.Sound(os.path.join(HOME, "shoot.wav"))
        except:
            self.shoot = None
        
    def OnSize(self, event):
        self.Width, self.Height = self.GetClientSizeTuple()
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        self.DrawTarget()
        
    def OnPaint(self,event):
        event.Skip()
        self.DrawTarget()

    def DrawTarget(self, dc=None):
        if dc is None: dc = wx.ClientDC(self)
        width, height = self.Width, self.Height
        aspect = width/float(height)
        
        self.x,self.y=0,0
        if aspect>self.aspect:
            width = height*self.aspect
            self.x=(self.Width-width)/2
        else:
            height = width/self.aspect
            self.y=(self.Height-height)/2
            
        dc.BeginDrawing()
        dc.Clear()
        self.bitmap = self.image.Scale(width,height, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.bitmap_mask = self.mask.Scale(width,height, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        dc.DrawBitmap(self.bitmap,self.x,self.y,True)
        dc.EndDrawing()
        self.w, self.h = width, height

    def OnLeftClick(self, evt):
        if self.shoot is not None: self.shoot.Play(wx.SOUND_ASYNC)
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen(self.color))
        dc.SetBrush(wx.Brush(self.color))
        pos = evt.GetPosition()
        dc.DrawCircle(pos.x, pos.y, 3)
        self.time = time.time()
        self.click += 1
        points=0
        if (pos.x>self.x and pos.x<self.x+self.w and
            pos.y>self.y and pos.y<self.y+self.h):
            pixelData = wx.AlphaPixelData(self.bitmap_mask)
            pixelAccessor = pixelData.GetPixels()
            pixelAccessor.MoveTo(pixelData, pos.x-self.x, pos.y-self.y)
            r,g,b,a = pixelAccessor.Get() 
            points =  int(round(r/24.0))

        self.score+=points
        self.shoots.append((pos.x/float(self.Width), pos.y/float(self.Height), points))
        self.win.frame.SetTitle('Diana %s disparos - %s puntos' % (self.click, self.score))

    def OnLeftClickEnd(self, evt):
        ms = ((time.time() - self.time)*1000.0)
        points = self.shoots[-1][2]
        self.log("Disparo "+str(self.click)+": "+str(ms)+" ms. "+str(points)+" puntos.\n")

    def OnMotion(self, evt):
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen(self.color))
        pos = evt.GetPositionTuple()
        if not evt.Moving():
            if self.lastPos is None:
                self.lastPos = pos
            dc.DrawLine(*(pos + self.lastPos))
            self.lastPos = pos
        else:
            self.lastPos = pos

    def log(self, text):
        self.win.console.write(text)


class TestLaser(wx.Panel):
    def __init__(self, parent):
        self.frame = parent
        wx.Panel.__init__(self, parent, -1)
        self.win = TargetWindow(self)
        self.win.SetBackgroundColour((0,0,0))
        self.console = wx.TextCtrl(self, -1, "", (0,0), (64,64), wx.TE_MULTILINE|wx.BORDER_NONE)
        self.console.SetFont(wx.SystemSettings.GetFont(getattr(wx, 'SYS_SYSTEM_FIXED_FONT')))
        self.console.SetBackgroundColour((0,0,0))
        self.console.SetForegroundColour((0,203,255))
        self.console.Hide()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.win,  proportion=10, flag=wx.EXPAND | wx.ALL)
        sizer.Add(self.console,  proportion=0, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)
        self.console.write("Listo.\n")


class Principal(wx.Frame):
    def __init__(self):
        super(Principal, self).__init__(parent=None, title=TITLE, size=(640,400))
        TestLaser(self)


class Application(wx.App): 
    def OnInit(self): 
        self.window = Principal() 
        self.window.Show() 
        self.SetTopWindow(self.window) 
        return True 


APP = Application(redirect=False,
                  filename=None,
                  useBestVisual=True,
                  clearSigInt=True)

APP.MainLoop() 
