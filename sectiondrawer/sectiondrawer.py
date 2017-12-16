# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import gc
import os
import time
from math import sqrt

len_p = str(len(height)) + " 枚の平面図を生成します"
len_s = str(len(curve_s)) + " 枚の断面図を生成します"

# 平面図の基準点を作成
def MakePlanPreview(num):
	points = [(0, 0, 0 + i) for i in num]
	vec_p = [rs.VectorCreate(i, (0,0,0)) for i in points]
	guid = []
	origin = []
	for i in vec_p:
		guid.append(rs.CopyObject(point_p, i))
	for i in guid:
		origin.append(rs.coerce3dpoint(i))# ガイドから3dpointに変換
	return origin

# 断面を見る方向を示す目印を作る
def MakeSectionPreview(line, size):
	arrow = []# 目印を格納するリスト
	for i in range(len(line)):
		vec_x = rs.VectorCreate(rs.CurveStartPoint(line[i]), rs.CurveEndPoint(line[i]))
		vec_y = rs.VectorUnitize(rs.VectorCrossProduct(vec_x, [0,0,1]))
		pt3 = rs.DivideCurve(line[i], size)
		seglen = rs.Distance(pt3[0], pt3[1])
		tri_s = [rs.AddPoint(pt3[i]) for i in range(3)]
		tri_e = [rs.AddPoint(pt3[len(pt3) - i]) for i in range(1, 4)]
		rs.MoveObject(tri_s[1], vec_y * (seglen * sqrt(3)))
		rs.MoveObject(tri_e[1], vec_y * (seglen * sqrt(3)))
		arrow.append(rs.AddInterpCurve(rs.coerce3dpointlist(tri_s), 1))
		arrow.append(rs.AddInterpCurve(rs.coerce3dpointlist(tri_e), 1))
	return arrow

if mode == 0 or mode == 2:# モードが平面図のみor両方のとき
	center = MakePlanPreview(height)
	print("■previewed plan■")
if mode == 1 or mode == 2:# モードが断面図のみor両方のとき
	direction = MakeSectionPreview(curve_s, mark)
	print("■previewed section■")

