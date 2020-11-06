from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse
from myapp.functions.functions import handle_uploaded_file, getRoundedTime  
from .forms import FileUpload
from zipfile import ZipFile
import os
import pathlib
from Elucidata.settings import BASE_DIR

'''
view to handle file uploading 
'''
def home(request):
	flag=False
	if request.method=='POST':
		file_uploads=FileUpload(request.POST, request.FILES)
		if file_uploads.is_valid():
			handle_uploaded_file(request.FILES['files']) 
			flag=True
			context={
			'data':flag,
			'msg':'File Uploaded Successfully.',
			'link1':request.FILES['files'].name.split('.')[0]+'/part1/',
			'link2':request.FILES['files'].name.split('.')[0]+'/part2and3/',
			}
			
			return render(request,"output.html",context=context)
	else:
		file_uploads=FileUpload()
		context={
			'data':flag,
			'form':file_uploads,
		}
		return render(request,"home.html",context=context)
	
'''
view to genenerate 3 child dataset according to given constraints
and make a zipfile of all 3 datasets
''' 
def part1(request,filename):
	base_path=os.path.join(BASE_DIR,'myapp\\static\\myapp')
	df = pd.read_excel(os.path.join(base_path,'upload',filename+'.xlsx'))
	df1 = df[(df['Accepted Compound ID'].str.endswith('PC',na=False)) & (df['Accepted Compound ID'].str[-3]!='L')]
	df1.to_csv(base_path+'\\output_files\\PC.csv',index=False)
	df2 = df[df['Accepted Compound ID'].str.endswith('LPC',na=False)]
	df2.to_csv(base_path+'\\output_files\\LPC.csv',index=False)
	df3 = df[df['Accepted Compound ID'].str.endswith('plasmalogen',na=False)]
	df3.to_csv(base_path+'\\output_files\\Plasmalogen.csv',index=False)
	dataset_path_list = [base_path+'\\output_files\\PC.csv',base_path+'\\output_files\\LPC.csv',base_path+'\\output_files\\Plasmalogen.csv']
	zipWriteObj = ZipFile(base_path+'\\output_files\\child_datasets.zip', 'w')
	for csv_file in dataset_path_list:
		zipWriteObj.write(csv_file)
		os.remove(csv_file) 
	zipWriteObj.close()	
	zipReadObj = ZipFile(base_path+'\\output_files\\child_datasets.zip', 'r')
	response = HttpResponse(zipReadObj,content_type='application/octet-stream')		
	response['Content-Disposition'] = 'attachment; filename="child_datasets.zip"'
	zipReadObj.close()
	return response

'''
view to Add a new column in the parent dataset with the name “Retention Time Roundoff (in mins)”.
This column have rounded-off values of the corresponding retention time. Retention time
is rounded-off to the nearest natural number.
After that, find the mean of all the metabolites which have same "Retention Time Roundoff" across all
the samples.
Then remove columns like m/z, Accepted Compound Id and Retention time.
'''
def part2and3(request,filename):
	base_path=os.path.join(BASE_DIR,'myapp\\static\\myapp')
	df = pd.read_excel(base_path+'\\upload\\'+filename+'.xlsx')
	rounded_retention_time = df.apply(lambda row : getRoundedTime(row),axis=1)
	df.insert(2,'Retention Time Roundoff (in mins)',rounded_retention_time)
	df.drop(['m/z','Retention time (min)'],axis=1,inplace=True)
	df = df.groupby(df['Retention Time Roundoff (in mins)']).mean()
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Rounded_Retention_Time.csv"'
	df.to_csv(response,index=True)
	return response

