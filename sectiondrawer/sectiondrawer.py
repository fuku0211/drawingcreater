# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

if "count_sec" not in sc.sticky:
	sc.sticky["count_sec"] = 0
if "dict_sec" not in sc.sticky:
	sc.sticky["dict_sec"] = {}

class SectionLine():
	def __init__(self, crv, mode, para):# コンストラクタ
		self.crv = crv
		self.mode = mode
		self.para = para

	def get_seg(self):
		segment = len(rs.ExplodeCurves(self.crv))
		return segment
		
	def get_flip(self):
		if self.mode:
			flip = True
		else:
			flip = False
		return flip

	def get_originpt(self):# 図面にした時基点になる点
		pt = rs.EvaluateCurve(self.crv, self.para)
		return pt
data = SectionLine(curve[sc.sticky["count_sec"]], reverse, parameter)

# 断面を見る方向を示す目印を作る
def MakeXvectorPt(seg, line, reverse):
	if seg == 0:
		if reverse:
			start_x = rs.CurveStartPoint(line)
			end_x = rs.CurveEndPoint(line)
		else:
			start_x = rs.CurveEndPoint(line)
			end_x = rs.CurveStartPoint(line)
	else:
		if reverse:
			start_x = rs.CurveStartPoint(rs.ExplodeCurves(line)[0])
			end_x = rs.CurveEndPoint(rs.ExplodeCurves(line)[0])
		else:
			start_x = rs.CurveEndPoint(rs.ExplodeCurves(line)[0])
			end_x = rs.CurveStartPoint(rs.ExplodeCurves(line)[0])
	return (start_x, end_x)

vec_x = rs.VectorCreate(MakeXvectorPt(data.get_seg(), curve[sc.sticky["count_sec"]], data.get_flip())[0], MakeXvectorPt(data.get_seg(), curve[sc.sticky["count_sec"]], data.get_flip())[1])
vec_y = rs.VectorReverse(rs.VectorUnitize(rs.VectorCrossProduct(vec_x, [0,0,1]))) * mark
circle = rs.AddCircle(data.get_originpt(), 1000)
direction = rs.AddLine(data.get_originpt(), rs.MoveObject(sc.doc.Objects.AddPoint(data.get_originpt()), vec_y))

#各情報を辞書に登録
sc.sticky["dict_sec"][sc.sticky["count_sec"]] = [data.get_seg(), data.get_flip(), data.get_originpt()]
print(sc.sticky["dict_sec"])

#ボタン入力したあとの動作///////////////////////////////////////////////////////////
if next:
	if len(sc.sticky["dict_sec"]) == len(curve):
		print("start draw?")
	else:
		sc.sticky["count_sec"] += 1

if redo:
	if sc.sticky["count_sec"] == 0:
		pass
	else:
		del sc.sticky["dict_sec"][sc.sticky["count_sec"]]
		sc.sticky["count_sec"] -= 1

def Reset():
	sc.sticky["count_sec"] = 0
	sc.sticky["dict_sec"] = {}
	rs.Command("_CPlane " + "_W " + "_T ")
	rs.Command("_Setview " + "_W " + "_P ")
	print("end")

if reset:
	Reset()

if draw:
	print("startdrawing")

	def ConvertPt(pt3d):# "X座標,Y座標,Z座標"と入力用の文を作る
		text = (str(pt3d[0]) + "," + str(pt3d[1]) + "," + str(pt3d[2]))
		return text
	
	def SelEndPt(line, flip):
		if flip:
			start_x = rs.CurveStartPoint(line)
			end_x = rs.CurveEndPoint(line)
		else:
			start_x = rs.CurveEndPoint(line)
			end_x = rs.CurveStartPoint(line)

	count = 0
	#rs.EnableRedraw(False)# 画面の描画を停止
	while count != len(sc.sticky["dict_sec"]):
		sectionline = curve[count]
		if sc.sticky["dict_sec"][count][1] == True:# flipするとき
			rs.ReverseCurve(sectionline)
		else:# flip しないとき
			pass
		if sc.sticky["dict_sec"][count][0] == 0:# 折れ曲がらない断面線のとき
			rs.Command("_SelPt")
			rs.Command("_SelCrv")
			rs.Command("_Lock")
			rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(sectionline)) + " " + "_V " + ConvertPt(rs.CurveEndPoint(sectionline)) + " ")
			rs.Command("_Clippingplane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
			rs.Command("_Plan")
			rs.ZoomExtents()
			rs.Command("_SelVisible " + "_Enter ")
			rs.Command("-_Make2d " + "_D " + "_C " + "_Enter ")
			rs.Command("_CPlane " + "_W " + "_T ")
			rs.Command("-_Export " + directory + name + str(count) + ".3dm")
			rs.Command("_SelCrv")
			rs.Command("_SelClippingPlane")
			rs.Command("_Delete")
			rs.Command("_Unlock")
		else:# 複雑な断面線のとき
			rs.Command("_SelPt")
			rs.Command("_SelCrv")
			rs.Command("_Lock")
			segment = range(0,sc.sticky["dict_sec"][count][0],2)
			for i in segment:
				if i == 0:
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
					rs.Command("_CPlane " + "_W " + "_T ")
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i + 1])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i + 1])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				elif i == segment[-1]:
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
					rs.Command("_CPlane " + "_W " + "_T ")
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i - 1])) + " " + "_V " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i - 1])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				else:
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
					rs.Command("_CPlane " + "_W " + "_T ")
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i + 1])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i + 1])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
					rs.Command("_CPlane " + "_W " + "_T ")
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[i - 1])) + " " + "_V " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[i - 1])) + " ")
					rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[0])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[0])) + " ")
				rs.Command("_Plan")
				rs.ZoomExtents()
				rs.Command("_SelVisible " + "_Enter ")
				rs.Command("-_Make2d " + "_D " + "_U " + "_Enter ")
				rs.Command("_Hide")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_SelClippingPlane")
				rs.Command("_Delete")
			rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[0])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[0])) + " ")
			rs.Command("_Show")
			rs.Command("_SelCrv")
			rs.Command("-_Make2d " + "_D " + "_C " + "_Enter ")
			rs.Command("_CPlane " + "_W " + "_T ")
			rs.Command("-_Export " + directory + name + str(count) + ".3dm")
			rs.Command("_SelCrv")
			rs.Command("_Delete")
			rs.Command("_Unlock")
		count += 1
	Reset()
	#rs.EnableRedraw(True)