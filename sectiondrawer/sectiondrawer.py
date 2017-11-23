# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

if "count_section" not in sc.sticky:
	sc.sticky["count_section"] = 0
if "dict_section" not in sc.sticky:
	sc.sticky["dict_section"] = {}

class Sectionline():
	def __init__(self, crv, mode, para):# コンストラクタ
		self.crv = crv
		self.mode = mode
		self.para = para

	def get_Xvector(self):#　断面をつくる作業平面のX軸の始点:p0、終点:p1
		if len(rs.ExplodeCurves(self.crv)) == 0:# 途中で折れ曲がらない断面線のとき
			poly = 1# ベイクする時にこれを使って場合分けする
			if self.mode == True:# 断面を見る方向で場合分け
				p0 = rs.CurveEndPoint(self.crv)
				p1 = rs.CurveStartPoint(self.crv)
			elif self.mode == False:
				p0 = rs.CurveStartPoint(self.crv)
				p1 = rs.CurveEndPoint(self.crv)
		elif len(rs.ExplodeCurves(self.crv)) >= 2:# 途中で折れ曲がる断面線のとき
			poly = len(rs.ExplodeCurves(self.crv))
			if self.mode == True:
				p0 = rs.CurveEndPoint(rs.ExplodeCurves(self.crv)[0])
				p1 = rs.CurveStartPoint(rs.ExplodeCurves(self.crv)[0])
			elif self.mode == False:
				p0 = rs.CurveStartPoint(rs.ExplodeCurves(self.crv)[0])
				p1 = rs.CurveEndPoint(rs.ExplodeCurves(self.crv)[0])
		return (poly, p0, p1)

	def get_originpt(self):# 図面にした時基点になる点
		pt = rs.EvaluateCurve(self.crv, self.para)
		return pt

data = Sectionline(curve[sc.sticky["count_section"]], reverse, parameter)


# 断面を見る方向を示す目印を作る
vec_x = rs.VectorCreate(data.get_Xvector()[1], data.get_Xvector()[2])
vec_y = rs.VectorUnitize(rs.VectorCrossProduct(vec_x, [0,0,1])) * mark
circle = rs.AddCircle(data.get_originpt(), 1000)
direction = rs.AddLine(data.get_originpt(), rs.MoveObject(sc.doc.Objects.AddPoint(data.get_originpt()), vec_y))

#各情報を辞書に登録
sc.sticky["dict_section"][sc.sticky["count_section"]] = [data.get_Xvector()[0], data.get_Xvector()[1], data.get_Xvector()[2], data.get_originpt()]
print(sc.sticky["dict_section"])

#ボタン入力したあとの動作///////////////////////////////////////////////////////////
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

def Reset():
	sc.sticky["count_section"] = 0
	sc.sticky["dict_section"] = {}
	rs.Command("_CPlane " + "_W " + "_T ")
	rs.Command("_Setview " + "_W " + "_P ")
	print("end")

if draw:
	print("startdrawing")

	def Convertpt(pt3d):# "X座標,Y座標,Z座標"という文を作る
		text = (str(pt3d[0]) + "," + str(pt3d[1]) + "," + str(pt3d[2]))
		return text

	count = 0
	rs.EnableRedraw(False)# 画面の描画を停止
	while count != len(sc.sticky["dict_section"]):
		if sc.sticky["dict_section"][count][0] == 1:# 折れ曲がらない断面線のとき
			rs.Command("_SelPt")
			rs.Command("_SelCrv")
			rs.Command("_Lock")
			rs.Command("_SelAll")
			rs.Command("_CPlane " + "_I " + Convertpt(sc.sticky["dict_section"][count][1]) + " " + "_V " + Convertpt(sc.sticky["dict_section"][count][2]) + " ")
			rs.Command("_Clippingplane " + "_C " + Convertpt(sc.sticky["dict_section"][count][1]) + " " + str(1000) + " " + str(1000) + " ")
			rs.Command("_Plan")
			rs.Command("-_Make2d " + "_D " + "_C " + "_Enter ")
			rs.Command("_CPlane " + "_W " + "_T ")
			rs.Command("-_Export " + directory + name + str(count) + ".3dm")
			rs.Command("_Delete")
			rs.Command("_SelClippingPlane")
			rs.Command("_Delete")
			rs.Command("_Unlock")
		elif sc.sticky["dict_setion"][count][0] != 1:# 複雑な断面線のとき
			pass
		count += 1
	rs.EnableRedraw(True)
	Reset()