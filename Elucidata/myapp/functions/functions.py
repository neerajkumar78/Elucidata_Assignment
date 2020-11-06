def handle_uploaded_file(f):  
    with open('myapp/static/myapp/upload/'+f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)
def getRoundedTime(row):
    time = row['Retention time (min)'] 
    if time>1:
        return round(time)
    else:
        return 1