#coding utf-8
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

if "count_section" not in sc.sticky:
	sc.sticky["count_section"] = 0
if "dict_section" not in sc.sticky:
	sc.sticky["dict_section"] = {}
if "openfile" not in sc.sticky:
	sc.sticky["openfile"] = False

if openfile:
	sc.sticky["openfile"] = True
	filename = rs.OpenFileName()
	file = open(filename, 'r')
	curve = rs.ObjectsByLayer(rs.GetLayer())
	file.close()
else:
	sc.sticky["openfile"] = False

if sc.sticky["openfile"] == True:
	def Reset():
		sc.sticky["count_section"] = 0
		sc.sticky["dict_section"] = {}
		rs.Command("_CPlane " + "_W " + "_T ")
		rs.Command("_Setview " + "_W " + "_P ")
		Rhino.RhinoApp.Exit()
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

	height = rs.AddPoint(startpt[0], startpt[1], startpt[2] + 1000)
	sc.sticky["dict_section"][sc.sticky["count_section"]] = [str(startpt), str(endpt), str(rs.coerce3dpoint(height))]
	print(sc.sticky["dict_section"][sc.sticky["count_section"]][0])

	#///////////////////////////ボタン入力したあとの動作
	draw = False
	if next:
		if len(sc.sticky["dict_section"]) == len(curve):
			draw = True
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
		count = 0
		rs.EnableRedraw(False)
		while count != len(sc.sticky["dict_section"]):
			rs.Command("_Selall")
			rs.Command("_Clippingplane " + "_p " + sc.sticky["dict_section"][count][0] + " " + sc.sticky["dict_section"][count][1] + " " + sc.sticky["dict_section"][count][2] + " ")
			rs.Command("_CPlane " + "_I " + sc.sticky["dict_section"][count][0] + " " + sc.sticky["dict_section"][count][1] + " " + sc.sticky["dict_section"][count][2] + " ")
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