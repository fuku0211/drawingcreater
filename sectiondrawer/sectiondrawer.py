# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import gc
import os

if "count_s" not in sc.sticky:
	sc.sticky["count_s"] = 0
if "dict_s" not in sc.sticky:
	sc.sticky["dict_s"] = {}

if mode == 0 or mode == 2:# モードが平面図のみか両方のとき
	# 平面図のプレビュー
	points = [(0, 0, 0 + i) for i in height]
	vec_p = [rs.VectorCreate(i, (0,0,0)) for i in points]
	guid = []
	center = []
	for i in vec_p:
		guid.append(rs.CopyObject(point_p, i))
	for i in guid:
		center.append(rs.coerce3dpoint(i))

if mode == 1 or mode == 2:# モードが断面図のみか両方のとき
	# 断面線に関する情報をまとめる
	class SectionLine():
		def __init__(self, crv, dir, para):# コンストラクタ
			self.crv = crv
			self.dir = dir
			self.para = para

		def get_seg(self):# 断面線を分解したら何本になるかを返却
			segment = len(rs.ExplodeCurves(self.crv))
			return segment
		
		def get_flip(self):# 断面の方向を反転するかを返却
			if self.dir:
				flip = True
			else:
				flip = False
			return flip

		def get_originpt(self):# 図面にした時基点になる点を返却
			pt = rs.EvaluateCurve(self.crv, self.para)
			return pt
	data = SectionLine(curve_s[sc.sticky["count_s"]], reverse, parameter)

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

	vec_x = rs.VectorCreate(MakeXvectorPt(data.get_seg(), curve_s[sc.sticky["count_s"]], data.get_flip())[0], MakeXvectorPt(data.get_seg(), curve_s[sc.sticky["count_s"]], data.get_flip())[1])
	vec_y = rs.VectorReverse(rs.VectorUnitize(rs.VectorCrossProduct(vec_x, [0,0,1]))) * mark
	circle = rs.AddCircle(data.get_originpt(), 1000)
	direction = rs.AddLine(data.get_originpt(), rs.MoveObject(sc.doc.Objects.AddPoint(data.get_originpt()), vec_y))

	#各情報を辞書に登録
	sc.sticky["dict_s"][sc.sticky["count_s"]] = [data.get_seg(), data.get_flip(), data.get_originpt()]
	print(sc.sticky["dict_s"])
	len_p = str(len(height)) + " 枚の平面図が作成されます"
	len_s = str(len(sc.sticky["dict_s"])) + " 本/" + str(len(curve_s)) + "本の切断線が設定済みです"

#ボタン入力したあとの動作///////////////////////////////////////////////////////////
if next:
	if len(sc.sticky["dict_s"]) == len(curve_s):
		len_s = "※※すべて設定済みです※※"
	else:
		sc.sticky["count_s"] += 1

if undo:
	if sc.sticky["count_s"] == 0:
		pass
	else:
		del sc.sticky["dict_s"][sc.sticky["count_s"]]
		sc.sticky["count_s"] -= 1

def Reset():
	sc.sticky["count_p"] = 0
	sc.sticky["dict_p"] = {}
	sc.sticky["count_s"] = 0
	sc.sticky["dict_s"] = {}
	rs.Command("_CPlane " + "_W " + "_T ")
	rs.Command("_Setview " + "_W " + "_P ")
	gc.collect()
	print("end")

if reset:
	Reset()

if draw:
	print("startdrawing")
	exist = []
	for i in height:# 指定の場所で重複しないか確認(平面)
		if i > 0:
			i = "+" + str(i)
		exist.append(os.path.exists(str(directory) + str(name) + "_plan_" + str(i) + ".3dm"))
	for i in range(len(sc.sticky["dict_s"])):# 指定の場所で重複しないか確認(断面)
		exist.append(os.path.exists(str(directory) + str(name) + "_section_" + str(i) + ".3dm"))
	if True in exist:# 一個でも重複する場合
		ans = rs.MessageBox("ファイルがすでに存在します　上書きしますか？", 4, "上書きの確認")
		if ans == int(6):# Massageboxのはいは6で返却される
			save = True
		else:
			save = False
	else:
		save = True

	if save == True:# 重複がない/上書きするときに実行
		def ConvertPt(pt3d):# "X座標,Y座標,Z座標"と入力用の文を作る
			text = (str(pt3d[0]) + "," + str(pt3d[1]) + "," + str(pt3d[2]))
			return text

		rs.Command("_CPlane " + "_W " + "_T ")
		rs.Command("_Show")
		rs.Command("_SelLight")
		rs.Command("_SelPt")
		rs.Command("_SelCrv")
		rs.Command("_Lock")
		if mode == 0 or mode == 2:
			count = 0
			while count != len(height):
				rs.Command("_CPlane " + "_T " + ConvertPt(center[count]))
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				rs.Command("_Plan")
				rs.Command("_SelAll")
				rs.ZoomSelected()
				rs.Command("_SelNone")
				rs.Command("_SelVisible " + "_Enter")
				rs.Command("-_Make2d " + "_D " + "_C " + "_Enter")
				rs.Command("_CPlane " + "_W " + "_T ")
				if height[count] > 0:
					num = "+" + str(height[count])
				else:
					num = height[count]
				rs.Command("-_Export " + directory + name + "_plan_" + str(num) + ".3dm")
				rs.Command("_SelCrv")
				rs.Command("_SelClippingPlane")
				rs.Command("_Delete")
				count += 1
		if mode == 1 or mode == 2:
			count = 0
			while count != len(sc.sticky["dict_s"]):
				sectionline = curve_s[count]
				if sc.sticky["dict_s"][count][1] == True:# flipするとき
					rs.ReverseCurve(sectionline)
				else:# flip しないとき
					pass
				if sc.sticky["dict_s"][count][0] == 0:# 折れ曲がらない断面線のとき
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(sectionline)) + " " + "_V " + ConvertPt(rs.CurveEndPoint(sectionline)) + " ")
					rs.Command("_Clippingplane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
					rs.Command("_Plan")
					rs.Command("_SelAll")
					rs.ZoomSelected()
					rs.Command("_SelNone")
					rs.Command("_SelVisible " + "_Enter")
					rs.Command("-_Make2d " + "_D " + "_C " + "_Enter")
					rs.Command("_CPlane " + "_W " + "_T ")
					rs.Command("-_Export " + directory + name + "_section_" + str(count) + ".3dm")
					rs.Command("_SelCrv")
					rs.Command("_SelClippingPlane")
					rs.Command("_Delete")
				else:# 複雑な断面線のとき
					segment = range(0,sc.sticky["dict_s"][count][0],2)
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
						rs.Command("_SelAll")
						rs.ZoomSelected()
						rs.Command("_SelVisible " + "_Enter")
						rs.Command("-_Make2d " + "_D " + "_U " + "_Enter")
						rs.Command("_Hide")
						rs.Command("_CPlane " + "_W " + "_T ")
						rs.Command("_SelClippingPlane")
						rs.Command("_Delete")
					rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(sectionline)[0])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(sectionline)[0])) + " ")
					rs.Command("_Show")
					rs.Command("_SelCrv")
					rs.Command("-_Make2d " + "_D " + "_C " + "_Enter ")
					rs.Command("_CPlane " + "_W " + "_T ")
					rs.Command("-_Export " + directory + name + "_section_" + str(count) + ".3dm")
					rs.Command("_SelCrv")
					rs.Command("_Delete")
				count += 1
		rs.Command("_Unlock")
		Reset()