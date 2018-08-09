#!/bin/bash/python3
# -*- coding:utf-8 -*-

import numpy as np
import sys
import argparse
import copy
import time
import pdb


def getTime():
	return time.asctime()

def convertTime(t):
	day = t // 86400
	rest = t % 86400
	hour = rest // 3600
	rest = rest % 3600
	minute = rest // 60
	rest = rest % 60
	return "{} days, {} hours, {} minutes, {} seconds.".format(day,hour,minute,rest)

class Sudoku:
	"""
	docstring for Sudoku
	****************************************
	*A Good Sudoku Only Has *One* Solution.
	****************************************

	squ 0,8 from l to r, from up to down
	row 0,8 from up to down
	col 0,8 from l to r
	
	Enumeration of the fix line
	enumLine(self,array,comparingArray)
	Return a series of array with all enumerations.

	Brute-force Algorithm:
	recFitIn(self,original,rowNumber,array)
	362880 for total blank line
	at most 362880 * 9 conditions
	iterate through numbers and return if wrong
	when reaching 8 index row check for finishflag and 
	appended to self.result
	"""
	def __init__(self,fileName):
		try:
			f = open(fileName,"r")
		except:
			print("Cannot open file : %s." % fileName)
			sys.exit(1)
		tmp = []
		for i in f.readlines():
			tmp.append([int(k) for k in list(i.rstrip())])
		self.board = np.array(tmp,dtype=np.int16)
		self.avail = np.zeros((9,9),dtype=object)
		self.intermediate = None
		self.result = []
		self.tag = False
		

	def preProcess(self):
		self.intermediate = copy.deepcopy(self.board)
		for i in range(9):
			for j in range(9):
				if self.intermediate[i,j] != 0:
					continue
				self.avail[i,j] = self.intersect(self.getSqu(self.intermediate,self.getSquIndex(i,j)),self.intermediate[i,:],self.intermediate[:,j])
				if len(self.avail[i,j]) == 1:
					value = self.avail[i,j].pop()
					#place to change others availability
					self.changeAvail(i,j,value,self.avail)
					self.intermediate[i,j] = value
					self.avail[i,j] = 0
		a2 = copy.deepcopy(self.avail)
		# while true fill
		while True:
			a1 = copy.deepcopy(a2)
			for i in range(9):
				for j in range(9):
					#squ
					#if i == 0 and j == 7:
					#	pdb.set_trace()
					if a1[i,j] == 0:
						continue
					listWithoutPosition = self.getSqu(a1,self.getSquIndex(i,j)).tolist()
					listWithoutPosition.pop(self.getSquInnerIndex(i,j))
					#[0, 0, [8, 3, 7], [9, 2, 3, 7], [8, 9, 2, 3, 7], [8, 9, 3, 7], 0, 0]	
					#pdb.set_trace()
					array1 = self.toSetCompare(a1[i,j],listWithoutPosition)
					# row
					# without difference element [] so we conduct a function to select intersection with only
					listWithoutPosition = a1[i,:].tolist()
					listWithoutPosition.pop(j)
					array2 = self.toSetCompare(a1[i,j],listWithoutPosition)
					#col
					listWithoutPosition = a1[:,j].tolist()
					listWithoutPosition.pop(i) 
					array3 = self.toSetCompare(a1[i,j],listWithoutPosition)
					inter = self.intersectX(array1,array2,array3)
					if inter == None:
						continue
					if len(inter) == 1:
						value = inter[0]
						#place to change others availability
						self.changeAvail(i,j,value,a2)
						a2[i,j] = 0
						self.intermediate[i,j] = value 
					else:
						a2[i,j] = inter
			if np.array_equal(a1,a2):
				#pdb.set_trace()
				break

	def toSetCompare(self,element,listX):
		tmp = []
		#pdb.set_trace()
		for i in listX:
			if i == 0:
				continue
			else:
				for k in i:
					tmp.append(k)
		#pdb.set_trace()
		return list(set(element).difference(set(tmp)))

	def intersectX(self,array1,array2,array3):
		tmp = [len(array1),len(array2),len(array3)]
		if set(tmp) == {0}:
			return None
		tmp = np.array(tmp)
		for i in range(3):
			if tmp[i] == 0:
				tmp[i] = 10
		index = np.argmin(tmp)
		return list([array1,array2,array3][index])

	def changeAvail(self,x,y,value,board):
		#squ
		tmp = self.getSqu(board,self.getSquIndex(x,y))
		for i in range(len(tmp)):
			if isinstance(tmp[i],int):
				continue
			tmp[i] = [k for k in tmp[i] if k != value]
		self.manNpSqu(board,self.getSquIndex(x,y),tmp.reshape(3,3))
		#row
		tmp = copy.deepcopy(board[x,:])
		for i in range(len(tmp)):
			if isinstance(tmp[i],int):
				continue
			tmp[i] = [k for k in tmp[i] if k != value]
		board[x,:] = copy.deepcopy(tmp)
		#col
		tmp = copy.deepcopy(board[:,y])
		for i in range(len(tmp)):
			if isinstance(tmp[i],int):
				continue
			tmp[i] = [k for k in tmp[i] if k != value]
		board[:,y] = copy.deepcopy(tmp)

	def getSquInnerIndex(self,x,y):
		row = x % 3
		col = y % 3
		return row * 3 + col

	def getSquIndex(self,x,y):
		row = x // 3
		rowIn = {0+row*3,1+row*3,2+row*3}
		col = y // 3
		colIn = {col,col+3,col+6}
		return list(colIn.intersection(rowIn)).pop()

	def intersect(self,array1,array2,array3):
		# Not really intersection
		#pdb.set_trace()
		return list(self.remain(array1).intersection(self.remain(array2)).intersection(self.remain(array3)))

	def rowCheck(self,board):
		if set(board.sum(axis=1)) == {45} and self.rowSetCheck(board):
			return True
		return False

	def rowSetCheck(self,board):
		for i in range(9):
			if not set(board[i,:]) == {1,2,3,4,5,6,7,8,9}:
				return False
		return True

	def colCheck(self,board):
		if set(board.sum(axis=0)) == {45} and self.colSetCheck(board):
			return True
		return False

	def colSetCheck(self,board):
		for i in range(9):
			if not set(board[:,i]) == {1,2,3,4,5,6,7,8,9}:
				return False
		return True

	def manNpSqu(self,board,index,new):
		old = new
		row = index // 3
		col = index % 3
		board[0+row*3:3+row*3,0+col*3:3+col*3] = new

	def getSqu(self,board,index):
		row = index // 3
		col = index % 3
		return board[0+row*3:3+row*3,0+col*3:3+col*3].reshape(9)

	def squCheck(self,board):
		if set(self.squSum(board)) == {45} and self.squSetCheck(board):
			return True
		return False

	def squSum(self,board):
		tmp = []
		for i in range(9):
			tmp.append(self.getSqu(board,i).sum())
		return np.array(tmp)

	def squSetCheck(self,board):
		for i in range(9):
			if not set(self.getSqu(board,i)) == {1,2,3,4,5,6,7,8,9}:
				return False
		return True

	def finishFlag(self,board):
		if self.squCheck(board) and self.rowCheck(board) and self.colCheck(board):
			return True
		return False

	def remain(self,array):
		# returning set
		return {1,2,3,4,5,6,7,8,9}.difference(set(array))

	# input lines without filled
	def enumLine(self,array,comparingArray):
		tmp = []
		#pdb.set_trace()
		for i in self.combination(self.remain(array)):
			tag = False
			container = list(i)
			#container is a string list !! 
			inTmp = []
			for j in range(9):
				if array[j] == 0:
					value = int(container[0])
					if not value in comparingArray[j]:
						#pdb.set_trace()
						tag = True
						break
					# to let stack equal
					inTmp.append(int(container.pop(0)))
				else:
					inTmp.append(array[j])
			if tag:
				continue
			tmp.append(np.array(inTmp))
		#pdb.set_trace()
		return tmp

	def combination(self,setNumber):
		string = "".join([str(k) for k in list(setNumber)])
		return	self.recCombination(string)


	def recCombination(self,string):
		tmp = []
		if len(string) == 1:
			return [string]
		for i in range(len(string)):
			for j in self.recCombination(string[:i]+string[i+1:]):
				tmp.append(string[i] + j)
		return tmp

	def getSimple(self,board):
		squDict = {}
		for i in range(9):
			count = self.getSqu(board,i).tolist().count(0)
			if count != 0:
				squDict[i] = count 
		rowDict = {}
		for i in range(9):
			count = board[i,:].tolist().count(0)
			if count != 0:
				rowDict[i] = count
		colDict = {}
		for i in range(9):
			count = board[:,i].tolist().count(0)
			if count != 0:
				colDict[i] = count  
		# counting zero so ascending order	
		#pdb.set_trace()
		return sorted(squDict.items(),key=lambda x:x[1],reverse=True),sorted(rowDict.items(),key=lambda x:x[1],reverse=True),sorted(colDict.items(),key=lambda x:x[1],reverse=True)

	def getNext(self,simplified):
		#(10,10) is None
		if len(simplified[0]) != 0:
			squ = simplified[0].pop()
		else:
			squ = (10,10)
		if len(simplified[1]) != 0:
			row = simplified[1].pop()
		else:
			row = (10,10)
		if len(simplified[2]) != 0:
			col = simplified[2].pop()
		else:
			col = (10,10)
		if squ == (10,10) and row == (10,10) and col == (10,10):
			#pdb.set_trace()
			return None
		# None so we can't use np.argmin if we want to retain order in None
		tmp = np.array([squ,row,col])
		tag = np.argmin(tmp[:,1])
		tmp = tmp.tolist()
		#pdb.set_trace()
		# without reset, returning (index of (squ,row,col), index of inner)
		return tag,tmp[tag][0]

	def process(self,board,origin,avail):
		flag = self.getNext(self.getSimple(board))
		#pdb.set_trace()
		if flag == None:
			self.result.append(copy.deepcopy(board))
			self.tag = True
		else:
			#pdb.set_trace()
			self.recProcess(board,flag,origin,avail)
			#pdb.set_trace()
			
	def recProcess(self,board,flag,origin,avail):
		x,y = flag
		if x == 0:
			for i in self.enumLine(self.getSqu(board,y),self.getSqu(avail,y)):
				if np.array_equal(i,np.array([6, 1, 4, 9, 2, 5, 8, 3, 7])):
					pass
					#pdb.set_trace()
				# enumLine return [np.array]
				self.squAdd(board,y,i,origin,avail)
				# jumping out of the rest for loop
		elif x == 1:
			for i in self.enumLine(board[y,:],avail[y,:]):
				self.rowAdd(board,y,i,origin,avail)
		else:
			for i in self.enumLine(board[:,y],avail[:,y]):
				self.colAdd(board,y,i,origin,avail)


	def squAdd(self,board,index,array,origin,avail):
		#pdb.set_trace()
		self.manNpSqu(board,index,copy.deepcopy(array.reshape(3,3)))
		#pdb.set_trace()
		if self.allValid(board):
			self.process(board,origin,avail)
			if self.tag:
				return
		self.manNpSqu(board,index,copy.deepcopy(self.getSqu(origin,index).reshape(3,3)))

	def rowAdd(self,board,index,array,origin,avail):
		board[index,:] = copy.deepcopy(array)
		#pdb.set_trace()
		if self.allValid(board):
			self.process(board,origin,avail)
			if self.tag:
				return
		board[index,:] = copy.deepcopy(origin[index,:])

	def colAdd(self,board,index,array,origin,avail):
		board[:,index] = copy.deepcopy(array)
		#pdb.set_trace()
		if self.allValid(board):
			self.process(board,origin,avail)
			if self.tag:
				return
		board[:,index] = copy.deepcopy(origin[:,index])

	def valid(self,array):
		array = array.tolist()
		x = array.count(0)
		v = set(array)
		v.discard(0)
		if x + len(v) == 9:
			return True
		return False

	def allValid(self,board):
		for i in range(9):
			if not self.valid(board[i,:]):
				#print("*************")
				#print("%d row" % i)
				#print(board)
				#print("*************")
				return False
		for i in range(9):
			if not self.valid(board[:,i]):
				#print("*************")
				#print("%d col" % i)
				#print(board)
				#print("*************")
				return False
		for i in range(9):
			if not self.valid(self.getSqu(board,i)):
				#print("*************")
				#print("%d col" % i)
				#print(board)
				#print("*************")
				return False
		return True

	def exec(self,board,avail,method=0):
		tmp = copy.deepcopy(board)
		if method:
			self.process(tmp,board,avail)
			#pdb.set_trace()
		else:
			self.recFitIn(tmp,0,board,avail)
		


	def recFitIn(self,board,rowNumber,origin,avail):
		#pdb.set_trace()
		#print(rowNumber)
		## bug-freed: If row already filled will stop the recrusion.
		if rowNumber == 9:
			if self.finishFlag(board):
				#pdb.set_trace()
				tmp = copy.deepcopy(board)
				self.result.append(tmp)
				self.tag = True
			return
		combine = self.enumLine(origin[rowNumber,:],avail[rowNumber,:])
		if len(combine) == 0:
			self.recFitIn(board,rowNumber+1,origin,avail)
			if self.tag:
				return
		for i in combine:
			board[rowNumber,:] = i
			if self.allValid(board):
				#print(board)
				self.recFitIn(board,rowNumber+1,origin,avail)
				if self.tag:
					return
			else:
				board[rowNumber,:] = copy.deepcopy(origin[rowNumber,:])

	def print(self,element,fileDir=sys.stdout):
		if not isinstance(element,list):
			element = [element]
		print("",file=fileDir)
		for i in element:
			for j in range(9):
				print(" ",end="",file=fileDir)
				for k in range(9):
					print(i[j,k],end=" ",file=fileDir)
				print("",file=fileDir)

	def run(self,output=sys.stdout,method=0):
		a = time.time()
		self.print(self.board,fileDir=output)
		self.preProcess()
		#pdb.set_trace()
		#for debug
		#self.print(self.intermediate,fileDir=output)
		#end
		print("",file=output)
		self.exec(self.intermediate,self.avail,method=method)
		print("        ↓",file=output)
		self.print(self.result,fileDir=output)
		b = time.time()
		print("",file=output)
		print(convertTime(b-a),file=output)

def main():
	parser = argparse.ArgumentParser(description='Crack Your MoFuckin\' Sudoku.')
	parser.add_argument("file",type=str,help="The Sudoku file to proceed")
	parser.add_argument("--output",type=str,help="Output file")
	parser.add_argument("--method",type=int,help="The method to use : 0 for Row-bruteforce 1 for Smart-detect Default:0")
	args = parser.parse_args()
	m = 1 if args.method else 0
	program = Sudoku(args.file)
	if args.output:
		with open(args.output,"w") as fd:
			program.run(output=fd,method=m)
	else:	
		program.run(method=m)



	
if __name__ == '__main__':
	main()