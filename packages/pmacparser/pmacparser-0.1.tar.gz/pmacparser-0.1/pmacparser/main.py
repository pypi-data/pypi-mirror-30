from pmacparser.pmac_parser import PMACParser
import time
import numpy as np

p1 = np.array([21, 41])
p2 = np.array([21.5, 41.5])
p3 = np.array([22, 42])
p4 = np.array([22.5, 42.5])
p5 = np.array([23, 43])
p6 = np.array([23.5, 43.5])
p7 = np.array([24, 44])
p8 = np.array([24.5, 44.5])
p17 = np.array([26, 46])

input_vars = {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6, "P7": p7, "P8": p8,
              "P17": p17, "P4801": 1, "P4802": 2, "P4803": 3, "P4804": 4, "P4805": 5, "P4806": 6, "P4807": 7,
              "P4808": 8, "P4817": 9, "P4901": 10, "P4902": 11, "P4903": 12, "P4904": 13, "P4905": 14,
              "P4906": 15, "P4907": 16, "P4908": 17, "P4917": 18, "Q21": 31, "Q22": 32, "Q23": 33, "Q24": 34,
              "Q25": 35, "Q26": 36, "Q27": 37, "Q28": 38, "Q29": 3900, "Q30": 40}

lines = []
lines.append("Q1=(P(4800+1)*P1+P(4900+1))")
lines.append("Q5=(P(4800+2)*P2+P(4900+2))")
lines.append("Q9=(P(4800+7)*P7+P(4900+7))")
lines.append("IF(Q27=0)")
lines.append("Q2=(P(4800+3)*P3+P(4900+3))")
lines.append("Q3=(P(4800+5)*P5+P(4900+5))")
lines.append("Q4=(P(4800+3)*P3+P(4900+3))+(P(4800+8)*P8+P(4900+8))")
lines.append("Q6=(P(4800+4)*P4+P(4900+4))")
lines.append("Q7=(P(4800+6)*P6+P(4900+6))")
lines.append("Q8=(P(4800+4)*P4+P(4900+4))+(P(4800+17)*P17+P(4900+17))")
lines.append("ELSE")
lines.append("Q130=SQRT((Q24+Q29)*(Q24+Q29)-(Q28+(P(4800+17)*P17+P(4900+17))-Q30)*"
             "(Q28+(P(4800+17)*P17+P(4900+17))-Q30))")
lines.append("Q128=TAN(Q26)*(Q130+Q21)")
lines.append("Q131=(P(4800+3)*P3+P(4900+3))-(P(4800+1)*P1+P(4900+1))-Q128")
lines.append("Q6=(ATAN(Q131/(Q130+Q22))+Q26)/2")
lines.append("Q133=(P(4800+5)*P5+P(4900+5))-(P(4800+1)*P1+P(4900+1))-Q128")
lines.append("Q7=(ATAN(Q133/(Q130+Q23))+Q26)/2")
lines.append("Q4=(P(4800+1)*P1+P(4900+1))+(P(4800+8)*P8+P(4900+8))")
lines.append("Q129=TAN(Q25)*(Q130+Q21)")
lines.append("Q132=(P(4800+4)*P4+P(4900+4))-(P(4800+2)*P2+P(4900+2))-Q129")
lines.append("Q2=(ATAN(Q132/(Q130+Q22))+Q25)/2")
lines.append("Q134=(P(4800+6)*P6+P(4900+6))-(P(4800+2)*P2+P(4900+2))-Q129")
lines.append("Q3=(ATAN(Q134/(Q130+Q23))+Q25)/2")
lines.append("Q8=(P(4800+2)*P2+P(4900+2))+(P(4800+17)*P17+P(4900+17))")

parser = PMACParser(lines)

start = time.time()
for i in xrange(500):
    output = parser.parse(input_vars)
end = time.time()

print(end - start)

print output