import numpy as np
import time


board = np.array([[0,0,0,0,3,0,5,0,2],
                   [8,0,0,0,0,0,0,0,0],
                   [0,0,0,0,2,0,7,4,0],
                   [5,0,0,9,0,0,3,0,0],
                   [0,8,0,0,0,0,6,0,1],
                   [1,0,0,0,4,0,0,7,0],
                   [0,1,0,6,0,0,0,0,8],
                   [0,0,4,0,0,1,0,0,0],
                   [0,9,0,2,0,0,0,0,0]])






class Sudoku:
    def __init__(self, aboard):
        self.aboard = aboard
        self.cboard = np.full((9,9,9),[0,0,0,0,0,0,0,0,0], dtype=np.int)
        for i in range(9):
            for j in range(9):
                if self.aboard[i,j] > 0:
                    self.cboard[i,j] = [-1,-1,-1,-1,-1,-1,-1,-1,-1]
        self.count = 0
        self.initial = 0
        self.number_list = np.arange(1,10)

    def answer_check(self, aboard, cboard):
        length_array = (cboard.reshape(81,9) != 0).sum(axis = 1)
        blank_number = (length_array == 0).sum() #候補が0個になってしまったマスの数
        if blank_number >0:
            return False
        for i in range(9):
            b = aboard[i,:][aboard[i,:] > 0]
            if len(b) != len(np.unique(b)):
                print("Duplication Error:{}行".format((i)))
                return False
        for j in range(9):
            b = aboard[:,j][aboard[:,j] > 0]
            if len(b) != len(np.unique(b)):
                print("Duplication Error:{}列".format((j)))
                return False
        for i in range(3):
            for j in range(3):
                pre_b = aboard[3*i:3*i+3,3*j:3*j+3].flatten()
                b = pre_b[pre_b > 0]
                if len(b) != len(np.unique(b)):
                    print("Duplication Error:{}ブロック".format((i,j)))
                    return False
        return True


    def substitute(self,aboard,cboard):
        new_aboard = aboard.copy()
        new_cboard = cboard.copy()
        for i in range(9):
            for j in range(9):
                if aboard[i,j] >= 1:
                    continue 
                ij_candidate = cboard[i,j][cboard[i,j] >0]
                if len(ij_candidate) == 1:
                    ij_answer = ij_candidate[0]
                    new_aboard[i,j] = ij_answer
                    self.count +=1
                    new_cboard[i,j] = [-1,-1,-1,-1,-1,-1,-1,-1,-1]
                    print("update:",i,j, "→",ij_answer)
        return new_aboard, new_cboard

    
    def candidate(self,aboard, cboard):
        new_cboard = cboard.copy()
        for i in range(9):
            for j in range(9):
                if aboard[i,j] >= 1:
                    continue 
                not_candidate_list = np.unique(np.r_[aboard[i,:], aboard[:,j], aboard[i//3*3:i//3*3+3,j//3*3:j//3*3+3].flatten()])
                ij_candidate = np.setdiff1d(self.number_list, not_candidate_list)
                #print(i,j,ij_candidate, self.candidate_board[i,j])
                if self.initial > 0:
                    ij_candidate = np.intersect1d(ij_candidate, cboard[i,j])
                #print(i,j,ij_candidate)
                l = len(ij_candidate)
                ij_candidate_extend = np.r_[ij_candidate, np.array([0 for _ in range(9-l)])]
                new_cboard[i,j] = ij_candidate_extend
        return new_cboard



    def decrease_candidate1(self,aboard,cboard): #2つの組の候補を削除
        new_cboard = cboard.copy()
        for i in range(9):
            for j in range(9):
                if aboard[i,j] >= 1:
                    continue
                ij_candidate = cboard[i,j]
                if len(ij_candidate[ij_candidate > 0]) == 2:
                    i_candidate_list = cboard[i,:]
                    for k in range(9):
                        ik_candidate = i_candidate_list[k]
                        flag1 = len(np.setdiff1d(ik_candidate, ij_candidate)) == 0
                        flag2 = len(ik_candidate[ik_candidate > 0]) == 2
                        flag3 = j!=k 
                        if flag1 and flag2 and flag3:
                            #print((i,j),"and",(i,k),"行")
                            for l in range(9):
                                if l != j and l != k:
                                    il_new_candidate = np.setdiff1d(i_candidate_list[l],ij_candidate)     
                                    i_candidate_list[l] = np.r_[il_new_candidate, np.array([-1 for _ in range(9-len(il_new_candidate))])]
                            new_cboard[i,:] = i_candidate_list

                    
                    j_candidate_list = cboard[:,j]
                    for k in range(9):
                        flag1 = len(np.setdiff1d(j_candidate_list[k], ij_candidate)) == 0
                        flag2 = len(j_candidate_list[k][j_candidate_list[k] > 0]) == 2
                        flag3 = i != k
                        if flag1 and flag2 and flag3:
                            #print((i,j),"and",(k,j),"列")
                            for l in range(9):
                                if l != i and l != k:
                                    lj_new_candidate = np.setdiff1d(j_candidate_list[l],ij_candidate)
                                    j_candidate_list[l] = np.r_[lj_new_candidate, np.array([-1 for _ in range(9-len(lj_new_candidate))])]
                            new_cboard[:,j] = j_candidate_list

                    
                    ij33_candidate_list = np.reshape(cboard[i//3*3:i//3*3+3,j//3*3:j//3*3+3], (9,-1))
                    for k in range(9):
                        flag1 = len(np.setdiff1d(ij33_candidate_list[k], ij_candidate)) == 0
                        flag2 = len(ij33_candidate_list[k][ij33_candidate_list[k] > 0]) == 2
                        flag3 = not (i%3 == k//3 and j%3 == k%3)
                        if flag1 and flag2 and flag3:
                            #print((i,j),"and",(i//3*3+k//3, j//3*3+k%3),"ブロック")
                            for l in range(9):
                                if not (i%3 == l//3 and j%3 == l%3)  and not l == k:
                                    #print("i,j,k,l =",i,j,k,l)
                                    new_candidate = np.setdiff1d(ij33_candidate_list[l],ij_candidate)
                                    ij33_candidate_list[l] = np.r_[new_candidate, np.array([-1 for _ in range(9-len(new_candidate))])]
                            new_cboard[i//3*3:i//3*3+3,j//3*3:j//3*3+3] = np.reshape(ij33_candidate_list, (3,3,9))

        return new_cboard       


    def absurd_law(self, i,j):
        pass

    def one_rcb_candidate(self,cboard): #一つの行などにおいて、ある数字が入るマスが一か所だけなら確定
        new_cboard = cboard.copy()
        for i in range(9):
            i_candidate_list = cboard[i,:]
            for n in range(1,10):
                count = 0
                index = -1
                for j, ij_candidate in enumerate(i_candidate_list):
                    if n in ij_candidate:
                        count += 1
                        index = j
                if count == 1:
                    new_cboard[i,index] = np.array([n,0,0,0,0,0,0,0,0])
                    return new_cboard
        
        for j in range(9):
            j_candidate_list = cboard[:,j]
            for n in range(1,10):
                count = 0
                index = -1
                for i, ij_candidate in enumerate(j_candidate_list):
                    if n in ij_candidate:
                        count += 1
                        index = i
                if count == 1:
                    new_cboard[index,j] = np.array([n,0,0,0,0,0,0,0,0])
                    return new_cboard
        for i in range(3):
            for j in range(3):
                ij33_candidate_list = np.reshape(cboard[3*i:3*i+3,3*j:3*j+3], (9,-1))
                #print(ij33_candidate_list)
                for n in range(1,10):
                    count = 0
                    index = -1
                    for k in range(9):
                        if n in ij33_candidate_list[k]:
                            count += 1
                            index = i
                    if count == 1:
                        new_cboard[3*i+k%3, 3*j+k//3] = np.array([n,0,0,0,0,0,0,0,0])
                        return new_cboard
        return new_cboard

    def elimination_process(self, aboard, cboard):
        new_aboard = aboard
        new_cboard = cboard
        while True:
            old_aboard = new_aboard.copy()
            old_cboard = new_cboard.copy()

            new_cboard = self.candidate(new_aboard, new_cboard)
            new_cboard = self.decrease_candidate1(new_aboard, new_cboard)
            new_aboard, new_cboard = self.substitute(new_aboard, new_cboard)
            new_cboard = self.candidate(new_aboard, new_cboard)
            new_cboard = self.one_rcb_candidate(new_cboard)
            new_aboard, new_cboard = self.substitute(new_aboard, new_cboard)
            
            flag = self.answer_check(new_aboard, new_cboard)
            if not flag:
                break
            if np.all(old_aboard == new_aboard) and np.all(old_cboard == new_cboard):
                break
        return new_aboard, new_cboard, flag
        #flag ==False => 矛盾発生


    def deep_search(self,aboard, cboard):
        if np.all(aboard > 0):
            return aboard, cboard
        
        new_aboard = aboard.copy()
        new_cboard = cboard.copy()

        length_array = (cboard.reshape(81,9) > 0).sum(axis = 1)
        min_index = np.argmin(np.where(length_array> 0, length_array, 10))
        i,j = min_index//9, min_index%9
        print("min length = {}".format(length_array[min_index]))
        print("cboard[i,j] = {}".format(cboard[i,j]))
        for l in range(length_array[min_index]):
            test_value = cboard[i,j,l]
            print("if {},{} → {}".format(i,j,test_value))

            new_aboard[i,j] = test_value
            new_cboard[i,j] = [-1,-1,-1,-1,-1,-1,-1,-1,-1]
            end_aboard, end_cboard, flag = self.elimination_process(new_aboard, new_cboard)
            #flag == True => 矛盾はしていないが、完成ではないかもしれない
            #flag == False => 矛盾発生で終了
            if flag:
                return self.deep_search(end_aboard, end_cboard)
            else:
                print("next candidate")
                continue
        return None, None

def main(board):
    inital_time = time.time()
    print("-"*20,"start","-"*20)

    sudoku = Sudoku(board)
    sudoku.cboard = sudoku.candidate(sudoku.aboard, sudoku.cboard)
    sudoku.initial = 1
    aboard, cboard, flag =sudoku.elimination_process(sudoku.aboard, sudoku.cboard)
    aboard, cboard = sudoku.deep_search(aboard, cboard)

    print(aboard)
    if sudoku.answer_check(aboard, cboard):
        print("succeeded")
    end_time = time.time()
    print("processing time:",end_time-inital_time)

main(board)
