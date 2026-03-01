from build123d import *
from ocp_vscode import *

set_port(3939)

class BasePart:
    def __init__(self):
        self.width = 250
        self.taperBodyDistance = 125
        self.minHeight = 100
        self.height = 150
        self.thickness = 80
        self.internalOffset = 10
        self.rampBottomOffset = 40
        self._part = None
        self.numberOfSlots = 4

    def compute(self, debug = False):
        with BuildPart() as basePartSource:
            with BuildSketch(Plane.XY) as originSketch:
                Rectangle(self.width, self.height)

                with BuildLine() as taperBuildLine:
                    mainConstLine = PolarLine((-self.width / 2, self.minHeight / 2), self.taperBodyDistance, 0, mode = Mode.PRIVATE)
                    angledLine = IntersectingLine((mainConstLine.end_point().X, self.height/2), (-.95, -.3), mainConstLine)
                    closingLine1 = Line(angledLine @ 0, (mainConstLine.start_point().X, angledLine.start_point().Y))
                    closingLine2 = Line(closingLine1 @ 1, mainConstLine @ 0)
                    closingLine3 = Line(closingLine2 @ 1, angledLine @ 1)
                
                taperFace = make_face(mode = Mode.SUBTRACT)
                mirror(taperFace, about = Plane.XZ, mode = Mode.SUBTRACT)
            
            extrude(amount = self.thickness)
            fillet(basePartSource.edges(Select.LAST).filter_by(Axis.Z), 5)
            offsetFace = offset(basePartSource.faces(Select.ALL).filter_by_position(Axis.Z, self.thickness - 1, self.thickness + 1), -self.internalOffset)

            extrude(offsetFace, amount = -self.thickness + self.internalOffset, mode = Mode.SUBTRACT)

            internalFilletEdges = basePartSource.edges(Select.LAST).filter_by(Axis.Z).filter_by_position(Axis.X, (-self.width / 2 + self.internalOffset) - 1, (-self.width / 2 + self.internalOffset) + 1)
            internalFilletEdges.extend(basePartSource.edges(Select.LAST).filter_by(Axis.Z).filter_by_position(Axis.X, (self.width / 2 - self.internalOffset) - 1, (self.width / 2 - self.internalOffset) + 1))

            fillet(internalFilletEdges, 4)

            with BuildSketch(Plane.XZ) as rampSketch:
                with BuildLine() as rampSketchBl1:
                    baseLine = Line((-self.width / 2 + self.internalOffset, self.internalOffset), (self.width / 2 - self.internalOffset, self.internalOffset))
                    backLine = PolarLine(baseLine @ 1, self.rampBottomOffset, 90)
                    hypoLine = Line(baseLine @ 0, backLine @ 1)
                make_face()
            
            rampExt = extrude(rampSketch.sketch, amount = self.height / 2 - (self.internalOffset), both = True, mode = Mode.PRIVATE)
            rampExt -= extrude(taperFace, amount = self.thickness, mode = Mode.PRIVATE)
            rampExt -= extrude(taperFace.mirror(Plane.XZ), amount = self.thickness, mode = Mode.PRIVATE)

            add(rampExt)

            with BuildSketch(Plane.XZ) as topRampSketch:
                with BuildLine() as topRampSketchTriangleBL:
                    baseLine = PolarLine((-self.width / 2, self.thickness), self.internalOffset, 0)
                    backLine = PolarLine(baseLine @ 0, self.internalOffset, -90)
                    hypotLine = Line(baseLine @ 1, backLine @ 1)
                make_face()
            
            extrude(topRampSketch.sketch, amount = self.height, both = True, mode = Mode.SUBTRACT)

        if debug:
            show_all(reset_camera = Camera.KEEP)

        self._part = basePartSource

if __name__ == "__main__":
    part = BasePart()
    part.compute(debug = True)