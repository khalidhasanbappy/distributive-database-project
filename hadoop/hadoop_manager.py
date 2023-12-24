import os
import shutil
import pyhdfs

HOST = 'localhost'
PORT = '9870'
USER_NAME = 'root'
ARTICLES_PATH = '/user/root/articles/'


class HadoopManager:

    def __init__(self) -> None:
        self.client = pyhdfs.HdfsClient(hosts=[
            f'{HOST}:{PORT}'
        ], user_name=USER_NAME)

    # general monitoring methods

    def exists(self, path) -> bool:
        return self.client.exists(ARTICLES_PATH + path)

    def list_status(self, path) -> list:
        try:
            return self.client.list_status(ARTICLES_PATH + path)
        except pyhdfs.HdfsFileNotFoundException as e:
            print(e)

    def content_summary(self, path):
        try:
            return self.client.get_content_summary(ARTICLES_PATH + path)
        except pyhdfs.HdfsFileNotFoundException as e:
            print(e)

    # individual file managing methods

    def read_file(self, article, file_name) -> bytes:
        try:
            with self.client.open(ARTICLES_PATH + article + '/' + file_name) as f:
                return f.read()
        except pyhdfs.HdfsFileNotFoundException as e:
            print(e)

    def upload_file(self, source_path: str, article: str, file_name: str) -> None:
        try:
            self.client.copy_from_local(source_path, ARTICLES_PATH + article + '/' + file_name)
        except pyhdfs.HdfsFileNotFoundException as e:
            print('hdfs error:' + str(e))
        except FileNotFoundError as e:
            print('local error:' + str(e))

    def download_file(self, article: str, file_name: str, dest_path: str, ) -> None:
        try:
            self.client.copy_to_local(ARTICLES_PATH + article + '/' + file_name, dest_path)
        except pyhdfs.HdfsFileNotFoundException as e:
            print('hdfs error:' + str(e))
        except FileNotFoundError as e:
            print('local error:' + str(e))

    def delete_file(self, article: str, file_name: str) -> None:
        try:
            self.client.delete(ARTICLES_PATH + article + '/' + file_name)
        except pyhdfs.HdfsFileNotFoundException as e:
            print(e)

    # articles managing methods

    def list_article(self, article: str) -> list:
        return self.client.listdir(ARTICLES_PATH + article + '/')

    def read_article(self, article) -> dict:
        files = {}
        for file in self.list_article(article):
            files[file] = self.read_file(article, file)
        return files

    def upload_article(self, source_path: str, article: str) -> None:
        if self.exists(article):
            self.delete_article(article)
        else:
            self.client.mkdirs(article)
        for source_file in os.listdir(source_path):
            self.upload_file(source_file, article, source_file.split('/')[-1])

    def download_article(self, article: str, dest_path: str) -> None:
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path, ignore_errors=True)
        os.mkdir(dest_path)
        files = self.list_article(article)
        for file in files:
            self.download_file(article, file, dest_path + file)

    def delete_article(self, article: str) -> None:
        files = self.list_article(article)
        for file in files:
            self.delete_file(article, file)
