import json;


def hello():

   # printing welcome
   print("welcome to python call function tutorials!")


def  ReadFile():
    with open('spray.json') as json_data:
        data = json_data.read();
        parsed_data = json.loads(data)
        json_data.close()
        return parsed_data;


def UseData():
    data = ReadFile();
    chemicals = data.get("chemicals");
    for chemical in chemicals:
            print(j.get("name"));


def Run():
    data = UseData();

Run();
