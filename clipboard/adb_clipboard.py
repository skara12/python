raw = open("clipboard.txt", "r")
str = ""
i = 0
out =raw.readlines()

for line in out :
  s = line.split("'")
  if len(s) > 1:
   str+=s[1]
   if i < 4:
    str+=" " 
  i+=1
  
print ''.join(str.split("."))
