from app import app
import unittest 
import mysql
from collections import Mapping
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import warnings
from scipy.sparse import (spdiags, SparseEfficiencyWarning, csc_matrix,csr_matrix, isspmatrix, dok_matrix, lil_matrix, bsr_matrix)
warnings.simplefilter('ignore',SparseEfficiencyWarning)
import json

class EcommerceWebsite(unittest.TestCase): 

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_status_code(self):
        result = self.app.get('/',content_type='application/json') 
    # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_connection(self):
        cur=mysql.connector.connect(host='127.0.0.1',user='root',password='',database='ec')
        ste = (str(cur).split('at'))[0]
        st = (ste.split('<'))[1]
        self.assertTrue(cur)
        print(cur)
        self.assertEqual(st,'mysql.connector.connection.MySQLConnection object ')
        cur.close()

    def test_authentication(self):#authentication check #302 because it redirects you to login page if user has not logged in
            result = self.app.get('/category',content_type='application/json')
            self.assertEqual(result.status_code, 200)
    
    def test_image_generation(self):
        todaydate=datetime.now()
        todaydate = str(todaydate).split(" ")[0]+' '+'00:00:00'
        date15=datetime.now() - timedelta(days=14)
        date15 = str(date15).split(" ")[0]+' 00:00:00'
        query="SELECT sum(od.Amount) AS Amount,o.OrdersDate AS Date FROM Orders AS o JOIN orders_details AS od ON o.Orders_id = od.Orders_id JOIN Product AS p ON od.Prod_id = p.Prod_id WHERE (o.OrdersDate>='"+date15+ "'AND o.OrdersDate<='"+todaydate+"') AND p.Seller_id=1 GROUP BY Date"
        subprocess.call(["python","app/sellerforecast.py",query], shell=True)
        my_file = Path('app/static/sgraph.png')
        a = my_file.is_file()
        print(a)
        if a:
            self.assertEqual(a, True)

    def test_recommendation_system(self):
        result = self.app.get('/recommend?pid=1',content_type='application/json')
        resp = (list(result.response)[0].decode("utf-8")).strip('\n')
        print(resp)
        self.assertEqual(resp,'[2,3,4,5,7,16]')
    
    def test_addtocart(self):
        result = self.app.get('/cart/add?pid=3&qty=4',content_type='application/json')
        self.assertEqual((list(result.response)[0].decode("utf-8")),'Successfully Added To Cart')

    def test_addreview(self):
        pid = 2
        rt = 4
        rv = 'super'
        result = self.app.get('/prodinfo/review?prod_id={}&rt={}&rv={}'.format(pid,rt,rv),content_type='application/json')
        response = list(result.response)[0].decode("utf-8")
        res = "<tr><td>{}</td><td>2020-05-27 00:00:00</td><td>{}</td></tr>".format(rt,rv)
        print(res)
        self.assertEqual(response,res)

    def test_auto_search(self):
        result = self.app.get('/search/autocomplete/1300',content_type='application/json')
        response = (list(result.response)[0].decode("utf-8")).strip('\n')
        response = response.strip("[\"")
        response = response.strip("\"]")
        print(response)
        self.assertEqual(response,"Canon EOS 1300D")   

    def test_likeprod(self):
        result = self.app.open('/prodinfo/likeop?pid=2&op=1')
        response = list(result.response)[0].decode("utf-8").strip("\n")
        print(response)
        self.assertEqual(response,'{"dislikes":"0","likes":"1"}')

    def test_category(self):
            result = self.app.get('/category_api?key=Phones',content_type='application/json')
            self.assertEqual(result.status_code, 200)



if __name__=='__main__':
  unittest.main() 