#!python3

import numpy as np

class Exam(object):
    BB_ERROR = None
    BB_QUESTION_TOTAL = 1
    BB_EXAM_TOTAL = 2
    BB_SUBQUESTION = 3

    def __init__(self, offsetBoxLeft, offsetBoxTop, tableShape, examNo = 0):
        self.__examNo = examNo        
        self.__offsetBoxTop = np.array(offsetBoxTop)
        self.__offsetBoxLeft = np.array(offsetBoxLeft)
        self.__questions = len(self.__offsetBoxTop) - 1
        self.__subQuestions = len(self.__offsetBoxLeft) - 1
        self.__examTableWidth = int(tableShape[1]/2)
        self.__examTableHeight = tableShape[0]

        self.__offsetBoxTop = self.__examTableHeight * self.__offsetBoxTop
        self.__offsetBoxLeft = self.__examTableWidth * self.__offsetBoxLeft
        self.__offsetBoxTop = self.__offsetBoxTop.astype(int)
        self.__offsetBoxLeft = self.__offsetBoxLeft.astype(int)
        if (self.__examNo == 1):
            self.__offsetBoxLeft = self.__examTableWidth + self.__offsetBoxLeft
        
        self.__shapeBbSubquestion = [self.__offsetBoxTop[1] - self.__offsetBoxTop[0], self.__offsetBoxLeft[1] - self.__offsetBoxLeft[0]]
        self.__shapeBbQuestionTotal = [self.__offsetBoxTop[1] - self.__offsetBoxTop[0], self.__examTableWidth - self.__offsetBoxLeft[self.__subQuestions]]
        self.__shapeBbExamTotal = [self.__examTableHeight - self.__offsetBoxTop[self.__questions], self.__shapeBbQuestionTotal[1]]
        
        # print("[self.__offsetBoxTop, self.__offsetBoxLeft] = [%s, %s]" % (self.__offsetBoxTop, self.__offsetBoxLeft))

    def __listSearchFloor(self, list, x):
        index = np.searchsorted(list, x, side='left')
        if index > 0 and index < len(list) and (list[index-1] <= x and x < list[index]):
            return index - 1
        return index
        
    def getExamShape(self):
        return [self.__questions, self.__subQuestions]
        
    def getTableShapeForExam(self):
        offsetLeft = self.__examTableWidth if (self.__examNo == 1) else 0
        return [0, offsetLeft, self.__examTableHeight, self.__examTableWidth]
        
    def getBoundsLimitForDetection(self):
        return np.array([[self.__shapeBbSubquestion[0]/6, self.__shapeBbQuestionTotal[0]], [self.__shapeBbSubquestion[1]/10, self.__shapeBbQuestionTotal[1]]], int)
        
    def getBbSubquestion(self, q = 0, s = 0):
        # print("getBbSubquestion q = %d, s = %d" % (q, s))
        if q < self.__questions and s < self.__subQuestions:
            return [self.__offsetBoxTop[q], self.__offsetBoxLeft[s], *self.__shapeBbSubquestion[:]]
        return None
            
    def getBbQuestionTotal(self, q = 0):
        # print("getBbQuestionTotal q = %d" % (q))
        if q < self.__questions:
            return [self.__offsetBoxTop[q], self.__offsetBoxLeft[self.__subQuestions], *self.__shapeBbQuestionTotal[:]]
        return None
        
    def getBbExamTotal(self):
        return [self.__offsetBoxTop[self.__questions], self.__offsetBoxLeft[self.__subQuestions], *self.__shapeBbExamTotal[:]]
        
    def getIndicesForPosition(self, top, left):
        # print("top = %d, left = %d" % (top, left))
        # print(self.__offsetBoxLeft[self.__subQuestions])
        if not ((self.__offsetBoxTop[0] <= top and top <= self.__examTableHeight) 
                and (self.__offsetBoxLeft[0] <= left and left <= self.__examTableWidth)):
            return [Exam.BB_ERROR, 0, 0]
            
        elif top > self.__offsetBoxTop[self.__questions]:
            if left <= self.__offsetBoxLeft[self.__subQuestions]:
                return [Exam.BB_ERROR, 0, 0]
            else:
                return [Exam.BB_EXAM_TOTAL, 0, 0]
            
        elif left > self.__offsetBoxLeft[self.__subQuestions]:
            # question = np.searchsorted(self.__offsetBoxTop, top, side='left')
            question = self.__listSearchFloor(self.__offsetBoxTop, top)
            return [Exam.BB_QUESTION_TOTAL, question, 0]
        
        else:        
            #question = np.searchsorted(self.__offsetBoxTop, top, side='left')
            question = self.__listSearchFloor(self.__offsetBoxTop, top)
            #subquestion = np.searchsorted(self.__offsetBoxLeft, left, side='left')
            subquestion = self.__listSearchFloor(self.__offsetBoxLeft, left)
            return [Exam.BB_SUBQUESTION, question, subquestion]
        
    def getBbForPosition(self, top, left):
        ret, question, subquestion = self.getIndicesForPosition(top, left)
            
        if ret == Exam.BB_SUBQUESTION:
            return [self.getBbSubquestion(question, subquestion), [ret, question, subquestion]]
        
        elif ret == Exam.BB_QUESTION_TOTAL:
            return [self.getBbQuestionTotal(question), [ret, question, subquestion]]
        
        elif ret == Exam.BB_EXAM_TOTAL:
            return [self.getBbExamTotal(), [ret, question, subquestion]]
        
        return Exam.BB_ERROR
        
class Internal(Exam):
    def __init__(self, tableShape, examNo = 0):
        offsetBoxTop = [0.288113695090439,0.388888888888889,0.489664082687339,0.590439276485788,0.691214470284238,0.791989664082687,0.892764857881137]
        offsetBoxLeft = [0.090252707581227,0.232851985559567,0.375451263537906,0.518050541516246,0.660649819494585,0.803249097472924]
        super(Internal, self).__init__(offsetBoxLeft, offsetBoxTop, tableShape, examNo)

if __name__ == "__main__":        
    i = Internal([321, 384])
    print("getExamShape = %s" % i.getExamShape())
    print("getBoundsLimitForDetection = %s" % i.getBoundsLimitForDetection())
    print("getBbSubquestion = %s" % i.getBbSubquestion(0,0))
    print("getBbQuestionTotal = %s" % i.getBbQuestionTotal(0))
    print("getBbExamTotal = %s" % i.getBbExamTotal())
    print("getIndicesForPosition = %s" % i.getIndicesForPosition(290, 160))
    print("getBbForPosition = %s" % i.getBbForPosition(110, 160))
    
    