# author: Mauro Bambil de Paula
import twint
from datetime import date
from datetime import datetime

# Configure
c = twint.Config()
c.Search = "quarentena OR isolamento"
month = 6
day = 19
start = datetime(2020, month=month, day=day, hour=19)
while datetime.timestamp(start) < datetime.timestamp(datetime.now()):
    end = datetime(2020, month=month, day=day, hour=21)


    c.Since = str(start) 
    c.Until = str(end)
    c.Store_csv = True
    file_name =f"tweets/2020_{day}_0{month}.csv" 
    c.Output = file_name
    c.Hide_output = True
    twint.run.Search(c)
    
    day = day+7
    if(day > 31 and month == (3 or 5)):
        month += 1
        day = day - 31 
    elif(day >30):
        month += 1
        day = day - 30
    print(day, month)
    start = datetime(2020, month=month, day=day, hour=19)
