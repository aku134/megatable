from datetime import date
import streamlit as st
import zipfile
import requests
import shutil
from pathlib import Path
import os
import uuid
import time
from backend.init import s3, s3_client, database_url, conn
from sqlalchemy.orm import sessionmaker, session
from backend.models import Training, Frame, Base, Test_frame
import pandas as pd
from sqlalchemy import create_engine,text

cursor = conn.cursor()

engine = create_engine(database_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
s = Session()

sidebar=st.sidebar
my_bucket = s3.Bucket('megatabletest')


class Megatable:
    def _get_all_files(self, folder):
        assert (os.path.isdir(folder))
        ls = []
        for path in Path(folder).rglob('*'):
            if os.path.isfile(path):
                rel_path = os.path.relpath(path, folder)
                ls.append((path, rel_path))
        return ls

    def _add_uuid_stamp(self, filename):
        name, ext = os.path.splitext(filename)
        return name + '(' + str(time.time_ns()) + str(uuid.uuid4()) + ')' + ext

    def _get_upload_name(self, filepath):
        return self._add_uuid_stamp(filepath.replace('/', '!'))

    def upload(self, folder):
        files_uploaded = 0
        files = self._get_all_files(folder)
        id=1

        for path, rel_path in files:

            upload_name = self._get_upload_name(rel_path)

            s3.Bucket('megatabletest').upload_file(
                Filename=str(path),
                Key=upload_name
            )
            self.insert(upload_name,id)
            files_uploaded += 1
            id+=1
        return files_uploaded

    # Insert data into db
    def insert(self,file,id):
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'megatabletest',

                'Key': file
            }
        )
        url = url.split("?")[0]
        st.text(url)


        fid = f'f0{id}'

        frame = Test_frame(
          frame_id = fid,
          frame_url = url
        )
        st.text(frame)
        s.add(frame)
        s.commit()



    #     training = Training(
    #         frame_id=fid,
    #         frame_date=date(2022, 12, 15),
    #         customer_id=1002,
    #         artifact_type=2,
    #         bounding_boxes_url=url,
    #         video_url="",
    #         frame_metadata_json=""
    #     )
    #     s.add(training)
    #
    #
    #



    # Delete data into db
    def delete(self, table_name):

        d = s.query(Training).filter(Training.frame_id == 'f01').one()
        s.delete(d)
        s.commit()

    def update(self, table_name):

        res = s.query(Training).filter(Training.artifact_type == 1).all()
        for data in res:
            data.artifact_type = 2
            s.add(data)
        s.commit()

    # for downloading images/annotations
    '''
    :input:query 
           Examples:
           1.Select frame_url from frame;
           -fetch frame_urls from frame table

           2.Select bounding_boxes_url from training;
           -fetch annotations from training table

           3.Select f.frame_url from 
           training as t inner join frame as f 
           on t.frame_id=f.frame_id 
           where t.artifact_type=1;
           -fetch frame_urls that are of artifact_type=1 (Hook)

    :output: downloads the frames or annotations in a zip file
    '''

    def download(self, query, saveas):
        ans = []
        # st.text(type(query))
        # print(query)
        try:
            cursor.execute(f'''{query}''')
            result = cursor.fetchall()

            for i in range(len(result)):
                ans.append(result[i][1])

            if len(ans) > 0:

                folder_name = saveas
                zipfile_name = folder_name + '.zip'
                zipfile_path = zipfile_name
                zipf = zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED)

                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                i = 0

                while (i < len(ans)):
                    # print(ans[i])
                    file_name = ans[i].split("/", 3)[3]
                    # print(f"file_name {file_name}")
                    try:
                        r = requests.get(ans[i], stream=True)

                        with open(os.path.join(folder_name, file_name), 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=128):
                                fd.write(chunk)
                        zipf.write(os.path.join(folder_name, file_name))
                    except Exception as e:
                        st.text(e)


                    fd.close()
                    i += 1

                shutil.rmtree(f"{saveas}")
                zipf.close()
                return zipfile_name
            else:
                return st.text("No file exists,check the query")

        except Exception as e:
            return st.text(f"error level1 {e}")



    def show(self,table):
        try:

            q=f'select * from {table} limit 5; '
            r = pd.read_sql_query(sql=text(q), con=engine.connect())
            st.table(r)

        except Exception as e:
            st.text(e)




    def show_table(self):
        res=[]
        try:
            query = 'SELECT table_name as tables FROM information_schema.tables where table_schema=\'public\';'
            result = pd.read_sql_query(sql=text(query), con=engine.connect())
            sidebar.title('List of tables in db')
            # sidebar.header('Header')
            for i in result.index:
                res.append(result['tables'][i])
            selected_option = sidebar.selectbox('Select the table to view',res)
            for i in result.index:

                if selected_option == result['tables'][i]:
                    st.text(result['tables'][i])
                    self.show(result['tables'][i])

            # for i in result.index:
                # if st.button(result['tables'][i]):

                        # self.show(result['tables'][i])
            # st.table(result)
        except Exception as e:
            st.text(e)
        # try:
        #     print(s.query(Training).filter(Training.artifact_type == 1).all())
        # except Exception as e:
        #     print(e)



# Call the functions here as obj.function_name()
# f=obj.upload('sample') #folder name
# print("files_uploaded :")
# print(f)
#
# obj=Megatable()
# obj.download('select * from test_frame;')