if draw:
	print("//////////start drawing//////////")

	# "Make2D"レイヤーが存在するか確認する
	def ConfirmLayer():
		print("■start confirmlayer■")
		sc.doc = Rhino.RhinoDoc.ActiveDoc
		layers = rs.LayerNames()
		if "Make2D" in layers:
			dellayer = rs.MessageBox("既に存在する'Make2D'レイヤーは削除されます　問題ないですか？", 4, "レイヤーの確認")
			if dellayer == int(6):# Massageboxのはいは6で返却される
				rs.PurgeLayer("Make2D")# 作図中にMake2Dレイヤーが作成されるため、前もって削除
				layer = True
				print("deleted layer")
			else:
				rs.MessageBox("作図をキャンセルしました")
				layer = False
				print("canceled writing")
		else:
			layer = True
			print("no make2d layer")
		sc.doc = ghdoc
		print("■end confirmfolder■")
		return layer# "Make2D"レイヤーが存在しないor削除するときはTrueを返却
				
	# 指定のフォルダが存在するか確認する
	def Confirmfolder(dir):
		print("■start confirmfolder■")
		if os.path.exists(str(dir)):# 指定したフォルダが存在するか確認
			folder = True
			print("confirmedfolder")
		else:
			newfolder = rs.MessageBox("指定したフォルダが存在しません(" + str(dir) + ")　フォルダを新規作成しますか？", 4, "フォルダの確認")
			if newfolder == int(6):# Massageboxのはいは6で返却される
				os.mkdir(str(dir))# 指定したディレクトリにフォルダを新規作成
				folder = True
				print("makingnewfolder")
			else:
				rs.MessageBox("作図をキャンセルしました")
				folder = False
				print("canceled writing")
		print("■end confirmfolder■")
		return folder# フォルダを作成orすでに存在したらTrueで返却

	# ファイル名に重複がないか確認する
	def ConfirmDup(dir, num, nam, line):
		print("■start confirmdup■")
		dup = []# ダブリがある場合はTrue、ない場合はFalseが格納されるリスト
		for i in num:# 指定の場所で重複しないか確認(平面)
			if i > 0:
				i = "+" + str(i)
			dup.append(os.path.exists(str(dir) + str(nam) + "_plan_" + str(i) + ".3dm"))
		for i in range(len(curve_s)):# 指定の場所で重複しないか確認(断面)
			dup.append(os.path.exists(str(dir) + str(nam) + "_section_" + str(i) + ".3dm"))
		if True in dup:# 一個でも重複する場合
			ans = rs.MessageBox("ファイルがすでに存在します　上書きしますか？", 4, "上書きの確認")
			if ans == int(6):# Massageboxのはいは6で返却される
				dup = True
				print("overwriting")
			else:
				rs.MessageBox("作図をキャンセルしました")
				dup = False
				print("canceled writing")
		else:
			dup = True
			print("no duplicate")
		print("■end confirmdup■")
		return dup# 重複が存在しないor上書きする場合はTrueで返却

	# "X座標,Y座標,Z座標"と入力用の文を作る
	def ConvertPt(pt3d):
		text = (str(pt3d[0]) + "," + str(pt3d[1]) + "," + str(pt3d[2]))
		return text

	# 平面図を作成
	def MakePlan(num, pt, dir, nam, mode):
		count = 0
		while count != len(num):
			s = time.time()
			print("makeing no." + str(count) + " plan")
			rs.Command("_CPlane " + "_T " + ConvertPt(pt[count]))
			rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
			rs.Command("_Plan")
			rs.Command("_SelAll")
			rs.Command("_Zoom " + "_S ")
			rs.Command("_SelNone")
			if mode == "fast":
				rs.Command("_SelVisible " + "_Enter")
			if mode == "slow":
				rs.Command("_SelAll")
			sc.doc = Rhino.RhinoDoc.ActiveDoc
			select = len(rs.SelectedObjects())
			sc.doc = ghdoc
			print("selected " + str(select) + " objects")
			if select == 0:
				print("canceled")
			else:
				rs.Command("-_Make2d " + "_D " + "_C " + "_M=はい " + "_Enter")
				rs.Command("_CPlane " + "_W " + "_T ")
				if num[count] > 0:
					end = "+" + str(num[count])
				else:
					end = num[count]
				rs.Command("-_Export " + dir + nam + "_plan_" + str(end) + ".3dm")
				rs.Command("_SelCrv")
				print("exported plan")
			rs.Command("_SelClippingPlane")
			rs.Command("_Delete")
			print("time = " + str(time.time() - s))
			print("completed no." + str(count) + " plan")
			count += 1

	# 断面図を作成(折れ曲がらない切断線のとき)
	def MakeSimpleSec(dir, nam, num, line, mode):
		s = time.time()
		rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(line)) + " " + "_V " + ConvertPt(rs.CurveEndPoint(line)) + " ")
		rs.Command("_Clippingplane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
		rs.Command("_Plan")
		rs.Command("_SelAll")
		rs.Command("_Zoom " + "_S ")
		rs.Command("_SelNone")
		if mode == "fast":
			rs.Command("_SelVisible " + "_Enter")
		elif mode == "slow":
			rs.Command("_SelAll")
		sc.doc = Rhino.RhinoDoc.ActiveDoc
		select = len(rs.SelectedObjects())
		sc.doc = ghdoc
		print("selected " + str(select) + " objects")
		if select == 0:
			print("canceled")
		else:
			rs.Command("-_Make2d " + "_D " + "_C " + "_M=はい " + "_Enter")
			rs.Command("_CPlane " + "_W " + "_T ")
			rs.Command("-_Export " + dir + nam + "_section_" + str(num) + ".3dm")
			print("exported section")
			rs.Command("_SelCrv")
		rs.Command("_SelClippingPlane")
		rs.Command("_Delete")
		print("time = " + str(time.time() - s))

	# 断面図を作成(折れ曲がる切断線のとき)
	def MakeComplexSec(dir, nam, num, line, mode):
		s = time.time()
		segment = range(0, len(rs.ExplodeCurves(line)), 2)
		for i in segment:
			print("segment num = " + str(i))
			if i == 0:
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i + 1])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i + 1])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
			elif i == segment[-1]:
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i - 1])) + " " + "_V " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i - 1])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
			else:
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i + 1])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i + 1])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[i - 1])) + " " + "_V " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[i - 1])) + " ")
				rs.Command("_ClippingPlane " + "_C " + "0,0,0" + " " + str(1000) + " " + str(1000) + " ")
			rs.Command("_CPlane " + "_W " + "_T ")
			rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[0])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[0])) + " ")
			rs.Command("_Plan")
			rs.Command("_SelAll")
			rs.Command("_Zoom " + "_S ")
			rs.Command("_SelNone")
			rs.Command("_SelVisible " + "_Enter")
			sc.doc = Rhino.RhinoDoc.ActiveDoc
			select = len(rs.SelectedObjects())
			sc.doc = ghdoc
			print("selected " + str(select) + " objects")
			if select == 0:
				print("canceled")
			else:
				rs.Command("-_Make2d " + "_D " + "_U " + "_M=はい " + "_Enter")
				rs.Command("_Hide")
			rs.Command("_CPlane " + "_W " + "_T ")
			rs.Command("_SelClippingPlane")
			rs.Command("_Delete")
		rs.Command("_CPlane " + "_I " + ConvertPt(rs.CurveStartPoint(rs.ExplodeCurves(line)[0])) + " " + "_V " + ConvertPt(rs.CurveEndPoint(rs.ExplodeCurves(line)[0])) + " ")
		rs.Command("_Show")
		rs.Command("_SelCrv")
		rs.Command("_Zoom " + "_S ")
		rs.Command("-_Make2d " + "_D " + "_C " + "_M=はい " + "_Enter")
		rs.Command("_CPlane " + "_W " + "_T ")
		rs.Command("-_Export " + dir + nam + "_section_" + str(num) + ".3dm")
		rs.Command("_SelCrv")
		rs.Command("_Delete")
		print("time = " + str(time.time() - s))

	# 屋根伏せ図(断面位置図)の作成
	def MakeRoofPlan(dir, nam, mode):
		s = time.time()
		rs.Command("_Plan")
		rs.Command("_SelCrv")
		rs.Command("_Invert")
		rs.Command("_Zoom " + "_S ")
		rs.Command("_SelNone")
		rs.Command("_SelCrv")
		sc.doc = Rhino.RhinoDoc.ActiveDoc
		select = len(rs.SelectedObjects())
		sc.doc = ghdoc
		print("selected " + str(select) + " objects")
		if select == 0:
			print("canceled")
		else:
			rs.Command("-_Make2d " + "_D " + "_U " + "_M=はい " + "_Enter")
			rs.Command("_Lock")
			rs.Command("_SelCrv")
			rs.Command("_Hide")
			if mode == "fast":
				rs.Command("_SelVisible " + "_Enter")
			elif mode == "slow":
				rs.Command("_SelAll")
			sc.doc = Rhino.RhinoDoc.ActiveDoc
			select = len(rs.SelectedObjects())
			sc.doc = ghdoc
			print("selected " + str(select) + " objects")
			if select == 0:
				print("canceled")
			else:
				rs.Command("-_Make2d " + "_D " + "_U " + "_M=はい " + "_Enter")
				rs.Command("_Unlock")
				rs.Command("_SelCrv")
				rs.Command("-_Make2d " + "_D " + "_C " + "_M=はい " + "_Enter")
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("-_Export " + dir + nam + "_roof" + ".3dm")
				rs.Command("_SelCrv")
				rs.Command("_Delete")
			rs.Command("_Unlock")
			rs.Command("_Show")
		print("time = " + str(time.time() - s))

	# リセットする
	def Reset():
		print("■start reset■")
		sc.doc = Rhino.RhinoDoc.ActiveDoc
		rs.PurgeLayer("Make2D")
		sc.doc = ghdoc
		rs.Command("_CPlane " + "_W " + "_T ")
		rs.Command("_Setview " + "_W " + "_P ")
		rs.Command("_SelLight")
		rs.Command("_SelPt")
		rs.Command("_SelCrv")
		rs.Command("_Invert")
		rs.Command("_Zoom " + "_S ")
		rs.Command("_SelNone")
		gc.collect()
		print("■end reset■")

	#/////////////////////////////////////////////////////////////////////////
	# 作図の全体の流れ
	#/////////////////////////////////////////////////////////////////////////
	if ConfirmLayer():# Make2Dレイヤーの存在を確認
		if Confirmfolder(directory):# フォルダの存在を確認
			if ConfirmDup(directory, height, name, curve_s):# ファイルの重複を確認
				rs.Command("_CPlane " + "_W " + "_T ")
				rs.Command("_Show")
				rs.Command("_SelLight")
				rs.Command("_SelPt")
				rs.Command("_SelCrv")
				rs.Command("_Lock")
				if mode == 0 or mode == 2:# 平面図作成
					print("■start makeplan■")
					MakePlan(height, center, directory, name, speed)
					print("■end makeplan■")
				if mode == 1 or mode == 2:# 断面図作成
					print("■start makesection■")
					count = 0
					while count != len(curve_s):
						print("making no." + str(count) + " section")
						sectionline = curve_s[count]
						if len(rs.ExplodeCurves(sectionline)) == 0:# 折れ曲がらない断面線のとき
							print("this is simple sectionline")
							MakeSimpleSec(directory, name, count, sectionline, speed)
						else:# 複雑な断面線のとき
							print("this is complex sectionline")
							MakeComplexSec(directory, name, count, sectionline, speed)
						print("completed no." + str(count) + " section")
						count += 1
					print("■end makesection■")
				rs.Command("_Unlock")
				if mode == 3:# 屋根伏図作成
					print("■start makeroofplan■")
					MakeRoofPlan(directory, name, speed)
					print("■end makeroofplan■")
				print("//////////end drawing//////////")
				Reset()