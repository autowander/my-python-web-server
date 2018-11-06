from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys

class ServerException(Exception):
	'''服务器内部错误'''
	pass

class RequestHandler(BaseHTTPRequestHandler):
	
	Error_Page = """\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """
	
	def send_content(self, page):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-Length", str(len(page)))
		self.end_headers()
		self.wfile.write(page)
		
	def handler_file(self, full_path):
		try:
			with open(full_path, 'rb') as f:
				content = f.read()
			self.send_content(content)
		except IOError as msg:
			msg = "'{0}' cannot be read: {1}".format(self.path, msg)
			self.handler_error(msg)
	
	def handler_error(self, msg):
		values = {
			'path': self.path,
			'msg' : msg
		}
		page = self.Error_Page.format(**values)
		self.send_content(page.encode('utf-8'))
		
	def do_GET(self):
		try:
			#os.getcwd() 是当前的工作目录，self.path 保存了请求的相对路径
			#不要忘了 RequestHandler 继承自 BaseHTTPRequestHandler
			#它已经帮我们将请求的相对路径保存在self.path中了。
			full_path = os.getcwd()+self.path
			#如果路径不存在...
			if not os.path.exists(full_path):
				#抛出异常：文件未找到
				raise ServerException("'{0}' not found".format(self.path))
			#是一个路径文件
			elif os.path.isfile(full_path):
				#调用handler处理文件
				self.handler_file(full_path)
			else:
				#抛出异常路径为不知名对象
				raise ServerException("Unkown object '{0}'".format(self.path))
				
		except Exception as msg:
			self.handler_error(msg)
		
if __name__ == '__main__':
	serverAddress = ('', 8080)
	server = HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()