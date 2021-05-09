from __future__ import print_function
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import csv
import os
import shutil

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    files1 = os.listdir(os.curdir)

    for file1 in files1:
        shutil.rmtree(file1, ignore_errors=True)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials1.json', SCOPES)
            creds = flow.run_local_server(port=5555)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # f
    service = build('drive', 'v3', credentials=creds)

    with open('fileids.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        page_token = None
        while True:
            response = service.files().list(q ="name contains 'DB_CRCL'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
            for file in response.get('files', []):
                # print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                name = file.get('name')
                id1 = file.get('id')
                writer.writerow([name, id1])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
    str1 = "gdown https://drive.google.com/uc?id="
    with open('fileids.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            str2 = row[1]
            str3 = str1+str2
            # print(type(str3))
            # print(row)
            os.system(str3)
    files = os.listdir(os.curdir)
    for i in range(0,len(files)):
        print(files[i][len(files)-3 : len(files)])
        result = files[i].find('.pdf')
        print(files[i] , result)
        if(result != -1):
            branch = files[i][8:10]
            year =  files[i][11:13]
            study = files[i][14:16]
            # print(branch , year , study)
            if(os.path.isfile(os.path.join(os.path.abspath(os.getcwd()) , branch)) == False and branch != 'HA'):
                os.makedirs(os.path.join(os.path.abspath(os.getcwd()) , branch) , exist_ok = True)
            # elif(os.path.isfile(os.path.join(os.path.abspath(os.getcwd()) , branch)) == False and branch == 'HA'):
            #     os.makedirs(os.path.join(os.path.abspath(os.getcwd()) , "Academic_Handbook") , exist_ok = True)

            # if(branch == "HA" or branch == "Ha" or branch == "ha"):
            #     src = os.curdir[1:len(os.curdir)] + 'Academic_Handbook'
            #     dst = os.curdir[1:len(os.curdir)] + 'Academic_Handbook' + '.pdf'
            #     os.rename(os.path.join(os.path.abspath(os.getcwd()) , "Academic_Handbook") , os.path.join(os.path.abspath(os.getcwd()) , dst))

            
            src = os.curdir[1:len(os.curdir)] + files[i] 
                # print(src)
            if(branch =="HA" or branch == "Ha" or branch == "ha"):
                dst =  os.curdir[1:len(os.curdir)] + "Academic_Handbook" '.pdf'
            else:
                dst =  os.curdir[1:len(os.curdir)] + branch + '/' + branch + '_' + study + '_' + '20' + year + '.pdf'
            os.rename(os.path.join(os.path.abspath(os.getcwd()) , files[i]) , os.path.join(os.path.abspath(os.getcwd()) , dst))
            print(branch , year , study)

    files2 = os.listdir(os.curdir)

    for file2 in files2:
        if(file2 == "_H"):
            shutil.rmtree(file2, ignore_errors=True)


if __name__ == '__main__':
    main()
