import os
import time


class AsciiGif:
    def __init__(self, ListOfFrames, FrameRate):
        self.Frames = ListOfFrames
        self.FrameRate = FrameRate
        self.ClearCommand = "os.system('cls')"

    def SetClearCommand(self, Command):
        self.ClearCommand = Command

    def DrawLogic(self):
        for i in self.Frames:
            print(i)
            time.sleep(1 / self.FrameRate)
            exec(self.ClearCommand)


    def Draw(self, Iterations):
        CurrentIteration = 1
        while CurrentIteration <= Iterations:
            self.DrawLogic()
            CurrentIteration += 1
        while Iterations == -1:
            self.DrawLogic()

