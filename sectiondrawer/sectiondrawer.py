#coding utf-8
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

if "count_section" not in sc.sticky:
	sc.sticky["count_section"] = 0
if "dict_section" not in sc.sticky:
	sc.sticky["dict_section"] = {}

def Reset():
	sc.sticky["count_section"] = 0
	sc.sticky["dict_section"] = {}
	rs.Command("_CPlane " + "_W " + "_T ")
	rs.Command("_Setview " + "_W " + "_P ")
	print("end")
if reset:
	Reset()

pt_0 = rs.CurveStartPoint(curve[sc.sticky["count_section"]])
pt_1 = rs.CurveEndPoint(curve[sc.sticky["count_section"]])
if reverse:
	startpt = pt_0
	endpt = pt_1
else:
	startpt = pt_1
	endpt = pt_0

vec_x = rs.VectorCreate(startpt, endpt)
vec_y = rs.VectorUnitize(rs.VectorCrossProduct(vec_x, [0,0,1])) * mark
movedpt = [rs.MoveObject(rs.AddPoint([pt[0], pt[1], pt[2]]), vec_y) for pt in [startpt, endpt]]
preview = [rs.AddLine(movedpt[0], startpt)] + [rs.AddLine(movedpt[1], endpt)]

def Roundnum(pt_sta, pt_end):
	coordinate = ((int(pt_sta.X), int(pt_sta.Y), int(pt_sta.Z)), (int(pt_end.X), int(pt_end.Y), int(pt_end.Z)))
	return coordinate

sc.sticky["dict_section"][sc.sticky["count_section"]] = Roundnum(startpt, endpt)
print sc.sticky["dict_section"]

#///////////////////////////ボタン入力したあとの動作
if next:
	if len(sc.sticky["dict_section"]) == len(curve):
		print("start draw?")
	else:
		sc.sticky["count_section"] += 1

if redo:
	if sc.sticky["count_section"] == 0:
		pass
	else:
		del sc.sticky["dict_section"][sc.sticky["count_section"]]
		sc.sticky["count_section"] -= 1

if draw:
	print("startdrawing")

	def Convertpt(dict, index, type):
		text = str(dict[index][type][0]) + "," + str(dict[index][type][1]) + "," + str(dict[index][type][2])
		return text

	count = 0
	rs.EnableRedraw(False)
	while count != len(sc.sticky["dict_section"]):
		rs.Command("_SelAll")
		rs.Command("_CPlane " + "_I " + Convertpt(sc.sticky["dict_section"], count, 0) + " " + "_V " + Convertpt(sc.sticky["dict_section"], count, 1) + " ")
		rs.Command("_Clippingplane " + "_C " + Convertpt(sc.sticky["dict_section"], count, 0) + " " + str(1000) + " " + str(1000) + " ")
		rs.Command("_Plan")
		rs.Command("-_Make2d " + "_D " + "_C " + "_Enter ")
		rs.Command("_CPlane " + "_W " + "_T ")
		rs.Command("-_Export " + directory + name + str(count) + ".3dm")
		rs.Command("_Delete")
		rs.Command("_SelClippingPlane")
		rs.Command("_Delete")
		count += 1
	rs.EnableRedraw(True)
	Reset()