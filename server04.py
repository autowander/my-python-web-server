from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys

class case_no_files(object):
	#handler == RequestHandler的self
	def test(self, handler):
		return not os.path.exists(handler.full_path)
		
	def act(self, handler):
		raise ServerException("'{0}' not found".format(handler.path))

class case_existing_files(object):
	def test(self, handler):
		return os.path.isfile(handler.full_path)
	def act(self, handler):
		handler.handler_file(handler.full_path)
		
class case_always_fail(object):
	def test(self, handler):
		return True
		
	def act(self, handler):
		raise ServerException("Unkown object '{0}'".format(handler.path))
		
class case_directory_index_file(object):
	def index_path(self, handler):
		return os.path.join(handler.full_path, 'index.html')
	
	def test(self, handler):
		return os.path.isdir(handler.path) and \
				os.path.isfile(self.index_path(handler))
	
	def act(self, handler):
		handler.handler_file(self.index_path(handler))		
		
class ServerException(Exception):
	'''服务器内部错误'''
	pass

class RequestHandler(BaseHTTPRequestHandler):
	
	Cases = [
				case_no_files(),
				case_existing_files(),
				case_directory_index_file(),
				case_always_fail(),
			]

	Error_Page = """\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """
	
	def send_content(self, page, status=200):
		self.send_response(status)
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
		self.send_content(page.encode('utf-8'), 404)
	
	def do_GET(self):
		try:
			#os.getcwd() 是当前的工作目录，self.path 保存了请求的相对路径
			#不要忘了 RequestHandler 继承自 BaseHTTPRequestHandler
			#它已经帮我们将请求的相对路径保存在self.path中了。
			self.full_path = os.getcwd()+self.path
			
			for case in self.Cases:
				if case.test(self):
					case.act(self)
					break
				
		except Exception as msg:
			self.handler_error(msg)
			
if __name__ == '__main__':
	serverAddress = ('', 8080)
	server = HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()