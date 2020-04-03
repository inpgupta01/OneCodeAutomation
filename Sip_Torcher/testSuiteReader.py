import re

class testSuite:
    def __init__ ( self, filename):
      self.__file=open(filename,"r")
      self.__lastline = ''
      #print("Opening File:",filename)

    def __del__ (self):
      self.__file.close()
      #print("Closing File")

    def printfile(self):
      for line in self.__file:
        print(line)

    def getTestCase(self):
      '''
      This function will read the testsuite and return one testcase a time
      as a list. Returns empty list if there is no more test cases 
      available in the test suite.

      It ignores all the lines present before first test case encountered.
      When first "test case" line encountered it keeps on adding lines untill
      it finds another "test case" and then it returns the list as the testcase. 
      '''
      #print("Executing TestCase:")
      testcase = []
      if self.__lastline: testcase.append(self.__lastline)
      for line in self.__file:
        strline = str(line)
        #strline = strline.lower()
        strline = strline.replace("\n","")
        strline = strline.lstrip()
        strline = strline.lstrip("\t")
        commentline = re.match("#", strline)
        if commentline: continue
        if not strline: continue
        match = re.match("test case:", strline.lower())
        if match:
           if not self.__lastline:
              testcase = []
              self.__lastline = strline
              testcase.append(strline)
              continue
           self.__lastline = strline
           break
        else:
          testcase.append(strline)
      testcaselen = len(testcase)
      if testcaselen <= 1:
         testcase = [] 
      #print(testcase)
      return testcase
      
if __name__ == '__main__':
        suite1 = testSuite("sipptestsuite.txt")
        testcase = suite1.getTestCase()
        while len(testcase) >0:
            print("")
            for i in testcase:
                print(i)
            testcase = suite1.getTestCase()
        del testcase

